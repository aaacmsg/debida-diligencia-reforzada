import { useEffect, useState } from 'react';
import { clienteService } from '../services/clienteService';
import { beneficiarioService } from '../services/beneficiarioService';
import type { Cliente, BeneficiarioFinalCreate } from '../types';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import {
  User,
  Plus,
  Edit2,
  Trash2,
  ChevronDown,
  ChevronUp,
  ChevronRight,
  Save,
  FileText,
  Shield,
  DollarSign,
  Users,
  AlertTriangle,
  CheckCircle,
  Clock,
  X,
  BarChart3
} from 'lucide-react';

const clienteSchema = z.object({
  tipo_persona: z.enum(['natural', 'juridica']),
  nombre: z.string().min(1, 'Requerido'),
  apellido: z.string().optional(),
  razon_social: z.string().optional(),
  tipo_identificacion: z.enum(['cedula', 'pasaporte', 'ruc']),
  numero_identificacion: z.string().min(1, 'Requerido'),
  fecha_nacimiento: z.string().optional(),
  nacionalidad: z.string().optional(),
  pais_residencia: z.string().optional(),
  direccion: z.string().optional(),
  telefono: z.string().optional(),
  correo: z.string().email('Email invalido').optional().or(z.literal('')),
  es_pep: z.boolean().default(false),
  cargo_pep: z.string().optional(),
  relacion_pep: z.string().optional(),
  pais_residencia_fiscal: z.string().optional(),
  actividad_economica: z.string().optional(),
  sector_economico: z.string().optional(),
  ingresos_anuales: z.number().optional(),
  patrimonio: z.number().optional(),
  origen_fondos: z.string().optional(),
  comentario_aprobacion: z.string().optional(),
}).superRefine((data, ctx) => {
  if (data.tipo_persona === 'natural' && (!data.nombre || data.nombre.trim() === '')) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Nombre requerido', path: ['nombre'] });
  }
  if (data.tipo_persona === 'juridica' && (!data.razon_social || data.razon_social.trim() === '')) {
    ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Razon social requerida para persona juridica', path: ['razon_social'] });
  }
  if (data.es_pep) {
    if (!data.cargo_pep || data.cargo_pep.trim() === '') {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Cargo PEP requerido cuando el cliente es PEP', path: ['cargo_pep'] });
    }
    if (!data.relacion_pep || data.relacion_pep.trim() === '') {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Tipo de relacion requerido cuando el cliente es PEP', path: ['relacion_pep'] });
    }
    if (!data.pais_residencia_fiscal || data.pais_residencia_fiscal.trim() === '') {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'Pais de residencia fiscal requerido cuando el cliente es PEP', path: ['pais_residencia_fiscal'] });
    }
  }
});

type ClienteFormData = z.infer<typeof clienteSchema>;

const modulos = [
  { id: 'identificacion', label: 'I. Identificacion del Cliente', icon: User },
  { id: 'financiera', label: 'II. Informacion Financiera', icon: DollarSign },
  { id: 'beneficiario', label: 'III. Beneficiario Final', icon: Users },
  { id: 'riesgo', label: 'IV. Perfil de Riesgo', icon: BarChart3 },
  { id: 'documentos', label: 'V. Documentacion', icon: FileText },
  { id: 'aprobacion', label: 'VI. Aprobacion y Control', icon: CheckCircle },
  { id: 'auditoria', label: 'VII. Registro de Auditoria', icon: Clock },
];

const PAISES_ALTO_RIESGO = ['iran', 'corea del norte', 'siria', 'cuba', 'venezuela', 'myanmar', 'afganistan', 'sudan', 'zimbabwe', 'yemen'];
const SECTORES_ALTO_RIESGO = ['construccion', 'bienes raiz', 'real estate', 'metales preciosos', 'oro', 'casinos', 'armas'];

