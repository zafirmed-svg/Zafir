import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Textarea } from "./components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Badge } from "./components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { Alert, AlertDescription } from "./components/ui/alert";
import { Separator } from "./components/ui/separator";
import { Checkbox } from "./components/ui/checkbox";
import { Progress } from "./components/ui/progress";
import { CalendarIcon, DollarSign, FileText, Plus, Search, TrendingUp, Users, Clock, Calculator, Package, Heart, Stethoscope, Activity, Upload, FileUp, CheckCircle, XCircle } from "lucide-react";

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [quotes, setQuotes] = useState([]);
  const [filteredQuotes, setFilteredQuotes] = useState([]);
  const [procedures, setProcedures] = useState([]);
  const [surgeons, setSurgeons] = useState([]);
  const [dashboardStats, setDashboardStats] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterProcedure, setFilterProcedure] = useState("");
  const [selectedQuote, setSelectedQuote] = useState(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isPDFDialogOpen, setIsPDFDialogOpen] = useState(false);
  const [pricingSuggestions, setPricingSuggestions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [pdfProcessing, setPdfProcessing] = useState(false);
  const [pdfResult, setPdfResult] = useState(null);

  // Form state for new quote (changed estimated_duration to surgery_duration_hours)
  const [formData, setFormData] = useState({
    patient_id: "",
    patient_age: "",
    patient_phone: "",
    patient_email: "",
    procedure_name: "",
    procedure_code: "",
    procedure_description: "",
    surgeon_name: "",
    surgeon_specialty: "",
    facility_fee: "",
    equipment_costs: "",
    anesthesia_fee: "",
    other_costs: "",
    surgery_duration_hours: "", // Changed to hours only
    created_by: "Administrador",
    notes: "",
    surgical_package: {
      medications_included: [],
      postoperative_care: [],
      hospital_stay_nights: "",
      special_equipment: [],
      dietary_plan: false,
      additional_services: []
    }
  });

  useEffect(() => {
    fetchDashboardData();
    fetchQuotes();
    fetchProcedures();
    fetchSurgeons();
  }, []);

  useEffect(() => {
    filterQuotes();
  }, [quotes, searchTerm, filterProcedure]);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API}/dashboard`);
      setDashboardStats(response.data);
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
    }
  };

  const fetchQuotes = async () => {
    try {
      const response = await axios.get(`${API}/quotes`);
      setQuotes(response.data);
    } catch (error) {
      console.error("Error fetching quotes:", error);
    }
  };

  const fetchProcedures = async () => {
    try {
      const response = await axios.get(`${API}/procedures`);
      setProcedures(response.data.procedures);
    } catch (error) {
      console.error("Error fetching procedures:", error);
    }
  };

  const fetchSurgeons = async () => {
    try {
      const response = await axios.get(`${API}/surgeons`);
      setSurgeons(response.data.surgeons);
    } catch (error) {
      console.error("Error fetching surgeons:", error);
    }
  };

  const fetchPricingSuggestions = async (procedureName) => {
    if (!procedureName) return;
    try {
      setLoading(true);
      const response = await axios.get(`${API}/pricing-suggestions/${procedureName}`);
      setPricingSuggestions(response.data);
    } catch (error) {
      console.error("Error fetching pricing suggestions:", error);
    } finally {
      setLoading(false);
    }
  };

  const filterQuotes = () => {
    let filtered = quotes;
    
    if (searchTerm) {
      filtered = filtered.filter(quote => 
        (quote.patient_id && quote.patient_id.toLowerCase().includes(searchTerm.toLowerCase())) ||
        quote.procedure_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (quote.surgeon_name && quote.surgeon_name.toLowerCase().includes(searchTerm.toLowerCase()))
      );
    }
    
    if (filterProcedure && filterProcedure !== "todos") {
      filtered = filtered.filter(quote => quote.procedure_name === filterProcedure);
    }
    
    setFilteredQuotes(filtered);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Fetch pricing suggestions when procedure name changes
    if (name === 'procedure_name' && value.length > 2) {
      fetchPricingSuggestions(value);
    }
  };

  const handlePackageChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      surgical_package: {
        ...prev.surgical_package,
        [field]: value
      }
    }));
  };

  const handleArrayChange = (field, value) => {
    const items = value.split(',').map(item => item.trim()).filter(item => item);
    handlePackageChange(field, items);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      const submitData = {
        ...formData,
        patient_age: formData.patient_age ? parseInt(formData.patient_age) : null,
        facility_fee: parseFloat(formData.facility_fee) || 0,
        equipment_costs: parseFloat(formData.equipment_costs) || 0,
        anesthesia_fee: parseFloat(formData.anesthesia_fee) || 0,
        other_costs: parseFloat(formData.other_costs) || 0,
        surgery_duration_hours: parseInt(formData.surgery_duration_hours) || 0, // Changed to integer
        surgical_package: {
          ...formData.surgical_package,
          hospital_stay_nights: parseInt(formData.surgical_package.hospital_stay_nights) || 0
        }
      };

      await axios.post(`${API}/quotes`, submitData);
      setIsCreateDialogOpen(false);
      setFormData({
        patient_id: "",
        patient_age: "",
        patient_phone: "",
        patient_email: "",
        procedure_name: "",
        procedure_code: "",
        procedure_description: "",
        surgeon_name: "",
        surgeon_specialty: "",
        facility_fee: "",
        equipment_costs: "",
        anesthesia_fee: "",
        other_costs: "",
        surgery_duration_hours: "",
        created_by: "Administrador",
        notes: "",
        surgical_package: {
          medications_included: [],
          postoperative_care: [],
          hospital_stay_nights: "",
          special_equipment: [],
          dietary_plan: false,
          additional_services: []
        }
      });
      setPricingSuggestions(null);
      fetchQuotes();
      fetchDashboardData();
    } catch (error) {
      console.error("Error creating quote:", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePDFUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      alert('Por favor, seleccione solo archivos PDF');
      return;
    }

    try {
      setPdfProcessing(true);
      setPdfResult(null);

      const formData = new FormData();
      formData.append('file', file);

      const response = await axios.post(`${API}/upload-pdf`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setPdfResult(response.data);
      
      if (response.data.success) {
        // Refresh data after successful import
        await fetchQuotes();
        await fetchDashboardData();
        await fetchProcedures();
        await fetchSurgeons();
      }
    } catch (error) {
      console.error("Error uploading PDF:", error);
      setPdfResult({
        success: false,
        message: "Error al procesar el archivo PDF",
        quotes_created: 0,
        errors: [error.message]
      });
    } finally {
      setPdfProcessing(false);
    }
  };

  const applySuggestions = () => {
    if (pricingSuggestions) {
      setFormData(prev => ({
        ...prev,
        facility_fee: pricingSuggestions.avg_facility_fee.toString(),
        equipment_costs: pricingSuggestions.avg_equipment_costs.toString()
      }));
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('es-MX', {
      style: 'currency',
      currency: 'MXN'
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-ES');
  };

  const formatHours = (hours) => {
    if (!hours && hours !== 0) return 'N/A';
    if (hours === 1) return `${hours} hora`;
    return `${hours} horas`;
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'borrador': { label: 'Borrador', variant: 'secondary' },
      'aprobado': { label: 'Aprobado', variant: 'default' },
      'enviado': { label: 'Enviado', variant: 'outline' },
      'vencido': { label: 'Vencido', variant: 'destructive' }
    };
    const statusInfo = statusMap[status] || { label: status, variant: 'secondary' };
    return <Badge variant={statusInfo.variant}>{statusInfo.label}</Badge>;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <img 
                src="https://customer-assets.emergentagent.com/job_surgery-quotes/artifacts/2316l26e_zafir%20chico.png"
                alt="Zafir Medical Center"
                className="h-12 w-auto"
              />
              <div>
                <h1 className="text-2xl font-bold text-slate-900">Cotizaciones Quirúrgicas</h1>
                <p className="text-sm text-slate-600">Sistema de Gestión</p>
              </div>
            </div>
            <div className="flex space-x-3">
              {/* PDF Upload Dialog */}
              <Dialog open={isPDFDialogOpen} onOpenChange={setIsPDFDialogOpen}>
                <DialogTrigger asChild>
                  <Button variant="outline" className="border-blue-300 text-blue-700 hover:bg-blue-50">
                    <Upload className="mr-2 h-4 w-4" />
                    Importar PDF
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle className="flex items-center">
                      <FileUp className="mr-2 h-5 w-5" />
                      Importar Cotización desde PDF
                    </DialogTitle>
                    <DialogDescription>
                      Sube un archivo PDF con una cotización quirúrgica y la información se extraerá automáticamente
                    </DialogDescription>
                  </DialogHeader>
                  
                  <div className="space-y-6">
                    {/* File Upload Area */}
                    <div className="border-2 border-dashed border-slate-300 rounded-lg p-8 text-center">
                      <FileUp className="mx-auto h-12 w-12 text-slate-400 mb-4" />
                      <h3 className="text-lg font-medium text-slate-900 mb-2">
                        Seleccionar archivo PDF
                      </h3>
                      <p className="text-sm text-slate-600 mb-4">
                        El sistema extraerá automáticamente la información de la cotización
                      </p>
                      <input
                        type="file"
                        accept=".pdf"
                        onChange={handlePDFUpload}
                        className="hidden"
                        id="pdf-upload"
                        disabled={pdfProcessing}
                      />
                      <label
                        htmlFor="pdf-upload"
                        className={`inline-flex items-center px-4 py-2 border border-blue-300 text-blue-700 rounded-md cursor-pointer hover:bg-blue-50 ${
                          pdfProcessing ? 'opacity-50 cursor-not-allowed' : ''
                        }`}
                      >
                        {pdfProcessing ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                            Procesando...
                          </>
                        ) : (
                          <>
                            <Upload className="mr-2 h-4 w-4" />
                            Seleccionar PDF
                          </>
                        )}
                      </label>
                    </div>

                    {/* Processing Progress */}
                    {pdfProcessing && (
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span>Procesando PDF...</span>
                          <span>Extrayendo información</span>
                        </div>
                        <Progress value={65} className="w-full" />
                      </div>
                    )}

                    {/* Results */}
                    {pdfResult && (
                      <Alert className={pdfResult.success ? "border-green-200 bg-green-50" : "border-red-200 bg-red-50"}>
                        {pdfResult.success ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-600" />
                        )}
                        <AlertDescription>
                          <div className="space-y-2">
                            <p className={pdfResult.success ? "text-green-800" : "text-red-800"}>
                              <strong>{pdfResult.message}</strong>
                            </p>
                            {pdfResult.success && (
                              <p className="text-green-700">
                                Se creó {pdfResult.quotes_created} cotización exitosamente.
                              </p>
                            )}
                            {pdfResult.extracted_data && (
                              <div className="mt-3 p-3 bg-white rounded border text-sm">
                                <p><strong>Información extraída:</strong></p>
                                <ul className="mt-1 space-y-1 text-slate-600">
                                  {pdfResult.extracted_data.patient_id && (
                                    <li>• ID Paciente: {pdfResult.extracted_data.patient_id}</li>
                                  )}
                                  {pdfResult.extracted_data.procedure_name && (
                                    <li>• Procedimiento: {pdfResult.extracted_data.procedure_name}</li>
                                  )}
                                  {pdfResult.extracted_data.surgeon_name && (
                                    <li>• Cirujano: {pdfResult.extracted_data.surgeon_name}</li>
                                  )}
                                  {pdfResult.extracted_data.surgery_duration_hours && (
                                    <li>• Duración: {formatHours(pdfResult.extracted_data.surgery_duration_hours)}</li>
                                  )}
                                  {pdfResult.extracted_data.total_cost > 0 && (
                                    <li>• Costo Total: {formatCurrency(pdfResult.extracted_data.total_cost)}</li>
                                  )}
                                </ul>
                              </div>
                            )}
                            {pdfResult.errors && pdfResult.errors.length > 0 && (
                              <div className="mt-2 text-red-700">
                                <p><strong>Errores:</strong></p>
                                <ul className="list-disc list-inside">
                                  {pdfResult.errors.map((error, index) => (
                                    <li key={index}>{error}</li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        </AlertDescription>
                      </Alert>
                    )}

                    {/* Instructions */}
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">Información que se puede extraer:</h4>
                      <ul className="text-sm text-blue-800 space-y-1">
                        <li>• ID del paciente y datos de contacto</li>
                        <li>• Nombre del procedimiento quirúrgico</li>
                        <li>• Información del cirujano (opcional)</li>
                        <li>• Costos (instalaciones, equipos, anestesia)</li>
                        <li>• Duración de la cirugía en horas (requerido)</li>
                        <li>• Medicamentos y equipo especial</li>
                      </ul>
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <Button
                      variant="outline"
                      onClick={() => setIsPDFDialogOpen(false)}
                    >
                      Cerrar
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>

              {/* Create Quote Dialog */}
              <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                <DialogTrigger asChild>
                  <Button className="bg-blue-600 hover:bg-blue-700">
                    <Plus className="mr-2 h-4 w-4" />
                    Nueva Cotización
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>Crear Nueva Cotización Quirúrgica</DialogTitle>
                    <DialogDescription>
                      Complete los detalles a continuación para crear una nueva cotización quirúrgica
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Patient Information */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center">
                          <Users className="mr-2 h-5 w-5" />
                          Información del Paciente
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="patient_id">ID del Paciente</Label>
                          <Input
                            id="patient_id"
                            name="patient_id"
                            value={formData.patient_id}
                            onChange={handleInputChange}
                          />
                        </div>
                        <div>
                          <Label htmlFor="patient_age">Edad</Label>
                          <Input
                            id="patient_age"
                            name="patient_age"
                            type="number"
                            value={formData.patient_age}
                            onChange={handleInputChange}
                          />
                        </div>
                        <div>
                          <Label htmlFor="patient_phone">Teléfono</Label>
                          <Input
                            id="patient_phone"
                            name="patient_phone"
                            value={formData.patient_phone}
                            onChange={handleInputChange}
                          />
                        </div>
                        <div>
                          <Label htmlFor="patient_email">Correo Electrónico</Label>
                          <Input
                            id="patient_email"
                            name="patient_email"
                            type="email"
                            value={formData.patient_email}
                            onChange={handleInputChange}
                          />
                        </div>
                      </CardContent>
                    </Card>

                    {/* Procedure Information */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center">
                          <Activity className="mr-2 h-5 w-5" />
                          Información del Procedimiento
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="procedure_name">Nombre del Procedimiento *</Label>
                            <Input
                              id="procedure_name"
                              name="procedure_name"
                              value={formData.procedure_name}
                              onChange={handleInputChange}
                              required
                            />
                          </div>
                          <div>
                            <Label htmlFor="procedure_code">Código del Procedimiento</Label>
                            <Input
                              id="procedure_code"
                              name="procedure_code"
                              value={formData.procedure_code}
                              onChange={handleInputChange}
                            />
                          </div>
                        </div>
                        <div>
                          <Label htmlFor="procedure_description">Descripción</Label>
                          <Textarea
                            id="procedure_description"
                            name="procedure_description"
                            value={formData.procedure_description}
                            onChange={handleInputChange}
                            rows={3}
                          />
                        </div>
                      </CardContent>
                    </Card>

                    {/* Pricing Suggestions */}
                    {pricingSuggestions && pricingSuggestions.quote_count > 0 && (
                      <Alert className="border-blue-200 bg-blue-50">
                        <Calculator className="h-4 w-4" />
                        <AlertDescription>
                          <div className="flex justify-between items-center">
                            <div>
                              <strong>Datos Históricos Disponibles:</strong> Basado en {pricingSuggestions.quote_count} procedimientos similares
                              <br />
                              Promedio Total: {formatCurrency(pricingSuggestions.avg_total_cost)}
                            </div>
                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={applySuggestions}
                              className="border-blue-300 text-blue-700 hover:bg-blue-100"
                            >
                              Aplicar Sugerencias
                            </Button>
                          </div>
                        </AlertDescription>
                      </Alert>
                    )}

                    {/* Surgeon Information (now optional) */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center">
                          <Heart className="mr-2 h-5 w-5" />
                          Información del Cirujano
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="surgeon_name">Nombre del Cirujano</Label>
                          <Input
                            id="surgeon_name"
                            name="surgeon_name"
                            value={formData.surgeon_name}
                            onChange={handleInputChange}
                          />
                        </div>
                        <div>
                          <Label htmlFor="surgeon_specialty">Especialidad</Label>
                          <Input
                            id="surgeon_specialty"
                            name="surgeon_specialty"
                            value={formData.surgeon_specialty}
                            onChange={handleInputChange}
                          />
                        </div>
                      </CardContent>
                    </Card>

                    {/* Cost Breakdown */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center">
                          <DollarSign className="mr-2 h-5 w-5" />
                          Desglose de Costos
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="grid grid-cols-2 gap-4">
                        <div>
                          <Label htmlFor="facility_fee">Costo de Instalaciones *</Label>
                          <Input
                            id="facility_fee"
                            name="facility_fee"
                            type="number"
                            step="0.01"
                            value={formData.facility_fee}
                            onChange={handleInputChange}
                            required
                          />
                        </div>
                        <div>
                          <Label htmlFor="equipment_costs">Costo de Equipos *</Label>
                          <Input
                            id="equipment_costs"
                            name="equipment_costs"
                            type="number"
                            step="0.01"
                            value={formData.equipment_costs}
                            onChange={handleInputChange}
                            required
                          />
                        </div>
                        <div>
                          <Label htmlFor="anesthesia_fee">Costo de Anestesia</Label>
                          <Input
                            id="anesthesia_fee"
                            name="anesthesia_fee"
                            type="number"
                            step="0.01"
                            value={formData.anesthesia_fee}
                            onChange={handleInputChange}
                          />
                        </div>
                        <div>
                          <Label htmlFor="other_costs">Otros Costos</Label>
                          <Input
                            id="other_costs"
                            name="other_costs"
                            type="number"
                            step="0.01"
                            value={formData.other_costs}
                            onChange={handleInputChange}
                          />
                        </div>
                      </CardContent>
                    </Card>

                    {/* Surgery Duration (now hours only) */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center">
                          <Clock className="mr-2 h-5 w-5" />
                          Duración de la Cirugía
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="w-full md:w-1/2">
                          <Label htmlFor="surgery_duration_hours">Duración en Horas *</Label>
                          <Input
                            id="surgery_duration_hours"
                            name="surgery_duration_hours"
                            type="number"
                            min="1"
                            max="24"
                            value={formData.surgery_duration_hours}
                            onChange={handleInputChange}
                            placeholder="Ej: 3"
                            required
                          />
                          <p className="text-xs text-slate-500 mt-1">Ingrese solo horas cerradas (números enteros)</p>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Surgical Package Details */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg flex items-center">
                          <Package className="mr-2 h-5 w-5" />
                          Detalles del Paquete Quirúrgico
                        </CardTitle>
                        <CardDescription>
                          Especifique qué está incluido en el paquete quirúrgico
                        </CardDescription>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label>Medicamentos Incluidos</Label>
                            <Textarea
                              placeholder="Ej: Antibióticos, Analgésicos, Antiinflamatorios (separados por comas)"
                              value={formData.surgical_package.medications_included.join(', ')}
                              onChange={(e) => handleArrayChange('medications_included', e.target.value)}
                              rows={2}
                            />
                          </div>
                          <div>
                            <Label>Cuidados Postoperatorios</Label>
                            <Textarea
                              placeholder="Ej: Curaciones, Controles, Retiro de puntos (separados por comas)"
                              value={formData.surgical_package.postoperative_care.join(', ')}
                              onChange={(e) => handleArrayChange('postoperative_care', e.target.value)}
                              rows={2}
                            />
                          </div>
                          <div>
                            <Label>Equipo Especial</Label>
                            <Textarea
                              placeholder="Ej: Prótesis, Implantes, Dispositivos médicos (separados por comas)"
                              value={formData.surgical_package.special_equipment.join(', ')}
                              onChange={(e) => handleArrayChange('special_equipment', e.target.value)}
                              rows={2}
                            />
                          </div>
                          <div>
                            <Label>Servicios Adicionales</Label>
                            <Textarea
                              placeholder="Ej: Transporte, Acompañante, Servicios especiales (separados por comas)"
                              value={formData.surgical_package.additional_services.join(', ')}
                              onChange={(e) => handleArrayChange('additional_services', e.target.value)}
                              rows={2}
                            />
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <Label htmlFor="hospital_stay_nights">Noches de Hospitalización</Label>
                            <Input
                              id="hospital_stay_nights"
                              type="number"
                              value={formData.surgical_package.hospital_stay_nights}
                              onChange={(e) => handlePackageChange('hospital_stay_nights', e.target.value)}
                            />
                          </div>
                          <div className="flex items-center space-x-2 pt-6">
                            <Checkbox
                              id="dietary_plan"
                              checked={formData.surgical_package.dietary_plan}
                              onCheckedChange={(checked) => handlePackageChange('dietary_plan', checked)}
                            />
                            <Label htmlFor="dietary_plan">Incluye Plan Dietético</Label>
                          </div>
                        </div>
                      </CardContent>
                    </Card>

                    {/* Notes */}
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Notas Adicionales</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <Textarea
                          id="notes"
                          name="notes"
                          value={formData.notes}
                          onChange={handleInputChange}
                          rows={3}
                          placeholder="Notas adicionales o consideraciones especiales..."
                        />
                      </CardContent>
                    </Card>

                    <div className="flex justify-end space-x-3">
                      <Button
                        type="button"
                        variant="outline"
                        onClick={() => setIsCreateDialogOpen(false)}
                      >
                        Cancelar
                      </Button>
                      <Button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700">
                        {loading ? "Creando..." : "Crear Cotización"}
                      </Button>
                    </div>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs defaultValue="dashboard" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 bg-white border border-slate-200">
            <TabsTrigger value="dashboard" className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4" />
              <span>Panel de Control</span>
            </TabsTrigger>
            <TabsTrigger value="quotes" className="flex items-center space-x-2">
              <FileText className="h-4 w-4" />
              <span>Todas las Cotizaciones</span>
            </TabsTrigger>
            <TabsTrigger value="analysis" className="flex items-center space-x-2">
              <Calculator className="h-4 w-4" />
              <span>Análisis</span>
            </TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            {dashboardStats && (
              <>
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <Card className="bg-white border-slate-200">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium text-slate-600">Total de Cotizaciones</CardTitle>
                      <FileText className="h-4 w-4 text-blue-600" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-slate-900">{dashboardStats.total_quotes}</div>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-white border-slate-200">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium text-slate-600">Procedimientos Principales</CardTitle>
                      <TrendingUp className="h-4 w-4 text-green-600" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-slate-900">
                        {dashboardStats.top_procedures.length}
                      </div>
                      <p className="text-xs text-slate-500 mt-1">Diferentes procedimientos</p>
                    </CardContent>
                  </Card>
                  
                  <Card className="bg-white border-slate-200">
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                      <CardTitle className="text-sm font-medium text-slate-600">Actividad Reciente</CardTitle>
                      <Clock className="h-4 w-4 text-purple-600" />
                    </CardHeader>
                    <CardContent>
                      <div className="text-2xl font-bold text-slate-900">
                        {dashboardStats.recent_quotes.length}
                      </div>
                      <p className="text-xs text-slate-500 mt-1">Cotizaciones recientes</p>
                    </CardContent>
                  </Card>
                </div>

                {/* Recent Quotes and Top Procedures */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card className="bg-white border-slate-200">
                    <CardHeader>
                      <CardTitle>Cotizaciones Recientes</CardTitle>
                      <CardDescription>Últimas cotizaciones quirúrgicas creadas</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {dashboardStats.recent_quotes.map((quote) => (
                          <div key={quote.id} className="flex items-center justify-between border-b border-slate-100 pb-3">
                            <div>
                              <p className="font-medium text-slate-900">{quote.patient_id || 'ID N/A'}</p>
                              <p className="text-sm text-slate-600">{quote.procedure_name}</p>
                              <p className="text-xs text-slate-500">⏱️ {formatHours(quote.surgery_duration_hours)}</p>
                            </div>
                            <div className="text-right">
                              <p className="font-semibold text-green-600">{formatCurrency(quote.total_cost)}</p>
                              <p className="text-xs text-slate-500">{formatDate(quote.created_at)}</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-white border-slate-200">
                    <CardHeader>
                      <CardTitle>Procedimientos Principales</CardTitle>
                      <CardDescription>Procedimientos más cotizados</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-4">
                        {dashboardStats.top_procedures.map((proc, index) => (
                          <div key={index} className="flex items-center justify-between">
                            <div className="flex items-center space-x-3">
                              <div className="bg-blue-100 text-blue-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-semibold">
                                {index + 1}
                              </div>
                              <p className="font-medium text-slate-900">{proc.name}</p>
                            </div>
                            <Badge variant="secondary">{proc.count} cotizaciones</Badge>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </>
            )}
          </TabsContent>

          {/* Quotes Tab */}
          <TabsContent value="quotes" className="space-y-6">
            {/* Search and Filter */}
            <Card className="bg-white border-slate-200">
              <CardHeader>
                <CardTitle>Buscar y Filtrar Cotizaciones</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1">
                    <div className="relative">
                      <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />
                      <Input
                        placeholder="Buscar por ID del paciente, procedimiento o cirujano..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="pl-10"
                      />
                    </div>
                  </div>
                  <Select value={filterProcedure} onValueChange={setFilterProcedure}>
                    <SelectTrigger className="w-full md:w-64">
                      <SelectValue placeholder="Filtrar por procedimiento" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="todos">Todos los Procedimientos</SelectItem>
                      {procedures.map((procedure) => (
                        <SelectItem key={procedure} value={procedure}>
                          {procedure}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </CardContent>
            </Card>

            {/* Quotes List */}
            <div className="grid gap-4">
              {filteredQuotes.map((quote) => (
                <Card key={quote.id} className="bg-white border-slate-200 hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <h3 className="font-semibold text-slate-900">{quote.patient_id || 'ID N/A'}</h3>
                            <p className="text-sm text-slate-600">Edad: {quote.patient_age || 'N/A'}</p>
                            {quote.patient_email && (
                              <p className="text-sm text-slate-600">Email: {quote.patient_email}</p>
                            )}
                          </div>
                          <div>
                            <p className="font-medium text-slate-900">{quote.procedure_name}</p>
                            {quote.surgeon_name && (
                              <p className="text-sm text-slate-600">Dr. {quote.surgeon_name}</p>
                            )}
                            <p className="text-sm text-slate-600">{quote.surgeon_specialty || 'N/A'}</p>
                            <p className="text-sm text-blue-600 font-medium">⏱️ {formatHours(quote.surgery_duration_hours)}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-2xl font-bold text-green-600">{formatCurrency(quote.total_cost)}</p>
                            {getStatusBadge(quote.status)}
                          </div>
                        </div>
                        <Separator className="my-4" />
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-slate-600">Costo de Instalaciones:</span>
                            <p className="font-medium">{formatCurrency(quote.facility_fee)}</p>
                          </div>
                          <div>
                            <span className="text-slate-600">Equipos:</span>
                            <p className="font-medium">{formatCurrency(quote.equipment_costs)}</p>
                          </div>
                          <div>
                            <span className="text-slate-600">Anestesia:</span>
                            <p className="font-medium">{formatCurrency(quote.anesthesia_fee || 0)}</p>
                          </div>
                          <div>
                            <span className="text-slate-600">Otros:</span>
                            <p className="font-medium">{formatCurrency(quote.other_costs || 0)}</p>
                          </div>
                        </div>
                        
                        {/* Surgical Package Details */}
                        {quote.surgical_package && (
                          <div className="mt-4 p-4 bg-slate-50 rounded-lg">
                            <h4 className="font-semibold text-slate-900 mb-2 flex items-center">
                              <Package className="mr-2 h-4 w-4" />
                              Paquete Quirúrgico Incluido
                            </h4>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                              {quote.surgical_package.medications_included?.length > 0 && (
                                <div>
                                  <span className="font-medium text-slate-700">Medicamentos:</span>
                                  <p className="text-slate-600">{quote.surgical_package.medications_included.join(', ')}</p>
                                </div>
                              )}
                              {quote.surgical_package.postoperative_care?.length > 0 && (
                                <div>
                                  <span className="font-medium text-slate-700">Cuidados Postoperatorios:</span>
                                  <p className="text-slate-600">{quote.surgical_package.postoperative_care.join(', ')}</p>
                                </div>
                              )}
                              {quote.surgical_package.hospital_stay_nights > 0 && (
                                <div>
                                  <span className="font-medium text-slate-700">Hospitalización:</span>
                                  <p className="text-slate-600">{quote.surgical_package.hospital_stay_nights} noches</p>
                                </div>
                              )}
                              {quote.surgical_package.special_equipment?.length > 0 && (
                                <div>
                                  <span className="font-medium text-slate-700">Equipo Especial:</span>
                                  <p className="text-slate-600">{quote.surgical_package.special_equipment.join(', ')}</p>
                                </div>
                              )}
                              {quote.surgical_package.dietary_plan && (
                                <div>
                                  <span className="font-medium text-slate-700">Plan Dietético:</span>
                                  <p className="text-slate-600">Incluido</p>
                                </div>
                              )}
                              {quote.surgical_package.additional_services?.length > 0 && (
                                <div>
                                  <span className="font-medium text-slate-700">Servicios Adicionales:</span>
                                  <p className="text-slate-600">{quote.surgical_package.additional_services.join(', ')}</p>
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                        
                        {quote.notes && (
                          <div className="mt-3">
                            <p className="text-sm text-slate-600">
                              <strong>Notas:</strong> {quote.notes}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Analysis Tab */}
          <TabsContent value="analysis" className="space-y-6">
            <Card className="bg-white border-slate-200">
              <CardHeader>
                <CardTitle>Análisis de Cotizaciones</CardTitle>
                <CardDescription>
                  Analice tendencias de precios y obtenga información de datos históricos
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="analysis-procedure">Seleccionar Procedimiento para Análisis</Label>
                    <Select onValueChange={fetchPricingSuggestions}>
                      <SelectTrigger>
                        <SelectValue placeholder="Elegir un procedimiento" />
                      </SelectTrigger>
                      <SelectContent>
                        {procedures.map((procedure) => (
                          <SelectItem key={procedure} value={procedure}>
                            {procedure}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  {pricingSuggestions && pricingSuggestions.quote_count > 0 && (
                    <div className="mt-6">
                      <h3 className="text-lg font-semibold mb-4">Resultados del Análisis</h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <Card>
                          <CardHeader>
                            <CardTitle className="text-base">Desglose de Costos</CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-3">
                            <div className="flex justify-between">
                              <span>Promedio Costo de Instalaciones:</span>
                              <span className="font-semibold">{formatCurrency(pricingSuggestions.avg_facility_fee)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Promedio Costo de Equipos:</span>
                              <span className="font-semibold">{formatCurrency(pricingSuggestions.avg_equipment_costs)}</span>
                            </div>
                            <Separator />
                            <div className="flex justify-between text-lg">
                              <span className="font-semibold">Promedio Total:</span>
                              <span className="font-bold text-green-600">
                                {formatCurrency(pricingSuggestions.avg_total_cost)}
                              </span>
                            </div>
                          </CardContent>
                        </Card>

                        <Card>
                          <CardHeader>
                            <CardTitle className="text-base">Datos Históricos</CardTitle>
                          </CardHeader>
                          <CardContent>
                            <div className="text-center">
                              <div className="text-3xl font-bold text-blue-600 mb-2">
                                {pricingSuggestions.quote_count}
                              </div>
                              <p className="text-slate-600">Procedimientos similares en la base de datos</p>
                              <div className="mt-4">
                                <Badge variant="outline" className="text-xs">
                                  Precios basados en datos
                                </Badge>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  )}

                  {pricingSuggestions && pricingSuggestions.quote_count === 0 && (
                    <Alert>
                      <AlertDescription>
                        No hay datos históricos disponibles para este procedimiento. Considere esto como la primera cotización para establecer un punto de referencia para futuros procedimientos.
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

export default App;