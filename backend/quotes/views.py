from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Count
from .models import Quote
from .serializers import QuoteSerializer
from django.shortcuts import get_object_or_404
import pdfplumber
import io
import re


def extract_text_from_pdf(pdf_content: bytes) -> str:
    try:
        with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
            text = ''
            for page in pdf.pages:
                text += page.extract_text() or ''
        return text
    except Exception:
        return ''


def parse_quote_from_text(text: str) -> dict:
    # Simplified parsing adapted from server.py logic
    quote_data = {
        'procedure_name': '',
        'surgery_duration_hours': 0,
        'anesthesia_type': '',
        'facility_fee': 0.0,
        'equipment_costs': 0.0,
        'anesthesia_fee': 0.0,
        'other_costs': 0.0,
        'total_cost': 0.0,
        'created_by': 'Importación PDF',
        'notes': 'Cotización importada desde PDF',
    }

    t = text.replace('\n', ' ').replace('\t', ' ')
    t = re.sub(r'\s+', ' ', t).strip()

    # procedure
    m = re.search(r'(?:procedimiento|procedure|cirugía|surgery|operación)[\s:]*([^$\d]{5,100})', t, re.I)
    if m:
        quote_data['procedure_name'] = m.group(1).strip()[:200]

    # duration
    m = re.search(r'(?:duración|duration|tiempo)[\s:]*(\d+)[\s]*(?:horas?|hours?)', t, re.I)
    if m:
        quote_data['surgery_duration_hours'] = int(m.group(1))

    # costs
    m = re.search(r'(?:total|costo total|total cost)[\s:$]*(\$?[\d,]+\.?\d*)', t, re.I)
    if m:
        v = m.group(1).replace('$', '').replace(',', '')
        try:
            quote_data['total_cost'] = float(v)
        except:
            pass

    return quote_data


@api_view(['GET'])
def root(request):
    return Response({'message': 'Sistema de Gestión de Cotizaciones Quirúrgicas'})


@api_view(['POST'])
@parser_classes([MultiPartParser, FileUploadParser])
def upload_pdf(request):
    file = request.FILES.get('file')
    if not file or not file.name.lower().endswith('.pdf'):
        return Response({'detail': 'Solo se permiten archivos PDF'}, status=status.HTTP_400_BAD_REQUEST)

    content = file.read()
    text = extract_text_from_pdf(content)
    if not text:
        return Response({'success': False, 'message': 'No se pudo extraer texto del PDF', 'quotes_created': 0}, status=status.HTTP_400_BAD_REQUEST)

    quote_data = parse_quote_from_text(text)
    if not quote_data.get('procedure_name') or quote_data.get('surgery_duration_hours') == 0:
        return Response({'success': False, 'message': 'Información insuficiente en el PDF', 'quotes_created': 0, 'extracted_data': quote_data}, status=status.HTTP_400_BAD_REQUEST)

    # calculate total if not set
    if not quote_data.get('total_cost'):
        quote_data['total_cost'] = quote_data.get('facility_fee', 0) + quote_data.get('equipment_costs', 0) + quote_data.get('anesthesia_fee', 0) + quote_data.get('other_costs', 0)

    serializer = QuoteSerializer(data=quote_data)
    if serializer.is_valid():
        serializer.save()
        return Response({'success': True, 'message': 'Cotización creada exitosamente desde PDF', 'quotes_created': 1, 'extracted_data': quote_data})
    return Response({'success': False, 'message': 'Error validando datos', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def create_quote(request):
    data = request.data.copy()
    # compute total
    data['total_cost'] = float(data.get('facility_fee', 0)) + float(data.get('equipment_costs', 0)) + float(data.get('anesthesia_fee', 0)) + float(data.get('other_costs', 0))
    serializer = QuoteSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def list_quotes(request):
    procedure_name = request.GET.get('procedure_name')
    surgeon_name = request.GET.get('surgeon_name')
    qs = Quote.objects.all().order_by('-created_at')
    if procedure_name:
        qs = qs.filter(procedure_name__icontains=procedure_name)
    if surgeon_name:
        qs = qs.filter(surgeon_name__icontains=surgeon_name)
    serializer = QuoteSerializer(qs, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def retrieve_quote(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    serializer = QuoteSerializer(quote)
    return Response(serializer.data)


@api_view(['PUT'])
def update_quote(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    data = request.data.copy()
    data['total_cost'] = float(data.get('facility_fee', quote.facility_fee)) + float(data.get('equipment_costs', quote.equipment_costs)) + float(data.get('anesthesia_fee', quote.anesthesia_fee)) + float(data.get('other_costs', quote.other_costs))
    serializer = QuoteSerializer(quote, data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_quote(request, quote_id):
    quote = get_object_or_404(Quote, pk=quote_id)
    quote.delete()
    return Response({'message': 'Cotización eliminada exitosamente'})


@api_view(['GET'])
def pricing_suggestions(request, procedure_name):
    qs = Quote.objects.filter(procedure_name__icontains=procedure_name)
    stats = qs.aggregate(avg_facility_fee=Avg('facility_fee'), avg_equipment_costs=Avg('equipment_costs'), avg_total_cost=Avg('total_cost'), count=Count('id'))
    return Response({
        'procedure_name': procedure_name,
        'avg_facility_fee': round(stats['avg_facility_fee'] or 0, 2),
        'avg_equipment_costs': round(stats['avg_equipment_costs'] or 0, 2),
        'avg_total_cost': round(stats['avg_total_cost'] or 0, 2),
        'quote_count': stats['count'] or 0,
        'suggested_total': round(stats['avg_total_cost'] or 0, 2)
    })


@api_view(['GET'])
def procedures(request):
    procedures = Quote.objects.values_list('procedure_name', flat=True).distinct()
    return Response({'procedures': list(procedures)})


@api_view(['GET'])
def surgeons(request):
    surgeons = Quote.objects.values_list('surgeon_name', flat=True).distinct()
    return Response({'surgeons': list(surgeons)})


@api_view(['GET'])
def dashboard(request):
    total_quotes = Quote.objects.count()
    recent = Quote.objects.order_by('-created_at')[:5]
    top = Quote.objects.values('procedure_name').annotate(count=Count('id')).order_by('-count')[:5]
    return Response({
        'total_quotes': total_quotes,
        'recent_quotes': QuoteSerializer(recent, many=True).data,
        'top_procedures': [{'name': t['procedure_name'], 'count': t['count']} for t in top]
    })
