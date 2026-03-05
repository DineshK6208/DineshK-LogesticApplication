import { useQuery } from "@tanstack/react-query";
import { shipmentsApi, Shipment } from "@/lib/api/shipments";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Package, MapPin, Clock, User, Loader2 } from "lucide-react";

const statusColors: Record<string, string> = {
  assigned: "bg-blue-500 text-white",
  picked_up: "bg-yellow-500 text-black",
  in_transit: "bg-accent text-accent-foreground",
  out_for_delivery: "bg-indigo-500 text-white",
  delivered: "bg-success text-success-foreground",
  delivery_failed: "bg-destructive text-destructive-foreground",
};

const statusLabels: Record<string, string> = {
  assigned: "Assigned",
  picked_up: "Picked Up",
  in_transit: "In Transit",
  out_for_delivery: "Out for Delivery",
  delivered: "Delivered",
  delivery_failed: "Failed",
};

export default function ShipmentsPage() {
  const { data: shipments, isLoading, error } = useQuery({
    queryKey: ["assigned-shipments"],
    queryFn: shipmentsApi.getAssigned,
  });

  if (isLoading) {
    return (
      <div className="flex h-[50vh] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-accent" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-4 text-destructive bg-destructive/10 rounded-md">
        Error loading shipments: {(error as any).message}
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Assigned Shipments</h1>
        <Badge variant="outline" className="font-mono">
          {shipments?.length || 0} shipments
        </Badge>
      </div>

      {!shipments || shipments.length === 0 ? (
        <Card className="border-dashed flex flex-col items-center justify-center py-12 text-muted-foreground">
          <Package className="h-12 w-12 mb-4 opacity-20" />
          <p>No active shipments assigned to you.</p>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {shipments.map((s) => (
            <Card key={s.id} className="hover:shadow-md transition-shadow">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-semibold font-mono">{s.tracking_number}</CardTitle>
                  <Badge className={statusColors[s.status] || "bg-secondary"}>
                    {statusLabels[s.status] || s.status}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-2 text-sm">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <User className="h-4 w-4" /> {s.customer_name || "Unknown Customer"}
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <MapPin className="h-4 w-4 text-success" /> <span className="font-medium shrink-0">From:</span>
                  <span className="truncate">{s.origin_address}</span>
                </div>
                <div className="flex items-center gap-2 text-muted-foreground">
                  <MapPin className="h-4 w-4 text-destructive" /> <span className="font-medium shrink-0">To:</span>
                  <span className="truncate">{s.destination_address}</span>
                </div>
                <div className="flex items-center justify-between pt-2 border-t mt-2">
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Clock className="h-4 w-4" />
                    {s.estimated_delivery_at ? new Date(s.estimated_delivery_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : "Not scheduled"}
                  </div>
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Package className="h-4 w-4" /> {s.weight || "N/A"}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
