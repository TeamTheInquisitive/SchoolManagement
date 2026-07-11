import { useState } from 'react';
import { Send, Clock, ChevronDown, ChevronRight, Users, Eye, X, Search, Filter } from 'lucide-react';
import { Badge, Modal, Pagination, DatePicker, SearchableSelect } from 'school-erp-ui-shared';

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

const TARGET_FILTER_OPTIONS = [
  { value: '', label: 'All Audiences' },
  { value: 'all', label: 'Everyone' },
  { value: 'students', label: 'Students' },
  { value: 'teaching_staff', label: 'Teaching Staff' },
  { value: 'non_teaching_staff', label: 'Non-Teaching Staff' },
  { value: 'parents', label: 'Parents' },
  { value: 'transport', label: 'Transport' },
];

export default function SentHistoryTab({ notifications, pagination, notificationsData, filterDate, setFilterDate }) {
  const [expanded, setExpanded] = useState(null);
  const [viewNotification, setViewNotification] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [targetFilter, setTargetFilter] = useState('');

  const totalCount = notificationsData?.count || 0;
  const deliveredCount = notifications.filter(n => n.status === 'Sent' || n.status === 'Delivered').length;
  const scheduledCount = notifications.filter(n => n.status === 'Scheduled' || n.status === 'Pending').length;

  const filtered = notifications.filter(n => {
    const matchSearch = !searchQuery || (n.title || n.subject || '').toLowerCase().includes(searchQuery.toLowerCase()) || (n.message || n.body || n.content || '').toLowerCase().includes(searchQuery.toLowerCase());
    const matchTarget = !targetFilter || (n.target_type || '').toLowerCase() === targetFilter.toLowerCase();
    return matchSearch && matchTarget;
  });

  return (
    <div className="space-y-3">
      {/* Filters Row */}
      <div className="flex flex-wrap items-center gap-3 mb-2">
        <div className="w-56">
          <DatePicker
            value={filterDate}
            onChange={setFilterDate}
            placeholder="Filter by date"
            max={new Date().toISOString().split('T')[0]}
          />
        </div>
        <div className="w-44">
          <SearchableSelect value={targetFilter} onChange={setTargetFilter} options={TARGET_FILTER_OPTIONS} placeholder="All Audiences" />
        </div>
        <div className="flex-1 min-w-[200px] relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            placeholder="Search by title or content..."
            className="w-full pl-9 pr-3 py-2.5 border border-slate-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent hover:border-slate-400 transition-all"
          />
        </div>
        {(filterDate || targetFilter || searchQuery) && (
          <button onClick={() => { setFilterDate(''); setTargetFilter(''); setSearchQuery(''); }} className="flex items-center gap-1 text-xs font-medium text-red-500 hover:text-red-700 px-2 py-1.5 rounded-lg hover:bg-red-50 transition-colors">
            <X size={12} /> Clear all
          </button>
        )}
      </div>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-3 mb-2">
        <div className="bg-white border border-slate-200 rounded-xl p-4 text-center">
          <p className="text-xl font-bold text-slate-900">{totalCount}</p>
          <p className="text-xs text-slate-500">{filterDate ? 'Sent on Date' : 'Total Sent'}</p>
        </div>
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-center">
          <p className="text-xl font-bold text-emerald-700">{deliveredCount}</p>
          <p className="text-xs text-emerald-600">Delivered</p>
        </div>
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-center">
          <p className="text-xl font-bold text-amber-700">{scheduledCount}</p>
          <p className="text-xs text-amber-600">Scheduled</p>
        </div>
      </div>

      {filtered.length === 0 && (
        <div className="bg-white border border-slate-200 rounded-xl py-16 text-center">
          <div className="w-14 h-14 rounded-full bg-slate-100 flex items-center justify-center mx-auto mb-3">
            <Send size={22} className="text-slate-400" />
          </div>
          <p className="text-sm font-medium text-slate-600">{filterDate ? 'No notifications sent on this date' : searchQuery ? 'No notifications matching your search' : 'No notifications sent yet'}</p>
          <p className="text-xs text-slate-400 mt-1">{filterDate || searchQuery ? 'Try adjusting your filters' : 'Compose a message to get started'}</p>
        </div>
      )}

      {/* Notification List */}
      {filtered.length > 0 && <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
        {filtered.map((n, i) => (
          <div key={n.id || i} className="border-b border-slate-100 last:border-0">
            {/* Main Row */}
            <div className="flex items-center gap-3 px-5 py-4 transition-colors duration-150 hover:bg-slate-50 cursor-pointer" onClick={() => setExpanded(expanded === i ? null : i)}>
              <div className={`w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0 ${n.status === 'Sent' || n.status === 'Delivered' ? 'bg-emerald-50' : 'bg-amber-50'}`}>
                {n.status === 'Sent' || n.status === 'Delivered' ? <Send size={16} className="text-emerald-600" /> : <Clock size={16} className="text-amber-600" />}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-bold text-slate-900">{n.title || n.subject || 'Notification'}</p>
                <div className="flex items-center gap-3 mt-1">
                  <span className="flex items-center gap-1 text-xs text-slate-500"><Users size={11} /> {n.target_type || n.recipients || 'All'}</span>
                  <span className="text-xs text-slate-400" title={n.sent_at || n.created_at ? new Date(n.sent_at || n.created_at).toLocaleString() : ''}>{timeAgo(n.sent_at || n.created_at)}</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-xs font-medium bg-slate-100 text-slate-600 px-2.5 py-1 rounded-full">{n.recipients_count || 0} recipients</span>
                <Badge status={n.status || 'Sent'}>{n.status || 'Sent'}</Badge>
                {expanded === i ? <ChevronDown size={16} className="text-slate-400" /> : <ChevronRight size={16} className="text-slate-400" />}
              </div>
            </div>

            {/* Expanded Details */}
            {expanded === i && (
              <div className="px-5 pb-4 pt-0 border-t border-slate-100">
                <div className="ml-[52px] mt-3 space-y-3">
                  {/* Message bubble */}
                  <div className="bg-gradient-to-br from-slate-50 to-slate-100/50 rounded-xl p-4 border border-slate-100">
                    <p className="text-sm text-slate-800 whitespace-pre-wrap leading-relaxed">{n.message || n.body || n.content || 'No content available'}</p>
                  </div>

                  {/* Meta info */}
                  <div className="flex flex-wrap items-center gap-3">
                    <div className="flex items-center gap-1.5 text-xs text-slate-500">
                      <Clock size={11} />
                      <span>{n.sent_at || n.created_at ? new Date(n.sent_at || n.created_at).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'}</span>
                    </div>
                    {n.sent_via && (
                      <span className="text-[10px] bg-blue-50 text-blue-600 px-2 py-0.5 rounded-full font-medium">{n.sent_via}</span>
                    )}
                    {n.target_type && (
                      <span className="text-[10px] bg-purple-50 text-purple-600 px-2 py-0.5 rounded-full font-medium">To: {n.target_type}</span>
                    )}
                    {n.scheduled_at && (
                      <span className="text-[10px] bg-amber-50 text-amber-600 px-2 py-0.5 rounded-full font-medium">Scheduled: {new Date(n.scheduled_at).toLocaleString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })}</span>
                    )}
                    <button onClick={(e) => { e.stopPropagation(); setViewNotification(n); }} className="ml-auto flex items-center gap-1.5 text-xs font-medium text-primary-600 hover:text-primary-700 hover:bg-primary-50 px-2.5 py-1.5 rounded-lg transition-colors">
                      <Eye size={12} /> View Full Details
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>}

      {pagination && <Pagination
        page={pagination.page}
        totalPages={notificationsData?.total_pages || 1}
        totalCount={notificationsData?.count || 0}
        pageSize={pagination.pageSize}
        onPageChange={(p) => pagination.setPage(p)}
      />}

      {/* View Full Modal */}
      <Modal open={!!viewNotification} onClose={() => setViewNotification(null)} title="Notification Details" size="lg">
        {viewNotification && (
          <div className="space-y-5">
            {/* Header Card */}
            <div className="bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-100 rounded-xl p-5">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <div className={`w-11 h-11 rounded-xl flex items-center justify-center ${viewNotification.status === 'Sent' || viewNotification.status === 'Delivered' ? 'bg-emerald-100' : 'bg-amber-100'}`}>
                    {viewNotification.status === 'Sent' || viewNotification.status === 'Delivered' ? <Send size={18} className="text-emerald-600" /> : <Clock size={18} className="text-amber-600" />}
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-slate-900">{viewNotification.title || viewNotification.subject || 'Notification'}</h3>
                    <p className="text-xs text-slate-500 mt-0.5">Sent on {(viewNotification.sent_at || viewNotification.created_at) ? new Date(viewNotification.sent_at || viewNotification.created_at).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : viewNotification.date || '—'}</p>
                  </div>
                </div>
                <Badge status={viewNotification.status || 'Sent'}>{viewNotification.status || 'Sent'}</Badge>
              </div>
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              <div className="bg-white border border-slate-200 rounded-xl p-3.5 text-center">
                <Users size={16} className="text-blue-500 mx-auto mb-1" />
                <p className="text-lg font-bold text-slate-900">{viewNotification.recipients_count || 0}</p>
                <p className="text-[10px] text-slate-500">Recipients</p>
              </div>
              <div className="bg-white border border-slate-200 rounded-xl p-3.5 text-center">
                <Send size={16} className="text-emerald-500 mx-auto mb-1" />
                <p className="text-sm font-bold text-slate-900">{viewNotification.target_type || 'All'}</p>
                <p className="text-[10px] text-slate-500">Target Group</p>
              </div>
              <div className="bg-white border border-slate-200 rounded-xl p-3.5 text-center">
                <Clock size={16} className="text-purple-500 mx-auto mb-1" />
                <p className="text-sm font-bold text-slate-900">{viewNotification.sent_via || 'In-App'}</p>
                <p className="text-[10px] text-slate-500">Channel</p>
              </div>
              <div className="bg-white border border-slate-200 rounded-xl p-3.5 text-center">
                <Eye size={16} className="text-amber-500 mx-auto mb-1" />
                <p className="text-sm font-bold text-slate-900">{viewNotification.status === 'Sent' || viewNotification.status === 'Delivered' ? '✓' : '—'}</p>
                <p className="text-[10px] text-slate-500">Delivered</p>
              </div>
            </div>

            {/* Message Content */}
            <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
              <div className="px-4 py-3 border-b border-slate-100 bg-slate-50/50">
                <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Message Content</p>
              </div>
              <div className="p-5">
                <p className="text-sm text-slate-800 whitespace-pre-wrap leading-relaxed">{viewNotification.message || viewNotification.body || viewNotification.content || 'No content available'}</p>
              </div>
            </div>

            {/* Timeline & Info */}
            <div className="bg-slate-50 rounded-xl p-4">
              <p className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-3">Delivery Info</p>
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-emerald-500" />
                  <p className="text-xs text-slate-700"><span className="font-medium">Created</span> — {viewNotification.created_at ? new Date(viewNotification.created_at).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : viewNotification.date || '—'}</p>
                </div>
                {viewNotification.scheduled_at && (
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-amber-500" />
                    <p className="text-xs text-slate-700"><span className="font-medium">Scheduled</span> — {new Date(viewNotification.scheduled_at).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' })}</p>
                  </div>
                )}
                <div className="flex items-center gap-3">
                  <div className="w-2 h-2 rounded-full bg-blue-500" />
                  <p className="text-xs text-slate-700"><span className="font-medium">Sent</span> — {viewNotification.sent_at ? new Date(viewNotification.sent_at).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : viewNotification.date || '—'}</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className={`w-2 h-2 rounded-full ${viewNotification.status === 'Delivered' || viewNotification.status === 'Sent' ? 'bg-emerald-500' : 'bg-slate-300'}`} />
                  <p className="text-xs text-slate-700"><span className="font-medium">Delivered</span> — {viewNotification.status === 'Delivered' || viewNotification.status === 'Sent' ? 'Yes' : 'Pending'}</p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-3 mt-4 pt-3 border-t border-slate-200">
                <div>
                  <p className="text-[10px] text-slate-400 uppercase font-medium mb-0.5">Read Rate</p>
                  <p className="text-sm font-medium text-slate-800">{viewNotification.read_rate || '0%'}</p>
                </div>
                <div>
                  <p className="text-[10px] text-slate-400 uppercase font-medium mb-0.5">Channel</p>
                  <p className="text-sm font-medium text-slate-800">{viewNotification.send_via || viewNotification.sent_via || 'In-App'}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
