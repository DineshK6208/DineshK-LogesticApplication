import { useQuery } from "@tanstack/react-query";
import { earningsApi, Earning } from "@/lib/api/earnings";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { DollarSign, TrendingUp, History, Loader2, ArrowUpRight } from "lucide-react";

export default function EarningsPage() {
  const { data: earnings, isLoading, error } = useQuery({
    queryKey: ["driver-earnings"],
    queryFn: earningsApi.getAll,
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
        Error loading earnings: {(error as any).message}
      </div>
    );
  }

  const totalAmount = earnings?.reduce((acc, curr) => acc + parseFloat(curr.amount), 0) || 0;
  const basePay = earnings?.filter(e => e.earning_type === "base_pay").reduce((acc, curr) => acc + parseFloat(curr.amount), 0) || 0;
  const deliveryBonus = earnings?.filter(e => e.earning_type === "delivery_bonus").reduce((acc, curr) => acc + parseFloat(curr.amount), 0) || 0;

  return (
    <div className="space-y-6 animate-fade-in">
      <h1 className="text-2xl font-bold">Earnings</h1>

      <div className="grid gap-4 md:grid-cols-3">
        <Card className="bg-accent text-accent-foreground">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <DollarSign className="h-4 w-4" /> Total Earnings
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₹{totalAmount.toLocaleString()}</div>
            <p className="text-xs opacity-70">+0% from last month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-success" /> Base Pay
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₹{basePay.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Standard delivery rates</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <History className="h-4 w-4 text-indigo-500" /> Bonuses
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">₹{deliveryBonus.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Incentives and rewards</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <History className="h-5 w-5 text-accent" />
            Transaction History
          </CardTitle>
        </CardHeader>
        <CardContent>
          {!earnings || earnings.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No transactions found.
            </div>
          ) : (
            <div className="space-y-4">
              {earnings.map((e) => (
                <div key={e.id} className="flex items-center justify-between py-3 border-b last:border-0">
                  <div className="space-y-1">
                    <p className="font-medium capitalize">{e.earning_type.replace(/_/g, " ")}</p>
                    <p className="text-xs text-muted-foreground">
                      {new Date(e.calculated_at).toLocaleDateString()} {e.shipment ? `• Shipment ${e.shipment}` : ""}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="font-bold text-success flex items-center justify-end gap-1">
                      <ArrowUpRight className="h-3 w-3" />
                      ₹{parseFloat(e.amount).toLocaleString()}
                    </div>
                    <Badge variant="outline" className="text-[10px] uppercase">Completed</Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
