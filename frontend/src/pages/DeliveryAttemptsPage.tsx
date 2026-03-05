import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { shipmentsApi } from "@/lib/api/shipments";
import { deliveryAttemptsApi } from "@/lib/api/deliveryAttempts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { toast } from "sonner";
import { Plus, Loader2, Info } from "lucide-react";

const reasons: Record<string, string> = {
  no_answer: "No Answer",
  wrong_address: "Wrong Address",
  refused: "Delivery Refused",
  damaged: "Package Damaged",
  other: "Other",
};

export default function DeliveryAttemptsPage() {
  const queryClient = useQueryClient();
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<{ shipment_id: string; status: "success" | "failed"; reason: string; notes: string }>({
    shipment_id: "",
    status: "failed",
    reason: "",
    notes: ""
  });

  const { data: shipments, isLoading: isLoadingShipments } = useQuery({
    queryKey: ["assigned-shipments"],
    queryFn: shipmentsApi.getAssigned,
  });

  const mutation = useMutation({
    mutationFn: deliveryAttemptsApi.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assigned-shipments"] });
      toast.success("Delivery attempt recorded");
      setShowForm(false);
      setFormData({ shipment_id: "", status: "failed", reason: "", notes: "" });
    },
    onError: (error: any) => {
      toast.error(error.message || "Failed to record attempt");
    },
  });

  const handleSubmit = () => {
    if (!formData.shipment_id) {
      toast.error("Please select a shipment");
      return;
    }
    mutation.mutate(formData);
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-3xl">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Delivery Attempts</h1>
        <Button onClick={() => setShowForm(!showForm)} className="bg-accent text-accent-foreground hover:bg-accent/90">
          <Plus className="h-4 w-4 mr-2" /> Record Attempt
        </Button>
      </div>

      {showForm && (
        <Card className="border-accent/30">
          <CardHeader>
            <CardTitle className="text-lg">New Delivery Attempt</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Shipment</label>
              <Select value={formData.shipment_id} onValueChange={(val) => setFormData({ ...formData, shipment_id: val })}>
                <SelectTrigger>
                  <SelectValue placeholder={isLoadingShipments ? "Loading shipments..." : "Select shipment"} />
                </SelectTrigger>
                <SelectContent>
                  {shipments?.map((s) => (
                    <SelectItem key={s.id} value={s.id}>
                      {s.tracking_number} ({s.customer_name})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <label className="text-sm font-medium mb-1 block">Outcome</label>
              <Select value={formData.status} onValueChange={(val: "success" | "failed") => setFormData({ ...formData, status: val })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="failed">Delivery Failed</SelectItem>
                  <SelectItem value="success">Delivery Success</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {formData.status === "failed" && (
              <div>
                <label className="text-sm font-medium mb-1 block">Reason</label>
                <Select value={formData.reason} onValueChange={(val) => setFormData({ ...formData, reason: val })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select reason" />
                  </SelectTrigger>
                  <SelectContent>
                    {Object.entries(reasons).map(([k, v]) => (
                      <SelectItem key={k} value={k}>{v}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}
            <div>
              <label className="text-sm font-medium mb-1 block">Notes</label>
              <Textarea
                placeholder="Additional details..."
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              />
            </div>
            <div className="flex gap-2">
              <Button onClick={handleSubmit} disabled={mutation.isPending} className="bg-accent text-accent-foreground hover:bg-accent/90">
                {mutation.isPending && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                Submit
              </Button>
              <Button variant="outline" onClick={() => setShowForm(false)}>Cancel</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <Card className="bg-muted/30 border-dashed">
        <CardContent className="py-8 text-center text-muted-foreground flex flex-col items-center gap-2">
          <Info className="h-8 w-8 opacity-20" />
          <p className="text-sm">Historical attempts can be viewed in the details of each shipment.</p>
        </CardContent>
      </Card>
    </div>
  );
}
