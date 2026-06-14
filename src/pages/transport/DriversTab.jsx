import { Plus, Pencil, Trash2, Download, AlertTriangle } from 'lucide-react';
import { Button, SearchInput, Badge, useToast, exportToCsv, Pagination } from 'school-erp-ui-shared';

function LicenseExpiryBadge({ dateStr }) {
  if (!dateStr) return null;
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const target = new Date(dateStr + 'T00:00:00');
  const days = Math.ceil((target - today) / 86400000);
  if (days < 0) return <span className="inline-flex items-center gap-0.5 text-[9px] font-semibold bg-red-100 text-red-700 px-1.5 py-0.5 rounded mt-0.5"><AlertTriangle size={8} />EXPIRED</span>;
  if (days <= 30) return <span className="inline-flex items-center gap-0.5 text-[9px] font-semibold bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded mt-0.5">Expires in {days}d</span>;
  return null;
}

export default function DriversTab({ drivers, helpers, search, setSearch, onAddDriver, onEditDriver, onDeleteDriver, onAddHelper, onEditHelper, onDeleteHelper, pagination, totalPages, totalCount }) {
  const toast = useToast();
  const filteredDrivers = drivers.filter(d => !search || (d.full_name || d.name || '').toLowerCase().includes(search.toLowerCase()));
  return (
    <div>
      <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-5 mb-4 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
        <div className="flex justify-between items-center mb-3"><h3 className="text-base font-semibold text-slate-900">Driver & Helper Directory</h3><div className="flex gap-2"><Button variant="secondary" size="sm" icon={Plus} onClick={onAddHelper}>Add Helper</Button><Button variant="primary" size="sm" icon={Plus} onClick={onAddDriver}>Add Driver</Button></div></div>
        <div className="flex justify-between mb-3"><SearchInput value={search} onChange={setSearch} placeholder="Search drivers..." /><Button variant="secondary" size="sm" icon={Download} onClick={() => { const headers = ['Driver Name', 'Phone', 'License Number', 'License Type', 'Status', 'Assignment']; const rows = filteredDrivers.map(d => [d.full_name || d.name, d.phone, d.license_number, d.license_type, d.status || 'Active', d.assigned_vehicle || 'Available']); exportToCsv('drivers', headers, rows); toast.success('CSV exported successfully'); }}>Export CSV</Button></div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead><tr className="border-b border-slate-200 text-left"><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Driver</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Contact</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">License</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Status</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Assignment</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Actions</th></tr></thead>
            <tbody>
              {filteredDrivers.map(d => (
                <tr key={d.id} className="border-b border-slate-100 hover:bg-primary-50/40 transition-colors duration-150">
                  <td className="py-2 px-2"><div className="flex items-center gap-2"><div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-indigo-700 text-white flex items-center justify-center text-xs font-semibold shadow-sm">{(d.full_name || d.name || '??').slice(0, 2).toUpperCase()}</div><div><p className="font-semibold text-slate-800">{d.full_name || d.name}</p><p className="text-xs text-slate-400">{d.employee_code || ''}</p></div></div></td>
                  <td className="py-2 px-2 text-slate-500">📞 {d.phone || ''}</td>
                  <td className="py-2 px-2"><p className="font-medium text-slate-800">{d.license_number || '—'}</p><p className="text-xs text-slate-500">{d.license_type || ''}</p><LicenseExpiryBadge dateStr={d.license_expiry} /></td>
                  <td className="py-2 px-2"><Badge status={d.status || 'Active'} /></td>
                  <td className="py-2 px-2"><p className="font-medium text-slate-800">{d.assigned_vehicle || 'Available'}</p><p className="text-xs text-slate-500">{d.assigned_route || ''}</p></td>
                  <td className="py-2 px-2"><div className="flex gap-1"><button className="p-1 hover:bg-slate-100 rounded active:scale-[0.97]" onClick={() => onEditDriver(d)}><Pencil className="w-4 h-4 text-slate-500" /></button><button className="p-1 hover:bg-red-50 rounded active:scale-[0.97]" onClick={() => onDeleteDriver(d.id)}><Trash2 className="w-4 h-4 text-red-500" /></button></div></td>
                </tr>
              ))}
              {drivers.length === 0 && <tr><td colSpan={6} className="text-center py-8 text-slate-400">No drivers found</td></tr>}
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

      <h3 className="text-base font-semibold text-slate-800 mb-3">Helpers / Attendants</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {helpers.map(h => (
          <div key={h.id} className="bg-white border border-slate-200 rounded-xl p-3 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-soft-lg hover:border-slate-300">
            <div className="flex items-center gap-2 mb-2"><div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 text-white flex items-center justify-center text-xs font-semibold shadow-sm">{(h.full_name || h.name || '??').slice(0, 2).toUpperCase()}</div><div className="flex-1"><p className="text-sm font-semibold text-slate-800">{h.full_name || h.name}</p></div><Badge status={h.status || 'Active'} /></div>
            <div className="text-xs text-slate-500 space-y-0.5 mb-2"><p>📞 {h.phone || ''}</p><p>📅 Joined: {h.join_date || '—'}</p><p>🚌 {h.assigned_vehicle || 'Unassigned'}</p></div>
            <div className="flex gap-2 border-t border-slate-200 pt-2"><button className="flex-1 text-xs text-slate-500 border border-slate-200 rounded-lg py-1 hover:bg-slate-50" onClick={() => onEditHelper(h)}>Edit</button><button className="text-xs text-red-500 px-2" onClick={() => onDeleteHelper(h.id)}>Remove</button></div>
          </div>
        ))}
        {helpers.length === 0 && <div className="col-span-3 border-2 border-dashed border-slate-200 rounded-xl p-6 text-center text-slate-400">No helpers found</div>}
      </div>
    </div>
  );
}
