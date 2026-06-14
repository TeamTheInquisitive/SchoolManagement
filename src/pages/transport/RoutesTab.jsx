import { Plus, Pencil, Trash2, Users } from 'lucide-react';
import { Button, SearchInput, Badge, Pagination } from 'school-erp-ui-shared';

export default function RoutesTab({ routes, search, setSearch, onAdd, onEdit, onDelete, onManageStudents, pagination, totalPages, totalCount }) {
  const filtered = routes.filter(r => !search || (r.name || '').toLowerCase().includes(search.toLowerCase()) || (r.area || '').toLowerCase().includes(search.toLowerCase()));
  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
      <div className="flex justify-between items-center mb-3"><h3 className="text-base font-semibold text-slate-900">Routes Management</h3><Button variant="primary" size="sm" icon={Plus} onClick={onAdd}>Add Route</Button></div>
      <div className="mb-3"><SearchInput value={search} onChange={setSearch} placeholder="Search routes..." /></div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-slate-200 text-left"><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Route Code</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Name</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Area</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Shift</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Status</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Actions</th></tr></thead>
          <tbody>
            {filtered.map(r => (
              <tr key={r.id} className="border-b border-slate-100 hover:bg-primary-50/40 transition-colors duration-150">
                <td className="py-2 px-2 font-semibold text-slate-800">{r.route_code || ''}</td>
                <td className="py-2 px-2">{r.name || ''}</td>
                <td className="py-2 px-2 text-slate-500">{r.area || '—'}</td>
                <td className="py-2 px-2 text-slate-500">{r.shift || '—'}</td>
                <td className="py-2 px-2"><Badge status={r.status || 'Active'} /></td>
                <td className="py-2 px-2"><div className="flex gap-1"><button className="p-1 hover:bg-blue-50 rounded active:scale-[0.97]" title="Manage Students" onClick={() => onManageStudents && onManageStudents(r)}><Users className="w-4 h-4 text-blue-500" /></button><button className="p-1 hover:bg-slate-100 rounded active:scale-[0.97]" onClick={() => onEdit(r)}><Pencil className="w-4 h-4 text-slate-500" /></button><button className="p-1 hover:bg-red-50 rounded active:scale-[0.97]" onClick={() => onDelete(r.id)}><Trash2 className="w-4 h-4 text-red-500" /></button></div></td>
              </tr>
            ))}
            {filtered.length === 0 && <tr><td colSpan={6} className="text-center py-8 text-slate-400">No routes found</td></tr>}
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
