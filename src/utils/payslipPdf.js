import jsPDF from 'jspdf';
import 'jspdf-autotable';

/**
 * Generate a professional payslip PDF with school header, earnings, deductions, and net pay.
 *
 * @param {object} options
 * @param {object} options.schoolInfo - { name, address, phone, email, logo_url, affiliation }
 * @param {object} options.employee - { full_name, employee_id, designation, department, joining_date }
 * @param {object} options.payslip - { month, year, basic_salary, hra, da, transport_allowance, allowances, deductions, deduction_breakup, net_salary, paid_amount, paid_on, working_days, total_days, payment_method, reference, notes }
 */
export function generatePayslipPdf({ schoolInfo, employee, payslip }) {
  const doc = new jsPDF('portrait');
  const pageWidth = doc.internal.pageSize.width;
  const margin = 14;
  const contentWidth = pageWidth - margin * 2;
  let y = 14;

  const MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  const monthName = MONTHS[(payslip.month || 1) - 1];
  const periodStr = `${monthName} ${payslip.year}`;

  // --- School Header ---
  doc.setFontSize(16);
  doc.setTextColor(15, 23, 42);
  doc.setFont(undefined, 'bold');
  doc.text(schoolInfo?.name || 'School Name', pageWidth / 2, y, { align: 'center' });
  y += 5;

  if (schoolInfo?.affiliation) {
    doc.setFontSize(8);
    doc.setTextColor(100, 116, 139);
    doc.setFont(undefined, 'normal');
    doc.text(schoolInfo.affiliation, pageWidth / 2, y, { align: 'center' });
    y += 4;
  }

  if (schoolInfo?.address) {
    doc.setFontSize(8);
    doc.setTextColor(100, 116, 139);
    doc.text(schoolInfo.address, pageWidth / 2, y, { align: 'center' });
    y += 4;
  }

  const contactParts = [
    schoolInfo?.phone ? `Ph: ${schoolInfo.phone}` : '',
    schoolInfo?.email || '',
  ].filter(Boolean);
  if (contactParts.length) {
    doc.setFontSize(7);
    doc.setTextColor(148, 163, 184);
    doc.text(contactParts.join('  •  '), pageWidth / 2, y, { align: 'center' });
    y += 5;
  }

  // Divider
  doc.setDrawColor(30, 41, 59);
  doc.setLineWidth(0.5);
  doc.line(margin, y, pageWidth - margin, y);
  y += 6;

  // --- Document Title ---
  doc.setFontSize(11);
  doc.setTextColor(30, 41, 59);
  doc.setFont(undefined, 'bold');
  doc.text('SALARY SLIP', pageWidth / 2, y, { align: 'center' });
  y += 4;
  doc.setFontSize(9);
  doc.setTextColor(100, 116, 139);
  doc.setFont(undefined, 'normal');
  doc.text(`For the month of ${periodStr}`, pageWidth / 2, y, { align: 'center' });
  y += 8;

  // --- Employee Info Box ---
  doc.setFillColor(248, 250, 252);
  doc.roundedRect(margin, y, contentWidth, 24, 2, 2, 'F');

  const col1X = margin + 4;
  const col2X = pageWidth / 2 + 4;
  let infoY = y + 6;

  doc.setFontSize(8);
  doc.setTextColor(100, 116, 139);
  doc.text('Employee Name', col1X, infoY);
  doc.text('Employee ID', col2X, infoY);
  infoY += 4;
  doc.setFontSize(9);
  doc.setTextColor(15, 23, 42);
  doc.setFont(undefined, 'bold');
  doc.text(employee.full_name || '-', col1X, infoY);
  doc.text(employee.employee_id || '-', col2X, infoY);
  infoY += 6;

  doc.setFontSize(8);
  doc.setTextColor(100, 116, 139);
  doc.setFont(undefined, 'normal');
  doc.text('Department', col1X, infoY);
  doc.text('Designation', col2X, infoY);
  infoY += 4;
  doc.setFontSize(9);
  doc.setTextColor(15, 23, 42);
  doc.setFont(undefined, 'bold');
  doc.text(employee.department || '-', col1X, infoY);
  doc.text(employee.designation || '-', col2X, infoY);

  y += 28;

  // --- Working Days & Payment Info ---
  const metaY = y;
  doc.setFontSize(7.5);
  doc.setTextColor(100, 116, 139);
  doc.setFont(undefined, 'normal');
  doc.text(`Working Days: ${payslip.working_days || 26}/${payslip.total_days || 30}`, col1X, metaY);
  doc.text(`Payment Date: ${payslip.paid_on || 'Pending'}`, col2X, metaY);
  y += 7;

  // --- Earnings & Deductions Side by Side ---
  const earnings = [];
  earnings.push(['Basic Salary', formatCurrency(payslip.basic_salary)]);
  if (num(payslip.hra) > 0) earnings.push(['House Rent Allowance (HRA)', formatCurrency(payslip.hra)]);
  if (num(payslip.da) > 0) earnings.push(['Dearness Allowance (DA)', formatCurrency(payslip.da)]);
  if (num(payslip.transport_allowance) > 0) earnings.push(['Transport Allowance', formatCurrency(payslip.transport_allowance)]);

  const otherAllowances = num(payslip.allowances) - num(payslip.hra) - num(payslip.da) - num(payslip.transport_allowance);
  if (otherAllowances > 0) earnings.push(['Other Allowances', formatCurrency(otherAllowances)]);

  const grossEarnings = num(payslip.basic_salary) + num(payslip.allowances);
  earnings.push([{ content: 'Gross Earnings', styles: { fontStyle: 'bold' } }, { content: formatCurrency(grossEarnings), styles: { fontStyle: 'bold', textColor: [22, 163, 74] } }]);

  const deductions = [];
  if (payslip.deduction_breakup && typeof payslip.deduction_breakup === 'object') {
    Object.entries(payslip.deduction_breakup).forEach(([key, value]) => {
      if (num(value) > 0) {
        const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
        deductions.push([label, formatCurrency(value)]);
      }
    });
  }
  if (deductions.length === 0 && num(payslip.deductions) > 0) {
    deductions.push(['Total Deductions', formatCurrency(payslip.deductions)]);
  }
  deductions.push([{ content: 'Total Deductions', styles: { fontStyle: 'bold' } }, { content: formatCurrency(payslip.deductions), styles: { fontStyle: 'bold', textColor: [220, 38, 38] } }]);

  // Earnings Table
  doc.setFontSize(9);
  doc.setTextColor(30, 41, 59);
  doc.setFont(undefined, 'bold');
  doc.text('EARNINGS', margin, y);

  doc.autoTable({
    startY: y + 2,
    head: [['Component', 'Amount (₹)']],
    body: earnings,
    theme: 'plain',
    styles: { fontSize: 8, cellPadding: 2.5, textColor: [51, 65, 85] },
    headStyles: { fillColor: [241, 245, 249], textColor: [51, 65, 85], fontStyle: 'bold', fontSize: 7.5 },
    columnStyles: { 0: { cellWidth: (contentWidth / 2 - 6) * 0.65 }, 1: { halign: 'right' } },
    margin: { left: margin, right: pageWidth / 2 + 2 },
  });

  const earningsEndY = doc.lastAutoTable.finalY;

  // Deductions Table
  doc.setFontSize(9);
  doc.setTextColor(30, 41, 59);
  doc.setFont(undefined, 'bold');
  doc.text('DEDUCTIONS', pageWidth / 2 + 4, y);

  doc.autoTable({
    startY: y + 2,
    head: [['Component', 'Amount (₹)']],
    body: deductions,
    theme: 'plain',
    styles: { fontSize: 8, cellPadding: 2.5, textColor: [51, 65, 85] },
    headStyles: { fillColor: [241, 245, 249], textColor: [51, 65, 85], fontStyle: 'bold', fontSize: 7.5 },
    columnStyles: { 0: { cellWidth: (contentWidth / 2 - 6) * 0.65 }, 1: { halign: 'right' } },
    margin: { left: pageWidth / 2 + 4, right: margin },
  });

  const deductionsEndY = doc.lastAutoTable.finalY;
  y = Math.max(earningsEndY, deductionsEndY) + 8;

  // --- Net Pay Box ---
  doc.setFillColor(240, 253, 244);
  doc.setDrawColor(34, 197, 94);
  doc.setLineWidth(0.3);
  doc.roundedRect(margin, y, contentWidth, 16, 2, 2, 'FD');

  doc.setFontSize(10);
  doc.setTextColor(30, 41, 59);
  doc.setFont(undefined, 'bold');
  doc.text('NET PAYABLE', margin + 6, y + 10);

  doc.setFontSize(14);
  doc.setTextColor(22, 163, 74);
  doc.text(formatCurrency(payslip.net_salary), pageWidth - margin - 6, y + 10, { align: 'right' });

  y += 22;

  // --- Payment Status ---
  if (num(payslip.paid_amount) > 0) {
    doc.setFontSize(8);
    doc.setTextColor(100, 116, 139);
    doc.setFont(undefined, 'normal');
    doc.text(`Paid: ${formatCurrency(payslip.paid_amount)}`, margin, y);
    if (payslip.payment_method) doc.text(`Method: ${payslip.payment_method}`, pageWidth / 2, y);
    y += 4;
    if (payslip.reference) {
      doc.text(`Reference: ${payslip.reference}`, margin, y);
      y += 4;
    }
  }

  // --- Notes ---
  if (payslip.notes) {
    y += 2;
    doc.setFontSize(7.5);
    doc.setTextColor(148, 163, 184);
    doc.setFont(undefined, 'italic');
    doc.text(`Note: ${payslip.notes}`, margin, y);
    y += 6;
  }

  // --- Footer: Signatures ---
  y = Math.max(y + 10, doc.internal.pageSize.height - 40);

  doc.setDrawColor(226, 232, 240);
  doc.setLineWidth(0.2);

  // Signature lines
  const sigY = y;
  doc.line(margin, sigY, margin + 50, sigY);
  doc.line(pageWidth - margin - 50, sigY, pageWidth - margin, sigY);

  doc.setFontSize(7);
  doc.setTextColor(100, 116, 139);
  doc.setFont(undefined, 'normal');
  doc.text('Employee Signature', margin, sigY + 4);
  doc.text('Authorized Signatory', pageWidth - margin - 50, sigY + 4);

  // Generation date
  doc.setFontSize(6);
  doc.setTextColor(203, 213, 225);
  doc.text(`Generated on ${new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}`, pageWidth / 2, doc.internal.pageSize.height - 8, { align: 'center' });

  // --- Save ---
  const fileName = `Payslip_${employee.employee_id || employee.full_name}_${monthName}_${payslip.year}.pdf`;
  doc.save(fileName);
}


function num(v) {
  return Number(v || 0);
}

function formatCurrency(value) {
  const n = Number(value || 0);
  return '₹ ' + n.toLocaleString('en-IN', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}
