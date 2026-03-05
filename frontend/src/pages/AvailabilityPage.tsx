import { useState, useEffect } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { availabilityApi } from "@/lib/api/availability";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import { Clock, Loader2 } from "lucide-react";

export default function AvailabilityPage() {
  const queryClient = useQueryClient();

  const { data: profile, isLoading, error } = useQuery({
    queryKey: ["driver-profile"],
    queryFn: availabilityApi.getStatus,
  });

  const mutation = useMutation({
    mutationFn: availabilityApi.toggleOnline,
    onSuccess: (updatedProfile) => {
      queryClient.setQueryData(["driver-profile"], updatedProfile);
      toast.success(`You are now ${updatedProfile.is_available ? "Online" : "Offline"}`);
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
        Error loading profile: {(error as any).message}
      </div>
    );
  }

  const online = profile?.is_available || false;

  return (
    <div className="space-y-6 animate-fade-in max-w-3xl">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Availability</h1>
        <Badge variant={online ? "default" : "secondary"} className={online ? "bg-success text-success-foreground" : ""}>
          {online ? "Online" : "Offline"}
        </Badge>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Clock className="h-5 w-5 text-accent" />
            Current Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <span className="text-sm font-medium">Duty Status</span>
              <p className="text-xs text-muted-foreground">Toggle your availability to receive new shipments</p>
            </div>
            <Switch
              checked={online}
              onCheckedChange={(checked) => mutation.mutate(checked)}
              disabled={mutation.isPending}
            />
          </div>
        </CardContent>
      </Card>

      <Card className="bg-muted/30 border-dashed">
        <CardContent className="pt-6">
          <p className="text-sm text-center text-muted-foreground">
            License: <span className="font-mono">{profile?.license_number}</span> |
            KYC: <span className="capitalize">{profile?.kyc_status}</span>
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
