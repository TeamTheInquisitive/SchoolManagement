import { useState } from 'react';
import { Megaphone, History, UserCheck } from 'lucide-react';
import { useCreateNotification, useNotifications } from '../../services/notificationService';
import { useClassSectionFilter } from '../../hooks/useClassSectionFilter';
import { RECIPIENT_GROUPS } from '../../constants.jsx';
import { useToast, Breadcrumb, Pagination, usePagination, useTabState } from 'school-erp-ui-shared';
import { useDashboardStats } from '../../services/dashboardService';
import ComposeTab from './ComposeTab';
import SentHistoryTab from './SentHistoryTab';
import TeacherSentTab from './TeacherSentTab';

export default function NotificationsPage() {
  const notifTabs = [{ id: 'compose', label: 'Compose', icon: Megaphone }, { id: 'sent', label: 'Sent', icon: History }];
  const [tab, setTab] = useTabState(notifTabs);
  const [selectedGroups, setSelectedGroups] = useState([]);
  const { selectedClass: classFilter, setSelectedClass: setClassFilter, selectedSection: sectionFilter, setSelectedSection: setSectionFilter, classOptions, sectionOptions } = useClassSectionFilter();
  const [title, setTitle] = useState('');
  const [message, setMessage] = useState('');
  const [scheduleDate, setScheduleDate] = useState('');
  const [scheduleTime, setScheduleTime] = useState('');
  const [filterDate, setFilterDate] = useState('');

  const toast = useToast();
  const pagination = usePagination(20, "admin-notifications");
  const createMutation = useCreateNotification();
  const { data: notificationsData } = useNotifications({ ...pagination.params, date: filterDate || undefined });
  const notifications = Array.isArray(notificationsData?.results) ? notificationsData.results : [];

  const { data: statsData } = useDashboardStats();
  const totalStudents = statsData?.total_students || 0;
  const totalTeachers = statsData?.total_teachers || 0;

  const getGroupCount = (groupId) => {
    switch (groupId) {
      case 'teaching_staff': return totalTeachers;
      case 'non_teaching_staff': return Math.max(0, (statsData?.total_staff || totalTeachers) - totalTeachers);
      case 'students': return totalStudents;
      case 'parents': return totalStudents;
      case 'transport': return statsData?.total_drivers || 0;
      case 'all': return totalStudents + totalTeachers;
      default: return 0;
    }
  };

  const toggleGroup = (id) => { setSelectedGroups(prev => prev.includes(id) ? prev.filter(g => g !== id) : [...prev, id]); };
  const recipientCount = selectedGroups.reduce((sum, g) => sum + getGroupCount(g), 0);

  const handleSend = () => {
    const targetType = selectedGroups.length === 1 ? selectedGroups[0] : 'all';
    createMutation.mutate({ title, message, target_type: targetType, target_class_name: classFilter || undefined, target_section: sectionFilter || undefined, send_via: 'in_app', scheduled_at: scheduleDate && scheduleTime ? `${scheduleDate}T${scheduleTime}:00` : undefined }, {
      onSuccess: () => { setTitle(''); setMessage(''); setSelectedGroups([]); setScheduleDate(''); setScheduleTime(''); toast.success('Notification sent successfully'); },
      onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to send notification'); },
    });
  };

  const displayTabs = [{ label: 'Compose', icon: Megaphone }, { label: `Sent (${notificationsData?.count || notifications.length})`, icon: History }, { label: 'Teacher Sent', icon: UserCheck }];

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Notifications' }]} />
      <div className="mb-6"><h1 className="text-2xl md:text-3xl font-bold text-slate-900">Notifications</h1><p className="text-sm text-slate-500 mt-1">Send announcements and messages to students, parents & staff</p></div>
      <div className="flex border-b border-slate-200 mb-4">
        {displayTabs.map((t, i) => (<button key={t.label} onClick={() => setTab(i)} className={`flex items-center gap-1.5 px-3 py-2 text-sm font-medium border-b-2 transition ${tab === i ? 'border-purple-600 text-purple-600' : 'border-transparent text-slate-500'}`}><t.icon className="w-4 h-4" />{t.label}</button>))}
      </div>
      {tab === 0 && <ComposeTab selectedGroups={selectedGroups} toggleGroup={toggleGroup} setSelectedGroups={setSelectedGroups} classFilter={classFilter} setClassFilter={setClassFilter} sectionFilter={sectionFilter} setSectionFilter={setSectionFilter} classOptions={classOptions} sectionOptions={sectionOptions} title={title} setTitle={setTitle} message={message} setMessage={setMessage} scheduleDate={scheduleDate} setScheduleDate={setScheduleDate} scheduleTime={scheduleTime} setScheduleTime={setScheduleTime} onSend={handleSend} recipientCount={recipientCount} notifications={notifications} />}
      {tab === 1 && <SentHistoryTab notifications={notifications} pagination={pagination} notificationsData={notificationsData} filterDate={filterDate} setFilterDate={(v) => { setFilterDate(v); pagination.reset(); }} />}
      {tab === 2 && <TeacherSentTab />}
    </div>
  );
}
