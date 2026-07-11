import ExcelJS from 'exceljs';
import { saveAs } from 'file-saver';

/**
 * Generate a bulk upload template Excel file with actual in-cell dropdown validations.
 * @param {object} options
 * @param {string} options.filename - Output filename (without extension)
 * @param {string} options.schoolName - School name for header
 * @param {string} options.schoolCode - School code for header
 * @param {string} options.sheetName - Name of the data sheet
 * @param {Array<{header: string, key: string, mandatory?: boolean, dropdown?: string[], description?: string}>} options.columns
 * @param {Array<{name: string, sections: Array<{section_name: string}>}>} [options.classSectionMap] - Class to section mapping
 * @param {Array<{title: string, values: string[]}>} [options.referenceData] - Extra reference lists to show in Instructions sheet
 */
export async function downloadBulkTemplate({ filename, schoolName, schoolCode, sheetName, columns, classSectionMap, referenceData }) {
  const wb = new ExcelJS.Workbook();

  // === Sheet 1: Data Sheet ===
  const ws = wb.addWorksheet(sheetName);

  // Row 1: School info
  ws.mergeCells(1, 1, 1, columns.length);
  const titleCell = ws.getCell(1, 1);
  titleCell.value = `${schoolName}${schoolCode ? ` (${schoolCode})` : ''} - Bulk Upload Template`;
  titleCell.font = { bold: true, size: 14 };

  // Row 2: Note
  ws.mergeCells(2, 1, 2, columns.length);
  ws.getCell(2, 1).value = 'Note: Fields marked with * are mandatory. Dropdown fields have selectable values.';
  ws.getCell(2, 1).font = { italic: true, color: { argb: 'FF666666' } };

  // Row 3: Headers
  columns.forEach((col, idx) => {
    const cell = ws.getCell(3, idx + 1);
    cell.value = col.mandatory ? `${col.header} *` : col.header;
    cell.font = { bold: true, color: { argb: 'FFFFFFFF' } };
    cell.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF4472C4' } };
    cell.alignment = { horizontal: 'center' };
    ws.getColumn(idx + 1).width = Math.max(col.header.length + 4, 18);
  });

  // Add data validation dropdowns for rows 4-500
  columns.forEach((col, idx) => {
    if (col.dropdown?.length) {
      for (let row = 4; row <= 500; row++) {
        ws.getCell(row, idx + 1).dataValidation = {
          type: 'list',
          allowBlank: !col.mandatory,
          formulae: [`"${col.dropdown.join(',')}"`],
          showErrorMessage: true,
          errorTitle: 'Invalid Value',
          error: `Please select from: ${col.dropdown.join(', ')}`,
        };
      }
    }
  });

  // === Sheet 2: Class-Section Mapping (if provided) ===
  if (classSectionMap?.length) {
    const wsRef = wb.addWorksheet('Class-Section Mapping');
    wsRef.getCell(1, 1).value = 'Class';
    wsRef.getCell(1, 2).value = 'Available Sections';
    wsRef.getRow(1).font = { bold: true };
    wsRef.getColumn(1).width = 15;
    wsRef.getColumn(2).width = 40;
    classSectionMap.forEach((cls, i) => {
      wsRef.getCell(i + 2, 1).value = cls.name;
      wsRef.getCell(i + 2, 2).value = (cls.sections || []).map(s => s.section_name).join(', ') || 'No sections';
    });
  }

  // === Sheet 3: Instructions ===
  const wsInstr = wb.addWorksheet('Instructions');
  wsInstr.getColumn(1).width = 25;
  wsInstr.getColumn(2).width = 12;
  wsInstr.getColumn(3).width = 40;
  wsInstr.getColumn(4).width = 50;

  const instrRows = [
    ['BULK UPLOAD INSTRUCTIONS'],
    [],
    ['School Name:', schoolName || ''],
    ['School Code:', schoolCode || ''],
    [],
    ['COLUMN DESCRIPTIONS'],
    ['Column', 'Mandatory', 'Description', 'Allowed Values'],
    ...columns.map(c => [c.header, c.mandatory ? 'Yes' : 'No', c.description || '', c.dropdown?.join(', ') || 'Free text']),
    [],
    ['NOTES:'],
    ['1. Fields marked with * are mandatory'],
    ['2. Do not modify the column headers'],
    ['3. Start entering data from row 4'],
    ['4. Dropdown fields have in-cell selection - click the cell to see options'],
    ['5. For Class/Section mapping, refer to the "Class-Section Mapping" sheet'],
    ['6. Date fields should be in YYYY-MM-DD format'],
  ];
  instrRows.forEach(row => wsInstr.addRow(row));
  wsInstr.getRow(1).font = { bold: true, size: 14 };
  wsInstr.getRow(7).font = { bold: true };

  // Add reference data columns (e.g., available subjects list for copy-paste)
  if (referenceData?.length) {
    const startCol = 6;
    referenceData.forEach((ref, refIdx) => {
      const col = startCol + refIdx;
      wsInstr.getColumn(col).width = 25;
      const headerCell = wsInstr.getCell(1, col);
      headerCell.value = ref.title;
      headerCell.font = { bold: true, size: 11 };
      ref.values.forEach((val, i) => {
        wsInstr.getCell(i + 2, col).value = val;
      });
    });
  }

  // Save
  const buffer = await wb.xlsx.writeBuffer();
  saveAs(new Blob([buffer]), `${filename}.xlsx`);
}
