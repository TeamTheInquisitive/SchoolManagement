import { useState, useMemo } from 'react';
import { Button, useToast, SearchableSelect } from 'school-erp-ui-shared';
import { Download } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useSchoolProfile, useClassSections } from '../../../services/settingsService';
import { getSchoolInfo } from '../../../utils/getSchoolInfo';
import api from '../../../services/api';
import jsPDF from 'jspdf';

const DOC_TYPES = [
  { id: 'tc', name: 'Transfer Certificate', icon: '📋' },
  { id: 'bonafide', name: 'Bonafide Certificate', icon: '📄' },
  { id: 'conduct', name: 'Conduct Certificate', icon: '✅' },
];

export default function TcBonafideTab() {
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
    queryKey: ['tc-students', selectedClass, selectedSection],
    queryFn: () => api.get('/admin/students', { params: { class_name: selectedClass, section: selectedSection, page_size: 100 } }).then(r => r.data),
    enabled: !!selectedClass && !!selectedSection,
  });
  const students = (studentsData?.results || []).filter(s => s.class_name === selectedClass && s.section === selectedSection);
  const studentOptions = useMemo(() => students.map(s => ({ value: s.id, label: `${s.full_name} (${s.roll_number})` })), [students]);
  const selectedStudent = students.find(s => s.id === selectedStudentId);

  const [docType, setDocType] = useState('tc');
  const [form, setForm] = useState({
    admissionDate: '', leavingDate: '', reason: 'Parent request', conduct: 'Good',
    remarks: '', serialNo: `TC/${new Date().getFullYear()}/${String(Math.floor(Math.random() * 9000) + 1000)}`,
    date: new Date().toISOString().split('T')[0],
    signatory: schoolProfile?.principal_name || '',
  });

  // Auto-derived from selected student
  const studentName = selectedStudent?.full_name || '';
  const parentName = selectedStudent?.parent_name || '';
  const studentClass = selectedStudent?.class_name || selectedClass || '';
  const studentSection = selectedStudent?.section || selectedSection || '';
  const admissionNo = selectedStudent?.roll_number || '';
  const dob = selectedStudent?.date_of_birth || '';

  const generatePdf = () => {
    const doc = new jsPDF();
    const pw = doc.internal.pageSize.width;
    const m = 18;
    let y = 15;

    // School header
    doc.setFontSize(15); doc.setTextColor(30, 58, 95); doc.setFont(undefined, 'bold');
    doc.text(schoolInfo?.name || 'School Name', pw / 2, y, { align: 'center' }); y += 6;
    if (schoolInfo?.address) { doc.setFontSize(9); doc.setTextColor(100, 116, 139); doc.setFont(undefined, 'normal'); doc.text(schoolInfo.address, pw / 2, y, { align: 'center' }); y += 4; }
    if (schoolInfo?.phone || schoolInfo?.email) { doc.setFontSize(8); doc.text([schoolInfo.phone ? `Ph: ${schoolInfo.phone}` : '', schoolInfo.email].filter(Boolean).join(' | '), pw / 2, y, { align: 'center' }); y += 4; }
    if (schoolInfo?.board || schoolInfo?.code) { doc.setFontSize(7); doc.setTextColor(140, 150, 160); doc.text([schoolInfo.board ? `Board: ${schoolInfo.board}` : '', schoolInfo.code ? `Code: ${schoolInfo.code}` : ''].filter(Boolean).join(' | '), pw / 2, y, { align: 'center' }); y += 4; }

    // Divider
    doc.setDrawColor(30, 58, 95); doc.setLineWidth(0.5); doc.line(m, y, pw - m, y); y += 2;
    doc.setDrawColor(200, 210, 220); doc.setLineWidth(0.2); doc.line(m, y, pw - m, y); y += 10;

    // Title
    const title = docType === 'tc' ? 'TRANSFER CERTIFICATE' : docType === 'bonafide' ? 'BONAFIDE CERTIFICATE' : 'CONDUCT CERTIFICATE';
    doc.setFontSize(14); doc.setTextColor(30, 41, 59); doc.setFont(undefined, 'bold');
    doc.text(title, pw / 2, y, { align: 'center' }); y += 10;

    // Serial & Date
    doc.setFontSize(9); doc.setFont(undefined, 'normal'); doc.setTextColor(71, 85, 105);
    doc.text(`No: ${form.serialNo}`, m, y); doc.text(`Date: ${new Date(form.date).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}`, pw - m, y, { align: 'right' }); y += 10;

    // Content based on type
    doc.setFontSize(10); doc.setTextColor(51, 65, 85); doc.setFont(undefined, 'normal');

    if (docType === 'tc') {
      const rows = [
        ['1. Name of the Student', studentName || '___________'],
        ['2. Father/Mother/Guardian Name', parentName || '___________'],
        ['3. Date of Birth', dob || '___________'],
        ['4. Admission Number', admissionNo || '___________'],
        ['5. Class at time of leaving', `${studentClass}${studentSection ? `-${studentSection}` : ''}`],
        ['6. Date of Admission', form.admissionDate || '___________'],
        ['7. Date of Leaving', form.leavingDate || '___________'],
        ['8. Reason for Leaving', form.reason || '___________'],
        ['9. Conduct and Character', form.conduct || '___________'],
        ['10. Remarks', form.remarks || 'None'],
      ];
      rows.forEach(([label, value]) => {
        doc.setFont(undefined, 'normal'); doc.text(label, m, y);
        doc.setFont(undefined, 'bold'); doc.text(`: ${value}`, m + 65, y);
        y += 7;
      });
    } else if (docType === 'bonafide') {
      const body = `This is to certify that ${studentName || '___________'}, son/daughter of ${parentName || '___________'}, is a bonafide student of this institution, studying in Class ${studentClass || '___'}${studentSection ? `-${studentSection}` : ''} during the academic year ${new Date().getFullYear()}-${new Date().getFullYear() + 1}.\n\nAdmission Number: ${admissionNo || '___________'}\nDate of Birth: ${dob || '___________'}\n\nThis certificate is issued for the purpose of ${form.reason || '___________'}.`;
      const lines = doc.splitTextToSize(body, pw - m * 2);
      doc.text(lines, m, y); y += lines.length * 5.5;
    } else {
      const body = `This is to certify that ${studentName || '___________'}, son/daughter of ${parentName || '___________'}, was a student of this institution from ${form.admissionDate || '___________'} to ${form.leavingDate || '___________'}.\n\nDuring this period, his/her conduct and character were found to be ${form.conduct || 'Good'}.\n\n${form.remarks ? `Remarks: ${form.remarks}` : ''}`;
      const lines = doc.splitTextToSize(body, pw - m * 2);
      doc.text(lines, m, y); y += lines.length * 5.5;
    }

    // Signature
    y = Math.max(y + 20, doc.internal.pageSize.height - 40);
    doc.setFontSize(10); doc.setTextColor(30, 41, 59); doc.setFont(undefined, 'bold');
    doc.text(form.signatory || 'Principal', pw - m - 30, y, { align: 'center' });
    doc.setFont(undefined, 'normal'); doc.setFontSize(8); doc.setTextColor(100, 116, 139);
    doc.text('Principal', pw - m - 30, y + 5, { align: 'center' });
    doc.line(pw - m - 55, y - 3, pw - m - 5, y - 3);

    // School seal placeholder
    doc.setDrawColor(180, 180, 180); doc.setFillColor(250, 250, 250);
    doc.circle(m + 20, y - 5, 12, 'FD');
    doc.setFontSize(5); doc.setTextColor(180, 180, 180);
    doc.text('SCHOOL', m + 20, y - 7, { align: 'center' });
    doc.text('SEAL', m + 20, y - 3, { align: 'center' });

    doc.save(`${title.replace(/ /g, '_')}_${studentName || 'student'}.pdf`);
    toast.success(`${title} PDF generated`);
  };

  return (
    <div className="space-y-5">
      {/* Doc type selector */}
      <div className="flex gap-2">
        {DOC_TYPES.map(t => (
          <button key={t.id} onClick={() => setDocType(t.id)} className={`flex items-center gap-1.5 px-4 py-2 rounded-lg border text-xs font-medium transition-all ${docType === t.id ? 'bg-primary-50 border-primary-300' : 'border-slate-200 hover:border-slate-300'}`}>
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
            <div className="bg-slate-50 border border-slate-100 rounded-lg p-3 grid grid-cols-3 gap-x-4 gap-y-1 text-xs">
              <span className="text-slate-500">Name:</span><span className="col-span-2 text-slate-800 font-medium">{studentName}</span>
              <span className="text-slate-500">Parent:</span><span className="col-span-2 text-slate-800 font-medium">{parentName || '-'}</span>
              <span className="text-slate-500">Class:</span><span className="col-span-2 text-slate-800 font-medium">{studentClass}-{studentSection}</span>
              <span className="text-slate-500">Adm No:</span><span className="col-span-2 text-slate-800 font-medium">{admissionNo}</span>
              <span className="text-slate-500">DOB:</span><span className="col-span-2 text-slate-800 font-medium">{dob || '-'}</span>
            </div>
          )}
          {/* Only manual fields that aren't in student data */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Admission Date</label>
              <input value={form.admissionDate} onChange={e => setForm(f => ({ ...f, admissionDate: e.target.value }))} type="date" className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Leaving Date</label>
              <input value={form.leavingDate} onChange={e => setForm(f => ({ ...f, leavingDate: e.target.value }))} type="date" className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Reason / Purpose</label>
              <input value={form.reason} onChange={e => setForm(f => ({ ...f, reason: e.target.value }))} placeholder="Parent request" className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Conduct</label>
              <select value={form.conduct} onChange={e => setForm(f => ({ ...f, conduct: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white">
                <option value="Excellent">Excellent</option>
                <option value="Very Good">Very Good</option>
                <option value="Good">Good</option>
                <option value="Satisfactory">Satisfactory</option>
              </select>
            </div>
          </div>
          <input value={form.remarks} onChange={e => setForm(f => ({ ...f, remarks: e.target.value }))} placeholder="Remarks (optional)" className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
        </div>
        <div className="space-y-3">
          <div className="bg-white border border-slate-200 rounded-xl p-4 space-y-2.5">
            <input value={form.serialNo} onChange={e => setForm(f => ({ ...f, serialNo: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs" placeholder="Serial No" />
            <input type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs" />
            <input value={form.signatory} onChange={e => setForm(f => ({ ...f, signatory: e.target.value }))} className="w-full border border-slate-200 rounded-lg px-3 py-1.5 text-xs" placeholder="Principal Name" />
          </div>
          <Button variant="primary" icon={Download} onClick={generatePdf} disabled={!studentName} className="w-full">{studentName ? 'Generate PDF' : 'Select a student first'}</Button>
          <p className="text-[10px] text-slate-400 text-center">Includes school header, seal placeholder, and signature. Student details auto-filled from records.</p>
        </div>
      </div>
    </div>
  );
}
