import jsPDF from 'jspdf';
import 'jspdf-autotable';

/**
 * Generate a PDF containing all credentials (students + teachers) grouped by role.
 *
 * @param {object} options
 * @param {object} options.schoolInfo - { name, address, phone, email, code }
 * @param {Array} options.students - [{ full_name, class_name, section, roll_number, password_changed }]
 * @param {Array} options.teachers - [{ full_name, department, email, password_changed }]
 */
export function generateCredentialsPdf({ schoolInfo, students = [], teachers = [] }) {
  const doc = new jsPDF('landscape');
  const pageWidth = doc.internal.pageSize.width;
  const margin = 14;
  let y = 14;

  // --- School Header ---
  doc.setFontSize(16);
  doc.setTextColor(15, 23, 42);
  doc.setFont(undefined, 'bold');
  doc.text(schoolInfo?.name || 'School Name', pageWidth / 2, y, { align: 'center' });
  y += 5;

  if (schoolInfo?.address) {
    doc.setFontSize(8);
    doc.setTextColor(100, 116, 139);
    doc.setFont(undefined, 'normal');
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
    doc.text(contactParts.join('  |  '), pageWidth / 2, y, { align: 'center' });
    y += 5;
  }

  // Divider
  doc.setDrawColor(30, 41, 59);
  doc.setLineWidth(0.5);
  doc.line(margin, y, pageWidth - margin, y);
  y += 6;

  // Document Title
  doc.setFontSize(12);
  doc.setTextColor(30, 41, 59);
  doc.setFont(undefined, 'bold');
  doc.text('LOGIN CREDENTIALS', pageWidth / 2, y, { align: 'center' });
  y += 4;
  doc.setFontSize(8);
  doc.setTextColor(100, 116, 139);
  doc.setFont(undefined, 'normal');
  doc.text(`Generated on ${new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}`, pageWidth / 2, y, { align: 'center' });
  y += 8;

  // --- Student Credentials Table ---
  if (students.length > 0) {
    doc.setFontSize(10);
    doc.setTextColor(30, 41, 59);
    doc.setFont(undefined, 'bold');
    doc.text(`Student Credentials (${students.length})`, margin, y);
    y += 2;

    const studentRows = students.map(s => [
      s.full_name || s.name || '',
      'Student',
      s.class_name ? `${s.class_name}${s.section ? '-' + s.section : ''}` : '',
      s.roll_number || '',
      s.password_changed ? '(Changed by user)' : (s.roll_number || ''),
    ]);

    doc.autoTable({
      startY: y,
      head: [['Name', 'Role', 'Class', 'Username', 'Default Password']],
      body: studentRows,
      theme: 'grid',
      styles: { fontSize: 8, cellPadding: 2.5, textColor: [51, 65, 85] },
      headStyles: { fillColor: [241, 245, 249], textColor: [30, 41, 59], fontStyle: 'bold', fontSize: 8 },
      columnStyles: {
        0: { cellWidth: 60 },
        1: { cellWidth: 30 },
        2: { cellWidth: 30 },
        3: { cellWidth: 55 },
        4: { cellWidth: 55 },
      },
      margin: { left: margin, right: margin },
      didDrawPage: () => {},
    });

    y = doc.lastAutoTable.finalY + 10;
  }

  // --- Teacher Credentials Table ---
  if (teachers.length > 0) {
    // Check if we need a new page
    if (y > doc.internal.pageSize.height - 40) {
      doc.addPage();
      y = 14;
    }

    doc.setFontSize(10);
    doc.setTextColor(30, 41, 59);
    doc.setFont(undefined, 'bold');
    doc.text(`Teacher Credentials (${teachers.length})`, margin, y);
    y += 2;

    const teacherRows = teachers.map(t => [
      t.full_name || t.name || '',
      'Teacher',
      t.department || '',
      t.email || '',
      t.password_changed ? '(Changed by user)' : (t.email || ''),
    ]);

    doc.autoTable({
      startY: y,
      head: [['Name', 'Role', 'Department', 'Email / Username', 'Default Password']],
      body: teacherRows,
      theme: 'grid',
      styles: { fontSize: 8, cellPadding: 2.5, textColor: [51, 65, 85] },
      headStyles: { fillColor: [241, 245, 249], textColor: [30, 41, 59], fontStyle: 'bold', fontSize: 8 },
      columnStyles: {
        0: { cellWidth: 55 },
        1: { cellWidth: 30 },
        2: { cellWidth: 40 },
        3: { cellWidth: 60 },
        4: { cellWidth: 60 },
      },
      margin: { left: margin, right: margin },
    });
  }

  // Footer
  const totalPages = doc.internal.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setFontSize(7);
    doc.setTextColor(148, 163, 184);
    doc.setFont(undefined, 'italic');
    doc.text('CONFIDENTIAL - For administrative use only', pageWidth / 2, doc.internal.pageSize.height - 8, { align: 'center' });
    doc.text(`Page ${i} of ${totalPages}`, pageWidth - margin, doc.internal.pageSize.height - 8, { align: 'right' });
  }

  // Save
  const fileName = `Credentials_${schoolInfo?.name?.replace(/\s+/g, '_') || 'School'}_${new Date().toISOString().split('T')[0]}.pdf`;
  doc.save(fileName);
}
