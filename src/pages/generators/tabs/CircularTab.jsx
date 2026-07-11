import { useState } from 'react';
import { Button, Modal, useToast } from 'school-erp-ui-shared';
import { Download, Copy, Eye, RotateCcw } from 'lucide-react';
import { useSchoolProfile } from '../../../services/settingsService';
import { getSchoolInfo } from '../../../utils/getSchoolInfo';
import jsPDF from 'jspdf';

const TEMPLATES = [
  { id: 'holiday', name: 'Holiday Notice', icon: '🏖️', subject: 'Holiday Notice', body: `Dear Parents/Guardians,\n\nThis is to inform you that the school will remain closed on [DATE] on account of [OCCASION].\n\nClasses will resume on [RESUME DATE]. Students are advised to complete their pending assignments during the holiday.\n\nWishing you and your family a wonderful holiday.` },
  { id: 'event', name: 'Event', icon: '🎉', subject: 'Invitation - School Event', body: `Dear Parents/Guardians,\n\nWe are pleased to invite you to [EVENT NAME].\n\nDate: [DATE]\nTime: [TIME]\nVenue: [VENUE]\n\nAll parents are cordially invited. Looking forward to your kind presence.` },
  { id: 'fee-reminder', name: 'Fee Reminder', icon: '💰', subject: 'Fee Payment Reminder', body: `Dear Parents/Guardians,\n\nThis is a gentle reminder that the fees for the current term are due by [DUE DATE].\n\nFee Type: [FEE TYPE]\nAmount: ₹[AMOUNT]\n\nPayment can be made online or at the school office.\n\nThank you for your cooperation.` },
  { id: 'exam', name: 'Exam Schedule', icon: '📝', subject: 'Examination Schedule', body: `Dear Parents/Guardians,\n\nThe schedule for [EXAM NAME] has been finalized.\n\nClasses: [CLASSES]\nStart Date: [START DATE]\nEnd Date: [END DATE]\n\nParents are requested to ensure regular study hours.\n\nBest wishes to all students.` },
  { id: 'ptm', name: 'PTM', icon: '🤝', subject: 'Parent-Teacher Meeting', body: `Dear Parents/Guardians,\n\nA Parent-Teacher Meeting has been scheduled.\n\nDate: [DATE]\nTime: [TIME]\nVenue: [VENUE]\n\nYour presence is mandatory.` },
  { id: 'general', name: 'General', icon: '📢', subject: 'Important Notice', body: `Dear Parents/Guardians,\n\n[YOUR CONTENT HERE]\n\nFor any queries, please contact the school office.` },
];

