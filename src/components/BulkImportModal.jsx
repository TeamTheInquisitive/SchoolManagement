import { useState, useRef } from 'react';
import * as XLSX from 'xlsx';
import { Upload, CheckCircle, XCircle, FileSpreadsheet, Loader2 } from 'lucide-react';
import { Modal, Button } from 'school-erp-ui-shared';

function normalizeDate(val) {
  if (!val) return val;
  const s = String(val).trim();
  // Already YYYY-MM-DD
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;
  // M/D/YY or M/D/YYYY or MM/DD/YY or MM/DD/YYYY
  const slashMatch = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{2,4})$/);
  if (slashMatch) {
    let [, m, d, y] = slashMatch;
    if (y.length === 2) y = (parseInt(y) > 50 ? '19' : '20') + y;
    return `${y}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`;
  }
  // D-M-YYYY
  const dashMatch = s.match(/^(\d{1,2})-(\d{1,2})-(\d{4})$/);
  if (dashMatch) {
    const [, d, m, y] = dashMatch;
    return `${y}-${m.padStart(2, '0')}-${d.padStart(2, '0')}`;
  }
  // Excel serial number
  const num = Number(s);
  if (!isNaN(num) && num > 1 && num < 100000) {
    const d = new Date((num - 25569) * 86400000);
    return d.toISOString().split('T')[0];
  }
  return s;
}

const DATE_KEYS = ['date_of_birth', 'admission_date', 'joining_date', 'left_date', 'dob'];

function cleanErrorMessage(msg) {
  if (!msg) return msg;
  return msg
    .replace(/DuplicateRollNumber:\s*/gi, 'Duplicate: ')
    .replace(/IntegrityError.*?Duplicate entry/gi, 'Already exists')
    .replace(/\(pymysql\.err[^)]*\)[^:]*/gi, '')
    .replace(/Traceback[\s\S]*?(?=\w+Error:)/gi, '')
    .replace(/File ".*?",\s*line \d+[\s\S]*?(?=\w+Error:)/gi, '')
    .trim();
}

