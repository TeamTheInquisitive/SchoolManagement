import { useState } from 'react';
import { Breadcrumb, Tabs, useTabState } from 'school-erp-ui-shared';
import { FileText, CreditCard, Award, ScrollText } from 'lucide-react';
import CircularTab from './tabs/CircularTab';
import IdCardTab from './tabs/IdCardTab';
import CertificateTab from './tabs/CertificateTab';
import TcBonafideTab from './tabs/TcBonafideTab';

const TABS = [
  { id: 'circulars', label: 'Circulars', icon: FileText },
  { id: 'id-cards', label: 'ID Cards', icon: CreditCard },
  { id: 'certificates', label: 'Certificates', icon: Award },
  { id: 'tc-bonafide', label: 'TC / Bonafide', icon: ScrollText },
];

export default function GeneratorsPage() {
  const [activeTab, setActiveTab] = useTabState(TABS);

  return (
    <div className="space-y-6">
      <Breadcrumb items={[{ label: 'Dashboard', href: '/admin/dashboard' }, { label: 'Generators' }]} />
      <div>
        <h1 className="text-2xl md:text-3xl font-bold text-slate-900">Document Generators</h1>
        <p className="text-sm text-slate-500 mt-0.5">Create circulars, ID cards, certificates, and official documents</p>
      </div>

      <Tabs tabs={TABS} active={activeTab} onChange={setActiveTab} />

      {activeTab === 0 && <CircularTab />}
      {activeTab === 1 && <IdCardTab />}
      {activeTab === 2 && <CertificateTab />}
      {activeTab === 3 && <TcBonafideTab />}
    </div>
  );
}
