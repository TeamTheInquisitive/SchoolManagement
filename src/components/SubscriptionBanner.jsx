import { useEffect, useState } from 'react';
import { AlertTriangle, Info, XCircle } from 'lucide-react';
import api from '../services/api';

const bannerStyles = {
  trial: { bg: 'bg-amber-50', border: 'border-l-amber-500', text: 'text-amber-800', Icon: Info },
  expiring: { bg: 'bg-red-50', border: 'border-l-red-500', text: 'text-red-800', Icon: AlertTriangle },
  expired: { bg: 'bg-red-100', border: 'border-l-red-600', text: 'text-red-900', Icon: XCircle },
};

export default function SubscriptionBanner() {
  const [banner, setBanner] = useState(null);

  useEffect(() => {
    api.get('/admin/dashboard/subscription-banner')
      .then(({ data }) => {
        if (data.show_banner) setBanner(data);
      })
      .catch(() => {});
  }, []);

  if (!banner) return null;

  const style = bannerStyles[banner.type] || bannerStyles.trial;

  return (
    <div className={`flex items-center gap-2.5 px-4 py-2.5 ${style.bg} border-l-4 ${style.border} rounded mb-4`}>
      <style.Icon className={`w-4 h-4 ${style.text} shrink-0`} />
      <p className={`text-sm font-medium ${style.text}`}>{banner.message}</p>
    </div>
  );
}
