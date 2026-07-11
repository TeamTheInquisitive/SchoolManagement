import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider, MutationCache, QueryCache } from '@tanstack/react-query';
import { ToastProvider, useToast, ErrorBoundary, NetworkStatus } from 'school-erp-ui-shared';
import App from './App';
import './index.css';

// Global toast ref for use in QueryCache/MutationCache callbacks
const toastRef = { current: null };

function ToastBridge() {
  const toast = useToast();
  toastRef.current = toast;
  return null;
}

const extractError = (error) => {
  const data = error?.response?.data;
  if (data?.error) return data.error;
  if (data?.detail) return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
  if (data?.message) return data.message;
  if (error?.message) return error.message;
  return 'Something went wrong';
};

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 5 * 60 * 1000, gcTime: 30 * 60 * 1000, retry: 2, refetchOnWindowFocus: false },
  },
  queryCache: new QueryCache({
    onError: (error) => {
      if (error?.response?.status === 401) return;
      toastRef.current?.error(extractError(error));
    },
  }),
  mutationCache: new MutationCache({
    onError: (error, _vars, _ctx, mutation) => {
      if (mutation.options.meta?.skipGlobalError) return;
      toastRef.current?.error(extractError(error));
    },
  }),
});

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <ToastBridge />
          <NetworkStatus />
          <App />
        </ToastProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>
);
