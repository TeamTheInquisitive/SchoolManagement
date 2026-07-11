import { useState } from 'react';
import { useDebounceValue } from 'usehooks-ts';
import { Plus, Download, ArrowLeftRight, BookOpen, AlertTriangle, DollarSign, Inbox } from 'lucide-react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../../services/api';
import { ENDPOINTS } from '../../config/api';
import { Button, SearchInput, Badge, Modal, SearchableSelect, Tabs, DateInput, useToast, exportStyledExcel, Pagination, usePagination, useTabState, Breadcrumb } from 'school-erp-ui-shared';
import { useSchoolProfile } from '../../services/settingsService';
import { getSchoolInfo } from '../../utils/getSchoolInfo';
import { BOOK_CATEGORIES } from '../../constants.jsx';

const useBooks = (params) => useQuery({ queryKey: ['library', 'books', params], queryFn: () => api.get(ENDPOINTS.library.books, { params }).then(r => r.data).catch(() => ({ results: [], count: 0 })), placeholderData: (prev) => prev });
const useIssuedBooks = (params) => useQuery({ queryKey: ['library', 'issued', params], queryFn: () => api.get(ENDPOINTS.library.issued, { params }).then(r => r.data).catch(() => ({ results: [], count: 0 })), placeholderData: (prev) => prev });
const useOverdueBooks = () => useQuery({ queryKey: ['library', 'overdue'], queryFn: () => api.get(ENDPOINTS.library.overdue).then(r => r.data).catch(() => ({ results: [], total_fines: 0 })) });
const useBookSearch = (search) => useQuery({ queryKey: ['library', 'books-search', search], queryFn: () => api.get(ENDPOINTS.library.books, { params: { search: search || undefined, limit: 20 } }).then(r => r.data).catch(() => ({ results: [] })) });
const useUserSearch = (search) => useQuery({ queryKey: ['users', 'search', search], queryFn: async () => {
  const [students, teachers, staff] = await Promise.all([
    api.get(ENDPOINTS.students.list, { params: { search: search || undefined, page_size: 10 } }).then(r => r.data).catch(() => ({ results: [] })),
    api.get(ENDPOINTS.teachers.list, { params: { search: search || undefined, page_size: 10 } }).then(r => r.data).catch(() => ({ results: [] })),
    api.get(ENDPOINTS.staff.list, { params: { search: search || undefined, page_size: 10 } }).then(r => r.data).catch(() => ({ results: [] })),
  ]);
  return [
    ...(students.results || []).map(s => ({ id: s.user_id || s.id, name: s.full_name, type: 'student', sub: `Student • ${s.roll_number || s.class_name || ''}` })),
    ...(teachers.results || []).map(t => ({ id: t.user_id || t.id, name: t.user?.full_name || t.full_name, type: 'teacher', sub: `Teacher • ${t.primary_subject || t.subject || ''}` })),
    ...(staff.results || []).filter(s => !s.is_teacher).map(s => ({ id: s.user_id || s.id, name: s.full_name, type: 'staff', sub: `Staff • ${s.department || ''}` })),
  ];
} });

