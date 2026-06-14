import { CheckCircle, XCircle } from 'lucide-react';
import { Badge, DataTable } from 'school-erp-ui-shared';

export default function LeaveTab({ leaves, onApprove, onReject }) {
  const columns = [
    { key: 'employee', label: 'Employee', render: (l) => <span className="font-medium text-slate-800">{l.teacher_name || l.employee_name || ''}</span> },
    { key: 'leave_type', label: 'Type', render: (l) => <span className="text-slate-500">{l.leave_type || l.type || ''}</span> },
    { key: 'from_date', label: 'From', render: (l) => <span className="text-slate-500">{l.from_date || l.start_date || ''}</span> },
    { key: 'to_date', label: 'To', render: (l) => <span className="text-slate-500">{l.to_date || l.end_date || ''}</span> },
    { key: 'days', label: 'Days', render: (l) => <span className="text-slate-500">{l.days || ''}</span> },
    { key: 'reason', label: 'Reason', render: (l) => <span className="text-slate-500 max-w-[150px] truncate block">{l.reason || ''}</span> },
    { key: 'status', label: 'Status', render: (l) => <Badge status={l.status || 'Pending'} /> },
    {
      key: 'actions', label: 'Actions',
      render: (l) => l.status === 'Pending' ? (
        <div className="flex gap-1">
          <button onClick={() => onApprove(l.id)} className="p-1.5 hover:bg-green-50 rounded-lg transition-all duration-150 active:scale-[0.97]"><CheckCircle className="w-4 h-4 text-green-600" /></button>
          <button onClick={() => onReject(l.id)} className="p-1.5 hover:bg-red-50 rounded-lg transition-all duration-150 active:scale-[0.97]"><XCircle className="w-4 h-4 text-red-500" /></button>
        </div>
      ) : null,
    },
  ];

  return (
    <DataTable
      columns={columns}
      data={leaves}
      loading={false}
      emptyMessage="No pending leave requests"
      emptyIcon={CheckCircle}
      headerTitle="Pending Leave Requests"
    />
  );
}
