import { Construction } from 'lucide-react';

export default function ComingSoon({ title }) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px]">
      <div className="w-16 h-16 rounded-full bg-gradient-to-br from-slate-100 to-slate-200 flex items-center justify-center mx-auto mb-4 shadow-sm">
        <Construction className="w-8 h-8 text-slate-400" />
      </div>
      <h2 className="text-xl font-bold text-slate-900">{title}</h2>
      <p className="text-sm text-slate-500 mt-1">This module will be available in the next phase.</p>
    </div>
  );
}
