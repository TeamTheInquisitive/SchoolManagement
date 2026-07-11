import { useState } from 'react';
import { Plus, Pencil, Trash2, Download, AlertTriangle, Shield } from 'lucide-react';
import { Button, SearchInput, Badge, useToast, exportStyledExcel, Pagination } from 'school-erp-ui-shared';
import { useSchoolProfile } from '../../services/settingsService';
import { getSchoolInfo } from '../../utils/getSchoolInfo';

function daysUntil(dateStr) {
  if (!dateStr) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(dateStr + 'T00:00:00');
  return Math.ceil((target - today) / 86400000);
}

function ExpiryBadge({ dateStr, label }) {
  const days = daysUntil(dateStr);
  if (days === null) return null;
  if (days < 0) return <span className="inline-flex items-center gap-0.5 text-[9px] font-semibold bg-red-100 text-red-700 px-1.5 py-0.5 rounded"><AlertTriangle size={9} />{label} Expired</span>;
  if (days <= 30) return <span className="inline-flex items-center gap-0.5 text-[9px] font-semibold bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded"><AlertTriangle size={9} />{label} in {days}d</span>;
  return null;
}

export default function VehiclesTab({ vehicles, search, setSearch, onAdd, onEdit, onDelete, pagination, totalPages, totalCount }) {
  const toast = useToast();
  const { data: schoolProfile } = useSchoolProfile();
  const [exporting, setExporting] = useState(false);
  const filtered = vehicles.filter(v => !search || (v.vehicle_number || '').toLowerCase().includes(search.toLowerCase()) || (v.type || '').toLowerCase().includes(search.toLowerCase()));

  const expiredCount = vehicles.filter(v => daysUntil(v.insurance_expiry) < 0 || daysUntil(v.fitness_expiry) < 0).length;
  const expiringCount = vehicles.filter(v => { const ins = daysUntil(v.insurance_expiry); const fit = daysUntil(v.fitness_expiry); return (ins !== null && ins >= 0 && ins <= 30) || (fit !== null && fit >= 0 && fit <= 30); }).length;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
      <div className="flex justify-between items-center mb-3"><h3 className="text-base font-semibold text-slate-900">Vehicle Registry</h3><Button variant="primary" size="sm" icon={Plus} onClick={onAdd}>Add Vehicle</Button></div>

      {/* Compliance alerts */}
      {(expiredCount > 0 || expiringCount > 0) && (
        <div className="flex items-center gap-3 mb-3 p-2.5 bg-amber-50 border border-amber-200 rounded-lg">
          <Shield size={16} className="text-amber-600 flex-shrink-0" />
          <div className="flex items-center gap-3 text-xs">
            {expiredCount > 0 && <span className="font-medium text-red-700">{expiredCount} vehicle(s) with expired documents</span>}
            {expiringCount > 0 && <span className="font-medium text-amber-700">{expiringCount} vehicle(s) expiring within 30 days</span>}
          </div>
        </div>
      )}

      <div className="flex justify-between mb-3"><SearchInput value={search} onChange={setSearch} placeholder="Search vehicles..." /><Button variant="secondary" size="sm" icon={Download} onClick={() => { const headers = ['Vehicle Number', 'Type', 'Model', 'Capacity', 'Status', 'Driver']; const rows = filtered.map(v => [v.vehicle_number, v.type, v.model, v.capacity, v.status, v.driver_name || 'Unassigned']); setExporting(true); exportStyledExcel({ filename: 'Vehicle_Directory', schoolInfo: getSchoolInfo(schoolProfile), reportTitle: 'Vehicle Directory', headers, rows }).then(() => { toast.success('Exported successfully'); }).finally(() => setExporting(false)); }} disabled={exporting} loading={exporting}>{exporting ? 'Exporting...' : 'Export Excel'}</Button></div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-slate-200 text-left"><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Vehicle Number</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Type / Model</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Capacity</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Status</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Driver</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Compliance</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Actions</th></tr></thead>
          <tbody>
            {filtered.map(v => {
              const capPct = v.capacity ? Math.round(((v.occupied_seats || 0) / v.capacity) * 100) : 0;
              const noDriver = !v.driver_name && (v.occupied_seats || 0) > 0;
              return (
                <tr key={v.id} className={`border-b border-slate-100 hover:bg-primary-50/40 transition-colors duration-150 ${noDriver ? 'bg-red-50/30' : ''}`}>
                  <td className="py-2.5 px-2"><p className="font-semibold text-slate-800">{v.vehicle_number}</p><p className="text-xs text-slate-400">{v.registration_number || ''}</p></td>
                  <td className="py-2.5 px-2"><p className="text-slate-800">{v.type || ''}</p><p className="text-xs text-slate-400">{v.model || ''} {v.year ? `(${v.year})` : ''}</p></td>
                  <td className="py-2.5 px-2">
                    <p className={`text-xs font-medium ${capPct >= 100 ? 'text-red-600' : capPct >= 80 ? 'text-amber-600' : 'text-slate-700'}`}>{v.occupied_seats ?? 0}/{v.capacity ?? 0} {capPct >= 100 && <span className="text-[9px] bg-red-100 text-red-700 px-1 rounded ml-1">FULL</span>}</p>
                    <div className="w-16 h-1.5 bg-slate-200 rounded-full mt-1"><div className={`h-full rounded-full ${capPct >= 100 ? 'bg-red-500' : capPct >= 80 ? 'bg-amber-500' : 'bg-emerald-500'}`} style={{ width: `${Math.min(capPct, 100)}%` }} /></div>
                  </td>
                  <td className="py-2.5 px-2"><Badge status={v.status || 'Unknown'} /></td>
                  <td className="py-2.5 px-2">
                    {v.driver_name ? (
                      <span className="text-slate-700">{v.driver_name}</span>
                    ) : (
                      <span className={`text-xs font-medium ${noDriver ? 'text-red-600' : 'text-slate-400'}`}>{noDriver ? '⚠️ No Driver!' : 'Unassigned'}</span>
                    )}
                  </td>
                  <td className="py-2.5 px-2">
                    <div className="flex flex-col gap-0.5">
                      <ExpiryBadge dateStr={v.insurance_expiry} label="Insurance" />
                      <ExpiryBadge dateStr={v.fitness_expiry} label="Fitness" />
                      {!v.insurance_expiry && !v.fitness_expiry && <span className="text-[9px] text-slate-300">—</span>}
                    </div>
                  </td>
                  <td className="py-2.5 px-2"><div className="flex gap-1"><button className="p-1 hover:bg-slate-100 rounded active:scale-[0.97]" onClick={() => onEdit(v)}><Pencil className="w-4 h-4 text-slate-500" /></button><button className="p-1 hover:bg-red-50 rounded active:scale-[0.97]" onClick={() => onDelete(v.id)}><Trash2 className="w-4 h-4 text-red-500" /></button></div></td>
                </tr>
              );
            })}
            {filtered.length === 0 && <tr><td colSpan={7} className="text-center py-8 text-slate-400">No vehicles found</td></tr>}
          </tbody>
        </table>
      </div>
      {pagination && <Pagination
        page={pagination.page}
        totalPages={totalPages || 1}
        totalCount={totalCount || 0}
        pageSize={pagination.pageSize}
        onPageChange={(p) => pagination.setPage(p)}
      />}
    </div>
  );
}
