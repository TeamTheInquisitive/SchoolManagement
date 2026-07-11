import { useState } from 'react';
import { useDebounceValue } from 'usehooks-ts';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Bus, Wrench, Users, MapPin, UserCheck, Pencil, Trash2, Check, X } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button, Modal, ConfirmDialog, Tabs, SearchableSelect, useToast, Breadcrumb, Pagination, usePagination, useTabState, DatePicker , AnimatedNumber } from 'school-erp-ui-shared';
import { useTransportStats, useVehicles, useDrivers, useHelpers, useRoutes, useRouteAssignments, useCreateVehicle, useUpdateVehicle, useDeleteVehicle, useCreateDriver, useUpdateDriver, useDeleteDriver, useCreateHelper, useUpdateHelper, useDeleteHelper, useCreateRoute, useUpdateRoute, useDeleteRoute, useCreateAssignment, useUpdateAssignment, useDeleteAssignment, useRouteStudents, useAssignRouteStudents, useRemoveRouteStudent } from '../../services/transportService';
import api from '../../services/api';
import { ENDPOINTS } from '../../config/api';
import { VEHICLE_TYPES, FUEL_TYPES, VEHICLE_STATUSES, LICENSE_TYPES, SHIFT_OPTIONS } from '../../constants.jsx';
import VehiclesTab from './VehiclesTab';
import DriversTab from './DriversTab';
import RoutesTab from './RoutesTab';
import AssignmentsTab from './AssignmentsTab';

const phoneRegex = /^[6-9]\d{9}$/;

const vehicleSchema = z.object({
  vehicle_number: z.string().min(1, 'Required').regex(/^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$/, 'Format: MH12AB1234'),
  plate_number: z.string().optional(),
  type: z.string().min(1, 'Required'),
  model: z.string().optional(),
  year: z.coerce.number().min(1990).max(new Date().getFullYear()).optional().or(z.literal('')),
  fuel_type: z.string().optional(),
  capacity: z.coerce.number().min(1, 'Required'),
  status: z.string().default('Operational'),
  next_service_date: z.string().optional(),
  insurance_expiry: z.string().optional(),
  fitness_expiry: z.string().optional(),
});

const driverSchema = z.object({
  full_name: z.string().min(1, 'Required'),
  phone: z.string().regex(phoneRegex, 'Must be 10 digits starting with 6-9'),
  email: z.string().email('Invalid email').optional().or(z.literal('')),
  license_number: z.string().min(1, 'Required'),
  license_type: z.string().optional(),
  license_expiry: z.string().optional(),
  experience_years: z.coerce.number().min(0).optional().or(z.literal('')),
  join_date: z.string().optional(),
  emergency_contact_name: z.string().optional(),
  emergency_contact_phone: z.string().regex(phoneRegex, 'Must be 10 digits starting with 6-9').optional().or(z.literal('')),
});

const helperSchema = z.object({
  full_name: z.string().min(1, 'Required'),
  phone: z.string().regex(phoneRegex, 'Must be 10 digits starting with 6-9'),
  join_date: z.string().optional(),
});

const routeSchema = z.object({
  name: z.string().min(1, 'Required'),
  area: z.string().optional(),
  shift: z.string().optional(),
  stops: z.coerce.number().min(0).optional().or(z.literal('')),
  distance_km: z.coerce.number().min(0).optional().or(z.literal('')),
  start_time: z.string().optional(),
  end_time: z.string().optional(),
}).refine(data => !data.start_time || !data.end_time || data.end_time > data.start_time, { message: 'End time must be after start time', path: ['end_time'] });

const assignmentSchema = z.object({
  route_id: z.string().min(1, 'Required'),
  vehicle_id: z.string().min(1, 'Required'),
  driver_id: z.string().min(1, 'Required'),
  helper_id: z.string().optional(),
});

const cleanError = (err) => {
  const msg = err.response?.data?.error || err.response?.data?.detail || 'Operation failed';
  return msg.replace(/IntegrityError.*Duplicate entry/i, 'Duplicate record').replace(/\(.*\)/g, '').trim();
};

