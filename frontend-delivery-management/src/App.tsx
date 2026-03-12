import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import CreateRequest from './pages/CreateRequest';
import RequestDetail from './pages/RequestDetail';
import PaymentPage from './pages/Payment';
import DeliveryAttempt from './pages/DeliveryAttempt';
import AdminConfig from './pages/AdminConfig';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/create" element={<CreateRequest />} />
            <Route path="/request/:id" element={<RequestDetail />} />
            <Route path="/payment/:id" element={<PaymentPage />} />
            <Route path="/attempt/:id" element={<DeliveryAttempt />} />
            <Route path="/admin" element={<AdminConfig />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}
