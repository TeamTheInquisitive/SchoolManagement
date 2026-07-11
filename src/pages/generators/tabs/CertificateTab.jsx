import { useState, useMemo } from 'react';
import { Button, useToast, SearchableSelect } from 'school-erp-ui-shared';
import { Download, RotateCcw } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useSchoolProfile, useClassSections } from '../../../services/settingsService';
import { getSchoolInfo } from '../../../utils/getSchoolInfo';
import api from '../../../services/api';
import jsPDF from 'jspdf';

const CERT_TYPES = [
  { id: 'merit', name: 'Merit Certificate', icon: '🏆', template: 'This is to certify that [STUDENT NAME] of Class [CLASS] has been awarded the Merit Certificate for outstanding academic performance during the academic year [YEAR].' },
  { id: 'participation', name: 'Participation', icon: '🎗️', template: 'This is to certify that [STUDENT NAME] of Class [CLASS] has actively participated in [EVENT NAME] held on [DATE] and has shown commendable effort.' },
  { id: 'attendance', name: 'Best Attendance', icon: '⭐', template: 'This is to certify that [STUDENT NAME] of Class [CLASS] has maintained an exemplary attendance record of [PERCENTAGE]% during the academic year [YEAR] and is hereby awarded the Best Attendance Certificate.' },
  { id: 'sports', name: 'Sports Achievement', icon: '🏅', template: 'This is to certify that [STUDENT NAME] of Class [CLASS] has secured [POSITION] in [EVENT NAME] held during the Annual Sports Day on [DATE].' },
  { id: 'character', name: 'Character Certificate', icon: '📜', template: 'This is to certify that [STUDENT NAME], son/daughter of [PARENT NAME], has been a student of this institution from [FROM DATE] to [TO DATE]. During this period, his/her conduct and character have been found to be good.' },
  { id: 'custom', name: 'Custom', icon: '✏️', template: '[YOUR CERTIFICATE TEXT HERE]' },
];

