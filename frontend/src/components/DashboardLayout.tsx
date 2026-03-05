import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { DriverSidebar } from "@/components/DriverSidebar";
import { Outlet, Navigate } from "react-router-dom";

export default function DashboardLayout() {
  const token = localStorage.getItem("auth_token");

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full">
        <DriverSidebar />
        <div className="flex-1 flex flex-col">
          <header className="h-14 flex items-center border-b bg-card px-4">
            <SidebarTrigger className="mr-4" />
            <h2 className="text-sm font-semibold text-muted-foreground tracking-wide uppercase">
              Driver Dashboard
            </h2>
          </header>
          <main className="flex-1 p-6 overflow-auto">
            <Outlet />
          </main>
        </div>
      </div>
    </SidebarProvider>
  );
}
