import { useState, useCallback, useMemo } from 'react';

function toSlug(label) {
  return label
    .toLowerCase()
    .replace(/&/g, 'and')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}

export function useTabState(tabs = [], { paramName = 'tab' } = {}) {
  const slugs = useMemo(
    () => tabs.map((t) => t.id || toSlug(t.label || '')),
    [tabs.map(t => t.id || t.label).join(',')]
  );

  const getInitialIndex = () => {
    try {
      const params = new URLSearchParams(window.location.search);
      const value = params.get(paramName);
      if (value != null) {
        const idx = slugs.indexOf(value);
        if (idx !== -1) return idx;
      }
    } catch {
      // fallback
    }
    return 0;
  };

  const [tab, setTabState] = useState(getInitialIndex);

  const setTab = useCallback(
    (index) => {
      setTabState(index);
      try {
        const url = new URL(window.location.href);
        const slug = slugs[index];
        if (index === 0) {
          url.searchParams.delete(paramName);
        } else if (slug) {
          url.searchParams.set(paramName, slug);
        }
        window.history.replaceState({}, '', url.toString());
      } catch {
        // ignore
      }
    },
    [slugs, paramName]
  );

  return [tab, setTab];
}
