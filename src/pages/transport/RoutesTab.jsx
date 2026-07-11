import { useState, Fragment } from 'react';
import { Plus, Pencil, Trash2, Users, ChevronDown, ChevronRight, MapPin, Clock, Route } from 'lucide-react';
import { Button, SearchInput, Badge, Pagination } from 'school-erp-ui-shared';
import { useRouteStudents } from '../../services/transportService';

function RouteVisualization({ route }) {
  const { data: studentsData, isLoading } = useRouteStudents(route.id);
  const students = studentsData?.results || studentsData || [];

  // Try to use the route's stops field first, then fall back to grouping students by pickup_point
  let stops = [];
  if (route.stops && Array.isArray(route.stops) && route.stops.length > 0) {
    stops = route.stops.map((stop, idx) => {
      const stopName = stop.name || stop.stop_name || `Stop ${idx + 1}`;
      const studentCount = students.filter(s => (s.pickup_point || s.stop_name) === stopName).length;
      return { name: stopName, order: stop.order || idx + 1, student_count: stop.student_count || studentCount, time: stop.time || stop.pickup_time || null };
    });
  } else {
    // Group students by pickup_point
    const stopMap = {};
    students.forEach(s => {
      const stop = s.pickup_point || s.stop_name || 'Unknown Stop';
      if (!stopMap[stop]) stopMap[stop] = [];
      stopMap[stop].push(s);
    });
    stops = Object.entries(stopMap).map(([name, studs], idx) => ({ name, order: idx + 1, student_count: studs.length, time: null }));
  }

  if (isLoading) return <div className="py-4 px-6 text-sm text-slate-400">Loading route details...</div>;

  if (stops.length === 0) {
    return (
      <div className="px-6 py-5 bg-slate-50/70 border-t border-slate-100">
        <div className="flex items-center gap-2 text-slate-400">
          <MapPin size={16} />
          <span className="text-sm">No stops configured</span>
        </div>
      </div>
    );
  }

  return (
    <div className="px-6 py-5 bg-slate-50/70 border-t border-slate-100">
      {/* Route metadata */}
      <div className="flex items-center gap-4 mb-4 pb-3 border-b border-slate-200">
        <div className="flex items-center gap-1.5">
          <Route size={14} className="text-indigo-500" />
          <span className="text-xs font-semibold text-slate-700">{stops.length} {stops.length === 1 ? 'stop' : 'stops'}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <Users size={14} className="text-indigo-500" />
          <span className="text-xs font-semibold text-slate-700">{students.length} {students.length === 1 ? 'student' : 'students'} total</span>
        </div>
        {(route.start_time || route.departure_time) && (
          <div className="flex items-center gap-1.5">
            <Clock size={14} className="text-indigo-500" />
            <span className="text-xs text-slate-600">Departs: {route.start_time || route.departure_time}</span>
          </div>
        )}
        {(route.end_time || route.arrival_time) && (
          <div className="flex items-center gap-1.5">
            <Clock size={14} className="text-indigo-500" />
            <span className="text-xs text-slate-600">Arrives: {route.end_time || route.arrival_time}</span>
          </div>
        )}
        {route.total_distance && (
          <div className="flex items-center gap-1.5">
            <span className="text-xs text-slate-600">Distance: {route.total_distance}</span>
          </div>
        )}
      </div>

      {/* Vertical timeline */}
      <div className="relative pl-6">
        {/* Start marker */}
        <div className="flex items-start mb-0">
          <div className="absolute left-0 flex flex-col items-center">
            <div className="w-5 h-5 rounded-full bg-green-500 border-2 border-green-200 flex items-center justify-center shadow-sm">
              <div className="w-2 h-2 rounded-full bg-white" />
            </div>
            <div className="w-0.5 h-6 bg-slate-300" />
          </div>
          <div className="ml-4 pb-2">
            <span className="text-xs font-bold text-green-700 uppercase tracking-wide">Start</span>
            {route.start_location && <span className="text-xs text-slate-500 ml-2">{route.start_location}</span>}
          </div>
        </div>

        {/* Stop nodes */}
        {stops.map((stop, i) => (
          <div key={i} className="flex items-start mb-0">
            <div className="absolute left-0 flex flex-col items-center" style={{ top: `${(i + 1) * 56 + 12}px` }}>
              {i < stops.length - 1 && <div className="w-0.5 h-6 bg-slate-300" />}
            </div>
            <div className="relative flex items-start w-full">
              <div className="absolute -left-6 flex flex-col items-center">
                <div className="w-0.5 h-3 bg-slate-300" />
                <div className="w-4 h-4 rounded-full bg-indigo-500 border-2 border-indigo-200 flex items-center justify-center shadow-sm z-10">
                  <span className="text-[8px] font-bold text-white">{stop.order}</span>
                </div>
                <div className="w-0.5 h-3 bg-slate-300" />
              </div>
              <div className="ml-4 flex items-center gap-3 py-1.5 px-3 rounded-lg bg-white border border-slate-200 shadow-sm w-full max-w-md hover:border-indigo-200 transition-colors">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-800 truncate" title={stop.name}>{stop.name}</p>
                  {stop.time && <p className="text-[10px] text-slate-400">{stop.time}</p>}
                </div>
                {stop.student_count > 0 && (
                  <span className="flex items-center gap-1 text-xs font-medium text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full whitespace-nowrap">
                    <Users size={10} />
                    {stop.student_count}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* School (end) marker */}
        <div className="flex items-start mt-0">
          <div className="absolute left-0 flex flex-col items-center">
            <div className="w-0.5 h-3 bg-slate-300" />
            <div className="w-5 h-5 rounded-full bg-indigo-600 border-2 border-indigo-200 flex items-center justify-center shadow-sm">
              <div className="w-2 h-2 rounded-sm bg-white" />
            </div>
          </div>
          <div className="ml-4 pt-1">
            <span className="text-xs font-bold text-indigo-700 uppercase tracking-wide">School</span>
            {route.end_location && <span className="text-xs text-slate-500 ml-2">{route.end_location}</span>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function RoutesTab({ routes, search, setSearch, onAdd, onEdit, onDelete, onManageStudents, pagination, totalPages, totalCount }) {
  const [expandedRoute, setExpandedRoute] = useState(null);
  const filtered = routes.filter(r => !search || (r.name || '').toLowerCase().includes(search.toLowerCase()) || (r.area || '').toLowerCase().includes(search.toLowerCase()));

  const toggleExpand = (routeId) => {
    setExpandedRoute(expandedRoute === routeId ? null : routeId);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
      <div className="flex justify-between items-center mb-3"><h3 className="text-base font-semibold text-slate-900">Routes Management</h3><Button variant="primary" size="sm" icon={Plus} onClick={onAdd}>Add Route</Button></div>
      <div className="mb-3"><SearchInput value={search} onChange={setSearch} placeholder="Search routes..." /></div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead><tr className="border-b border-slate-200 text-left"><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase w-8"></th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Route Code</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Name</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Area</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Shift</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Status</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Actions</th></tr></thead>
          <tbody>
            {filtered.map(r => (
              <Fragment key={r.id}>
                <tr className="border-b border-slate-100 hover:bg-primary-50/40 transition-colors duration-150">
                  <td className="py-2 px-2">
                    <button onClick={() => toggleExpand(r.id)} className="p-1 hover:bg-slate-100 rounded transition-colors" title="View route stops">
                      {expandedRoute === r.id ? <ChevronDown className="w-4 h-4 text-slate-500" /> : <ChevronRight className="w-4 h-4 text-slate-400" />}
                    </button>
                  </td>
                  <td className="py-2 px-2 font-semibold text-slate-800">{r.route_code || ''}</td>
                  <td className="py-2 px-2">{r.name || ''}</td>
                  <td className="py-2 px-2 text-slate-500">{r.area || '—'}</td>
                  <td className="py-2 px-2 text-slate-500">{r.shift || '—'}</td>
                  <td className="py-2 px-2"><Badge status={r.status || 'Active'} /></td>
                  <td className="py-2 px-2"><div className="flex gap-1"><button className="p-1 hover:bg-blue-50 rounded active:scale-[0.97]" title="Manage Students" onClick={() => onManageStudents && onManageStudents(r)}><Users className="w-4 h-4 text-blue-500" /></button><button className="p-1 hover:bg-slate-100 rounded active:scale-[0.97]" onClick={() => onEdit(r)}><Pencil className="w-4 h-4 text-slate-500" /></button><button className="p-1 hover:bg-red-50 rounded active:scale-[0.97]" onClick={() => onDelete(r.id)}><Trash2 className="w-4 h-4 text-red-500" /></button></div></td>
                </tr>
                {expandedRoute === r.id && (
                  <tr>
                    <td colSpan={7} className="p-0">
                      <RouteVisualization route={r} />
                    </td>
                  </tr>
                )}
              </Fragment>
            ))}
            {filtered.length === 0 && <tr><td colSpan={7} className="text-center py-8 text-slate-400">No routes found</td></tr>}
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
