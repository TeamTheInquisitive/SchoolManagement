import { Plus, Bus, MapPin, Route, Clock, Pencil, Trash2, Users, ArrowRight } from 'lucide-react';
import { Button, Badge, Pagination } from 'school-erp-ui-shared';

export default function AssignmentsTab({ assignments, onAdd, onEdit, onDelete, pagination, totalPages, totalCount }) {
  return (
    <div>
      <div className="flex justify-between items-center mb-5">
        <div>
          <h3 className="text-base font-semibold text-slate-900">Route Assignments</h3>
          <p className="text-xs text-slate-500 mt-0.5">{assignments.length} active assignment{assignments.length !== 1 ? 's' : ''}</p>
        </div>
        <Button variant="primary" size="sm" icon={Plus} onClick={onAdd}>Create Assignment</Button>
      </div>

      {assignments.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-xl p-12 text-center">
          <div className="w-14 h-14 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3">
            <MapPin size={24} className="text-slate-400" />
          </div>
          <p className="text-sm font-medium text-slate-600">No route assignments yet</p>
          <p className="text-xs text-slate-400 mt-1">Create an assignment to link routes, vehicles, and drivers</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {assignments.map((a, i) => {
            const colors = ['border-l-blue-500', 'border-l-purple-500', 'border-l-emerald-500', 'border-l-amber-500', 'border-l-pink-500', 'border-l-indigo-500'];
            const leftColor = colors[i % colors.length];
            return (
            <div key={a.id} className={`bg-white border border-slate-200 ${leftColor} border-l-4 rounded-xl p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300 group`}>
              {/* Top Row: Route + Status + Actions */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-50 to-indigo-100 flex items-center justify-center border border-indigo-200">
                    <Route size={18} className="text-indigo-600" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <p className="text-base font-bold text-slate-900">{a.route_name || 'Unnamed Route'}</p>
                      {a.route_code && <span className="text-[10px] font-mono bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded">{a.route_code}</span>}
                    </div>
                    <p className="text-xs text-slate-500">{a.route_area || a.area || 'No area'} • {a.shift || 'Morning'} Shift{a.distance_km ? ` • ${a.distance_km} km` : ''}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge status={a.status || 'Active'}>{a.status || 'Active'}</Badge>
                  <button onClick={() => onEdit(a)} className="p-1.5 rounded-lg text-slate-400 hover:text-primary-600 hover:bg-primary-50 transition-all duration-150 opacity-0 group-hover:opacity-100">
                    <Pencil size={14} />
                  </button>
                  <button onClick={() => onDelete(a.id)} className="p-1.5 rounded-lg text-slate-400 hover:text-red-600 hover:bg-red-50 transition-all duration-150 opacity-0 group-hover:opacity-100">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>

              {/* Details Grid */}
              <div className="space-y-2.5">
                {/* Vehicle */}
                <div className="flex items-center gap-3 p-3 bg-blue-50/60 rounded-xl border border-blue-100/80">
                  <div className="w-9 h-9 rounded-lg bg-white border border-blue-200 flex items-center justify-center flex-shrink-0">
                    <Bus size={16} className="text-blue-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-blue-500 font-medium uppercase">Vehicle</p>
                    <p className="text-sm font-bold text-slate-900 truncate">{a.vehicle_number || '—'}</p>
                  </div>
                  <span className="text-[11px] text-slate-500">{a.vehicle_type || 'Bus'} • {a.vehicle_capacity || 0} seats</span>
                </div>

                {/* Driver */}
                <div className="flex items-center gap-3 p-3 bg-purple-50/60 rounded-xl border border-purple-100/80">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-purple-700 text-white flex items-center justify-center text-[10px] font-bold flex-shrink-0">
                    {(a.driver_name || '??').slice(0, 2).toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-purple-500 font-medium uppercase">Driver</p>
                    <p className="text-sm font-bold text-slate-900 truncate">{a.driver_name || 'Unassigned'}</p>
                  </div>
                  {a.helper_name ? <span className="text-[11px] text-slate-500">Helper: {a.helper_name}</span> : <span className="text-[10px] font-medium text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">No Helper</span>}
                </div>

                {/* Schedule */}
                <div className="flex items-center gap-3 p-3 bg-amber-50/60 rounded-xl border border-amber-100/80">
                  <div className="w-9 h-9 rounded-lg bg-white border border-amber-200 flex items-center justify-center flex-shrink-0">
                    <Clock size={16} className="text-amber-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs text-amber-500 font-medium uppercase">Schedule</p>
                    <div className="flex items-center gap-1.5">
                      <span className="text-sm font-bold text-slate-900">{a.start_time || '—'}</span>
                      <span className="text-xs text-slate-400">→</span>
                      <span className="text-sm font-bold text-slate-900">{a.end_time || '—'}</span>
                      {a.start_time && a.end_time && (() => {
                        const [sh, sm] = (a.start_time || '').split(':').map(Number);
                        const [eh, em] = (a.end_time || '').split(':').map(Number);
                        const diff = (eh * 60 + em) - (sh * 60 + sm);
                        if (diff > 0) { const h = Math.floor(diff / 60); const m = diff % 60; return <span className="text-[10px] text-amber-600 bg-amber-100 px-1.5 py-0.5 rounded ml-1">{h > 0 ? `${h}h ` : ''}{m > 0 ? `${m}m` : ''}</span>; }
                        return null;
                      })()}
                    </div>
                  </div>
                  <span className="text-[11px] text-slate-500">{a.stops_count || a.stops || 0} stops{a.distance_km ? ` • ${a.distance_km} km` : ''}</span>
                </div>
              </div>
            </div>
          );
          })}
        </div>
      )}
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
