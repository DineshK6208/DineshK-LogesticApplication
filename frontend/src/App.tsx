import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import DashboardLayout from "./components/DashboardLayout";
import AvailabilityPage from "./pages/AvailabilityPage";
import ShipmentsPage from "./pages/ShipmentsPage";
import DeliveryStatusPage from "./pages/DeliveryStatusPage";
import DeliveryAttemptsPage from "./pages/DeliveryAttemptsPage";
import EarningsPage from "./pages/EarningsPage";
import LoginPage from "./pages/LoginPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<DashboardLayout />}>
            <Route path="/" element={<AvailabilityPage />} />
            <Route path="/shipments" element={<ShipmentsPage />} />
            <Route path="/delivery-status" element={<DeliveryStatusPage />} />
            <Route path="/delivery-attempts" element={<DeliveryAttemptsPage />} />
            <Route path="/earnings" element={<EarningsPage />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
