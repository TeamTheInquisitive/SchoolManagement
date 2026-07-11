import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Send, Users, Eye, Clock, Search, ChevronDown, ChevronRight, User } from 'lucide-react';
import { Badge, Modal, Pagination, usePagination, DatePicker, SearchableSelect } from 'school-erp-ui-shared';
import api from '../../services/api';

function timeAgo(dateStr) {
  if (!dateStr) return '';
  const now = new Date();
  const date = new Date(dateStr);
  const diff = Math.floor((now - date) / 1000);
  if (diff < 60) return 'Just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  if (diff < 604800) return `${Math.floor(diff / 86400)}d ago`;
  return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

export default function TeacherSentTab() {
  const pagination = usePagination(20);
  const [teacherFilter, setTeacherFilter] = useState('');
  const [dateFilter, setDateFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [viewMessage, setViewMessage] = useState(null);
  const [expanded, setExpanded] = useState(null);

  const { data, isFetching } = useQuery({
    queryKey: ['admin-teacher-notifications', pagination.params, teacherFilter, dateFilter],
    queryFn: () => api.get('/admin/notifications/teacher-sent', {
      params: { ...pagination.params, teacher_id: teacherFilter || undefined, date: dateFilter || undefined }
    }).then(r => r.data).catch(() => ({ results: [], teacher_summary: [], total_messages: 0, total_teachers_sent: 0 })),
    placeholderData: (prev) => prev,
  });

  const messages = data?.results || [];
  const teacherSummary = data?.teacher_summary || [];
  const totalMessages = data?.total_messages || data?.count || 0;
  const totalTeachers = data?.total_teachers_sent || 0;

  const filtered = messages.filter(n => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (n.title || '').toLowerCase().includes(q) || (n.sender_name || '').toLowerCase().includes(q) || (n.message || '').toLowerCase().includes(q);
  });

  const teacherOptions = [{ value: '', label: 'All Teachers' }, ...teacherSummary.map(t => ({ value: t.teacher_id, label: `${t.teacher_name} (${t.messages_sent})` }))];

  return (
    <div className="space-y-4">
      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <div className="bg-white border border-slate-200 rounded-xl p-4 text-center">
          <p className="text-xl font-bold text-slate-900">{totalMessages}</p>
          <p className="text-xs text-slate-500">Total Messages</p>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 text-center">
          <p className="text-xl font-bold text-blue-700">{totalTeachers}</p>
          <p className="text-xs text-blue-600">Teachers Sent</p>
        </div>
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-center">
          <p className="text-xl font-bold text-emerald-700">{messages.reduce((s, m) => s + (m.recipients_count || 0), 0)}</p>
          <p className="text-xs text-emerald-600">Total Recipients</p>
        </div>
        <div className="bg-purple-50 border border-purple-200 rounded-xl p-4 text-center">
          <p className="text-xl font-bold text-purple-700">{teacherSummary.length > 0 ? Math.round(totalMessages / totalTeachers) : 0}</p>
          <p className="text-xs text-purple-600">Avg per Teacher</p>
        </div>
      </div>

      {/* Teacher Summary Table */}
      {teacherSummary.length > 0 && (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-slate-100 bg-slate-50/50">
            <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wider">Teacher Activity Summary</h3>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 border-b border-slate-100">
                <tr>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-slate-500">#</th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-slate-500">Teacher</th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-slate-500">Messages Sent</th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-slate-500">Total Recipients</th>
                  <th className="px-4 py-2.5 text-left text-xs font-medium text-slate-500">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {teacherSummary.map((t, idx) => (
                  <tr key={t.teacher_id} className="hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-2.5 text-xs text-slate-400">{idx + 1}</td>
                    <td className="px-4 py-2.5">
                      <div className="flex items-center gap-2">
                        <div className="w-7 h-7 rounded-full bg-indigo-600 text-white flex items-center justify-center text-[10px] font-bold">{(t.teacher_name || '').slice(0, 2).toUpperCase()}</div>
                        <span className="text-sm font-medium text-slate-900">{t.teacher_name}</span>
                      </div>
                    </td>
                    <td className="px-4 py-2.5">
                      <span className="text-sm font-semibold text-slate-900">{t.messages_sent}</span>
                    </td>
                    <td className="px-4 py-2.5">
                      <span className="text-sm text-slate-600">{t.total_recipients}</span>
                    </td>
                    <td className="px-4 py-2.5">
                      <button onClick={() => setTeacherFilter(t.teacher_id)} className="text-xs font-medium text-primary-600 hover:text-primary-700 hover:underline">
                        View Messages
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="w-52">
          <SearchableSelect value={teacherFilter} onChange={(v) => { setTeacherFilter(v); pagination.reset(); }} options={teacherOptions} placeholder="All Teachers" />
        </div>
        <div className="w-44">
          <DatePicker value={dateFilter} onChange={(v) => { setDateFilter(v); pagination.reset(); }} placeholder="Filter by date" max={new Date().toISOString().split('T')[0]} />
        </div>
        <div className="flex-1 min-w-[200px] relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input value={searchQuery} onChange={e => setSearchQuery(e.target.value)} placeholder="Search by title, teacher, or content..." className="w-full pl-9 pr-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 hover:border-slate-400 transition-all" />
        </div>
        {(teacherFilter || dateFilter || searchQuery) && (
          <button onClick={() => { setTeacherFilter(''); setDateFilter(''); setSearchQuery(''); }} className="text-xs font-medium text-red-500 hover:text-red-700 px-2 py-1.5 rounded-lg hover:bg-red-50 transition-colors">Clear</button>
        )}
      </div>

      {/* Messages List */}
      {filtered.length === 0 ? (
        <div className="bg-white border border-slate-200 rounded-xl py-16 text-center">
          <Send size={24} className="text-slate-300 mx-auto mb-3" />
          <p className="text-sm font-medium text-slate-600">No teacher messages found</p>
          <p className="text-xs text-slate-400 mt-1">Teachers haven't sent any notifications yet</p>
        </div>
      ) : (
        <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
          {filtered.map((n, i) => (
            <div key={n.id || i} className="border-b border-slate-100 last:border-0">
              <div className="flex items-center gap-3 px-5 py-4 hover:bg-slate-50 cursor-pointer transition-colors" onClick={() => setExpanded(expanded === i ? null : i)}>
                <div className="w-9 h-9 rounded-full bg-indigo-600 text-white flex items-center justify-center text-xs font-bold flex-shrink-0">
                  {(n.sender_name || '').slice(0, 2).toUpperCase()}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-0.5">
                    <p className="text-sm font-semibold text-slate-900 truncate">{n.title}</p>
                  </div>
                  <div className="flex items-center gap-3 text-[11px] text-slate-500">
                    <span className="font-medium text-indigo-600">{n.sender_name}</span>
                    <span>To: {n.target_type}{n.target_class_name ? ` (${n.target_class_name}${n.target_section ? `-${n.target_section}` : ''})` : ''}</span>
                    <span>{timeAgo(n.sent_at || n.created_at)}</span>
                  </div>
                </div>
                <div className="flex items-center gap-3 flex-shrink-0">
                  <span className="text-xs font-medium bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">{n.recipients_count} recipients</span>
                  <Badge status={n.status}>{n.status}</Badge>
                  {expanded === i ? <ChevronDown size={14} className="text-slate-400" /> : <ChevronRight size={14} className="text-slate-400" />}
                </div>
              </div>

              {expanded === i && (
                <div className="px-5 pb-4 border-t border-slate-100">
                  <div className="ml-12 mt-3 space-y-3">
                    <div className="bg-slate-50 rounded-xl p-4 border border-slate-100">
                      <p className="text-sm text-slate-800 whitespace-pre-wrap leading-relaxed">{n.message}</p>
                    </div>
                    <div className="flex items-center gap-4 text-[11px] text-slate-500">
                      <span><Clock size={10} className="inline mr-1" />{n.sent_at ? new Date(n.sent_at).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'}</span>
                      <span><User size={10} className="inline mr-1" />{n.sender_name}</span>
                      <span><Users size={10} className="inline mr-1" />{n.recipients_count} recipients</span>
                      <button onClick={(e) => { e.stopPropagation(); setViewMessage(n); }} className="ml-auto flex items-center gap-1 text-xs font-medium text-primary-600 hover:text-primary-700 px-2 py-1 rounded-lg hover:bg-primary-50 transition-colors">
                        <Eye size={12} /> Full Details
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      <Pagination page={pagination.page} totalPages={data?.total_pages || 1} totalCount={data?.count || 0} pageSize={pagination.pageSize} onPageChange={p => pagination.setPage(p)} />

      {/* View Full Modal */}
      <Modal open={!!viewMessage} onClose={() => setViewMessage(null)} title="Teacher Message Details" size="lg">
        {viewMessage && (
          <div className="space-y-4">
            <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-indigo-600 text-white flex items-center justify-center text-sm font-bold">{(viewMessage.sender_name || '').slice(0, 2).toUpperCase()}</div>
                <div>
                  <p className="text-sm font-bold text-slate-900">{viewMessage.sender_name}</p>
                  <p className="text-xs text-slate-500">{viewMessage.sent_at ? new Date(viewMessage.sent_at).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'}</p>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              <div className="bg-white border border-slate-200 rounded-xl p-3 text-center">
                <p className="text-lg font-bold text-slate-900">{viewMessage.recipients_count || 0}</p>
                <p className="text-[10px] text-slate-500">Recipients</p>
              </div>
              <div className="bg-white border border-slate-200 rounded-xl p-3 text-center">
                <p className="text-sm font-bold text-slate-900">{viewMessage.target_type}</p>
                <p className="text-[10px] text-slate-500">Target Group</p>
              </div>
              <div className="bg-white border border-slate-200 rounded-xl p-3 text-center">
                <p className="text-sm font-bold text-slate-900">{viewMessage.target_class_name ? `${viewMessage.target_class_name}${viewMessage.target_section ? `-${viewMessage.target_section}` : ''}` : 'All'}</p>
                <p className="text-[10px] text-slate-500">Class/Section</p>
              </div>
            </div>

            <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
              <div className="px-4 py-2.5 border-b border-slate-100 bg-slate-50/50">
                <p className="text-xs font-semibold text-slate-500 uppercase">{viewMessage.title}</p>
              </div>
              <div className="p-4">
                <p className="text-sm text-slate-800 whitespace-pre-wrap leading-relaxed">{viewMessage.message}</p>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