export default function LibraryPage() {
  const toast = useToast();
  const { data: schoolProfile } = useSchoolProfile();
  const [exporting, setExporting] = useState(false);
  const libraryTabs = [{ id: 'inventory', label: 'Book Inventory', icon: BookOpen }, { id: 'history', label: 'Issue/Return History', icon: ArrowLeftRight }];
  const [tab, setTab] = useTabState(libraryTabs);
  const [search, setSearch] = useState('');
  const [debouncedSearch] = useDebounceValue(search, 300);
  const [bookDialog, setBookDialog] = useState(false);
  const [issueDialog, setIssueDialog] = useState(false);
  const [bookForm, setBookForm] = useState({});
  const [issueForm, setIssueForm] = useState({});
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const pagination = usePagination(20, "admin-library");

  const { data: booksData } = useBooks({ ...pagination.params, search: debouncedSearch || undefined });
  const { data: issuedData } = useIssuedBooks({ ...pagination.params, search: tab === 1 ? (debouncedSearch || undefined) : undefined });
  const { data: overdueData } = useOverdueBooks();
  const [bookSearch, setBookSearch] = useState('');
  const [userSearch, setUserSearch] = useState('');
  const { data: bookOptions, isLoading: booksLoading } = useBookSearch(bookSearch);
  const { data: userOptions, isLoading: usersLoading } = useUserSearch(userSearch);

  const qc = useQueryClient();
  const addBookMutation = useMutation({ mutationFn: (data) => api.post(ENDPOINTS.library.books, data).then(r => r.data), onSuccess: () => { qc.invalidateQueries({ queryKey: ['library'] }); toast.success('Book added successfully'); }, onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to add book'); } });
  const issueBookMutation = useMutation({ mutationFn: (data) => api.post(ENDPOINTS.library.issue, data).then(r => r.data), onSuccess: () => { qc.invalidateQueries({ queryKey: ['library'] }); toast.success('Book issued successfully'); }, onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to issue book'); } });
  const returnBookMutation = useMutation({ mutationFn: (id) => api.post(ENDPOINTS.library.return, { issue_id: id }).then(r => r.data), onSuccess: () => { qc.invalidateQueries({ queryKey: ['library'] }); toast.success('Book returned successfully'); }, onError: (err) => { toast.error(err.response?.data?.error || err.response?.data?.detail || 'Failed to return book'); } });

  const books = Array.isArray(booksData?.results) ? booksData.results : [];
  const rawIssued = Array.isArray(issuedData?.results) ? issuedData.results : [];
  const issued = rawIssued.filter(i => {
    if (tab !== 1) return true;
    if (fromDate && i.issue_date && i.issue_date < fromDate) return false;
    if (toDate && i.issue_date && i.issue_date > toDate) return false;
    return true;
  });
  const overdue = Array.isArray(overdueData?.results) ? overdueData.results : [];
  const booksSummary = booksData?.summary || {};
  const totalBooks = booksSummary.total_books || booksData?.count || books.length;
  const available = booksSummary.available ?? books.reduce((s, b) => s + Number(b.available_copies || 0), 0);
  const issuedCount = booksSummary.issued || issuedData?.count || issued.length;
  const overdueCount = overdueData?.count || overdue.length;
  const penalties = overdueData?.total_fines || overdue.reduce((s, o) => s + Number(o.fine_amount || o.penalty || 0), 0);

  const kpis = [
    { label: 'Total Books', value: totalBooks, icon: BookOpen, color: 'text-blue-600', bg: 'bg-blue-50' },
    { label: 'Available', value: available, icon: BookOpen, color: 'text-green-600', bg: 'bg-green-50' },
    { label: 'Issued', value: issuedCount, icon: ArrowLeftRight, color: 'text-amber-600', bg: 'bg-amber-50' },
    { label: 'Overdue', value: overdueCount, icon: AlertTriangle, color: 'text-red-600', bg: 'bg-red-50' },
    { label: 'Penalties', value: `₹${Math.round(penalties)}`, icon: DollarSign, color: 'text-green-600', bg: 'bg-green-50' },
  ];

  return (
    <div>
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Library' }]} />
      <div className="flex justify-between items-center mb-6">
        <div><h1 className="text-2xl md:text-3xl font-bold text-slate-900">Library Management</h1><p className="text-sm text-slate-500 mt-1">Manage books, track issues, returns and penalties</p></div>
        <div className="flex gap-2"><Button variant="secondary" icon={ArrowLeftRight} onClick={() => setIssueDialog(true)}>Issue Book</Button><Button variant="primary" icon={Plus} onClick={() => setBookDialog(true)}>Add Book</Button></div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-4">
        {kpis.map(k => (<div key={k.label} className="bg-white border border-slate-200 rounded-xl p-3 flex items-center gap-3 transition-all duration-200 hover:-translate-y-0.5 hover:shadow-soft-lg hover:border-slate-300 cursor-default group"><div className={`${k.bg} p-2.5 rounded-xl transition-transform duration-200 group-hover:scale-110`}><k.icon className={`w-4 h-4 ${k.color}`} /></div><div><p className="text-xs text-slate-500 font-medium">{k.label}</p><p className="text-lg font-bold text-slate-900">{k.value}</p></div></div>))}
      </div>

      {overdue.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-3 mb-4">
          <p className="text-sm font-semibold text-red-700 mb-1">⚠️ Overdue Books ({overdue.length})</p>
          {overdue.slice(0, 3).map((o, i) => (
            <div key={i} className="flex justify-between items-center mb-1"><span className="text-xs text-slate-600">{o.student_name || o.user_name || ''} — "{o.book_title || o.title || ''}" ({o.days_overdue || ''} days, ₹{o.fine_amount || o.penalty || 0})</span><Button variant="danger" size="sm" onClick={() => returnBookMutation.mutate(o.id)}>Return Now</Button></div>
          ))}
        </div>
      )}

      <Tabs tabs={libraryTabs} active={tab} onChange={(i) => { setTab(i); setSearch(''); pagination.reset(); }} className="mb-4" />

      <div className="bg-white border border-slate-200 rounded-xl p-4 md:p-5 transition-all duration-200 hover:shadow-soft-lg hover:border-slate-300">
        <div className="flex justify-between mb-3"><SearchInput value={search} onChange={(v) => { setSearch(v); pagination.reset(); }} placeholder={tab === 0 ? "Search books..." : "Search issues..."} /><Button variant="secondary" size="sm" icon={Download} disabled={exporting} loading={exporting} onClick={async () => { if (exporting) return; setExporting(true); try { if (tab === 0) { const headers = ['Title', 'Author', 'ISBN', 'Category', 'Total Copies', 'Available', 'Issued']; const rows = books.map(b => [b.title, b.author, b.isbn, b.category, b.total_copies, b.available_copies, (b.total_copies || 0) - (b.available_copies || 0)]); await exportStyledExcel({ filename: 'Library_Books', schoolInfo: getSchoolInfo(schoolProfile), reportTitle: 'Library Books', headers, rows }); } else { const headers = ['Book', 'Student', 'Issue Date', 'Due Date', 'Penalty', 'Status']; const rows = issued.map(i => [i.book_title || i.title, i.student_name || i.user_name, i.issue_date, i.due_date, i.fine_amount || 0, i.status]); await exportStyledExcel({ filename: 'Library_Issues', schoolInfo: getSchoolInfo(schoolProfile), reportTitle: 'Library Issues', headers, rows }); } toast.success('Exported successfully'); } catch { toast.error('Failed to export'); } setExporting(false); }}>{exporting ? 'Exporting...' : 'Export Excel'}</Button></div>

        {tab === 0 && (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-slate-200 text-left"><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Book Title</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Author</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">ISBN</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Category</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Total</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Available</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Issued</th></tr></thead>
              <tbody>
                {books.map(b => (<tr key={b.id} className="border-b border-slate-100"><td className="py-2 px-2 font-medium text-slate-800">{b.title || ''}</td><td className="py-2 px-2 text-slate-500">{b.author || ''}</td><td className="py-2 px-2 text-slate-500">{b.isbn || ''}</td><td className="py-2 px-2 text-slate-500">{b.category || ''}</td><td className="py-2 px-2 text-slate-500">{b.total_copies || 0}</td><td className="py-2 px-2 text-green-600 font-semibold">{b.available_copies || 0}</td><td className="py-2 px-2 text-slate-500">{(b.total_copies || 0) - (b.available_copies || 0)}</td></tr>))}
                {books.length === 0 && <tr><td colSpan={7} className="text-center py-12 text-slate-400"><Inbox className="w-10 h-10 mx-auto mb-2 text-slate-300" /><p className="text-sm font-medium">No books in library</p><p className="text-xs text-slate-400 mt-1">Add books to see them listed here.</p></td></tr>}
              </tbody>
            </table>
          </div>
        )}

        {tab === 1 && (
          <div>
          {/* Date Range Filter for Issue History */}
          <div className="flex items-center gap-2 mb-3 flex-wrap">
            <span className="text-sm font-medium text-slate-600">Issue Date Range:</span>
            <label className="text-sm text-gray-600">From</label>
            <input type="date" className="border border-slate-200 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" value={fromDate} onChange={e => setFromDate(e.target.value)} />
            <label className="text-sm text-gray-600">To</label>
            <input type="date" className="border border-slate-200 rounded-lg px-2 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" value={toDate} onChange={e => setToDate(e.target.value)} />
            {(fromDate || toDate) && <button onClick={() => { setFromDate(''); setToDate(''); }} className="text-xs text-red-500 hover:text-red-700 ml-2">Clear</button>}
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead><tr className="border-b border-slate-200 text-left"><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Book</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Student</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Issue Date</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Due Date</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Penalty</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Status</th><th className="py-2 px-2 text-xs font-semibold text-slate-500 uppercase">Actions</th></tr></thead>
              <tbody>
                {issued.map(i => (<tr key={i.id} className="border-b border-slate-100"><td className="py-2 px-2 font-medium text-slate-800">{i.book_title || i.title || ''}</td><td className="py-2 px-2 text-slate-500">{i.student_name || i.user_name || ''}</td><td className="py-2 px-2 text-slate-500">{i.issue_date || ''}</td><td className="py-2 px-2 text-slate-500">{i.due_date || ''}{i.days_overdue > 0 && <span className="text-xs text-red-500 block">{i.days_overdue} days overdue</span>}</td><td className={`py-2 px-2 ${i.fine_amount > 0 ? 'text-red-600' : 'text-slate-500'}`}>{i.fine_amount ? `₹${i.fine_amount}` : '—'}</td><td className="py-2 px-2"><Badge status={i.status || 'Issued'} /></td><td className="py-2 px-2">{i.status !== 'Returned' && <Button variant="primary" size="sm" onClick={() => returnBookMutation.mutate(i.id)}>📖 Return</Button>}</td></tr>))}
                {issued.length === 0 && <tr><td colSpan={7} className="text-center py-12 text-slate-400"><ArrowLeftRight className="w-10 h-10 mx-auto mb-2 text-slate-300" /><p className="text-sm font-medium">No issue records found</p><p className="text-xs text-slate-400 mt-1">Issue/return history will appear here.</p></td></tr>}
              </tbody>
            </table>
          </div>
          </div>
        )}
        <Pagination
          page={pagination.page}
          totalPages={(tab === 0 ? booksData?.total_pages : issuedData?.total_pages) || 1}
          totalCount={(tab === 0 ? booksData?.count : issuedData?.count) || 0}
          pageSize={pagination.pageSize}
          onPageChange={(p) => pagination.setPage(p)}
        />
      </div>

      {/* Add Book Modal */}
      <Modal open={bookDialog} onClose={() => setBookDialog(false)} title="Add New Book">
        <div className="grid grid-cols-2 gap-3 p-4">
          <div className="col-span-2"><label className="text-xs text-slate-600">Book Title *</label><input value={bookForm.title || ''} onChange={e => setBookForm({...bookForm, title: e.target.value})} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" /></div>
          <div><label className="text-xs text-slate-600">Author *</label><input value={bookForm.author || ''} onChange={e => setBookForm({...bookForm, author: e.target.value})} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" /></div>
          <div><label className="text-xs text-slate-600">ISBN *</label><input value={bookForm.isbn || ''} onChange={e => setBookForm({...bookForm, isbn: e.target.value})} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" /></div>
          <div><label className="text-xs text-slate-600">Category *</label><SearchableSelect value={bookForm.category || ''} onChange={(val) => setBookForm({...bookForm, category: val})} options={BOOK_CATEGORIES} placeholder="Select Category..." /></div>
          <div><label className="text-xs text-slate-600">Total Copies *</label><input type="number" value={bookForm.total_copies || ''} onChange={e => setBookForm({...bookForm, total_copies: e.target.value})} className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm" /></div>
        </div>
        <div className="flex justify-end gap-2 px-4 pb-4"><Button variant="ghost" onClick={() => setBookDialog(false)}>Cancel</Button><Button variant="primary" onClick={() => { addBookMutation.mutate({...bookForm, total_copies: Number(bookForm.total_copies)}, { onSuccess: () => { setBookDialog(false); setBookForm({}); }}); }}>Add Book</Button></div>
      </Modal>

      {/* Issue Book Modal */}
      <Modal open={issueDialog} onClose={() => setIssueDialog(false)} title="Issue Book">
        <div className="space-y-3 p-4">
          <div><label className="text-xs text-slate-600 mb-1 block">Book *</label>
            <SearchableSelect
              value={issueForm.book_id || ''}
              onChange={(val) => setIssueForm({...issueForm, book_id: val})}
              options={(bookOptions?.results || []).filter(b => b.available_copies > 0).map(b => ({ value: b.id, label: `${b.title}${b.author ? ' - ' + b.author : ''}`, sub: `${b.available_copies} available` }))}
              onSearch={setBookSearch}
              loading={booksLoading}
              placeholder="Search books..."
              renderOption={(o) => <div><span className="font-medium">{o.label}</span><span className="text-xs text-slate-400 ml-2">{o.sub}</span></div>}
            />
          </div>
          <div><label className="text-xs text-slate-600 mb-1 block">Issue To (Student / Teacher / Staff) *</label>
            <SearchableSelect
              value={issueForm.borrower_id || ''}
              onChange={(val) => { const user = (userOptions || []).find(u => u.id === val); setIssueForm({...issueForm, borrower_id: val, borrower_type: user?.type || 'student'}); }}
              options={(userOptions || []).map(u => ({ value: u.id, label: u.name, sub: u.sub }))}
              onSearch={setUserSearch}
              loading={usersLoading}
              placeholder="Search by name..."
              renderOption={(o) => <div><span className="font-medium">{o.label}</span><span className="text-xs text-slate-400 ml-2">{o.sub}</span></div>}
            />
          </div>
          <div><DateInput label="Due Date *" value={issueForm.due_date} onChange={v => setIssueForm({...issueForm, due_date: v})} /></div>
        </div>
        <div className="flex justify-end gap-2 px-4 pb-4"><Button variant="ghost" onClick={() => setIssueDialog(false)}>Cancel</Button><Button variant="primary" disabled={!issueForm.book_id || !issueForm.borrower_id || !issueForm.due_date} onClick={() => { issueBookMutation.mutate(issueForm, { onSuccess: () => { setIssueDialog(false); setIssueForm({}); }}); }}>Issue Book</Button></div>
      </Modal>
    </div>
  );
}
