from django.urls import path
from . import views

urlpatterns = [
    path('', views.root, name='root'),
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
    path('quotes/', views.list_quotes, name='list_quotes'),
    path('quotes/create/', views.create_quote, name='create_quote'),
    path('quotes/<str:quote_id>/', views.retrieve_quote, name='retrieve_quote'),
    path('quotes/<str:quote_id>/update/', views.update_quote, name='update_quote'),
    path('quotes/<str:quote_id>/delete/', views.delete_quote, name='delete_quote'),
    path('pricing-suggestions/<str:procedure_name>/', views.pricing_suggestions, name='pricing_suggestions'),
    path('procedures/', views.procedures, name='procedures'),
    path('surgeons/', views.surgeons, name='surgeons'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