export default function TransportPage() {
  const toast = useToast();
  const tabs = [{ id: 'vehicles', label: 'Vehicle Inventory', icon: Bus }, { id: 'drivers', label: 'Driver & Staff', icon: Users }, { id: 'routes', label: 'Routes', icon: MapPin }, { id: 'assignments', label: 'Assignments', icon: MapPin }, { id: 'student-assignments', label: 'Student Assignments', icon: UserCheck }];
  const [tab, setTab] = useTabState(tabs);
  const [search, setSearch] = useState('');
  const [debouncedSearch] = useDebounceValue(search, 300);
  const [modal, setModal] = useState({ type: null, data: null });
  const [deleteConfirm, setDeleteConfirm] = useState({ type: null, id: null });
  const [manageStudentsRoute, setManageStudentsRoute] = useState(null);
  const pagination = usePagination(20, "admin-transport");

  const { data: statsData } = useTransportStats();
  const { data: vehiclesData } = useVehicles(pagination.params);
  const { data: driversData } = useDrivers(pagination.params);
  const { data: helpersData } = useHelpers();
  const { data: routesData } = useRoutes(pagination.params);
  const { data: assignmentsData } = useRouteAssignments(pagination.params);

  const createVehicle = useCreateVehicle(); const updateVehicle = useUpdateVehicle(); const deleteVehicle = useDeleteVehicle();
  const createDriver = useCreateDriver(); const updateDriver = useUpdateDriver(); const deleteDriver = useDeleteDriver();
  const createHelper = useCreateHelper(); const updateHelper = useUpdateHelper(); const deleteHelper = useDeleteHelper();
  const createRoute = useCreateRoute(); const updateRoute = useUpdateRoute(); const deleteRoute = useDeleteRoute();
  const createAssignment = useCreateAssignment(); const updateAssignment = useUpdateAssignment(); const deleteAssignment = useDeleteAssignment();

  const vehicleForm = useForm({ resolver: zodResolver(vehicleSchema), mode: 'onSubmit', defaultValues: { vehicle_number: '', plate_number: '', type: '', model: '', year: '', fuel_type: '', capacity: '', status: 'Operational', next_service_date: '', insurance_expiry: '', fitness_expiry: '' } });
  const driverForm = useForm({ resolver: zodResolver(driverSchema), mode: 'onSubmit', defaultValues: { full_name: '', phone: '', email: '', license_number: '', license_type: '', license_expiry: '', experience_years: '', join_date: '', emergency_contact_name: '', emergency_contact_phone: '' } });
  const helperForm = useForm({ resolver: zodResolver(helperSchema), mode: 'onSubmit', defaultValues: { full_name: '', phone: '', join_date: '' } });
  const routeForm = useForm({ resolver: zodResolver(routeSchema), mode: 'onSubmit', defaultValues: { name: '', area: '', shift: '', stops: '', distance_km: '', start_time: '', end_time: '' } });
  const assignmentForm = useForm({ resolver: zodResolver(assignmentSchema), mode: 'onSubmit', defaultValues: { route_id: '', vehicle_id: '', driver_id: '', helper_id: '' } });

  const stats = statsData ?? {};
  const vehicles = Array.isArray(vehiclesData?.results) ? vehiclesData.results : [];
  const drivers = Array.isArray(driversData?.results) ? driversData.results : [];
  const helpers = Array.isArray(helpersData?.results) ? helpersData.results : [];
  const routes = Array.isArray(routesData?.results) ? routesData.results : [];
  const assignments = Array.isArray(assignmentsData?.results) ? assignmentsData.results : [];

  const closeModal = () => { vehicleForm.reset(undefined, { keepErrors: false, keepIsSubmitted: false }); driverForm.reset(undefined, { keepErrors: false, keepIsSubmitted: false }); helperForm.reset(undefined, { keepErrors: false, keepIsSubmitted: false }); routeForm.reset(undefined, { keepErrors: false, keepIsSubmitted: false }); assignmentForm.reset(undefined, { keepErrors: false, keepIsSubmitted: false }); setModal({ type: null, data: null }); };

  const openVehicle = (v) => { vehicleForm.reset(v ? { vehicle_number: v.vehicle_number, plate_number: v.plate_number || '', type: v.type, model: v.model || '', year: v.year || '', fuel_type: v.fuel_type || '', capacity: v.capacity, status: v.status || 'Operational', next_service_date: v.next_service_date || '', insurance_expiry: v.insurance_expiry || '', fitness_expiry: v.fitness_expiry || '' } : { vehicle_number: '', plate_number: '', type: '', model: '', year: '', fuel_type: '', capacity: '', status: 'Operational', next_service_date: '', insurance_expiry: '', fitness_expiry: '' }); setModal({ type: 'vehicle', data: v }); };
  const openDriver = (d) => { driverForm.reset(d ? { full_name: d.full_name, phone: d.phone, email: d.email || '', license_number: d.license_number, license_type: d.license_type || '', license_expiry: d.license_expiry || '', experience_years: d.experience_years || '', join_date: d.join_date || '', emergency_contact_name: d.emergency_contact_name || '', emergency_contact_phone: d.emergency_contact_phone || '' } : { full_name: '', phone: '', email: '', license_number: '', license_type: '', license_expiry: '', experience_years: '', join_date: '', emergency_contact_name: '', emergency_contact_phone: '' }); setModal({ type: 'driver', data: d }); };
  const openHelper = (h) => { helperForm.reset(h ? { full_name: h.full_name, phone: h.phone, join_date: h.join_date || '' } : { full_name: '', phone: '', join_date: '' }); setModal({ type: 'helper', data: h }); };
  const openRoute = (r) => { routeForm.reset(r ? { name: r.name || r.route_name, area: r.area || '', shift: r.shift || '', stops: r.stops || '', distance_km: r.distance_km || '', start_time: r.start_time || '', end_time: r.end_time || '' } : { name: '', area: '', shift: '', stops: '', distance_km: '', start_time: '', end_time: '' }); setModal({ type: 'route', data: r }); };
  const openAssignment = (a) => { assignmentForm.reset(a ? { route_id: a.route_id, vehicle_id: a.vehicle_id, driver_id: a.driver_id, helper_id: a.helper_id || '' } : { route_id: '', vehicle_id: '', driver_id: '', helper_id: '' }); setModal({ type: 'assignment', data: a }); };

  const clean = (d) => Object.fromEntries(Object.entries(d).filter(([, v]) => v !== '' && v !== undefined));
  const onVehicleSubmit = (data) => { const cb = { onSuccess: () => { closeModal(); toast.success('Vehicle saved successfully'); }, onError: (err) => { toast.error(cleanError(err)); } }; const payload = clean(data); modal.data ? updateVehicle.mutate({ id: modal.data.id, data: payload }, cb) : createVehicle.mutate(payload, cb); };
  const onDriverSubmit = (data) => { const cb = { onSuccess: () => { closeModal(); toast.success('Driver saved successfully'); }, onError: (err) => { toast.error(cleanError(err)); } }; const payload = clean(data); modal.data ? updateDriver.mutate({ id: modal.data.id, data: payload }, cb) : createDriver.mutate(payload, cb); };
  const onHelperSubmit = (data) => { const cb = { onSuccess: () => { closeModal(); toast.success('Helper saved successfully'); }, onError: (err) => { toast.error(cleanError(err)); } }; const payload = clean(data); modal.data ? updateHelper.mutate({ id: modal.data.id, data: payload }, cb) : createHelper.mutate(payload, cb); };
  const onRouteSubmit = (data) => { const cb = { onSuccess: () => { closeModal(); toast.success('Route saved successfully'); }, onError: (err) => { toast.error(cleanError(err)); } }; const payload = clean(data); modal.data ? updateRoute.mutate({ id: modal.data.id, data: payload }, cb) : createRoute.mutate(payload, cb); };
  const onAssignmentSubmit = (data) => { const cb = { onSuccess: () => { closeModal(); toast.success('Assignment saved successfully'); }, onError: (err) => { toast.error(cleanError(err)); } }; const payload = { ...clean(data), helper_id: data.helper_id || null }; modal.data ? updateAssignment.mutate({ id: modal.data.id, data: payload }, cb) : createAssignment.mutate(payload, cb); };

  const kpis = [
    { label: 'Total Vehicles', value: stats.total_vehicles ?? vehicles.length, icon: Bus, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'Students Allotted', value: stats.total_students_transported ?? 0, icon: UserCheck, color: 'text-indigo-600', bg: 'bg-indigo-50' },
    { label: 'Total Drivers', value: stats.total_drivers ?? drivers.length, icon: Users, color: 'text-green-600', bg: 'bg-green-50' },
    { label: 'Active Routes', value: stats.active_routes ?? routes.length, icon: MapPin, color: 'text-purple-600', bg: 'bg-purple-50' },
  ];

  const F = ({ label, req, children }) => (<div><label className="text-xs text-slate-600">{label}{req && ' *'}</label>{children}</div>);
  const inp = (form, name, err) => `w-full border rounded-lg px-3 py-2 text-sm ${err ? 'border-red-400' : 'border-slate-200'}`;
  const Err = ({ e }) => e ? <p className="text-xs text-red-500 mt-0.5">{e.message}</p> : null;

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Transport' }]} />
      <div className="mb-6"><h1 className="text-2xl md:text-3xl font-bold text-slate-900">Transport Management</h1><p className="text-sm text-slate-500 mt-1">Manage vehicles, drivers, routes and assignments</p></div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4 mb-4">
        {kpis.map(k => (<div key={k.label} className="bg-white border border-slate-200 rounded-xl p-4 md:p-5 flex items-center gap-3 md:gap-4 transition-all duration-200 hover:-translate-y-1 hover:shadow-soft-lg cursor-default group"><div className={`${k.bg} p-2.5 md:p-3 rounded-xl transition-transform duration-200 group-hover:scale-110`}><k.icon className={`w-5 h-5 ${k.color}`} /></div><div><p className="text-xs text-slate-500 font-medium">{k.label}</p><p className="text-xl md:text-2xl font-bold text-slate-900 mt-0.5"><AnimatedNumber value={k.value} id={k.label} /></p></div></div>))}
      </div>

      <Tabs tabs={tabs} active={tab} onChange={(i) => { setTab(i); setSearch(''); pagination.reset(); }} className="mb-4" />

      {tab === 0 && <VehiclesTab vehicles={vehicles} search={search} setSearch={(v) => { setSearch(v); pagination.reset(); }} onAdd={() => openVehicle(null)} onEdit={openVehicle} onDelete={(id) => setDeleteConfirm({ type: 'vehicle', id })} pagination={pagination} totalPages={vehiclesData?.total_pages} totalCount={vehiclesData?.count} />}
      {tab === 1 && <DriversTab drivers={drivers} helpers={helpers} search={search} setSearch={(v) => { setSearch(v); pagination.reset(); }} onAddDriver={() => openDriver(null)} onEditDriver={openDriver} onDeleteDriver={(id) => setDeleteConfirm({ type: 'driver', id })} onAddHelper={() => openHelper(null)} onEditHelper={openHelper} onDeleteHelper={(id) => setDeleteConfirm({ type: 'helper', id })} pagination={pagination} totalPages={driversData?.total_pages} totalCount={driversData?.count} />}
      {tab === 2 && <RoutesTab routes={routes} search={search} setSearch={(v) => { setSearch(v); pagination.reset(); }} onAdd={() => openRoute(null)} onEdit={openRoute} onDelete={(id) => setDeleteConfirm({ type: 'route', id })} onManageStudents={(r) => setManageStudentsRoute(r)} pagination={pagination} totalPages={routesData?.total_pages} totalCount={routesData?.count} />}
      {tab === 3 && <AssignmentsTab assignments={assignments} onAdd={() => openAssignment(null)} onEdit={openAssignment} onDelete={(id) => setDeleteConfirm({ type: 'assignment', id })} pagination={pagination} totalPages={assignmentsData?.total_pages} totalCount={assignmentsData?.count} />}
      {tab === 4 && <StudentAssignmentsTab routes={routes} />}

      {/* Vehicle Modal */}
      <Modal open={modal.type === 'vehicle'} onClose={closeModal} title={modal.data ? 'Edit Vehicle' : 'Add Vehicle'} size="lg">
        <form onSubmit={vehicleForm.handleSubmit(onVehicleSubmit)}>
          <div className="grid grid-cols-2 gap-4">
            <F label="Vehicle Number" req><input {...vehicleForm.register('vehicle_number')} placeholder="MH12AB1234" className={inp(vehicleForm, 'vehicle_number', vehicleForm.formState.errors.vehicle_number)} /><Err e={vehicleForm.formState.errors.vehicle_number} /></F>
            <F label="Plate Number"><input {...vehicleForm.register('plate_number')} className={inp(vehicleForm, 'plate_number')} /></F>
            <F label="Type" req><SearchableSelect value={vehicleForm.watch('type')} onChange={(val) => vehicleForm.setValue('type', val, { shouldDirty: true })} options={[{ value: '', label: 'Select' }, ...VEHICLE_TYPES]} placeholder="Select Type..." /><Err e={vehicleForm.formState.errors.type} /></F>
            <F label="Model"><input {...vehicleForm.register('model')} className={inp(vehicleForm, 'model')} /></F>
            <F label="Year"><input type="number" {...vehicleForm.register('year')} placeholder="2020" className={inp(vehicleForm, 'year', vehicleForm.formState.errors.year)} /><Err e={vehicleForm.formState.errors.year} /></F>
            <F label="Fuel Type"><SearchableSelect value={vehicleForm.watch('fuel_type')} onChange={(val) => vehicleForm.setValue('fuel_type', val, { shouldDirty: true })} options={[{ value: '', label: 'Select' }, ...FUEL_TYPES]} placeholder="Select Fuel Type..." /></F>
            <F label="Capacity" req><input type="number" {...vehicleForm.register('capacity')} className={inp(vehicleForm, 'capacity', vehicleForm.formState.errors.capacity)} /><Err e={vehicleForm.formState.errors.capacity} /></F>
            <F label="Status"><SearchableSelect value={vehicleForm.watch('status')} onChange={(val) => vehicleForm.setValue('status', val, { shouldDirty: true })} options={VEHICLE_STATUSES} placeholder="Select Status..." /></F>
            <F label="Next Service Date"><DatePicker value={vehicleForm.watch('next_service_date')} onChange={(v) => vehicleForm.setValue('next_service_date', v, { shouldDirty: true })} /></F>
            <F label="Insurance Expiry"><DatePicker value={vehicleForm.watch('insurance_expiry')} onChange={(v) => vehicleForm.setValue('insurance_expiry', v, { shouldDirty: true })} /></F>
            <F label="Fitness Expiry"><DatePicker value={vehicleForm.watch('fitness_expiry')} onChange={(v) => vehicleForm.setValue('fitness_expiry', v, { shouldDirty: true })} /></F>
          </div>
          {(createVehicle.isError || updateVehicle.isError) && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg mt-3">{(createVehicle.error || updateVehicle.error)?.response?.data?.error || 'Failed to save vehicle'}</p>}
          <div className="flex justify-end gap-2 mt-4"><Button variant="ghost" onClick={closeModal}>Cancel</Button><Button variant="primary" disabled={createVehicle.isPending || updateVehicle.isPending || (modal.data && !vehicleForm.formState.isDirty)}>{modal.data ? 'Update' : 'Add Vehicle'}</Button></div>
        </form>
      </Modal>

      {/* Driver Modal */}
      <Modal open={modal.type === 'driver'} onClose={closeModal} title={modal.data ? 'Edit Driver' : 'Add Driver'} size="lg">
        <form onSubmit={driverForm.handleSubmit(onDriverSubmit)}>
          <div className="grid grid-cols-2 gap-4">
            <F label="Full Name" req><input {...driverForm.register('full_name')} className={inp(driverForm, 'full_name', driverForm.formState.errors.full_name)} /><Err e={driverForm.formState.errors.full_name} /></F>
            <F label="Phone" req><input {...driverForm.register('phone')} placeholder="9876543210" maxLength={10} className={inp(driverForm, 'phone', driverForm.formState.errors.phone)} /><Err e={driverForm.formState.errors.phone} /></F>
            <F label="Email"><input {...driverForm.register('email')} className={inp(driverForm, 'email', driverForm.formState.errors.email)} /><Err e={driverForm.formState.errors.email} /></F>
            <F label="License Number" req><input {...driverForm.register('license_number')} className={inp(driverForm, 'license_number', driverForm.formState.errors.license_number)} /><Err e={driverForm.formState.errors.license_number} /></F>
            <F label="License Type"><SearchableSelect value={driverForm.watch('license_type')} onChange={(val) => driverForm.setValue('license_type', val, { shouldDirty: true })} options={[{ value: '', label: 'Select' }, ...LICENSE_TYPES]} placeholder="Select License Type..." /></F>
            <F label="License Expiry"><DatePicker value={driverForm.watch('license_expiry')} onChange={(v) => driverForm.setValue('license_expiry', v, { shouldDirty: true })} /></F>
            <F label="Experience (years)"><input type="number" {...driverForm.register('experience_years')} className={inp(driverForm, 'experience_years')} /></F>
            <F label="Join Date"><DatePicker value={driverForm.watch('join_date')} onChange={(v) => driverForm.setValue('join_date', v, { shouldDirty: true })} /></F>
            <F label="Emergency Contact Name"><input {...driverForm.register('emergency_contact_name')} className={inp(driverForm, 'emergency_contact_name')} /></F>
            <F label="Emergency Contact Phone"><input {...driverForm.register('emergency_contact_phone')} maxLength={10} className={inp(driverForm, 'emergency_contact_phone', driverForm.formState.errors.emergency_contact_phone)} /><Err e={driverForm.formState.errors.emergency_contact_phone} /></F>
          </div>
          {(createDriver.isError || updateDriver.isError) && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg mt-3">{(createDriver.error || updateDriver.error)?.response?.data?.error || 'Failed to save driver'}</p>}
          <div className="flex justify-end gap-2 mt-4"><Button variant="ghost" onClick={closeModal}>Cancel</Button><Button variant="primary" disabled={createDriver.isPending || updateDriver.isPending || (modal.data && !driverForm.formState.isDirty)}>{modal.data ? 'Update' : 'Add Driver'}</Button></div>
        </form>
      </Modal>

      {/* Helper Modal */}
      <Modal open={modal.type === 'helper'} onClose={closeModal} title={modal.data ? 'Edit Helper' : 'Add Helper'}>
        <form onSubmit={helperForm.handleSubmit(onHelperSubmit)}>
          <div className="grid grid-cols-2 gap-4">
            <F label="Full Name" req><input {...helperForm.register('full_name')} className={inp(helperForm, 'full_name', helperForm.formState.errors.full_name)} /><Err e={helperForm.formState.errors.full_name} /></F>
            <F label="Phone" req><input {...helperForm.register('phone')} placeholder="9876543210" maxLength={10} className={inp(helperForm, 'phone', helperForm.formState.errors.phone)} /><Err e={helperForm.formState.errors.phone} /></F>
            <F label="Join Date"><DatePicker value={helperForm.watch('join_date')} onChange={(v) => helperForm.setValue('join_date', v, { shouldDirty: true })} /></F>
          </div>
          {(createHelper.isError || updateHelper.isError) && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg mt-3">{(createHelper.error || updateHelper.error)?.response?.data?.error || 'Failed to save helper'}</p>}
          <div className="flex justify-end gap-2 mt-4"><Button variant="ghost" onClick={closeModal}>Cancel</Button><Button variant="primary" disabled={createHelper.isPending || updateHelper.isPending || (modal.data && !helperForm.formState.isDirty)}>{modal.data ? 'Update' : 'Add Helper'}</Button></div>
        </form>
      </Modal>

      {/* Route Modal */}
      <Modal open={modal.type === 'route'} onClose={closeModal} title={modal.data ? 'Edit Route' : 'Add Route'}>
        <form onSubmit={routeForm.handleSubmit(onRouteSubmit)}>
          <div className="grid grid-cols-2 gap-4">
            <F label="Route Name" req><input {...routeForm.register('name')} className={inp(routeForm, 'name', routeForm.formState.errors.name)} /><Err e={routeForm.formState.errors.name} /></F>
            <F label="Area"><input {...routeForm.register('area')} className={inp(routeForm, 'area')} /></F>
            <F label="Shift"><SearchableSelect value={routeForm.watch('shift')} onChange={(val) => routeForm.setValue('shift', val, { shouldDirty: true })} options={[{ value: '', label: 'Select' }, ...SHIFT_OPTIONS]} placeholder="Select Shift..." /></F>
            <F label="Stops"><input type="number" {...routeForm.register('stops')} className={inp(routeForm, 'stops')} /></F>
            <F label="Distance (km)"><input type="number" step="0.1" {...routeForm.register('distance_km')} className={inp(routeForm, 'distance_km')} /></F>
            <F label="Start Time"><input type="time" {...routeForm.register('start_time')} className={inp(routeForm, 'start_time')} /></F>
            <F label="End Time"><input type="time" {...routeForm.register('end_time')} className={inp(routeForm, 'end_time')} /></F>
          </div>
          {(createRoute.isError || updateRoute.isError) && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg mt-3">{(createRoute.error || updateRoute.error)?.response?.data?.error || 'Failed to save route'}</p>}
          <div className="flex justify-end gap-2 mt-4"><Button variant="ghost" onClick={closeModal}>Cancel</Button><Button variant="primary" disabled={createRoute.isPending || updateRoute.isPending || (modal.data && !routeForm.formState.isDirty)}>{modal.data ? 'Update' : 'Add Route'}</Button></div>
        </form>
      </Modal>

      {/* Assignment Modal */}
      <Modal open={modal.type === 'assignment'} onClose={closeModal} title={modal.data ? 'Edit Assignment' : 'Create Assignment'}>
        <form onSubmit={assignmentForm.handleSubmit(onAssignmentSubmit)}>
          <div className="grid grid-cols-1 gap-4">
            <F label="Route" req><SearchableSelect value={assignmentForm.watch('route_id')} onChange={(val) => assignmentForm.setValue('route_id', val, { shouldDirty: true })} options={routes.filter(r => !assignments.some(a => String(a.route_id) === String(r.id) && String(a.id) !== String(modal.data?.id))).map(r => ({ value: r.id, label: r.name || r.route_name }))} placeholder="Select Route..." /><Err e={assignmentForm.formState.errors.route_id} /></F>
            <F label="Vehicle" req><SearchableSelect value={assignmentForm.watch('vehicle_id')} onChange={(val) => assignmentForm.setValue('vehicle_id', val, { shouldDirty: true })} options={vehicles.filter(v => !assignments.some(a => String(a.vehicle_id) === String(v.id) && String(a.id) !== String(modal.data?.id))).map(v => ({ value: v.id, label: `${v.vehicle_number} (${v.type})` }))} placeholder="Select Vehicle..." /><Err e={assignmentForm.formState.errors.vehicle_id} /></F>
            <F label="Driver" req><SearchableSelect value={assignmentForm.watch('driver_id')} onChange={(val) => assignmentForm.setValue('driver_id', val, { shouldDirty: true })} options={drivers.filter(d => !assignments.some(a => String(a.driver_id) === String(d.id) && String(a.id) !== String(modal.data?.id))).map(d => ({ value: d.id, label: d.full_name }))} placeholder="Select Driver..." /><Err e={assignmentForm.formState.errors.driver_id} /></F>
            <F label="Helper"><SearchableSelect value={assignmentForm.watch('helper_id')} onChange={(val) => assignmentForm.setValue('helper_id', val, { shouldDirty: true })} options={[{ value: '', label: 'None' }, ...helpers.filter(h => !assignments.some(a => String(a.helper_id) === String(h.id) && String(a.id) !== String(modal.data?.id))).map(h => ({ value: h.id, label: h.full_name }))]} placeholder="Select Helper..." /></F>
          </div>
          {(createAssignment.isError || updateAssignment.isError) && <p className="text-sm text-red-600 bg-red-50 px-3 py-2 rounded-lg mt-3">{(createAssignment.error || updateAssignment.error)?.response?.data?.error || 'Failed to save assignment'}</p>}
          <div className="flex justify-end gap-2 mt-4"><Button variant="ghost" onClick={closeModal}>Cancel</Button><Button variant="primary" disabled={createAssignment.isPending || updateAssignment.isPending || (modal.data && !assignmentForm.formState.isDirty)}>{modal.data ? 'Update' : 'Create'}</Button></div>
        </form>
      </Modal>

      <ConfirmDialog
        open={!!deleteConfirm.id}
        onClose={() => setDeleteConfirm({ type: null, id: null })}
        onConfirm={() => {
          const cb = { onSuccess: () => { setDeleteConfirm({ type: null, id: null }); toast.success(`${deleteConfirm.type} deleted successfully`); }, onError: (err) => { toast.error(cleanError(err)); } };
          if (deleteConfirm.type === 'vehicle') deleteVehicle.mutate(deleteConfirm.id, cb);
          else if (deleteConfirm.type === 'driver') deleteDriver.mutate(deleteConfirm.id, cb);
          else if (deleteConfirm.type === 'helper') deleteHelper.mutate(deleteConfirm.id, cb);
          else if (deleteConfirm.type === 'route') deleteRoute.mutate(deleteConfirm.id, cb);
          else if (deleteConfirm.type === 'assignment') deleteAssignment.mutate(deleteConfirm.id, cb);
        }}
        loading={deleteVehicle.isPending || deleteDriver.isPending || deleteHelper.isPending || deleteRoute.isPending || deleteAssignment.isPending}
        message={`Are you sure you want to delete this ${deleteConfirm.type || 'item'}? This action cannot be undone.`}
      />

      {manageStudentsRoute && <RouteStudentsModal route={manageStudentsRoute} onClose={() => setManageStudentsRoute(null)} />}
    </div>
  );
}

function StudentAssignmentsTab({ routes }) {
  const navigate = useNavigate();
  const toast = useToast();
  const [selectedRoute, setSelectedRoute] = useState('');
  const [studentSearch, setStudentSearch] = useState('');
  const [classFilter, setClassFilter] = useState('');
  const [sectionFilter, setSectionFilter] = useState('');
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [editingTransport, setEditingTransport] = useState(null);
  const [pickup, setPickup] = useState('');
  const [drop, setDrop] = useState('');

  const { data: routeStudentsData, refetch } = useRouteStudents(selectedRoute || undefined);
  const { data: allStudentsData } = useQuery({
    queryKey: ['students-for-transport'],
    queryFn: () => api.get(ENDPOINTS.students.list, { params: { page_size: 500 } }).then(r => r.data),
  });
  const assignMutation = useAssignRouteStudents();
  const removeMutation = useRemoveRouteStudent();

  const assignedStudents = routeStudentsData?.students || [];
  const assignedIds = new Set(assignedStudents.map(s => s.student_id));
  const allStudents = allStudentsData?.results || [];
  const classOptions = [...new Set(allStudents.map(s => s.class_name).filter(Boolean))].sort().map(c => ({ value: c, label: `Class ${c}` }));
  const sectionOptions = [...new Set(allStudents.filter(s => !classFilter || s.class_name === classFilter).map(s => s.section).filter(Boolean))].sort().map(s => ({ value: s, label: s }));
  const availableStudents = allStudents
    .filter(s => !assignedIds.has(s.id) && s.student_type !== 'Hosteller' && (!classFilter || s.class_name === classFilter) && (!sectionFilter || s.section === sectionFilter) && (!studentSearch || s.full_name?.toLowerCase().includes(studentSearch.toLowerCase()) || (s.roll_number || '').toLowerCase().includes(studentSearch.toLowerCase())));

  const routeOptions = routes.map(r => ({ value: r.id, label: `${r.route_code || ''} - ${r.name}` }));
  const selectedRouteObj = routes.find(r => r.id === selectedRoute);

  const handleAssign = () => {
    if (!selectedRoute || !selectedStudents.length) return;
    assignMutation.mutate({ routeId: selectedRoute, data: { student_ids: selectedStudents, pickup_point: pickup || null, drop_point: drop || null } }, {
      onSuccess: (d) => { toast.success(d.message); setSelectedStudents([]); setPickup(''); setDrop(''); },
      onError: (e) => toast.error(e.response?.data?.detail || 'Failed'),
    });
  };

  const handleRemove = (studentId) => {
    removeMutation.mutate({ routeId: selectedRoute, studentId }, {
      onSuccess: () => toast.success('Student removed from route'),
    });
  };

  const handleEditSave = () => {
    if (!editingTransport) return;
    assignMutation.mutate({ routeId: selectedRoute, data: { student_ids: [editingTransport.student_id], pickup_point: editingTransport.pickup_point || null, drop_point: editingTransport.drop_point || null } }, {
      onSuccess: () => { toast.success('Updated successfully'); setEditingTransport(null); },
      onError: (e) => toast.error(e.response?.data?.detail || 'Failed'),
    });
  };

  const capacity = selectedRouteObj?.capacity || 0;
  const occupied = assignedStudents.length;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-5">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-base font-semibold text-slate-900">Student Route Assignments</h3>
      </div>

      {/* Route selector */}
      <div className="mb-4 max-w-xs">
        <SearchableSelect value={selectedRoute} onChange={setSelectedRoute} options={routeOptions} placeholder="Select a route..." />
      </div>

      {selectedRoute && (
        <>
          {/* Capacity bar */}
          <div className="flex items-center gap-3 mb-4">
            <div className="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden">
              <div className={`h-full rounded-full transition-all ${occupied >= capacity ? 'bg-red-500' : occupied > capacity * 0.8 ? 'bg-amber-500' : 'bg-green-500'}`} style={{ width: `${Math.min(100, capacity ? (occupied / capacity) * 100 : 0)}%` }}></div>
            </div>
            <span className="text-sm font-medium text-slate-700">{occupied}/{capacity} seats</span>
          </div>

          {/* Assigned students table */}
          <div className="mb-4">
            <p className="text-xs font-semibold text-slate-600 mb-2">Assigned Students ({assignedStudents.length})</p>
            {assignedStudents.length > 0 ? (
              <div className="overflow-x-auto border border-slate-200 rounded-lg">
                <table className="w-full text-sm">
                  <thead><tr className="bg-slate-50 border-b border-slate-200"><th className="text-left px-3 py-2 text-xs font-semibold text-slate-500">Name</th><th className="text-left px-3 py-2 text-xs font-semibold text-slate-500">Adm No</th><th className="text-left px-3 py-2 text-xs font-semibold text-slate-500">Class</th><th className="text-left px-3 py-2 text-xs font-semibold text-slate-500">Pickup</th><th className="text-left px-3 py-2 text-xs font-semibold text-slate-500">Drop</th><th className="px-3 py-2 text-xs font-semibold text-slate-500 text-right">Actions</th></tr></thead>
                  <tbody className="divide-y divide-slate-100">
                    {assignedStudents.map(s => (
                      <tr key={s.id} className="hover:bg-slate-50">
                        <td className="px-3 py-2 font-medium text-primary-600 hover:text-primary-700 cursor-pointer hover:underline" onClick={() => navigate(`/admin/students/${s.student_id}`)}>{s.student_name}</td>
                        <td className="px-3 py-2 text-slate-500">{s.admission_number}</td>
                        <td className="px-3 py-2 text-slate-500">{s.class_name}-{s.section}</td>
                        <td className="px-3 py-2 text-slate-500">{editingTransport?.student_id === s.student_id ? <input value={editingTransport.pickup_point || ''} onChange={e => setEditingTransport({...editingTransport, pickup_point: e.target.value})} className="border border-slate-300 rounded px-2 py-0.5 text-xs w-24" /> : (s.pickup_point || '—')}</td>
                        <td className="px-3 py-2 text-slate-500">{editingTransport?.student_id === s.student_id ? <input value={editingTransport.drop_point || ''} onChange={e => setEditingTransport({...editingTransport, drop_point: e.target.value})} className="border border-slate-300 rounded px-2 py-0.5 text-xs w-24" /> : (s.drop_point || '—')}</td>
                        <td className="px-3 py-2 text-right">
                          {editingTransport?.student_id === s.student_id ? (
                            <span className="flex gap-1 justify-end"><button onClick={handleEditSave} className="p-1 hover:bg-green-50 rounded"><Check className="w-4 h-4 text-green-600" /></button><button onClick={() => setEditingTransport(null)} className="p-1 hover:bg-slate-100 rounded"><X className="w-4 h-4 text-slate-400" /></button></span>
                          ) : (
                            <span className="flex gap-1 justify-end"><button onClick={() => setEditingTransport({ student_id: s.student_id, pickup_point: s.pickup_point || '', drop_point: s.drop_point || '' })} className="p-1 hover:bg-blue-50 rounded"><Pencil className="w-4 h-4 text-blue-500" /></button><button onClick={() => handleRemove(s.student_id)} className="p-1 hover:bg-red-50 rounded"><Trash2 className="w-4 h-4 text-red-500" /></button></span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : <p className="text-sm text-slate-400">No students assigned to this route</p>}
          </div>

          {/* Add students */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mt-4">
            <p className="text-sm font-semibold text-slate-800 mb-3">Add Students to Route</p>
            <div className="relative z-20 flex flex-wrap items-end gap-3 mb-3">
              <div className="w-40"><label className="text-xs text-slate-500 mb-1 block">Class</label><SearchableSelect value={classFilter} onChange={(v) => { setClassFilter(v); setSectionFilter(''); }} options={[{ value: '', label: 'All Classes' }, ...classOptions]} placeholder="All Classes" /></div>
              <div className="w-40"><label className="text-xs text-slate-500 mb-1 block">Section</label><SearchableSelect value={sectionFilter} onChange={setSectionFilter} options={[{ value: '', label: 'All Sections' }, ...sectionOptions]} placeholder="All Sections" /></div>
              <div className="flex-1 min-w-[200px]"><label className="text-xs text-slate-500 mb-1 block">Search</label><input value={studentSearch} onChange={e => setStudentSearch(e.target.value)} placeholder="Search by name or roll number..." className="w-full border border-slate-300 rounded-lg px-3 py-[7px] text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white" /></div>
            </div>
            <div className="grid grid-cols-2 gap-3 mb-3">
              <div><label className="text-xs text-slate-500 mb-1 block">Pickup Point</label><input value={pickup} onChange={e => setPickup(e.target.value)} placeholder="e.g. MG Road Stop" className="w-full border border-slate-300 rounded-lg px-3 py-[7px] text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
              <div><label className="text-xs text-slate-500 mb-1 block">Drop Point</label><input value={drop} onChange={e => setDrop(e.target.value)} placeholder="e.g. School Main Gate" className="w-full border border-slate-300 rounded-lg px-3 py-[7px] text-sm bg-white focus:outline-none focus:ring-2 focus:ring-primary-500" /></div>
            </div>
            <div className="max-h-48 overflow-y-auto border border-slate-200 rounded-lg bg-white">
              {!classFilter && !sectionFilter && !studentSearch ? (
                <p className="text-center text-xs text-slate-400 py-6">Select a class, section or search to find students</p>
              ) : (<>
              {availableStudents.slice(0, 30).map(s => (
                <label key={s.id} className="flex items-center gap-3 px-3 py-2 hover:bg-primary-50/40 cursor-pointer text-sm border-b border-slate-100 last:border-b-0 transition-colors">
                  <input type="checkbox" checked={selectedStudents.includes(s.id)} onChange={e => setSelectedStudents(e.target.checked ? [...selectedStudents, s.id] : selectedStudents.filter(id => id !== s.id))} className="rounded border-slate-300 text-primary-600 focus:ring-primary-500" />
                  <span className="font-medium text-slate-800">{s.full_name}</span>
                  <span className="text-xs text-slate-400">{s.roll_number}</span>
                  <span className="text-xs bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded ml-auto">{s.class_name}-{s.section}</span>
                </label>
              ))}
              {availableStudents.length === 0 && <p className="text-center text-xs text-slate-400 py-6">No students found</p>}
              {availableStudents.length > 30 && <p className="text-center text-xs text-slate-400 py-2 bg-slate-50">Showing 30 of {availableStudents.length} — use filters to narrow</p>}
              </>)}
            </div>
            {selectedStudents.length > 0 && (
              <div className="flex items-center justify-between mt-3">
                <span className="text-xs text-slate-500">{selectedStudents.length} student(s) selected</span>
                <Button variant="primary" size="sm" onClick={handleAssign} disabled={assignMutation.isPending}>
                  {assignMutation.isPending ? 'Assigning...' : `Assign ${selectedStudents.length} Student(s)`}
                </Button>
              </div>
            )}
          </div>
        </>
      )}

    </div>
  );
}

function RouteStudentsModal({ route, onClose }) {
  const toast = useToast();
  const { data: studentsData } = useRouteStudents(route.id);
  const assignMutation = useAssignRouteStudents();
  const removeMutation = useRemoveRouteStudent();
  const [studentSearch, setStudentSearch] = useState('');
  const [selectedStudents, setSelectedStudents] = useState([]);
  const [pickup, setPickup] = useState('');
  const [drop, setDrop] = useState('');

  // Fetch all students for search
  const { data: allStudentsData } = useQuery({
    queryKey: ['students-for-transport'],
    queryFn: () => api.get(ENDPOINTS.students.list, { params: { page_size: 500 } }).then(r => r.data),
  });

  const assignedStudents = studentsData?.students || [];
  const assignedIds = new Set(assignedStudents.map(s => s.student_id));

  const availableStudents = (allStudentsData?.results || [])
    .filter(s => !assignedIds.has(s.id) && (!studentSearch || s.full_name?.toLowerCase().includes(studentSearch.toLowerCase()) || s.admission_number?.toLowerCase().includes(studentSearch.toLowerCase())));

  const handleAssign = () => {
    if (!selectedStudents.length) return;
    assignMutation.mutate({ routeId: route.id, data: { student_ids: selectedStudents, pickup_point: pickup || null, drop_point: drop || null } }, {
      onSuccess: (d) => { toast.success(d.message); setSelectedStudents([]); setPickup(''); setDrop(''); },
      onError: (e) => toast.error(e.response?.data?.detail || 'Failed'),
    });
  };

  const handleRemove = (studentId) => {
    removeMutation.mutate({ routeId: route.id, studentId }, {
      onSuccess: () => toast.success('Student removed'),
      onError: (e) => toast.error(e.response?.data?.detail || 'Failed'),
    });
  };

  const capacity = route.capacity || 0;
  const occupied = assignedStudents.length;

  return (
    <Modal open onClose={onClose} title={`Students - ${route.name || route.route_code}`} size="lg">
      <div className="space-y-4">
        {/* Capacity indicator */}
        <div className="flex items-center gap-3">
          <div className="flex-1 bg-slate-100 rounded-full h-3 overflow-hidden">
            <div className={`h-full rounded-full ${occupied >= capacity ? 'bg-red-500' : occupied > capacity * 0.8 ? 'bg-amber-500' : 'bg-green-500'}`} style={{ width: `${Math.min(100, capacity ? (occupied / capacity) * 100 : 0)}%` }}></div>
          </div>
          <span className="text-sm font-medium text-slate-700">{occupied}/{capacity} seats</span>
        </div>

        {/* Assigned students */}
        <div>
          <p className="text-xs font-semibold text-slate-600 mb-2">Assigned Students ({assignedStudents.length})</p>
          {assignedStudents.length > 0 ? (
            <div className="max-h-40 overflow-y-auto border border-slate-200 rounded-lg divide-y divide-slate-100">
              {assignedStudents.map(s => (
                <div key={s.id} className="flex items-center justify-between px-3 py-2 text-sm">
                  <div><span className="font-medium text-slate-800">{s.student_name}</span> <span className="text-xs text-slate-400">{s.admission_number}</span>{s.pickup_point && <span className="text-xs text-slate-500 ml-2">• {s.pickup_point}</span>}</div>
                  <button onClick={() => handleRemove(s.student_id)} className="text-xs text-red-500 hover:text-red-700">Remove</button>
                </div>
              ))}
            </div>
          ) : <p className="text-sm text-slate-400">No students assigned to this route</p>}
        </div>

        {/* Add students */}
        <div className="border-t border-slate-200 pt-4">
          <p className="text-xs font-semibold text-slate-600 mb-2">Add Students</p>
          <div className="grid grid-cols-2 gap-2 mb-2">
            <input value={pickup} onChange={e => setPickup(e.target.value)} placeholder="Pickup point" className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm" />
            <input value={drop} onChange={e => setDrop(e.target.value)} placeholder="Drop point" className="border border-slate-200 rounded-lg px-3 py-1.5 text-sm" />
          </div>
          <input value={studentSearch} onChange={e => setStudentSearch(e.target.value)} placeholder="Search students by name or admission no..." className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm mb-2" />
          <div className="max-h-32 overflow-y-auto border border-slate-200 rounded-lg divide-y divide-slate-100">
            {availableStudents.slice(0, 20).map(s => (
              <label key={s.id} className="flex items-center gap-2 px-3 py-1.5 hover:bg-slate-50 cursor-pointer text-sm">
                <input type="checkbox" checked={selectedStudents.includes(s.id)} onChange={e => setSelectedStudents(e.target.checked ? [...selectedStudents, s.id] : selectedStudents.filter(id => id !== s.id))} className="rounded" />
                <span className="text-slate-800">{s.full_name}</span><span className="text-xs text-slate-400">{s.admission_number}</span>
              </label>
            ))}
            {availableStudents.length === 0 && <p className="text-center text-xs text-slate-400 py-3">No students found</p>}
          </div>
          {selectedStudents.length > 0 && (
            <Button variant="primary" size="sm" className="mt-2" onClick={handleAssign} disabled={assignMutation.isPending}>
              {assignMutation.isPending ? 'Assigning...' : `Assign ${selectedStudents.length} Student(s)`}
            </Button>
          )}
        </div>
      </div>
    </Modal>
  );
}