export default function CertificateTab() {
  const toast = useToast();
  const { data: schoolProfile } = useSchoolProfile();
  const schoolInfo = getSchoolInfo(schoolProfile);
  const { data: classSectionsData } = useClassSections();

  const [selectedClass, setSelectedClass] = useState('');
  const [selectedSection, setSelectedSection] = useState('');
  const [selectedStudentId, setSelectedStudentId] = useState('');

  const classes = classSectionsData?.classes || [];
  const classOptions = useMemo(() => classes.map(c => ({ value: c.name, label: `Class ${c.display_name || c.name}` })), [classes]);
  const sectionOptions = useMemo(() => {
    const cls = classes.find(c => c.name === selectedClass);
    return (cls?.sections || []).map(s => ({ value: s.section_name, label: s.section_name }));
  }, [classes, selectedClass]);

  const { data: studentsData } = useQuery({
    queryKey: ['cert-students', selectedClass, selectedSection],
    queryFn: () => api.get('/admin/students', { params: { class_name: selectedClass, section: selectedSection, page_size: 100 } }).then(r => r.data),
    enabled: !!selectedClass && !!selectedSection,
  });
  const students = (studentsData?.results || []).filter(s => s.class_name === selectedClass && s.section === selectedSection);
  const studentOptions = useMemo(() => students.map(s => ({ value: s.id, label: `${s.full_name} (${s.roll_number})` })), [students]);
  const selectedStudent = students.find(s => s.id === selectedStudentId);

  const [form, setForm] = useState({
    type: 'merit',
    body: CERT_TYPES[0].template,
    date: new Date().toISOString().split('T')[0],
    signatory: schoolProfile?.principal_name || '',
    signatoryDesignation: 'Principal',
    serialNo: `CERT/${new Date().getFullYear()}/${String(Math.floor(Math.random() * 9000) + 1000)}`,
  });

  const studentName = selectedStudent?.full_name || '';
  const studentClass = selectedStudent ? `${selectedStudent.class_name}-${selectedStudent.section}` : (selectedClass && selectedSection ? `${selectedClass}-${selectedSection}` : '');

  const selectType = (type) => {
    const t = CERT_TYPES.find(c => c.id === type);
    setForm(f => ({ ...f, type, body: t?.template || '' }));
  };

  const generatePdf = () => {
    const doc = new jsPDF('landscape');
    const pw = doc.internal.pageSize.width;
    const ph = doc.internal.pageSize.height;

    // Decorative border
    doc.setDrawColor(30, 58, 95);
    doc.setLineWidth(1.5);
    doc.rect(8, 8, pw - 16, ph - 16);
    doc.setDrawColor(180, 160, 100);
    doc.setLineWidth(0.5);
    doc.rect(11, 11, pw - 22, ph - 22);

    let y = 25;

    // School name
    doc.setFontSize(14);
    doc.setTextColor(30, 58, 95);
    doc.setFont(undefined, 'bold');
    doc.text(schoolInfo?.name || 'School Name', pw / 2, y, { align: 'center' });
    y += 6;

    if (schoolInfo?.address) {
      doc.setFontSize(9);
      doc.setTextColor(100, 116, 139);
      doc.setFont(undefined, 'normal');
      doc.text(schoolInfo.address, pw / 2, y, { align: 'center' });
      y += 10;
    } else {
      y += 5;
    }

    // Certificate title
    doc.setFontSize(24);
    doc.setTextColor(30, 58, 95);
    doc.setFont(undefined, 'bold');
    doc.text('CERTIFICATE', pw / 2, y, { align: 'center' });
    y += 5;

    // Decorative line
    doc.setDrawColor(180, 160, 100);
    doc.setLineWidth(0.8);
    doc.line(pw / 2 - 40, y, pw / 2 + 40, y);
    y += 4;
    doc.setLineWidth(0.3);
    doc.line(pw / 2 - 30, y, pw / 2 + 30, y);
    y += 12;

    // Certificate type subtitle
    const certType = CERT_TYPES.find(c => c.id === form.type);
    if (certType && certType.id !== 'custom') {
      doc.setFontSize(12);
      doc.setTextColor(100, 80, 40);
      doc.setFont(undefined, 'italic');
      doc.text(certType.name, pw / 2, y, { align: 'center' });
      y += 12;
    }

    // Body text
    doc.setFontSize(12);
    doc.setTextColor(51, 65, 85);
    doc.setFont(undefined, 'normal');
    const bodyText = form.body.replace('[STUDENT NAME]', studentName || '___________').replace('[CLASS]', studentClass || '___');
    const lines = doc.splitTextToSize(bodyText, pw - 60);
    doc.text(lines, pw / 2, y, { align: 'center', maxWidth: pw - 60 });
    y += lines.length * 7 + 15;

    // Date and Serial
    doc.setFontSize(9);
    doc.setTextColor(100, 116, 139);
    doc.text(`Date: ${new Date(form.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}`, 20, ph - 30);
    doc.text(`Ref: ${form.serialNo}`, 20, ph - 25);

    // Signature
    doc.setFontSize(10);
    doc.setTextColor(30, 41, 59);
    doc.setFont(undefined, 'bold');
    doc.text(form.signatory || 'Principal', pw - 50, ph - 30, { align: 'center' });
    doc.setFont(undefined, 'normal');
    doc.setFontSize(8);
    doc.setTextColor(100, 116, 139);
    doc.text(form.signatoryDesignation, pw - 50, ph - 25, { align: 'center' });
    doc.line(pw - 75, ph - 33, pw - 25, ph - 33);

    doc.save(`Certificate_${studentName || 'student'}.pdf`);
    toast.success('Certificate PDF generated');
  };

  return (
    <div className="space-y-5">
      {/* Type selector */}
      <div className="flex flex-wrap gap-2">
        {CERT_TYPES.map(t => (
          <button key={t.id} onClick={() => selectType(t.id)} className={`flex items-center gap-1.5 px-3 py-2 rounded-lg border text-xs font-medium transition-all ${form.type === t.id ? 'bg-primary-50 border-primary-300' : 'border-slate-200 hover:border-slate-300'}`}>
            <span>{t.icon}</span> {t.name}
          </button>
        ))}
      </div>

      {/* Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-white border border-slate-200 rounded-xl p-5 space-y-3">
          {/* Student selection */}
          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Class</label>
              <SearchableSelect value={selectedClass} onChange={(v) => { setSelectedClass(v); setSelectedSection(''); setSelectedStudentId(''); }} options={classOptions} placeholder="Class" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Section</label>
              <SearchableSelect value={selectedSection} onChange={(v) => { setSelectedSection(v); setSelectedStudentId(''); }} options={sectionOptions} placeholder="Section" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Student</label>
              <SearchableSelect value={selectedStudentId} onChange={setSelectedStudentId} options={studentOptions} placeholder="Select student" />
            </div>
          </div>
          {selectedStudent && (
            <div className="flex items-center gap-2 px-3 py-2 bg-emerald-50 border border-emerald-200 rounded-lg">
              <span className="text-xs text-emerald-700 font-medium">Selected: {studentName} — {studentClass}</span>
            </div>
          )}
          <textarea value={form.body} onChange={e => setForm(f => ({ ...f, body: e.target.value }))} rows={6} placeholder="Certificate body text..." className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 resize-y leading-relaxed" />
          <p className="text-[10px] text-slate-400">Use [STUDENT NAME], [CLASS], [DATE], [EVENT NAME], [YEAR] as placeholders — student details auto-fill on download</p>
        </div>
        <div className="space-y-3">
          <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-2.5">
            <input type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs" />
            <input value={form.serialNo} onChange={e => setForm(f => ({ ...f, serialNo: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs" placeholder="Serial No" />
            <input value={form.signatory} onChange={e => setForm(f => ({ ...f, signatory: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs" placeholder="Signatory Name" />
            <input value={form.signatoryDesignation} onChange={e => setForm(f => ({ ...f, signatoryDesignation: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs" placeholder="Designation" />
          </div>
          <Button variant="primary" icon={Download} onClick={generatePdf} disabled={!studentName} className="w-full">{studentName ? 'Generate Certificate PDF' : 'Select a student first'}</Button>
        </div>
      </div>
    </div>
  );
}
