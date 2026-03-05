import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { Loader2, Truck, Lock, Mail } from "lucide-react";
import { apiCall } from "@/lib/api";

export default function LoginPage() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState({ email: "", password: "" });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await fetch("/api/auth/login/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.detail || data.non_field_errors || "Invalid credentials");
            }

            // Store tokens and tenant ID
            localStorage.setItem("auth_token", data.tokens.access);
            localStorage.setItem("refresh_token", data.tokens.refresh);
            localStorage.setItem("tenant_id", data.user.tenant || "");
            localStorage.setItem("user_role", data.user.role);

            toast.success("Logged in successfully!");
            navigate("/");
        } catch (error: any) {
            toast.error(error.message || "Failed to login");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-muted/30 p-4">
            <Card className="w-full max-w-md shadow-lg border-accent/20">
                <CardHeader className="space-y-1 text-center">
                    <div className="flex justify-center mb-4">
                        <div className="p-3 bg-accent/10 rounded-full text-accent">
                            <Truck className="h-10 w-10" />
                        </div>
                    </div>
                    <CardTitle className="text-2xl font-bold">Driver Portal</CardTitle>
                    <CardDescription>Enter your credentials to access your dashboard</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium leading-none flex items-center gap-2">
                                <Mail className="h-4 w-4 text-muted-foreground" /> Email Address
                            </label>
                            <Input
                                type="email"
                                placeholder="driver@example.com"
                                value={formData.email}
                                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium leading-none flex items-center gap-2">
                                <Lock className="h-4 w-4 text-muted-foreground" /> Password
                            </label>
                            <Input
                                type="password"
                                placeholder="••••••••"
                                value={formData.password}
                                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                required
                            />
                        </div>
                        <Button
                            type="submit"
                            className="w-full bg-accent text-accent-foreground hover:bg-accent/90"
                            disabled={loading}
                        >
                            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : "Sign In"}
                        </Button>
                    </form>
                    <div className="mt-6 text-center text-xs text-muted-foreground">
                        Enterprise Logistics Platform v1.0
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