export default function CircularTab() {
  const toast = useToast();
  const { data: schoolProfile } = useSchoolProfile();
  const schoolInfo = getSchoolInfo(schoolProfile);

  const [form, setForm] = useState({
    subject: '', body: '',
    date: new Date().toISOString().split('T')[0],
    serial: `CIR/${new Date().getFullYear()}/${String(Math.floor(Math.random() * 900) + 100)}`,
    signatory: schoolProfile?.principal_name || '',
    signatoryDesignation: 'Principal',
    targetAudience: 'All Parents & Students',
  });
  const [showPreview, setShowPreview] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  const applyTemplate = (t) => { setForm(f => ({ ...f, subject: t.subject, body: t.body })); setSelectedTemplate(t.id); };
  const resetForm = () => { setForm({ subject: '', body: '', date: new Date().toISOString().split('T')[0], serial: `CIR/${new Date().getFullYear()}/${String(Math.floor(Math.random() * 900) + 100)}`, signatory: '', signatoryDesignation: 'Principal', targetAudience: 'All Parents & Students' }); setSelectedTemplate(null); };

  const generatePdf = () => {
    const doc = new jsPDF();
    const pw = doc.internal.pageSize.width;
    const m = 18;
    let y = 15;
    doc.setFontSize(16); doc.setTextColor(30, 58, 95); doc.setFont(undefined, 'bold');
    doc.text(schoolInfo?.name || 'School Name', pw / 2, y, { align: 'center' }); y += 6;
    if (schoolInfo?.address || schoolInfo?.phone) { doc.setFontSize(9); doc.setTextColor(100, 116, 139); doc.setFont(undefined, 'normal'); doc.text([schoolInfo.address, schoolInfo.phone ? `Ph: ${schoolInfo.phone}` : '', schoolInfo.email].filter(Boolean).join('  |  '), pw / 2, y, { align: 'center' }); y += 5; }
    doc.setDrawColor(30, 58, 95); doc.setLineWidth(0.5); doc.line(m, y, pw - m, y); y += 2; doc.setDrawColor(200, 210, 220); doc.setLineWidth(0.2); doc.line(m, y, pw - m, y); y += 8;
    doc.setFontSize(13); doc.setTextColor(30, 41, 59); doc.setFont(undefined, 'bold'); doc.text('CIRCULAR', pw / 2, y, { align: 'center' }); y += 8;
    doc.setFontSize(9); doc.setFont(undefined, 'normal'); doc.setTextColor(71, 85, 105); doc.text(`Ref: ${form.serial}`, m, y); doc.text(`Date: ${new Date(form.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}`, pw - m, y, { align: 'right' }); y += 8;
    doc.setFontSize(10); doc.setFont(undefined, 'bold'); doc.text(`To: ${form.targetAudience}`, m, y); y += 8;
    doc.setFontSize(11); doc.text(`Subject: ${form.subject}`, m, y); y += 10;
    doc.setFontSize(10); doc.setFont(undefined, 'normal'); doc.setTextColor(51, 65, 85);
    const lines = doc.splitTextToSize(form.body, pw - m * 2); doc.text(lines, m, y); y += lines.length * 5 + 15;
    if (y > doc.internal.pageSize.height - 50) { doc.addPage(); y = 20; }
    doc.setFontSize(10); doc.setTextColor(30, 41, 59); doc.setFont(undefined, 'bold'); doc.text('Yours sincerely,', pw - m - 50, y); y += 12;
    doc.text(form.signatory || 'Principal', pw - m - 50, y); y += 5;
    doc.setFont(undefined, 'normal'); doc.setFontSize(9); doc.setTextColor(100, 116, 139); doc.text(form.signatoryDesignation, pw - m - 50, y); y += 4; doc.text(schoolInfo?.name || '', pw - m - 50, y);
    doc.save(`Circular_${form.serial.replace(/\//g, '-')}.pdf`); toast.success('PDF downloaded');
  };

  const copyText = () => { navigator.clipboard.writeText(`${form.subject}\n\nRef: ${form.serial} | Date: ${form.date}\nTo: ${form.targetAudience}\n\n${form.body}\n\n${form.signatory}\n${form.signatoryDesignation}`).then(() => toast.success('Copied')); };

  return (
    <div className="space-y-5">
      {/* Templates */}
      <div className="flex flex-wrap gap-2">
        {TEMPLATES.map(t => (
          <button key={t.id} onClick={() => applyTemplate(t)} className={`flex items-center gap-1.5 px-3 py-2 rounded-lg border text-xs font-medium transition-all ${selectedTemplate === t.id ? 'bg-primary-50 border-primary-300' : 'border-slate-200 hover:border-slate-300'}`}>
            <span>{t.icon}</span> {t.name}
          </button>
        ))}
      </div>

      {/* Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-4 space-y-3">
          <input value={form.subject} onChange={e => setForm(f => ({ ...f, subject: e.target.value }))} placeholder="Subject / Title *" className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-primary-500" />
          <textarea value={form.body} onChange={e => setForm(f => ({ ...f, body: e.target.value }))} placeholder="Write circular content..." rows={14} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-y leading-relaxed" />
        </div>
        <div className="space-y-3">
          <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-2.5">
            <input value={form.serial} onChange={e => setForm(f => ({ ...f, serial: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs" placeholder="Serial No" />
            <input type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs" />
            <input value={form.targetAudience} onChange={e => setForm(f => ({ ...f, targetAudience: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs" placeholder="To (Audience)" />
          </div>
          <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-2.5">
            <p className="text-[10px] font-semibold text-slate-400 uppercase">Signature</p>
            <input value={form.signatory} onChange={e => setForm(f => ({ ...f, signatory: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs" placeholder="Name" />
            <input value={form.signatoryDesignation} onChange={e => setForm(f => ({ ...f, signatoryDesignation: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs" placeholder="Designation" />
          </div>
          <div className="flex flex-col gap-2">
            <Button variant="primary" size="sm" icon={Download} onClick={generatePdf} className="w-full">Download PDF</Button>
            <Button variant="secondary" size="sm" icon={Copy} onClick={copyText} className="w-full">Copy Text</Button>
            <Button variant="secondary" size="sm" icon={RotateCcw} onClick={resetForm} className="w-full">Reset</Button>
          </div>
        </div>
      </div>
    </div>
  );
}
