import { Download } from 'lucide-react';
import { Button, PrintHeader } from 'school-erp-ui-shared';
import { useSchoolProfile } from '../../services/settingsService';
import { generatePayslipPdf } from '../../utils/payslipPdf';

/**
 * Shared salary-slip receipt. Used by the Staff Directory "View Slip" and the
 * Payroll tab "View Payslip". Expects `staff` with: full_name, employee_id,
 * designation, department, month, year, month_name, basic_salary, hra, da, ta,
 * other_allowances, pf_deduction, tax_deduction, other_deductions, paid_on,
 * working_days, total_days, payment_method, reference.
 */
export default function SalarySlipView({ staff, onClose }) {
  const { data: schoolData } = useSchoolProfile();
  const basic = Number(staff.basic_salary || 0);
  const hra = Number(staff.hra || 0);
  const da = Number(staff.da || 0);
  const ta = Number(staff.ta || 0);
  const otherAllow = Number(staff.other_allowances || 0);
  const pf = Number(staff.pf_deduction || 0);
  const tax = Number(staff.tax_deduction || 0);
  const otherDed = Number(staff.other_deductions || 0);
  const grossEarnings = basic + hra + da + ta + otherAllow;
  const totalDeductions = pf + tax + otherDed;
  const netPayable = grossEarnings - totalDeductions;
  const fmt = (v) => `₹${Number(v || 0).toLocaleString()}`;

  return (
    <div id="salary-slip-content">
      <PrintHeader school={schoolData} title="Salary Slip" subtitle={`${staff.month_name || 'Current'} ${staff.year || new Date().getFullYear()}`} />
      {/* Staff Info */}
      <div className="pb-3 border-b border-slate-100 mb-4">
        <p className="text-lg font-bold text-slate-900">{staff.full_name}</p>
        <p className="text-xs text-slate-500">{staff.employee_id} • {staff.designation || staff.department || 'Staff'}</p>
        <p className="text-xs text-slate-500">{staff.department || 'Teaching'}</p>
        <div className="grid grid-cols-3 gap-3 mt-3 pt-3 border-t border-slate-50">
          <div><p className="text-[10px] text-slate-400">Period</p><p className="text-xs font-semibold text-slate-700">{staff.month_name || (staff.month ? ['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][staff.month] : 'Current')} {staff.year || new Date().getFullYear()}</p></div>
          <div><p className="text-[10px] text-slate-400">Payment Date</p><p className="text-xs font-semibold text-slate-700">{staff.paid_on || '-'}</p></div>
          <div><p className="text-[10px] text-slate-400">Working Days</p><p className="text-xs font-semibold text-slate-700">{staff.working_days || 26}/{staff.total_days || 30}</p></div>
        </div>
      </div>

      {/* Earnings */}
      <div className="mb-4">
        <p className="text-sm font-bold text-slate-800 mb-2">Earnings</p>
        <div className="space-y-1.5">
          <div className="flex justify-between text-sm"><span className="text-slate-600">Base Pay</span><span className="text-slate-800">{fmt(basic)}</span></div>
          <div className="flex justify-between text-sm"><span className="text-slate-600">HRA</span><span className="text-slate-800">{fmt(hra)}</span></div>
          <div className="flex justify-between text-sm"><span className="text-slate-600">DA</span><span className="text-slate-800">{fmt(da)}</span></div>
          <div className="flex justify-between text-sm"><span className="text-slate-600">Transport Allowance</span><span className="text-slate-800">{fmt(ta)}</span></div>
          <div className="flex justify-between text-sm"><span className="text-slate-600">Other Allowances</span><span className="text-slate-800">{fmt(otherAllow)}</span></div>
          <div className="flex justify-between text-sm font-bold pt-1 border-t border-slate-100"><span className="text-slate-800">Gross Earnings</span><span className="text-green-600">{fmt(grossEarnings)}</span></div>
        </div>
      </div>

      {/* Deductions */}
      <div className="mb-4">
        <p className="text-sm font-bold text-slate-800 mb-2">Deductions</p>
        <div className="space-y-1.5">
          <div className="flex justify-between text-sm"><span className="text-slate-600">Provident Fund</span><span className="text-slate-800">{fmt(pf)}</span></div>
          <div className="flex justify-between text-sm"><span className="text-slate-600">Professional Tax</span><span className="text-slate-800">{fmt(tax)}</span></div>
          <div className="flex justify-between text-sm"><span className="text-slate-600">Other Deductions</span><span className="text-slate-800">{fmt(otherDed)}</span></div>
          <div className="flex justify-between text-sm font-bold pt-1 border-t border-slate-100"><span className="text-slate-800">Total Deductions</span><span className="text-red-600">{fmt(totalDeductions)}</span></div>
        </div>
      </div>

      {/* Net Payable */}
      <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-4">
        <div className="flex justify-between items-center">
          <p className="text-base font-bold text-slate-800">Net Payable</p>
          <p className="text-2xl font-bold text-green-600">{fmt(netPayable)}</p>
        </div>
      </div>

      {/* Actions */}
      <div className="flex gap-2 pt-3 border-t border-slate-100">
        <Button variant="primary" className="flex-1" icon={Download} onClick={() => { generatePayslipPdf({ schoolInfo: schoolData, employee: staff, payslip: { month: staff.month, year: staff.year, basic_salary: basic, hra, da, transport_allowance: ta, allowances: grossEarnings - basic, deductions: totalDeductions, deduction_breakup: { provident_fund: pf, professional_tax: tax, other_deductions: otherDed }, net_salary: netPayable, working_days: staff.working_days, total_days: staff.total_days, paid_on: staff.paid_on, payment_method: staff.payment_method, reference: staff.reference } }); }}>Download PDF</Button>
        {onClose && <Button variant="ghost" onClick={onClose}>Close</Button>}
      </div>
    </div>
  );
}
