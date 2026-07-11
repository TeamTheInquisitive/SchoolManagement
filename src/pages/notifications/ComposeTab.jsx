import { useState } from 'react';
import { Send, GraduationCap, Briefcase, Bus, Users, UserCheck, Globe, Plus, Trash2 } from 'lucide-react';
import { useCustomTemplates, useUpdateCustomTemplates } from '../../services/notificationService';
import { Button, SearchableSelect, DateInput, TimeInput, Modal, NotificationComposer } from 'school-erp-ui-shared';
import { NOTIFICATION_TEMPLATES, RECIPIENT_GROUPS } from '../../constants.jsx';

const GROUP_ICONS = {
  teaching_staff: GraduationCap,
  non_teaching_staff: Briefcase,
  transport: Bus,
  students: Users,
  parents: UserCheck,
  all: Globe,
};

export default function ComposeTab({ selectedGroups, toggleGroup, setSelectedGroups, classFilter, setClassFilter, sectionFilter, setSectionFilter, classOptions, sectionOptions, title, setTitle, message, setMessage, scheduleDate, setScheduleDate, scheduleTime, setScheduleTime, onSend, recipientCount, notifications = [] }) {
  const [resendConfirm, setResendConfirm] = useState(null);

  const applyTemplate = (t) => { setTitle(t.title); setMessage(t.message); if (t.recipients && setSelectedGroups) setSelectedGroups(t.recipients); };

  const handleSend = () => {
    if (!title || !message || selectedGroups.length === 0) return;
    onSend();
  };

  const handleResend = (n) => {
    setResendConfirm(n);
  };

  const confirmResend = () => {
    if (resendConfirm) {
      setTitle(resendConfirm.title || resendConfirm.subject || '');
      setMessage(resendConfirm.message || resendConfirm.body || resendConfirm.content || '');
      setResendConfirm(null);
    }
  };

  const recipientLabel = selectedGroups.map(g => RECIPIENT_GROUPS.find(r => r.id === g)?.label).filter(Boolean).join(', ');

  return (
    <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
      <div className="md:col-span-8 space-y-4">
        {/* Recipients */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-50 to-indigo-100 flex items-center justify-center">
                <span className="text-xs">👥</span>
              </div>
              <h3 className="text-sm font-bold text-slate-900">Select Recipients</h3>
            </div>
            {selectedGroups.length > 0 && (
              <span className="text-xs font-semibold bg-emerald-50 text-emerald-700 px-2.5 py-1 rounded-full">{recipientCount || 0} recipients</span>
            )}
          </div>

          {/* Recipient Groups */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2.5 mb-4">
            {RECIPIENT_GROUPS.map(g => {
              const isSelected = selectedGroups.includes(g.id);
              const Icon = GROUP_ICONS[g.id] || Users;
              return (
                <div key={g.id} onClick={() => toggleGroup(g.id)} className={`relative p-3.5 rounded-xl cursor-pointer transition-all duration-200 active:scale-[0.97] border ${isSelected ? `${g.color} border-2 shadow-sm` : 'bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm'}`}>
                  {isSelected && <div className="absolute top-2.5 right-2.5 w-4 h-4 rounded-full bg-primary-500 flex items-center justify-center"><span className="text-[8px] text-white font-bold">✓</span></div>}
                  <Icon size={20} className={isSelected ? 'text-current' : 'text-slate-400'} />
                  <p className="text-xs font-bold text-slate-900 mt-2">{g.label}</p>
                  <p className="text-[10px] text-slate-400 mt-0.5">{g.description}</p>
                </div>
              );
            })}
          </div>

          {/* Selected Tags */}
          {selectedGroups.length > 0 && (
            <div className="flex items-center gap-2 flex-wrap mb-4 pb-4 border-b border-slate-100">
              {selectedGroups.map(g => (
                <span key={g} className="flex items-center gap-1 text-xs font-medium bg-primary-100 text-primary-700 px-2.5 py-1 rounded-full">
                  {RECIPIENT_GROUPS.find(r => r.id === g)?.label}
                  <button onClick={() => toggleGroup(g)} className="w-3.5 h-3.5 rounded-full bg-primary-200 flex items-center justify-center hover:bg-primary-300 transition-colors">
                    <span className="text-[9px] leading-none">×</span>
                  </button>
                </span>
              ))}
            </div>
          )}

          {/* Class/Section Filters */}
          <div className="flex items-center gap-3">
            <div className="flex-1">
              <label className="text-[10px] font-medium text-slate-400 uppercase mb-1 block">Filter by Class</label>
              <SearchableSelect value={classFilter} onChange={setClassFilter} options={classOptions || [{ value: '', label: 'All Classes' }]} placeholder="All Classes" />
            </div>
            <div className="flex-1">
              <label className="text-[10px] font-medium text-slate-400 uppercase mb-1 block">Filter by Section</label>
              <SearchableSelect value={sectionFilter} onChange={setSectionFilter} options={sectionOptions || [{ value: '', label: 'All Sections' }]} placeholder="All Sections" />
            </div>
          </div>
        </div>

        {/* NotificationComposer with emoji picker, preview, placeholder detection, confirm modal */}
        <NotificationComposer
          title={title}
          setTitle={setTitle}
          message={message}
          setMessage={setMessage}
          onSend={handleSend}
          isSending={false}
          recipientCount={recipientCount || 0}
          recipientLabel={recipientLabel}
          sendButtonLabel={scheduleDate ? 'Schedule Notification' : `Send to ${recipientCount || 0} Recipients`}
        >
          {/* Schedule fields */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
            <h3 className="text-base font-semibold text-slate-900 mb-3">Schedule (optional)</h3>
            <div className="grid grid-cols-2 gap-3">
              <DateInput value={scheduleDate} onChange={setScheduleDate} />
              <TimeInput value={scheduleTime} onChange={setScheduleTime} />
            </div>
          </div>
        </NotificationComposer>
      </div>

      {/* Resend Confirmation Modal */}
      <Modal open={!!resendConfirm} onClose={() => setResendConfirm(null)} title="Resend Notification" size="sm" persistent={false}>
        <div className="space-y-4">
          <p className="text-sm text-slate-600">Load this notification into the composer to resend?</p>
          <div className="bg-slate-50 rounded-lg p-3 border border-slate-100">
            <p className="text-sm font-medium text-slate-800">{resendConfirm?.title || resendConfirm?.subject}</p>
            <p className="text-xs text-slate-500 mt-1 line-clamp-2">{resendConfirm?.message || resendConfirm?.body || resendConfirm?.content}</p>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setResendConfirm(null)}>Cancel</Button>
            <Button variant="primary" onClick={confirmResend}>Load into Composer</Button>
          </div>
        </div>
      </Modal>

      {/* Sidebar: Templates + Recent + Tips */}
      <div className="md:col-span-4 space-y-4">
        {/* Custom Quick Templates (school-specific) */}
        <QuickTemplatesSection applyTemplate={applyTemplate} />

        {/* Standard Templates */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-purple-50 to-purple-100 flex items-center justify-center">
              <span className="text-xs">📝</span>
            </div>
            <h3 className="text-sm font-bold text-slate-900">Standard Templates</h3>
          </div>
          <div className="space-y-2">
            {NOTIFICATION_TEMPLATES.map((t, i) => {
              const icons = ['💰', '👥', '🏖️', '📋', '🎉'];
              const colors = ['bg-emerald-50 border-emerald-100', 'bg-blue-50 border-blue-100', 'bg-amber-50 border-amber-100', 'bg-purple-50 border-purple-100', 'bg-pink-50 border-pink-100'];
              return (
                <div key={i} onClick={() => applyTemplate(t)} className={`p-3 rounded-xl border cursor-pointer transition-all duration-200 hover:-translate-y-0.5 hover:shadow-sm active:scale-[0.98] ${colors[i % colors.length]}`}>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-sm">{icons[i % icons.length]}</span>
                    <p className="text-sm font-semibold text-slate-900">{t.title}</p>
                  </div>
                  <p className="text-[11px] text-slate-500 line-clamp-1 pl-6">{t.message}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Recent Notifications */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center">
              <span className="text-xs">📤</span>
            </div>
            <h3 className="text-sm font-bold text-slate-900">Recently Sent</h3>
          </div>
          {notifications.slice(0, 5).length > 0 ? (
            <div className="space-y-1.5">
              {notifications.slice(0, 5).map((n, i) => (
                <div key={n.id || i} className="flex items-center gap-2.5 p-2.5 rounded-lg hover:bg-slate-50 transition-colors group">
                  <div className="w-7 h-7 rounded-full bg-emerald-50 flex items-center justify-center flex-shrink-0">
                    <Send size={11} className="text-emerald-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-slate-900 truncate">{n.title || n.subject || 'Notification'}</p>
                    <p className="text-[10px] text-slate-400">{n.created_at || n.sent_at || n.date || ''}</p>
                  </div>
                  <button
                    onClick={() => handleResend(n)}
                    className="p-1.5 rounded-md text-slate-300 hover:text-primary-600 hover:bg-primary-50 transition-all duration-150 opacity-0 group-hover:opacity-100"
                    title="Resend this notification"
                  >
                    <Send size={12} />
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-400 text-center py-3">No notifications sent yet</p>
          )}
        </div>

        {/* Tips */}
        <div className="bg-gradient-to-br from-slate-50 to-slate-100/80 border border-slate-200 rounded-xl p-5">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-sm">💡</span>
            <p className="text-sm font-bold text-slate-900">Tips</p>
          </div>
          <div className="space-y-2">
            {['Keep messages concise and actionable', 'Include dates and deadlines clearly', 'Use templates for recurring messages', 'Schedule non-urgent for morning hours'].map((tip, i) => (
              <div key={i} className="flex items-start gap-2">
                <span className="w-4 h-4 rounded-full bg-white border border-slate-200 flex items-center justify-center text-[8px] text-slate-500 flex-shrink-0 mt-0.5">{i + 1}</span>
                <p className="text-xs text-slate-600">{tip}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function QuickTemplatesSection({ applyTemplate }) {
  const { data } = useCustomTemplates();
  const updateMutation = useUpdateCustomTemplates();
  const [showAdd, setShowAdd] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newMessage, setNewMessage] = useState('');

  const templates = data?.templates || [];

  const handleAdd = () => {
    if (!newTitle.trim() || !newMessage.trim()) return;
    const updated = [...templates, { title: newTitle.trim(), message: newMessage.trim() }];
    updateMutation.mutate(updated, { onSuccess: () => { setShowAdd(false); setNewTitle(''); setNewMessage(''); } });
  };

  const handleDelete = (index) => {
    const updated = templates.filter((_, i) => i !== index);
    updateMutation.mutate(updated);
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-emerald-50 to-emerald-100 flex items-center justify-center">
            <span className="text-xs">⚡</span>
          </div>
          <h3 className="text-sm font-bold text-slate-900">Quick Templates</h3>
        </div>
        <button onClick={() => setShowAdd(!showAdd)} className="p-1 rounded-md hover:bg-slate-100 text-slate-400 hover:text-primary-600 transition-colors">
          <Plus size={14} />
        </button>
      </div>

      {showAdd && (
        <div className="mb-3 p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-2">
          <input type="text" value={newTitle} onChange={e => setNewTitle(e.target.value)} placeholder="Template title" className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary-500" />
          <textarea value={newMessage} onChange={e => setNewMessage(e.target.value)} placeholder="Template message..." rows={2} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none" />
          <div className="flex gap-2 justify-end">
            <button onClick={() => { setShowAdd(false); setNewTitle(''); setNewMessage(''); }} className="text-xs text-slate-500 hover:text-slate-700">Cancel</button>
            <button onClick={handleAdd} disabled={!newTitle.trim() || !newMessage.trim()} className="text-xs font-medium text-primary-600 hover:text-primary-700 disabled:opacity-50">Save</button>
          </div>
        </div>
      )}

      {templates.length > 0 ? (
        <div className="space-y-2">
          {templates.map((t, i) => (
            <div key={i} onClick={() => applyTemplate(t)} className="group p-3 rounded-xl border bg-white border-slate-100 cursor-pointer transition-all duration-200 hover:-translate-y-0.5 hover:shadow-sm hover:border-primary-200 active:scale-[0.98]">
              <div className="flex items-center justify-between mb-1">
                <p className="text-sm font-semibold text-slate-900">{t.title}</p>
                <button onClick={(e) => { e.stopPropagation(); handleDelete(i); }} className="p-1 rounded text-slate-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-all"><Trash2 size={12} /></button>
              </div>
              <p className="text-[11px] text-slate-500 line-clamp-1">{t.message}</p>
            </div>
          ))}
        </div>
      ) : !showAdd && (
        <p className="text-xs text-slate-400 text-center py-3">No custom templates yet. Click + to create one.</p>
      )}
    </div>
  );
}
