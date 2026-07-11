import { useState, useRef } from 'react';
import { Breadcrumb, Button, Modal, useToast, SearchableSelect } from 'school-erp-ui-shared';
import { FileText, Download, Printer, Copy, Eye, Plus, RotateCcw, Stamp } from 'lucide-react';
import { useSchoolProfile } from '../../services/settingsService';
import { getSchoolInfo } from '../../utils/getSchoolInfo';
import jsPDF from 'jspdf';

const TEMPLATES = [
  {
    id: 'holiday',
    name: 'Holiday Notice',
    icon: '🏖️',
    subject: 'Holiday Notice',
    body: `Dear Parents/Guardians,

This is to inform you that the school will remain closed on [DATE] on account of [OCCASION].

Classes will resume on [RESUME DATE]. Students are advised to complete their pending assignments during the holiday.

Wishing you and your family a wonderful holiday.`,
  },
  {
    id: 'event',
    name: 'Event / Function',
    icon: '🎉',
    subject: 'Invitation - School Event',
    body: `Dear Parents/Guardians,

We are pleased to invite you to [EVENT NAME] being organized by our school.

Date: [DATE]
Time: [TIME]
Venue: [VENUE]

All parents are cordially invited to grace the occasion with their presence. Students are expected to participate actively.

Looking forward to your kind presence.`,
  },
  {
    id: 'fee-reminder',
    name: 'Fee Reminder',
    icon: '💰',
    subject: 'Fee Payment Reminder',
    body: `Dear Parents/Guardians,

This is a gentle reminder that the fees for the current term/quarter are due. Kindly ensure that the payment is made by [DUE DATE] to avoid any late fee charges.

Fee details:
- Fee Type: [FEE TYPE]
- Amount: ₹[AMOUNT]
- Due Date: [DUE DATE]

Payment can be made online through the school portal or at the school office during working hours.

Thank you for your cooperation.`,
  },
  {
    id: 'exam-schedule',
    name: 'Exam Schedule',
    icon: '📝',
    subject: 'Examination Schedule',
    body: `Dear Parents/Guardians,

The schedule for [EXAM NAME] has been finalized. Please find the details below:

Examination: [EXAM NAME]
Classes: [CLASSES]
Start Date: [START DATE]
End Date: [END DATE]

The detailed subject-wise timetable has been shared with students. Parents are requested to ensure regular study hours and timely arrival for examinations.

Best wishes to all students.`,
  },
  {
    id: 'general',
    name: 'General Notice',
    icon: '📢',
    subject: 'Important Notice',
    body: `Dear Parents/Guardians,

[YOUR CONTENT HERE]

Please take note of the above and cooperate accordingly.

For any queries, please contact the school office.`,
  },
  {
    id: 'ptm',
    name: 'Parent-Teacher Meeting',
    icon: '🤝',
    subject: 'Parent-Teacher Meeting',
    body: `Dear Parents/Guardians,

A Parent-Teacher Meeting (PTM) has been scheduled for your ward's class.

Date: [DATE]
Time: [TIME]
Venue: [VENUE]

Agenda:
- Academic progress discussion
- Attendance review
- Upcoming activities

Your presence is mandatory. Please carry this circular for entry.

Note: Only one parent/guardian per student is allowed.`,
  },
];