export default function BulkImportModal({ open, onClose, title, onImport, columns, dataStartRow = 4 }) {
  const [stage, setStage] = useState('upload'); // upload | processing | results
  const [file, setFile] = useState(null);
  const [results, setResults] = useState([]);
  const fileRef = useRef(null);

  const reset = () => { setStage('upload'); setFile(null); setResults([]); };
  const handleClose = () => { reset(); onClose(); };

  const handleFile = (f) => {
    if (!f || !f.name.endsWith('.xlsx')) return;
    setFile(f);
  };

  const parseAndImport = async () => {
    if (!file) return;
    setStage('processing');

    const buffer = await file.arrayBuffer();
    const wb = XLSX.read(buffer, { type: 'array', cellDates: true });
    const sheet = wb.Sheets[wb.SheetNames[0]];
    const allRows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '', raw: false });

    // Header row is at dataStartRow - 1 (0-indexed: row 3 = index 2)
    const headerRowIdx = dataStartRow - 2;
    const headers = allRows[headerRowIdx]?.map(h => String(h).replace(/\*$/, '').trim()) || [];
    const dataRows = allRows.slice(dataStartRow - 1).filter(row => row.some(cell => cell !== ''));

    // Map rows to objects
    const parsedRows = dataRows.map(row => {
      const obj = {};
      columns.forEach((col, i) => {
        const headerIdx = headers.findIndex(h => h.toLowerCase() === col.header.replace(/\*$/, '').trim().toLowerCase());
        const idx = headerIdx >= 0 ? headerIdx : i;
        let val = row[idx];
        if (val !== undefined && val !== null) val = String(val).trim();
        else val = '';
        if (DATE_KEYS.includes(col.key)) val = normalizeDate(val);
        obj[col.key] = val;
      });
      return obj;
    });

    // Client-side validation
    const validRows = [];
    const clientFailures = [];
    for (let i = 0; i < parsedRows.length; i++) {
      const row = parsedRows[i];
      const missing = columns.filter(c => c.mandatory && !row[c.key]).map(c => c.header);
      if (missing.length > 0) {
        clientFailures.push({ row: i + dataStartRow, data: row, success: false, error: `Missing: ${missing.join(', ')}` });
        continue;
      }
      if (row.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(row.email)) {
        clientFailures.push({ row: i + dataStartRow, data: row, success: false, error: 'Invalid email format' });
        continue;
      }
      if (row.phone && !/^[6-9]\d{9}$/.test(row.phone)) {
        clientFailures.push({ row: i + dataStartRow, data: row, success: false, error: 'Invalid phone (10 digits starting 6-9)' });
        continue;
      }
      // Validate date fields are in YYYY-MM-DD format after normalization
      const dateError = DATE_KEYS.find(k => row[k] && !/^\d{4}-\d{2}-\d{2}$/.test(row[k]));
      if (dateError) {
        clientFailures.push({ row: i + dataStartRow, data: row, success: false, error: `Invalid date format in ${dateError}: "${row[dateError]}". Use DD/MM/YYYY or YYYY-MM-DD` });
        continue;
      }
      validRows.push({ index: i, row });
    }

    // Bulk API call
    let apiResults = [];
    if (validRows.length > 0) {
      try {
        const response = await onImport(validRows.map(v => v.row));
        apiResults = (response.results || []).map((r, idx) => ({
          row: validRows[idx].index + dataStartRow,
          data: validRows[idx].row,
          success: r.success,
          error: r.error || null,
        }));
      } catch (err) {
        // Handle 422 validation errors gracefully
        const detail = err.response?.data?.detail;
        if (Array.isArray(detail)) {
          // Pydantic validation errors - map to specific rows
          const rowErrors = {};
          detail.forEach(e => {
            const loc = e.loc || [];
            const idx = loc.find(l => typeof l === 'number');
            if (idx != null) {
              const field = loc[loc.length - 1];
              rowErrors[idx] = rowErrors[idx] || [];
              rowErrors[idx].push(`${field}: ${e.msg}`);
            }
          });
          apiResults = validRows.map(v => {
            const errs = rowErrors[v.index];
            return { row: v.index + dataStartRow, data: v.row, success: !errs, error: errs ? errs.join('; ') : null };
          });
        } else {
          const msg = (typeof detail === 'string' ? detail : err.response?.data?.error) || err.message || 'API error';
          apiResults = validRows.map(v => ({ row: v.index + dataStartRow, data: v.row, success: false, error: msg }));
        }
      }
    }

    setResults([...clientFailures, ...apiResults].sort((a, b) => a.row - b.row));
    setStage('results');
  };

  const passed = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;

  return (
    <Modal open={open} onClose={handleClose} title={title} size="3xl">
      {stage === 'upload' && (
        <div className="space-y-4">
          <div
            className="border-2 border-dashed border-slate-300 rounded-xl p-8 text-center hover:border-primary-400 transition-colors cursor-pointer"
            onClick={() => fileRef.current?.click()}
            onDragOver={e => { e.preventDefault(); e.currentTarget.classList.add('border-primary-500', 'bg-primary-50'); }}
            onDragLeave={e => { e.currentTarget.classList.remove('border-primary-500', 'bg-primary-50'); }}
            onDrop={e => { e.preventDefault(); e.currentTarget.classList.remove('border-primary-500', 'bg-primary-50'); handleFile(e.dataTransfer.files[0]); }}
          >
            <Upload className="w-10 h-10 text-slate-400 mx-auto mb-3" />
            <p className="text-sm font-medium text-slate-700">Drag & drop your .xlsx file here</p>
            <p className="text-xs text-slate-400 mt-1">or click to browse</p>
            <input ref={fileRef} type="file" accept=".xlsx" className="hidden" onChange={e => handleFile(e.target.files[0])} />
          </div>
          {file && (
            <div className="flex items-center gap-2 bg-emerald-50 border border-emerald-200 rounded-lg px-4 py-2">
              <FileSpreadsheet className="w-5 h-5 text-emerald-600" />
              <span className="text-sm font-medium text-emerald-800">{file.name}</span>
            </div>
          )}
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="ghost" onClick={handleClose}>Cancel</Button>
            <Button variant="primary" disabled={!file} onClick={parseAndImport}>Import</Button>
          </div>
        </div>
      )}

      {stage === 'processing' && (
        <div className="py-8 text-center space-y-4">
          <Loader2 className="w-10 h-10 text-primary-600 mx-auto animate-spin" />
          <p className="text-sm font-medium text-slate-700">Importing...</p>
        </div>
      )}

      {stage === 'results' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-emerald-50 border border-emerald-200 rounded-lg p-4 text-center">
              <CheckCircle className="w-6 h-6 text-emerald-600 mx-auto mb-1" />
              <p className="text-2xl font-bold text-emerald-700">{passed}</p>
              <p className="text-xs text-emerald-600">Passed</p>
            </div>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-center">
              <XCircle className="w-6 h-6 text-red-600 mx-auto mb-1" />
              <p className="text-2xl font-bold text-red-700">{failed}</p>
              <p className="text-xs text-red-600">Failed</p>
            </div>
          </div>

          <div className="max-h-[40vh] overflow-y-auto rounded-lg border border-slate-200">
            <table className="w-full text-sm">
              <thead className="bg-slate-50 sticky top-0">
                <tr>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-slate-500">Row</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-slate-500">Name/ID</th>
                  <th className="px-3 py-2 text-center text-xs font-semibold text-slate-500">Status</th>
                  <th className="px-3 py-2 text-left text-xs font-semibold text-slate-500">Remarks</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {results.map((r, i) => (
                  <tr key={i} className={r.success ? '' : 'bg-red-50/50'}>
                    <td className="px-3 py-2 text-slate-600">{r.row}</td>
                    <td className="px-3 py-2 text-slate-700 font-medium">{r.data.full_name || r.data.roll_number || r.data.employee_id || '-'}</td>
                    <td className="px-3 py-2 text-center">{r.success ? <CheckCircle className="w-4 h-4 text-emerald-500 inline" /> : <XCircle className="w-4 h-4 text-red-500 inline" />}</td>
                    <td className="px-3 py-2 text-xs text-slate-500">{r.success ? 'Created successfully' : cleanErrorMessage(r.error)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex justify-end pt-2">
            <Button variant="primary" onClick={handleClose}>Close</Button>
          </div>
        </div>
      )}
    </Modal>
  );
}