export default function ClientesPage() {
  const [clientes, setClientes] = useState<Cliente[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [expandedModulos, setExpandedModulos] = useState<string[]>(['identificacion']);
  const [submitting, setSubmitting] = useState(false);
  const [editingCliente, setEditingCliente] = useState<Cliente | null>(null);
  const [beneficiarios, setBeneficiarios] = useState<BeneficiarioFinalCreate[]>([]);

  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm<ClienteFormData>({
    resolver: zodResolver(clienteSchema),
    defaultValues: {
      tipo_persona: 'natural',
      tipo_identificacion: 'cedula',
      es_pep: false,
    },
  });

  const watchTipoPersona = watch('tipo_persona');
  const watchEsPep = watch('es_pep');
  const watchOrigenFondos = watch('origen_fondos');

  useEffect(() => {
    fetchClientes();
  }, []);

  const fetchClientes = async () => {
    try {
      const data = await clienteService.list();
      setClientes(data);
    } catch (err) {
      toast.error('Error al cargar clientes');
    } finally {
      setLoading(false);
    }
  };

  const onSubmit = async (data: ClienteFormData) => {
    setSubmitting(true);
    try {
      const nuevoCliente = await clienteService.create(data);

      for (const bf of beneficiarios) {
        await beneficiarioService.create(nuevoCliente.id, bf);
      }

      toast.success('Cliente y expediente creados exitosamente');
      setShowForm(false);
      setBeneficiarios([]);
      reset();
      fetchClientes();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al guardar cliente');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEdit = async (cliente: Cliente) => {
    setEditingCliente(cliente);
    setShowForm(true);
    setExpandedModulos(['identificacion']);
    reset({
      tipo_persona: cliente.tipo_persona,
      nombre: cliente.nombre,
      apellido: cliente.apellido || '',
      razon_social: cliente.razon_social || '',
      tipo_identificacion: cliente.tipo_identificacion,
      numero_identificacion: cliente.numero_identificacion,
      fecha_nacimiento: cliente.fecha_nacimiento || '',
      nacionalidad: cliente.nacionalidad || '',
      pais_residencia: cliente.pais_residencia || '',
      direccion: cliente.direccion || '',
      telefono: cliente.telefono || '',
      correo: cliente.correo || '',
      es_pep: cliente.es_pep,
      cargo_pep: cliente.cargo_pep || '',
      relacion_pep: cliente.relacion_pep || '',
      pais_residencia_fiscal: cliente.pais_residencia_fiscal || '',
      actividad_economica: cliente.actividad_economica || '',
      sector_economico: cliente.sector_economico || '',
      ingresos_anuales: cliente.ingresos_anuales || undefined,
      patrimonio: cliente.patrimonio || undefined,
      origen_fondos: cliente.origen_fondos || '',
    });
    try {
      const beneficiariosExistentes = await beneficiarioService.list(cliente.id);
      setBeneficiarios(beneficiariosExistentes.map(b => ({
        nombre: b.nombre,
        apellido: b.apellido || '',
        numero_identificacion: b.numero_identificacion,
        porcentaje_participacion: b.porcentaje_participacion,
        tipo_control: b.tipo_control || 'accionista',
        pais_residencia: b.pais_residencia || '',
        es_pep: b.es_pep,
      })));
    } catch (err) {
      console.error('Error al cargar beneficiarios:', err);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Esta seguro de eliminar este cliente?')) return;
    try {
      await clienteService.delete(id);
      toast.success('Cliente eliminado');
      fetchClientes();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al eliminar cliente');
    }
  };

  const handleUpdate = async (data: ClienteFormData) => {
    if (!editingCliente) return;
    setSubmitting(true);
    try {
      await clienteService.update(editingCliente.id, data);
      toast.success('Cliente actualizado exitosamente');
      setShowForm(false);
      setEditingCliente(null);
      reset();
      fetchClientes();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Error al actualizar cliente');
    } finally {
      setSubmitting(false);
    }
  };

  const addBeneficiario = () => {
    const newBf: BeneficiarioFinalCreate = {
      nombre: '',
      apellido: '',
      numero_identificacion: '',
      porcentaje_participacion: 0,
      tipo_control: 'accionista',
      pais_residencia: '',
      es_pep: false,
    };
    setBeneficiarios([...beneficiarios, newBf]);
  };

  const updateBeneficiario = (index: number, field: keyof BeneficiarioFinalCreate, value: any) => {
    const updated = [...beneficiarios];
    (updated[index] as any)[field] = value;
    setBeneficiarios(updated);
  };

  const removeBeneficiario = (index: number) => {
    setBeneficiarios(beneficiarios.filter((_, i) => i !== index));
  };

  const sumaParticipaciones = beneficiarios.reduce((sum, bf) => sum + (Number(bf.porcentaje_participacion) || 0), 0);

  const getScorePais = () => {
    const pais = (watch('pais_residencia') || '').toLowerCase();
    for (const p of PAISES_ALTO_RIESGO) { if (pais.includes(p)) return 100; }
    return pais ? 25 : 0;
  };

  const getScoreCargo = () => {
    if (!watchEsPep) return 10;
    const cargo = (watch('cargo_pep') || '').toLowerCase();
    const altos = ['presidente', 'vicepresidente', 'ministro', 'director', 'gerente', 'magistrado'];
    for (const c of altos) { if (cargo.includes(c)) return 100; }
    return 60;
  };

  const getScoreSector = () => {
    const sector = (watch('sector_economico') || '').toLowerCase();
    for (const s of SECTORES_ALTO_RIESGO) { if (sector.includes(s)) return 100; }
    return sector ? 50 : 0;
  };

  const scoreTotal = (getScorePais() * 0.25) + (getScoreCargo() * 0.30) + (getScoreSector() * 0.15) + (beneficiarios.length > 0 ? 40 : 10) * 0.20 + (watchOrigenFondos ? 10 : 80) * 0.10;
  const nivelRiesgo = scoreTotal <= 35 ? 'Bajo' : scoreTotal <= 65 ? 'Medio' : 'Alto';

  const toggleModulo = (id: string) => {
    setExpandedModulos(prev =>
      prev.includes(id) ? prev.filter(m => m !== id) : [...prev, id]
    );
  };

  const sortByEstado = (a: Cliente, b: Cliente) => {
    const order: Record<string, number> = { alto: 0, medio: 1, bajo: 2 };
    return (order[(a as any).nivel_riesgo || 'bajo'] || 3) - (order[(b as any).nivel_riesgo || 'bajo'] || 3);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Clientes</h1>
          <p className="text-gray-500">Gestion de clientes y expedientes EDD</p>
        </div>
        <button
          onClick={() => { setShowForm(!showForm); setEditingCliente(null); reset(); setBeneficiarios([]); }}
          className="btn-primary flex items-center"
        >
          <Plus className="w-5 h-5 mr-2" />
          {showForm ? 'Cancelar' : 'Nuevo Cliente'}
        </button>
      </div>

      {showForm && (
        <div className="card">
          <h2 className="text-lg font-semibold mb-4 flex items-center">
            <Shield className="w-5 h-5 mr-2 text-primary-600" />
            {editingCliente ? 'Editar Cliente' : 'Formulario de Diligencia Reforzada (EDD)'}
          </h2>

          <form onSubmit={handleSubmit(editingCliente ? handleUpdate : onSubmit)} className="space-y-4">
            <div className="space-y-2">
              {modulos.map((modulo) => (
                <div key={modulo.id} className="border rounded-lg overflow-hidden">
                  <button
                    type="button"
                    onClick={() => toggleModulo(modulo.id)}
                    className="w-full flex items-center justify-between px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors"
                  >
                    <div className="flex items-center">
                      <modulo.icon className="w-5 h-5 mr-3 text-primary-600" />
                      <span className="font-medium">{modulo.label}</span>
                    </div>
                    {expandedModulos.includes(modulo.id) ? (
                      <ChevronUp className="w-5 h-5 text-gray-400" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400" />
                    )}
                  </button>

                  {expandedModulos.includes(modulo.id) && (
                    <div className="p-4 space-y-4 border-t">
                      {/* MODULO I - IDENTIFICACION */}
                      {modulo.id === 'identificacion' && (
                        <>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="label">Tipo de Persona *</label>
                              <select {...register('tipo_persona')} className="input">
                                <option value="natural">Persona Natural</option>
                                <option value="juridica">Persona Juridica</option>
                              </select>
                            </div>
                            <div>
                              <label className="label">Tipo de Identificacion *</label>
                              <select {...register('tipo_identificacion')} className="input">
                                <option value="cedula">Cedula</option>
                                <option value="pasaporte">Pasaporte</option>
                                <option value="ruc">RUC</option>
                              </select>
                            </div>
                          </div>

                          {watchTipoPersona === 'natural' ? (
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div>
                                <label className="label">Nombre *</label>
                                <input {...register('nombre')} className="input" />
                                {errors.nombre && <p className="text-red-500 text-xs mt-1">{errors.nombre.message}</p>}
                              </div>
                              <div>
                                <label className="label">Apellido</label>
                                <input {...register('apellido')} className="input" />
                              </div>
                            </div>
                          ) : (
                            <div>
                              <label className="label">Razon Social *</label>
                              <input {...register('razon_social')} className="input" />
                              {errors.razon_social && <p className="text-red-500 text-xs mt-1">{errors.razon_social.message}</p>}
                            </div>
                          )}

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="label">Numero de Identificacion *</label>
                              <input {...register('numero_identificacion')} className="input" />
                              {errors.numero_identificacion && (<p className="text-red-500 text-xs mt-1">{errors.numero_identificacion.message}</p>)}
                            </div>
                            <div>
                              <label className="label">Fecha de Nacimiento</label>
                              <input type="date" {...register('fecha_nacimiento')} className="input" />
                            </div>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="label">Nacionalidad</label>
                              <input {...register('nacionalidad')} className="input" />
                            </div>
                            <div>
                              <label className="label">Pais de Residencia</label>
                              <input {...register('pais_residencia')} className="input" />
                            </div>
                          </div>

                          <div>
                            <label className="label">Direccion</label>
                            <input {...register('direccion')} className="input" />
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="label">Telefono</label>
                              <input {...register('telefono')} className="input" />
                            </div>
                            <div>
                              <label className="label">Correo Electronico</label>
                              <input type="email" {...register('correo')} className="input" />
                            </div>
                          </div>

                          <div className="border-t pt-4 mt-4">
                            <div className="flex items-center mb-4">
                              <input
                                type="checkbox"
                                {...register('es_pep')}
                                className="w-4 h-4 text-primary-600 rounded mr-3"
                              />
                              <label className="label mb-0">El cliente es una Persona Expuesta Politicamente (PEP)</label>
                            </div>

                            {watchEsPep && (
                              <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-4">
                                <div className="flex items-center mb-2">
                                  <AlertTriangle className="w-5 h-5 text-amber-600 mr-2" />
                                  <h4 className="font-semibold text-amber-800">Informacion PEP Obligatoria</h4>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                  <div>
                                    <label className="label">Cargo Politico/Publico *</label>
                                    <select {...register('cargo_pep')} className="input">
                                      <option value="">Seleccione cargo</option>
                                      <option value="Presidente">Presidente</option>
                                      <option value="Vicepresidente">Vicepresidente</option>
                                      <option value="Ministro">Ministro</option>
                                      <option value="Viceministro">Viceministro</option>
                                      <option value="Director">Director</option>
                                      <option value="Gerente">Gerente</option>
                                      <option value="Secretario">Secretario</option>
                                      <option value="Subdirector">Subdirector</option>
                                      <option value="Jefe">Jefe</option>
                                      <option value="Magistrado">Magistrado</option>
                                      <option value="Vocal">Vocal</option>
                                      <option value="Embajador">Embajador</option>
                                      <option value="Otro">Otro</option>
                                    </select>
                                    {errors.cargo_pep && (<p className="text-red-500 text-xs mt-1">{errors.cargo_pep.message}</p>)}
                                  </div>
                                  <div>
                                    <label className="label">Tipo de Relacion *</label>
                                    <select {...register('relacion_pep')} className="input">
                                      <option value="">Seleccione</option>
                                      <option value="directo">Directo (ejerce el cargo)</option>
                                      <option value="indirecto">Indirecto (familiar o asociado)</option>
                                      <option value="representante">Representante legal</option>
                                    </select>
                                    {errors.relacion_pep && (<p className="text-red-500 text-xs mt-1">{errors.relacion_pep.message}</p>)}
                                  </div>
                                </div>
                                <div>
                                  <label className="label">Pais de Residencia Fiscal *</label>
                                  <input {...register('pais_residencia_fiscal')} className="input" placeholder="Ej: Panama, Estados Unidos, etc." />
                                  {errors.pais_residencia_fiscal && (<p className="text-red-500 text-xs mt-1">{errors.pais_residencia_fiscal.message}</p>)}
                                </div>
                              </div>
                            )}
                          </div>
                        </>
                      )}

                      {/* MODULO II - FINANCIERA */}
                      {modulo.id === 'financiera' && (
                        <>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="label">Actividad Economica</label>
                              <input {...register('actividad_economica')} className="input" />
                            </div>
                            <div>
                              <label className="label">Sector Economico</label>
                              <input {...register('sector_economico')} className="input" />
                            </div>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                              <label className="label">Ingresos Anuales (USD)</label>
                              <input type="number" step="0.01" {...register('ingresos_anuales', { valueAsNumber: true })} className="input" />
                            </div>
                            <div>
                              <label className="label">Patrimonio (USD)</label>
                              <input type="number" step="0.01" {...register('patrimonio', { valueAsNumber: true })} className="input" />
                            </div>
                          </div>
                          <div>
                            <label className="label">Origen de Fondos</label>
                            <textarea {...register('origen_fondos')} rows={3} className="input" placeholder="Describa el origen de los fondos..." />
                          </div>
                        </>
                      )}

                      {/* MODULO III - BENEFICIARIO FINAL */}
                      {modulo.id === 'beneficiario' && (
                        <>
                          <div className="flex items-center justify-between mb-4">
                            <p className="text-sm text-gray-600">
                              Identifique las personas naturales con control real o propiedad superior al 10%
                            </p>
                            <button type="button" onClick={addBeneficiario} className="btn-secondary flex items-center text-sm">
                              <Plus className="w-4 h-4 mr-1" /> Agregar
                            </button>
                          </div>

                          {sumaParticipaciones > 0 && (
                            <div className={`px-3 py-2 rounded text-sm font-medium mb-3 ${
                              sumaParticipaciones > 100 ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                            }`}>
                              Total participaciones: {sumaParticipaciones.toFixed(1)}%
                              {sumaParticipaciones > 100 && ' - Excede el 100%!'}
                            </div>
                          )}

                          {beneficiarios.length === 0 ? (
                            <div className="text-center py-8 text-gray-400">
                              <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                              <p>No hay beneficiarios finales registrados</p>
                              <p className="text-xs mt-1">Agregue al menos un beneficiario con participacion mayor a 10%</p>
                            </div>
                          ) : (
                            <div className="space-y-4">
                              {beneficiarios.map((bf, index) => (
                                <div key={index} className="bg-gray-50 rounded-lg p-4 border relative">
                                  <button
                                    type="button"
                                    onClick={() => removeBeneficiario(index)}
                                    className="absolute top-2 right-2 p-1 hover:bg-gray-200 rounded"
                                  >
                                    <X className="w-4 h-4 text-gray-500" />
                                  </button>
                                  <h5 className="font-medium text-sm mb-3">Beneficiario #{index + 1}</h5>
                                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                                    <div>
                                      <label className="label text-xs">Nombre *</label>
                                      <input value={bf.nombre} onChange={(e) => updateBeneficiario(index, 'nombre', e.target.value)} className="input text-sm" required />
                                    </div>
                                    <div>
                                      <label className="label text-xs">Apellido</label>
                                      <input value={bf.apellido} onChange={(e) => updateBeneficiario(index, 'apellido', e.target.value)} className="input text-sm" />
                                    </div>
                                    <div>
                                      <label className="label text-xs">Identificacion *</label>
                                      <input value={bf.numero_identificacion} onChange={(e) => updateBeneficiario(index, 'numero_identificacion', e.target.value)} className="input text-sm" required />
                                    </div>
                                  </div>
                                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-3">
                                    <div>
                                      <label className="label text-xs">% Participacion *</label>
                                      <input
                                        type="number"
                                        step="0.1"
                                        min="0"
                                        max="100"
                                        value={bf.porcentaje_participacion}
                                        onChange={(e) => updateBeneficiario(index, 'porcentaje_participacion', parseFloat(e.target.value) || 0)}
                                        className="input text-sm"
                                        required
                                      />
                                    </div>
                                    <div>
                                      <label className="label text-xs">Tipo de Control</label>
                                      <select value={bf.tipo_control} onChange={(e) => updateBeneficiario(index, 'tipo_control', e.target.value)} className="input text-sm">
                                        <option value="accionista">Accionista</option>
                                        <option value="representante">Representante Legal</option>
                                        <option value="beneficiario">Beneficiario Final</option>
                                        <option value="fiduciario">Fiduciario</option>
                                      </select>
                                    </div>
                                    <div>
                                      <label className="label text-xs">Pais de Residencia</label>
                                      <input value={bf.pais_residencia} onChange={(e) => updateBeneficiario(index, 'pais_residencia', e.target.value)} className="input text-sm" />
                                    </div>
                                  </div>
                                  <div className="flex items-center mt-3">
                                    <input
                                      type="checkbox"
                                      checked={bf.es_pep}
                                      onChange={(e) => updateBeneficiario(index, 'es_pep', e.target.checked)}
                                      className="w-4 h-4 text-primary-600 rounded mr-2"
                                    />
                                    <label className="label text-xs mb-0">Beneficiario es PEP</label>
                                  </div>
                                </div>
                              ))}
                            </div>
                          )}
                        </>
                      )}

                      {/* MODULO IV - RIESGO */}
                      {modulo.id === 'riesgo' && (
                        <div className="space-y-4">
                          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <p className="text-sm text-blue-800">
                              Calculo de nivel de riesgo basado en los datos ingresados en los modulos anteriores.
                            </p>
                          </div>

                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div className="bg-white border rounded-lg p-4">
                              <h5 className="font-medium text-sm mb-3">Variables del Calculo</h5>
                              <div className="space-y-2 text-sm">
                                <div className="flex justify-between"><span>Pais/Region (25%)</span><span className="font-medium">{getScorePais()}/100</span></div>
                                <div className="flex justify-between"><span>Cargo PEP (30%)</span><span className="font-medium">{watchEsPep ? getScoreCargo() : 'N/A'}/100</span></div>
                                <div className="flex justify-between"><span>Sector Economico (15%)</span><span className="font-medium">{getScoreSector()}/100</span></div>
                                <div className="flex justify-between"><span>Vinculos PEP (20%)</span><span className="font-medium">{beneficiarios.filter(b => b.es_pep).length > 0 ? '70' : '10'}/100</span></div>
                                <div className="flex justify-between"><span>Origen Fondos (10%)</span><span className="font-medium">{watchOrigenFondos ? '10' : '80'}/100</span></div>
                                <div className="border-t pt-2 flex justify-between font-semibold">
                                  <span>Score Total</span>
                                  <span>{scoreTotal.toFixed(1)}/100</span>
                                </div>
                                <div className="flex justify-between font-semibold">
                                  <span>Nivel de Riesgo</span>
                                  <span className={`px-2 py-0.5 rounded text-xs text-white font-bold ${
                                    nivelRiesgo === 'Alto' ? 'bg-red-500' : nivelRiesgo === 'Medio' ? 'bg-yellow-500' : 'bg-green-500'
                                  }`}>{nivelRiesgo}</span>
                                </div>
                              </div>
                            </div>

                            <div className="bg-white border rounded-lg p-4">
                              <h5 className="font-medium text-sm mb-3">Clasificacion</h5>
                              <div className="space-y-2 text-sm">
                                <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div><span>0-35: Bajo - Monitoreo estandar</span></div>
                                <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-yellow-500 mr-2"></div><span>36-65: Medio - Monitoreo intensificado</span></div>
                                <div className="flex items-center"><div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div><span>66-100: Alto - Diligencia Reforzada + Gerencia</span></div>
                              </div>
                              {watchEsPep && (
                                <div className="mt-3 bg-amber-50 border border-amber-200 rounded p-2 text-xs text-amber-800">
                                  Cliente marcado como PEP - Riesgo forzado a ALTO, requiere aprobacion gerencial
                                </div>
                              )}
                            </div>
                          </div>
                        </div>
                      )}

                      {/* MODULO V - DOCUMENTOS */}
                      {modulo.id === 'documentos' && (
                        <div className="space-y-4">
                          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                            <p className="text-sm text-blue-800">
                              Los documentos se adjuntan desde la pantalla de detalle del expediente
                              una vez el cliente ha sido creado.
                            </p>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                            <div className="border rounded-lg p-3 text-center">
                              <FileText className="w-8 h-8 mx-auto text-gray-400 mb-1" />
                              <span className="block text-gray-600">PDF</span>
                              <span className="text-xs text-gray-400">Documentos oficiales</span>
                            </div>
                            <div className="border rounded-lg p-3 text-center">
                              <FileText className="w-8 h-8 mx-auto text-gray-400 mb-1" />
                              <span className="block text-gray-600">PNG / JPG</span>
                              <span className="text-xs text-gray-400">Imagenes escaneadas</span>
                            </div>
                            <div className="border rounded-lg p-3 text-center">
                              <Shield className="w-8 h-8 mx-auto text-gray-400 mb-1" />
                              <span className="block text-gray-600">SHA-256</span>
                              <span className="text-xs text-gray-400">Integridad verificada</span>
                            </div>
                          </div>
                          {editingCliente && (
                            <div className="bg-gray-50 rounded-lg p-4 text-center">
                              <p className="text-sm text-gray-600 mb-2">Cliente ya creado. Vaya al expediente para adjuntar documentos.</p>
                              <button
                                type="button"
                                onClick={() => window.location.href = `/expedientes`}
                                className="btn-primary text-sm"
                              >
                                Ir a Expedientes
                              </button>
                            </div>
                          )}
                        </div>
                      )}

                      {/* MODULO VI - APROBACION */}
                      {modulo.id === 'aprobacion' && (
                        <div className="space-y-4">
                          <div className="bg-gray-50 border rounded-lg p-4">
                            <h5 className="font-medium text-sm mb-2">Flujo de Aprobacion</h5>
                            <div className="flex items-center space-x-2 text-sm text-gray-600">
                              <CheckCircle className="w-5 h-5 text-green-500" />
                              <span>Pendiente de envio a revision</span>
                              <ChevronRight className="w-4 h-4 text-gray-300" />
                              <CheckCircle className="w-5 h-5 text-gray-300" />
                              <span>Revision de cumplimiento</span>
                              <ChevronRight className="w-4 h-4 text-gray-300" />
                              <CheckCircle className="w-5 h-5 text-gray-300" />
                              <span>Aprobacion gerencial</span>
                            </div>
                          </div>

                          {watchEsPep && (
                            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                              <h5 className="font-medium text-sm text-red-800 mb-2">Alerta: Cliente de Alto Riesgo (PEP)</h5>
                              <p className="text-xs text-red-600">
                                Este cliente requiere aprobacion obligatoria de Alta Gerencia.
                                Se generara un expediente con estado "pendiente_gerencia".
                              </p>
                            </div>
                          )}

                          {editingCliente && (
                            <div>
                              <label className="label">Comentario de Aprobacion</label>
                              <textarea {...register('comentario_aprobacion')} rows={3} className="input" placeholder="Justificacion de la aprobacion..." />
                            </div>
                          )}
                        </div>
                      )}

                      {/* MODULO VII - AUDITORIA */}
                      {modulo.id === 'auditoria' && (
                        <div className="space-y-4">
                          <div className="bg-gray-50 border rounded-lg p-4">
                            <p className="text-sm text-gray-600">
                              Todos los cambios quedan registrados en el log de auditoria con fecha, hora exacta y usuario.
                            </p>
                          </div>
                          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-sm">
                            <div className="border rounded-lg p-3">
                              <h6 className="font-medium">Trazabilidad</h6>
                              <p className="text-xs text-gray-500">Cada accion registra: fecha UTC, usuario, ip_address</p>
                            </div>
                            <div className="border rounded-lg p-3">
                              <h6 className="font-medium">Inmutabilidad</h6>
                              <p className="text-xs text-gray-500">Los eventos de auditoria no pueden ser modificados ni eliminados</p>
                            </div>
                            <div className="border rounded-lg p-3">
                              <h6 className="font-medium">Retencion</h6>
                              <p className="text-xs text-gray-500">Minimo 5 anos segun Ley 23/2015</p>
                            </div>
                          </div>
                          {editingCliente && (
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-sm text-blue-800">
                              Para ver el historial completo de eventos, vaya a la pagina de Reportes.
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}
                </div>
              ))}
            </div>

            <div className="flex justify-end pt-4 border-t space-x-3">
              <button
                type="button"
                onClick={() => { setShowForm(false); setEditingCliente(null); }}
                className="btn-secondary"
              >
                Cancelar
              </button>
              <button
                type="submit"
                disabled={submitting || sumaParticipaciones > 100}
                className="btn-primary flex items-center"
              >
                {submitting ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Guardando...
                  </>
                ) : (
                  <>
                    <Save className="w-5 h-5 mr-2" />
                    {editingCliente ? 'Actualizar Cliente' : 'Guardar Cliente y Crear Expediente'}
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Lista de Clientes */}
      <div className="card">
        <h2 className="text-lg font-semibold mb-4">Clientes Registrados</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-sm text-gray-500 border-b">
                <th className="pb-3 font-medium">Nombre</th>
                <th className="pb-3 font-medium">Identificacion</th>
                <th className="pb-3 font-medium">Tipo</th>
                <th className="pb-3 font-medium">PEP</th>
                <th className="pb-3 font-medium">Cargo</th>
                <th className="pb-3 font-medium">Acciones</th>
              </tr>
            </thead>
            <tbody className="text-sm">
              {clientes.sort(sortByEstado).map((cliente) => (
                <tr key={cliente.id} className="border-b last:border-0 hover:bg-gray-50">
                  <td className="py-3 font-medium">
                    {cliente.tipo_persona === 'juridica'
                      ? cliente.razon_social
                      : `${cliente.nombre} ${cliente.apellido || ''}`}
                  </td>
                  <td className="py-3 text-gray-500">{cliente.numero_identificacion}</td>
                  <td className="py-3">
                    <span className="px-2 py-1 bg-gray-100 rounded text-xs">
                      {cliente.tipo_persona === 'natural' ? 'Natural' : 'Juridica'}
                    </span>
                  </td>
                  <td className="py-3">
                    {cliente.es_pep ? (
                      <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-medium">SI</span>
                    ) : (
                      <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">No</span>
                    )}
                  </td>
                  <td className="py-3 text-xs text-gray-500">{cliente.cargo_pep || '-'}</td>
                  <td className="py-3">
                    <div className="flex space-x-2">
                      <button onClick={() => handleEdit(cliente)} className="p-1 hover:bg-gray-100 rounded" title="Editar">
                        <Edit2 className="w-4 h-4 text-gray-500" />
                      </button>
                      <button onClick={() => handleDelete(cliente.id)} className="p-1 hover:bg-gray-100 rounded" title="Eliminar">
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {clientes.length === 0 && (
                <tr>
                  <td colSpan={6} className="py-6 text-center text-gray-400">
                    No hay clientes registrados
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
