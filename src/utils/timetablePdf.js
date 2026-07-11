import jsPDF from 'jspdf';
import 'jspdf-autotable';

/**
 * Generate a styled timetable PDF with school header, breaks, and subject+teacher per cell.
 *
 * @param {object} options
 * @param {object} options.schoolInfo - { name, code, address, phone, email, board }
 * @param {string} options.className - e.g. "10"
 * @param {string} options.section - e.g. "A"
 * @param {Array} options.periods - all periods (teaching + breaks) sorted by start_time
 * @param {string[]} options.days - e.g. ['Monday', 'Tuesday', ...]
 * @param {object} options.slots - timetable data: { Monday: [slot|null, ...], ... }
 * @param {string} [options.academicYear] - e.g. "2025-2026"
 */
export function generateTimetablePdf({ schoolInfo, className, section, periods, days, slots, academicYear }) {
  const doc = new jsPDF('landscape');
  const pageWidth = doc.internal.pageSize.width;

  // Header: School info on left, Class info on right
  let y = 12;
  const leftX = 10;
  const rightX = pageWidth - 10;

  if (schoolInfo?.name) {
    doc.setFontSize(14);
    doc.setTextColor(30, 58, 95);
    doc.setFont(undefined, 'bold');
    doc.text(schoolInfo.name, leftX, y);

    // Right side: Class timetable title
    doc.setFontSize(12);
    doc.setTextColor(30, 41, 59);
    doc.text(`Class ${className} - ${section} Timetable`, rightX, y, { align: 'right' });
    y += 5;

    const contactParts = [
      schoolInfo.address || '',
      schoolInfo.phone ? `Ph: ${schoolInfo.phone}` : '',
      schoolInfo.email || '',
    ].filter(Boolean);
    if (contactParts.length) {
      doc.setFontSize(8);
      doc.setTextColor(100, 116, 139);
      doc.setFont(undefined, 'normal');
      doc.text(contactParts.join('  |  '), leftX, y);
    }

    // Right side: Academic year + date
    doc.setFontSize(8);
    doc.setTextColor(100, 116, 139);
    doc.setFont(undefined, 'normal');
    const rightInfo = [academicYear ? `AY: ${academicYear}` : '', `Generated: ${new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}`].filter(Boolean).join('  |  ');
    doc.text(rightInfo, rightX, y, { align: 'right' });
    y += 4;

    const metaParts = [
      schoolInfo.board ? `Board: ${schoolInfo.board}` : '',
      schoolInfo.code ? `Code: ${schoolInfo.code}` : '',
    ].filter(Boolean);
    if (metaParts.length) {
      doc.setFontSize(7);
      doc.setTextColor(150, 155, 160);
      doc.text(metaParts.join('  |  '), leftX, y);
    }
    y += 4;
  } else {
    doc.setFontSize(13);
    doc.setTextColor(30, 41, 59);
    doc.setFont(undefined, 'bold');
    doc.text(`Class ${className} - Section ${section} Timetable`, leftX, y);
    y += 8;
  }

  // Divider line
  doc.setDrawColor(220, 225, 230);
  doc.setLineWidth(0.4);
  doc.line(leftX, y, rightX, y);
  y += 4;

  // Format time: "09:00:00" or "09:00" -> "09:00"
  const formatTime = (t) => {
    if (!t) return '';
    return t.slice(0, 5);
  };

  // Build table headers
  const colCount = 2 + days.length;
  const headers = ['Period', 'Time', ...days.map(d => d.slice(0, 3))];

  // Build table rows - include breaks
  const rows = [];
  let teachingIdx = 0;

  for (const period of periods) {
    if (period.is_break) {
      // Break row - single merged cell content
      const breakLabel = `${period.name || 'BREAK'}  (${formatTime(period.start_time)} - ${formatTime(period.end_time)})`;
      const row = [breakLabel, ...Array(colCount - 1).fill('')];
      rows.push({ data: row, isBreak: true });
    } else {
      // Teaching period row
      const row = [
        period.name || `Period ${teachingIdx + 1}`,
        `${formatTime(period.start_time)} - ${formatTime(period.end_time)}`,
      ];
      days.forEach(day => {
        const daySlots = slots[day] || [];
        const slot = daySlots[teachingIdx] || null;
        if (slot) {
          row.push(`${slot.subject || ''}\n${slot.teacher_name || ''}`);
        } else {
          row.push('');
        }
      });
      rows.push({ data: row, isBreak: false });
      teachingIdx++;
    }
  }

  // Generate table
  doc.autoTable({
    startY: y,
    head: [headers],
    body: rows.map(r => r.data),
    styles: {
      fontSize: 8.5,
      cellPadding: 2.5,
      valign: 'middle',
      halign: 'center',
      lineColor: [220, 225, 230],
      lineWidth: 0.3,
      minCellHeight: 12,
    },
    headStyles: {
      fillColor: [43, 87, 154],
      textColor: 255,
      fontStyle: 'bold',
      fontSize: 9,
      minCellHeight: 10,
    },
    columnStyles: {
      0: { cellWidth: 20, fontStyle: 'bold', halign: 'left' },
      1: { cellWidth: 22, halign: 'center', fontSize: 8 },
    },
    didParseCell: (data) => {
      if (data.section === 'body') {
        const rowInfo = rows[data.row.index];
        if (rowInfo?.isBreak) {
          data.cell.styles.fillColor = [254, 243, 199];
          data.cell.styles.textColor = [146, 64, 14];
          data.cell.styles.fontStyle = 'bold';
          data.cell.styles.fontSize = 9;
          data.cell.styles.halign = 'center';
          // Hide content in non-first cells for break rows
          if (data.column.index > 0) {
            data.cell.text = [];
          }
          // Span first cell across all columns
          if (data.column.index === 0) {
            data.cell.colSpan = colCount;
          }
        } else if (data.row.index % 2 === 0) {
          data.cell.styles.fillColor = [248, 250, 252];
        }
      }
    },
    margin: { left: 8, right: 8 },
  });

  // Footer
  const pageCount = doc.internal.getNumberOfPages();
  for (let i = 1; i <= pageCount; i++) {
    doc.setPage(i);
    doc.setFontSize(7);
    doc.setTextColor(148, 163, 184);
    doc.text(`Page ${i} of ${pageCount}`, pageWidth - 10, doc.internal.pageSize.height - 8, { align: 'right' });
  }

  doc.save(`Timetable_Class_${className}_${section}.pdf`);
}
