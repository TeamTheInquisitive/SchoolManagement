import { useState } from 'react';
import { DollarSign, FileText } from 'lucide-react';
import { usePayroll, useRunPayroll } from '../../services/payrollService';
import { Button, Badge, Tabs, useToast, Breadcrumb, Pagination, usePagination, useTabState } from 'school-erp-ui-shared';

export default function PayrollPage() {
  const toast = useToast();
  const payrollTabs = [{ id: 'salary-structure', label: 'Salary Structure', icon: DollarSign }, { id: 'payslips', label: 'Payslips', icon: FileText }];
  const [tab, setTab] = useTabState(payrollTabs);
  const pagination = usePagination(20, "admin-payroll");
  const { data: payrollData } = usePayroll(pagination.params);
  const runPayrollMutation = useRunPayroll();

  const salaries = payrollData?.salaries ?? [];
  const payslips = payrollData?.payslips ?? [];
  const kpis = payrollData?.kpis ?? [];

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Payroll' }]} />
      <div className="mb-6"><h1 className="text-2xl md:text-3xl font-bold text-slate-900">Payroll</h1><p className="text-sm text-slate-500 mt-1">Manage salary structure and payslips</p></div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4 mb-6">
        {kpis.map(k => (
          <div key={k.label} className="bg-white border border-slate-200 rounded-xl p-4 md:p-5 flex justify-between items-center transition-all duration-200 hover:-translate-y-0.5 hover:shadow-soft-lg hover:border-slate-300 cursor-default group">
            <div><p className="text-sm text-slate-500 font-medium">{k.label}</p><p className="text-2xl font-bold text-slate-900 mt-0.5">{k.value}</p></div>
            <div className="w-10 h-10 rounded-xl flex items-center justify-center transition-transform duration-200 group-hover:scale-110" style={{ backgroundColor: k.bgcolor }}><div className="w-3 h-3 rounded-full" style={{ backgroundColor: k.color }} /></div>
          </div>
        ))}
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
        <Tabs tabs={payrollTabs} active={tab} onChange={setTab} className="mb-4" />

        {tab === 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-slate-200 text-left">{['Name', 'Department', 'Basic', 'HRA', 'DA', 'Deductions', 'Net'].map(h => <th key={h} className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">{h}</th>)}</tr></thead>
              <tbody>{salaries.map(s => <tr key={s.id} className="border-b border-slate-100"><td className="py-2 px-2 font-medium text-slate-800">{s.name}</td><td className="py-2 px-2 text-slate-500">{s.dept}</td><td className="py-2 px-2 text-slate-500">₹{s.basic}</td><td className="py-2 px-2 text-slate-500">₹{s.hra}</td><td className="py-2 px-2 text-slate-500">₹{s.da}</td><td className="py-2 px-2 text-slate-500">₹{s.deductions}</td><td className="py-2 px-2 font-semibold text-slate-800">₹{s.net}</td></tr>)}</tbody>
            </table>
          </div>
        )}

        {tab === 1 && (
          <>
            <Button variant="primary" size="sm" onClick={() => runPayrollMutation.mutate({}, { onSuccess: () => toast.success('Payslips generated successfully'), onError: (err) => toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to generate payslips') })}>Generate Payslips</Button>
            <div className="overflow-x-auto mt-3">
              <table className="w-full text-sm">
                <thead><tr className="border-b border-slate-200 text-left">{['Name', 'Month', 'Amount', 'Status'].map(h => <th key={h} className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">{h}</th>)}</tr></thead>
                <tbody>{payslips.map(p => <tr key={p.id} className="border-b border-slate-100"><td className="py-2 px-2 font-medium text-slate-800">{p.name}</td><td className="py-2 px-2 text-slate-500">{p.month}</td><td className="py-2 px-2 text-slate-500">₹{p.amount}</td><td className="py-2 px-2"><Badge status={p.status} /></td></tr>)}</tbody>
              </table>
            </div>
          </>
        )}
        <Pagination
          page={pagination.page}
          totalPages={payrollData?.total_pages || 1}
          totalCount={payrollData?.count || 0}
          pageSize={pagination.pageSize}
          onPageChange={(p) => pagination.setPage(p)}
        />
      </div>
    </div>
  );
}
