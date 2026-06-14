import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, ArrowRight, LayoutDashboard, Users, GraduationCap, Calendar, ClipboardList, DollarSign, Bus, Bell, Briefcase, FileText, Settings, UserPlus, ClipboardCheck, UserCheck, KeyRound, BookOpen, BarChart2 } from 'lucide-react';

const PAGES = [
  { path: '/admin/dashboard', label: 'Dashboard', icon: LayoutDashboard, keywords: 'home overview stats' },
  { path: '/admin/students', label: 'Students', icon: Users, keywords: 'student list manage' },
  { path: '/admin/admissions', label: 'New Admissions', icon: UserPlus, keywords: 'admission enroll register' },
  { path: '/admin/teachers', label: 'Teachers & Staff', icon: GraduationCap, keywords: 'teacher faculty employee' },
  { path: '/admin/staff', label: 'Staff & Payroll', icon: Briefcase, keywords: 'staff salary payroll hr' },
  { path: '/admin/timetable', label: 'Timetable', icon: Calendar, keywords: 'schedule period class routine' },
  { path: '/admin/attendance', label: 'Attendance', icon: ClipboardCheck, keywords: 'present absent mark daily' },
  { path: '/admin/examinations', label: 'Examinations', icon: ClipboardList, keywords: 'exam test results marks grade' },
  { path: '/admin/fees', label: 'Fee Management', icon: DollarSign, keywords: 'fee payment receipt due collect' },
  { path: '/admin/transport', label: 'Transport', icon: Bus, keywords: 'bus vehicle route driver' },
  { path: '/admin/leaves', label: 'Leave Management', icon: FileText, keywords: 'leave approve reject absence' },
  { path: '/admin/mentoring', label: 'Mentoring', icon: UserCheck, keywords: 'mentor assign student guide' },
  { path: '/admin/notifications', label: 'Notifications', icon: Bell, keywords: 'notify message announcement send' },
  { path: '/admin/library', label: 'Library', icon: BookOpen, keywords: 'book issue return catalog' },
  { path: '/admin/analytics', label: 'Analytics', icon: BarChart2, keywords: 'report chart data insight' },
  { path: '/admin/credentials', label: 'Credentials', icon: KeyRound, keywords: 'password reset login credential' },
  { path: '/admin/settings', label: 'Settings', icon: Settings, keywords: 'settings config school profile academic' },
  { path: '/admin/settings?tab=classes-sections', label: 'Classes & Sections', icon: Settings, keywords: 'class section add create' },
  { path: '/admin/settings?tab=subjects', label: 'Subjects', icon: Settings, keywords: 'subject add manage' },
  { path: '/admin/settings?tab=fee-structure', label: 'Fee Structure', icon: Settings, keywords: 'fee structure component' },
  { path: '/admin/settings?tab=timetable', label: 'Timetable Settings', icon: Settings, keywords: 'slot type period configure' },
];

export default function CommandPalette() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);
  const listRef = useRef(null);
  const navigate = useNavigate();

  const filtered = query.trim()
    ? PAGES.filter(p => {
        const q = query.toLowerCase();
        return p.label.toLowerCase().includes(q) || p.keywords.includes(q);
      })
    : PAGES.slice(0, 8);

  useEffect(() => {
    function handleKeyDown(e) {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(prev => !prev);
      }
    }
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    if (open) {
      setQuery('');
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [open]);

  useEffect(() => {
    setSelectedIndex(0);
  }, [query]);

  const handleSelect = useCallback((page) => {
    setOpen(false);
    navigate(page.path);
  }, [navigate]);

  const handleKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(i => Math.min(i + 1, filtered.length - 1));
      scrollIntoView(Math.min(selectedIndex + 1, filtered.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(i => Math.max(i - 1, 0));
      scrollIntoView(Math.max(selectedIndex - 1, 0));
    } else if (e.key === 'Enter' && filtered[selectedIndex]) {
      handleSelect(filtered[selectedIndex]);
    } else if (e.key === 'Escape') {
      setOpen(false);
    }
  };

  const scrollIntoView = (idx) => {
    const item = listRef.current?.children[idx];
    if (item) item.scrollIntoView({ block: 'nearest' });
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100]">
      <div className="fixed inset-0 bg-black/40 backdrop-blur-sm" onClick={() => setOpen(false)} />
      <div className="fixed top-[20%] left-1/2 -translate-x-1/2 w-full max-w-lg">
        <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden">
          {/* Search Input */}
          <div className="flex items-center gap-3 px-4 py-3 border-b border-slate-100">
            <Search size={18} className="text-slate-400 flex-shrink-0" />
            <input
              ref={inputRef}
              value={query}
              onChange={e => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Search pages... (type to filter)"
              className="flex-1 text-sm text-slate-800 placeholder-slate-400 outline-none bg-transparent"
            />
            <kbd className="text-[10px] bg-slate-100 border border-slate-200 px-1.5 py-0.5 rounded text-slate-400 font-mono">ESC</kbd>
          </div>

          {/* Results */}
          <div ref={listRef} className="max-h-[320px] overflow-y-auto py-2">
            {filtered.length === 0 && (
              <div className="px-4 py-8 text-center">
                <p className="text-sm text-slate-400">No results for "{query}"</p>
              </div>
            )}
            {filtered.map((page, idx) => {
              const Icon = page.icon;
              const isActive = idx === selectedIndex;
              return (
                <button
                  key={page.path + page.label}
                  onClick={() => handleSelect(page)}
                  onMouseEnter={() => setSelectedIndex(idx)}
                  className={`w-full flex items-center gap-3 px-4 py-2.5 text-left transition-colors duration-75 ${isActive ? 'bg-primary-50' : 'hover:bg-slate-50'}`}
                >
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 ${isActive ? 'bg-primary-100' : 'bg-slate-100'}`}>
                    <Icon size={15} className={isActive ? 'text-primary-600' : 'text-slate-500'} />
                  </div>
                  <span className={`text-sm flex-1 ${isActive ? 'text-primary-700 font-medium' : 'text-slate-700'}`}>{page.label}</span>
                  {isActive && <ArrowRight size={14} className="text-primary-400" />}
                </button>
              );
            })}
          </div>

          {/* Footer */}
          <div className="flex items-center gap-4 px-4 py-2.5 border-t border-slate-100 bg-slate-50/50">
            <span className="flex items-center gap-1 text-[10px] text-slate-400"><kbd className="bg-white border border-slate-200 px-1 py-0.5 rounded font-mono">↑↓</kbd> navigate</span>
            <span className="flex items-center gap-1 text-[10px] text-slate-400"><kbd className="bg-white border border-slate-200 px-1 py-0.5 rounded font-mono">↵</kbd> open</span>
            <span className="flex items-center gap-1 text-[10px] text-slate-400"><kbd className="bg-white border border-slate-200 px-1 py-0.5 rounded font-mono">esc</kbd> close</span>
          </div>
        </div>
      </div>
    </div>
  );
}
