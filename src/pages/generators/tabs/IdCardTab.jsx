import { useState, useMemo } from 'react';
import { Button, useToast, SearchableSelect } from 'school-erp-ui-shared';
import { Download, User } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { useSchoolProfile, useClassSections } from '../../../services/settingsService';
import { getSchoolInfo } from '../../../utils/getSchoolInfo';
import api from '../../../services/api';
import jsPDF from 'jspdf';

export default function IdCardTab() {
  const toast = useToast();
  const { data: schoolProfile } = useSchoolProfile();
  const schoolInfo = getSchoolInfo(schoolProfile);
  const { data: classSectionsData } = useClassSections();

  const [selectedClass, setSelectedClass] = useState('');
  const [selectedSection, setSelectedSection] = useState('');
  const [selectedStudentId, setSelectedStudentId] = useState('');
  const [type, setType] = useState('student');

  const classes = classSectionsData?.classes || [];
  const classOptions = useMemo(() => classes.map(c => ({ value: c.name, label: `Class ${c.display_name || c.name}` })), [classes]);
  const sectionOptions = useMemo(() => {
    const cls = classes.find(c => c.name === selectedClass);
    return (cls?.sections || []).map(s => ({ value: s.section_name, label: s.section_name }));
  }, [classes, selectedClass]);

  // Fetch students for selected class-section
  const { data: studentsData } = useQuery({
    queryKey: ['generator-students', selectedClass, selectedSection],
    queryFn: () => api.get('/admin/students', { params: { class_name: selectedClass, section: selectedSection, page_size: 100 } }).then(r => r.data),
    enabled: !!selectedClass && !!selectedSection,
  });

  const students = (studentsData?.results || []).filter(s => s.class_name === selectedClass && s.section === selectedSection);
  const studentOptions = useMemo(() => students.map(s => ({ value: s.id, label: `${s.full_name} (${s.roll_number})` })), [students]);

  // Auto-fill form when student selected
  const selectedStudent = students.find(s => s.id === selectedStudentId);
  const form = useMemo(() => {
    if (!selectedStudent) return { name: '', rollNumber: '', class: selectedClass, section: selectedSection, parentName: '', phone: '', bloodGroup: '', address: '', dob: '', admissionNo: '' };
    return {
      name: selectedStudent.full_name || '',
      rollNumber: selectedStudent.roll_number || '',
      class: selectedStudent.class_name || selectedClass,
      section: selectedStudent.section || selectedSection,
      parentName: selectedStudent.parent_name || '',
      phone: selectedStudent.parent_phone || selectedStudent.phone || '',
      bloodGroup: selectedStudent.blood_group || '',
      address: selectedStudent.address || '',
      dob: selectedStudent.date_of_birth || '',
      admissionNo: selectedStudent.roll_number || '',
    };
  }, [selectedStudent, selectedClass, selectedSection]);

  const canGenerate = !!form.name && !!form.class;

  const generatePdf = () => {
    if (!canGenerate) { toast.error('Please select a student first'); return; }
    const doc = new jsPDF({ unit: 'mm', format: 'a4' });
    const pageW = doc.internal.pageSize.width;
    const pageH = doc.internal.pageSize.height;

    // Card dimensions (standard CR80: 85.6 x 53.98mm)
    const cw = 85.6, ch = 54;
    const cx = (pageW - cw) / 2;
    const cy = 20;

    // Card border
    doc.setDrawColor(180, 180, 180);
    doc.setLineWidth(0.3);
    doc.roundedRect(cx, cy, cw, ch, 2, 2);

    // Header band
    doc.setFillColor(30, 58, 95);
    doc.rect(cx, cy, cw, 11, 'F');
    // Round top corners manually
    doc.setFillColor(30, 58, 95);
    doc.roundedRect(cx, cy, cw, 13, 2, 2, 'F');
    doc.rect(cx, cy + 4, cw, 7, 'F');

    // School name in header
    doc.setFontSize(8); doc.setTextColor(255, 255, 255); doc.setFont(undefined, 'bold');
    doc.text(schoolInfo?.name || 'School Name', cx + cw / 2, cy + 4.5, { align: 'center' });
    doc.setFontSize(5); doc.setFont(undefined, 'normal');
    if (schoolInfo?.address) doc.text(schoolInfo.address, cx + cw / 2, cy + 8, { align: 'center' });
    if (schoolInfo?.phone) doc.text(`Ph: ${schoolInfo.phone}`, cx + cw / 2, cy + 10.5, { align: 'center' });

    // Photo box
    const photoX = cx + 4, photoY = cy + 14, photoW = 18, photoH = 22;
    doc.setDrawColor(180, 180, 180); doc.setFillColor(248, 248, 248);
    doc.roundedRect(photoX, photoY, photoW, photoH, 1, 1, 'FD');
    doc.setFontSize(5); doc.setTextColor(180, 180, 180);
    doc.text('PHOTO', photoX + photoW / 2, photoY + photoH / 2 + 1, { align: 'center' });

    // Student name
    const detailX = cx + 26;
    doc.setTextColor(30, 41, 59); doc.setFontSize(9); doc.setFont(undefined, 'bold');
    doc.text(form.name, detailX, cy + 17);

    // Details
    doc.setFontSize(6.5); doc.setFont(undefined, 'normal'); doc.setTextColor(71, 85, 105);
    let dy = cy + 21.5;
    const spacing = 3.8;
    const details = [
      [`Class`, `${form.class}${form.section ? `-${form.section}` : ''}`],
      [`Roll No`, form.rollNumber],
      [`DOB`, form.dob],
      [`Blood Group`, form.bloodGroup],
      [`Parent`, form.parentName],
      [`Phone`, form.phone],
    ].filter(([, v]) => v);

    details.forEach(([label, value]) => {
      if (dy < cy + ch - 7) {
        doc.setFont(undefined, 'normal'); doc.setTextColor(120, 130, 140);
        doc.text(`${label}:`, detailX, dy);
        doc.setFont(undefined, 'bold'); doc.setTextColor(51, 65, 85);
        doc.text(value, detailX + 18, dy);
        dy += spacing;
      }
    });

    // Footer band
    doc.setFillColor(30, 58, 95);
    doc.rect(cx, cy + ch - 5, cw, 5, 'F');
    doc.roundedRect(cx, cy + ch - 7, cw, 7, 2, 2, 'F');
    doc.rect(cx, cy + ch - 7, cw, 3, 'F');
    doc.setFontSize(5); doc.setTextColor(255, 255, 255); doc.setFont(undefined, 'normal');
    doc.text(`Valid for Academic Year ${new Date().getFullYear()}-${new Date().getFullYear() + 1}`, cx + cw / 2, cy + ch - 1.5, { align: 'center' });

    // Cut line guide
    doc.setDrawColor(200, 200, 200); doc.setLineWidth(0.1);
    doc.setLineDashPattern([1, 1], 0);
    doc.rect(cx - 2, cy - 2, cw + 4, ch + 4);
    doc.setFontSize(5); doc.setTextColor(200, 200, 200);
    doc.text('✂ Cut along dotted line', cx + cw / 2, cy + ch + 5, { align: 'center' });

    doc.save(`ID_Card_${form.name}.pdf`);
    toast.success('ID Card PDF generated');
  };

  return (
    <div className="space-y-5">
      <p className="text-sm text-slate-500">Select a student to auto-fill details and generate an ID card.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Selection + Form */}
        <div className="bg-white border border-slate-200 rounded-xl p-5 space-y-4">
          {/* Type toggle */}
          <div className="flex gap-2">
            <button onClick={() => setType('student')} className={`text-xs px-3 py-1.5 rounded-lg ${type === 'student' ? 'bg-primary-500 text-white' : 'border border-slate-200 text-slate-600'}`}>Student</button>
            <button onClick={() => setType('staff')} className={`text-xs px-3 py-1.5 rounded-lg ${type === 'staff' ? 'bg-primary-500 text-white' : 'border border-slate-200 text-slate-600'}`}>Staff</button>
          </div>

          {/* Class & Section dropdowns */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Class</label>
              <SearchableSelect value={selectedClass} onChange={(v) => { setSelectedClass(v); setSelectedSection(''); setSelectedStudentId(''); }} options={classOptions} placeholder="Select class" />
            </div>
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Section</label>
              <SearchableSelect value={selectedSection} onChange={(v) => { setSelectedSection(v); setSelectedStudentId(''); }} options={sectionOptions} placeholder="Select section" disabled={!selectedClass} />
            </div>
          </div>

          {/* Student dropdown */}
          {selectedClass && selectedSection && (
            <div>
              <label className="text-xs font-medium text-slate-600 mb-1 block">Student</label>
              <SearchableSelect value={selectedStudentId} onChange={setSelectedStudentId} options={studentOptions} placeholder="Search student..." />
            </div>
          )}

          {/* Auto-filled details (read-only display) */}
          {selectedStudent && (
            <div className="bg-slate-50 border border-slate-100 rounded-lg p-3 space-y-1.5">
              <p className="text-[10px] font-semibold text-slate-400 uppercase">Auto-filled from student record</p>
              <div className="grid grid-cols-2 gap-x-4 gap-y-1 text-xs">
                <span className="text-slate-500">Name:</span><span className="text-slate-800 font-medium">{form.name}</span>
                <span className="text-slate-500">Class:</span><span className="text-slate-800 font-medium">{form.class}-{form.section}</span>
                <span className="text-slate-500">Roll No:</span><span className="text-slate-800 font-medium">{form.rollNumber}</span>
                <span className="text-slate-500">DOB:</span><span className="text-slate-800 font-medium">{form.dob || '-'}</span>
                <span className="text-slate-500">Blood Group:</span><span className="text-slate-800 font-medium">{form.bloodGroup || '-'}</span>
                <span className="text-slate-500">Parent:</span><span className="text-slate-800 font-medium">{form.parentName || '-'}</span>
                <span className="text-slate-500">Phone:</span><span className="text-slate-800 font-medium">{form.phone || '-'}</span>
              </div>
            </div>
          )}

          <Button variant="primary" icon={Download} onClick={generatePdf} disabled={!canGenerate} className="w-full">
            {canGenerate ? 'Generate ID Card PDF' : 'Select a student to generate'}
          </Button>
        </div>

        {/* Live Preview */}
        <div className="flex items-start justify-center">
          <div className="w-[344px] h-[216px] bg-white border-2 border-slate-300 rounded-xl overflow-hidden shadow-lg">
            <div className="bg-[#1e3a5f] px-4 py-2 text-center">
              <p className="text-white text-xs font-bold">{schoolInfo?.name || 'School Name'}</p>
              <p className="text-white/70 text-[9px]">{schoolInfo?.address || 'School Address'}</p>
            </div>
            <div className="flex gap-4 p-4">
              <div className="w-[72px] h-[88px] bg-slate-100 border border-slate-300 rounded-lg flex items-center justify-center flex-shrink-0">
                <User size={24} className="text-slate-300" />
              </div>
              <div className="flex-1 space-y-1">
                <p className="text-sm font-bold text-slate-900">{form.name || 'Student Name'}</p>
                <p className="text-[10px] text-slate-500">Class: {form.class || '-'}{form.section ? `-${form.section}` : ''}</p>
                <p className="text-[10px] text-slate-500">Roll: {form.rollNumber || '-'}</p>
                <p className="text-[10px] text-slate-500">{form.dob ? `DOB: ${form.dob}` : ''}</p>
                <p className="text-[10px] text-slate-500">{form.bloodGroup ? `Blood: ${form.bloodGroup}` : ''}</p>
                <p className="text-[10px] text-slate-500">{form.parentName ? `Parent: ${form.parentName}` : ''}</p>
              </div>
            </div>
            <div className="bg-[#1e3a5f] px-4 py-1 text-center">
              <p className="text-white/80 text-[8px]">Valid for AY {new Date().getFullYear()}-{new Date().getFullYear() + 1}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