export default function CircularGeneratorPage() {
  const toast = useToast();
  const { data: schoolProfile } = useSchoolProfile();
  const schoolInfo = getSchoolInfo(schoolProfile);
  const previewRef = useRef(null);

  const [form, setForm] = useState({
    subject: '',
    body: '',
    date: new Date().toISOString().split('T')[0],
    serial: `CIR/${new Date().getFullYear()}/${String(Math.floor(Math.random() * 900) + 100)}`,
    signatory: schoolProfile?.principal_name || '',
    signatoryDesignation: 'Principal',
    targetAudience: 'All Parents & Students',
  });
  const [showPreview, setShowPreview] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  const applyTemplate = (template) => {
    setForm(f => ({ ...f, subject: template.subject, body: template.body }));
    setSelectedTemplate(template.id);
    toast.success(`Template "${template.name}" applied`);
  };

  const resetForm = () => {
    setForm({ subject: '', body: '', date: new Date().toISOString().split('T')[0], serial: `CIR/${new Date().getFullYear()}/${String(Math.floor(Math.random() * 900) + 100)}`, signatory: schoolProfile?.principal_name || '', signatoryDesignation: 'Principal', targetAudience: 'All Parents & Students' });
    setSelectedTemplate(null);
  };

  const generatePdf = () => {
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.width;
    const margin = 18;
    let y = 15;

    // School Header
    doc.setFontSize(16);
    doc.setTextColor(30, 58, 95);
    doc.setFont(undefined, 'bold');
    doc.text(schoolInfo?.name || 'School Name', pageWidth / 2, y, { align: 'center' });
    y += 6;

    if (schoolInfo?.address || schoolInfo?.phone || schoolInfo?.email) {
      doc.setFontSize(9);
      doc.setTextColor(100, 116, 139);
      doc.setFont(undefined, 'normal');
      const contact = [schoolInfo.address, schoolInfo.phone ? `Ph: ${schoolInfo.phone}` : '', schoolInfo.email].filter(Boolean).join('  |  ');
      doc.text(contact, pageWidth / 2, y, { align: 'center' });
      y += 5;
    }

    if (schoolInfo?.board || schoolInfo?.code) {
      doc.setFontSize(8);
      doc.setTextColor(140, 150, 160);
      const meta = [schoolInfo.board ? `Board: ${schoolInfo.board}` : '', schoolInfo.code ? `Code: ${schoolInfo.code}` : ''].filter(Boolean).join('  |  ');
      doc.text(meta, pageWidth / 2, y, { align: 'center' });
      y += 4;
    }

    // Divider
    doc.setDrawColor(30, 58, 95);
    doc.setLineWidth(0.5);
    doc.line(margin, y, pageWidth - margin, y);
    y += 3;
    doc.setDrawColor(200, 210, 220);
    doc.setLineWidth(0.2);
    doc.line(margin, y, pageWidth - margin, y);
    y += 8;

    // Circular heading
    doc.setFontSize(13);
    doc.setTextColor(30, 41, 59);
    doc.setFont(undefined, 'bold');
    doc.text('CIRCULAR', pageWidth / 2, y, { align: 'center' });
    y += 8;

    // Serial & Date row
    doc.setFontSize(9);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(71, 85, 105);
    doc.text(`Ref: ${form.serial}`, margin, y);
    doc.text(`Date: ${new Date(form.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}`, pageWidth - margin, y, { align: 'right' });
    y += 8;

    // To
    doc.setFontSize(10);
    doc.setFont(undefined, 'bold');
    doc.text(`To: ${form.targetAudience}`, margin, y);
    y += 8;

    // Subject
    doc.setFontSize(11);
    doc.setFont(undefined, 'bold');
    doc.setTextColor(30, 41, 59);
    doc.text(`Subject: ${form.subject}`, margin, y);
    y += 10;

    // Body
    doc.setFontSize(10);
    doc.setFont(undefined, 'normal');
    doc.setTextColor(51, 65, 85);
    const lines = doc.splitTextToSize(form.body, pageWidth - margin * 2);
    doc.text(lines, margin, y);
    y += lines.length * 5 + 15;

    // Ensure space for signature
    if (y > doc.internal.pageSize.height - 50) {
      doc.addPage();
      y = 20;
    }

    // Signature
    doc.setFontSize(10);
    doc.setTextColor(30, 41, 59);
    doc.setFont(undefined, 'bold');
    doc.text('Yours sincerely,', pageWidth - margin - 50, y);
    y += 12;
    doc.text(form.signatory || 'Principal', pageWidth - margin - 50, y);
    y += 5;
    doc.setFont(undefined, 'normal');
    doc.setFontSize(9);
    doc.setTextColor(100, 116, 139);
    doc.text(form.signatoryDesignation, pageWidth - margin - 50, y);
    y += 4;
    doc.text(schoolInfo?.name || '', pageWidth - margin - 50, y);

    // Footer
    doc.setFontSize(7);
    doc.setTextColor(180, 180, 180);
    doc.text('This is a computer-generated circular.', pageWidth / 2, doc.internal.pageSize.height - 10, { align: 'center' });

    doc.save(`Circular_${form.serial.replace(/\//g, '-')}.pdf`);
    toast.success('Circular PDF downloaded');
  };

  const copyText = () => {
    const text = `${form.subject}\n\nRef: ${form.serial} | Date: ${form.date}\nTo: ${form.targetAudience}\n\n${form.body}\n\n${form.signatory}\n${form.signatoryDesignation}`;
    navigator.clipboard.writeText(text).then(() => toast.success('Copied to clipboard'));
  };

  return (
    <div className="space-y-6">
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Circular Generator' }]} />
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Circular Generator</h1>
          <p className="text-sm text-slate-500 mt-0.5">Create official school circulars with templates</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" size="sm" icon={RotateCcw} onClick={resetForm}>Reset</Button>
          <Button variant="secondary" size="sm" icon={Copy} onClick={copyText}>Copy Text</Button>
          <Button variant="secondary" size="sm" icon={Eye} onClick={() => setShowPreview(true)}>Preview</Button>
          <Button variant="primary" size="sm" icon={Download} onClick={generatePdf}>Download PDF</Button>
        </div>
      </div>

      {/* Templates */}
      <div className="bg-white border border-slate-200 rounded-xl p-4">
        <h3 className="text-sm font-semibold text-slate-900 mb-3">Choose a Template</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
          {TEMPLATES.map(t => (
            <button key={t.id} onClick={() => applyTemplate(t)} className={`flex flex-col items-center gap-1.5 px-3 py-3 rounded-xl border transition-all hover:shadow-sm ${selectedTemplate === t.id ? 'bg-primary-50 border-primary-300 ring-2 ring-primary-100' : 'border-slate-200 hover:border-slate-300'}`}>
              <span className="text-xl">{t.icon}</span>
              <span className="text-[11px] font-medium text-slate-700 text-center">{t.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Editor */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 space-y-4">
          {/* Subject */}
          <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-3">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1.5 block">Subject / Title *</label>
              <input value={form.subject} onChange={e => setForm(f => ({ ...f, subject: e.target.value }))} placeholder="Enter circular subject..." className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1.5 block">Body *</label>
              <textarea value={form.body} onChange={e => setForm(f => ({ ...f, body: e.target.value }))} placeholder="Write circular content..." rows={12} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-y font-mono leading-relaxed" />
            </div>
          </div>
        </div>

        {/* Meta & Signature */}
        <div className="space-y-4">
          <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-3">
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Details</h4>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Serial Number</label>
              <input value={form.serial} onChange={e => setForm(f => ({ ...f, serial: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Date</label>
              <input type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">To (Audience)</label>
              <input value={form.targetAudience} onChange={e => setForm(f => ({ ...f, targetAudience: e.target.value }))} placeholder="All Parents & Students" className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-3">
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Signature</h4>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Signatory Name</label>
              <input value={form.signatory} onChange={e => setForm(f => ({ ...f, signatory: e.target.value }))} placeholder="Principal Name" className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Designation</label>
              <input value={form.signatoryDesignation} onChange={e => setForm(f => ({ ...f, signatoryDesignation: e.target.value }))} placeholder="Principal" className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
          </div>

          {/* Quick info */}
          <div className="bg-slate-50 border border-slate-200 rounded-xl p-3 text-[11px] text-slate-500 space-y-1">
            <p><strong>School:</strong> {schoolInfo?.name || 'Not configured'}</p>
            <p><strong>Address:</strong> {schoolInfo?.address || '-'}</p>
            <p><strong>Phone:</strong> {schoolInfo?.phone || '-'}</p>
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      <Modal open={showPreview} onClose={() => setShowPreview(false)} title="Circular Preview" size="lg">
        <div ref={previewRef} className="border-2 border-slate-200 rounded-xl p-8 bg-white max-w-[600px] mx-auto">
          {/* Header */}
          <div className="text-center mb-4 pb-3 border-b-2 border-slate-800">
            <h2 className="text-lg font-bold text-slate-900">{schoolInfo?.name || 'School Name'}</h2>
            <p className="text-xs text-slate-500 mt-0.5">{[schoolInfo?.address, schoolInfo?.phone ? `Ph: ${schoolInfo.phone}` : '', schoolInfo?.email].filter(Boolean).join(' | ')}</p>
          </div>

          {/* Circular */}
          <div className="text-center mb-4">
            <h3 className="text-base font-bold text-slate-900 underline">CIRCULAR</h3>
          </div>

          <div className="flex justify-between mb-4 text-xs text-slate-600">
            <span>Ref: {form.serial}</span>
            <span>Date: {new Date(form.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
          </div>

          <p className="text-sm text-slate-700 mb-2"><strong>To:</strong> {form.targetAudience}</p>
          <p className="text-sm text-slate-700 mb-4"><strong>Subject:</strong> {form.subject}</p>

          <div className="text-sm text-slate-700 whitespace-pre-wrap leading-relaxed mb-8">{form.body}</div>

          {/* Signature */}
          <div className="text-right mt-8">
            <p className="text-sm text-slate-600">Yours sincerely,</p>
            <p className="text-sm font-bold text-slate-900 mt-6">{form.signatory}</p>
            <p className="text-xs text-slate-500">{form.signatoryDesignation}</p>
            <p className="text-xs text-slate-500">{schoolInfo?.name}</p>
          </div>
        </div>
        <div className="flex justify-end gap-2 mt-4">
          <Button variant="secondary" icon={Printer} onClick={() => window.print()}>Print</Button>
          <Button variant="primary" icon={Download} onClick={() => { setShowPreview(false); generatePdf(); }}>Download PDF</Button>
        </div>
      </Modal>
    </div>
  );
}
