import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { shipmentsApi } from "@/lib/api/shipments";
import { deliveryStatusApi, DeliveryStatusType } from "@/lib/api/deliveryStatus";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { Truck, CheckCircle, AlertCircle, Loader2 } from "lucide-react";

const statusLabels: Record<string, string> = {
  assigned: "Assigned",
  picked_up: "Picked Up",
  in_transit: "In Transit",
  out_for_delivery: "Out for Delivery",
  delivered: "Delivered",
  delivery_failed: "Failed",
  rto: "RTO",
};

const statusIcons: Record<string, any> = {
  assigned: Truck,
  picked_up: Truck,
  in_transit: Truck,
  out_for_delivery: Truck,
  delivered: CheckCircle,
  delivery_failed: AlertCircle,
  rto: AlertCircle,
};

const allStatuses: DeliveryStatusType[] = ["assigned", "picked_up", "in_transit", "out_for_delivery", "delivered", "delivery_failed", "rto"];

export default function DeliveryStatusPage() {
  const queryClient = useQueryClient();

  const { data: shipments, isLoading, error } = useQuery({
    queryKey: ["assigned-shipments"],
    queryFn: shipmentsApi.getAssigned,
  });

  const mutation = useMutation({
    mutationFn: (data: { shipment_id: string; status: DeliveryStatusType }) =>
      deliveryStatusApi.update(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assigned-shipments"] });
      toast.success("Delivery status updated successfully");
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to update status");
    },
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
    <div className="space-y-6 animate-fade-in max-w-3xl">
      <h1 className="text-2xl font-bold">Update Delivery Status</h1>

      {!shipments || shipments.length === 0 ? (
        <Card className="border-dashed flex flex-col items-center justify-center py-12 text-muted-foreground">
          <Truck className="h-12 w-12 mb-4 opacity-20" />
          <p>No active shipments to update.</p>
        </Card>
      ) : (
        <div className="space-y-4">
          {shipments.map((s) => {
            const Icon = statusIcons[s.status] || Truck;
            return (
              <Card key={s.id}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base font-mono">{s.tracking_number}</CardTitle>
                    <Badge variant="outline">{statusLabels[s.status] || s.status}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">
                    {s.customer_name} — {s.destination_address}
                  </p>
                  <div className="flex items-center gap-3">
                    <Select
                      value={s.status}
                      onValueChange={(val) => mutation.mutate({ shipment_id: s.id, status: val as DeliveryStatusType })}
                      disabled={mutation.isPending}
                    >
                      <SelectTrigger className="w-48">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {allStatuses.map((stat) => (
                          <SelectItem key={stat} value={stat}>
                            {statusLabels[stat]}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    {mutation.isPending && mutation.variables?.shipment_id === s.id ? (
                      <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
                    ) : (
                      <Icon className="h-5 w-5 text-accent" />
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
