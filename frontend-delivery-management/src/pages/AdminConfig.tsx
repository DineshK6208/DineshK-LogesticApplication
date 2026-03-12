import React from 'react';
import { useDeliveryConfig, useUpdateDeliveryConfig } from '../hooks/useDeliveries';
import { 
  Settings, 
  ShieldCheck, 
  Bell, 
  Truck, 
  Save,
  AlertCircle,
  CheckCircle2
} from 'lucide-react';
import { cn } from '../lib/utils';

export default function AdminConfig() {
  const { data: config, isLoading } = useDeliveryConfig();
  const updateConfig = useUpdateDeliveryConfig();
  const [maxAttempts, setMaxAttempts] = React.useState(3);
  const [showSuccess, setShowSuccess] = React.useState(false);

  React.useEffect(() => {
    if (config) setMaxAttempts(config.max_delivery_attempts);
  }, [config]);

  const handleSave = async () => {
    try {
      await updateConfig.mutateAsync({ max_delivery_attempts: maxAttempts });
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (err) {
      console.error(err);
    }
  };

  if (isLoading) return <div className="animate-pulse h-64 bg-slate-100 rounded-2xl"></div>;

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">System Settings</h1>
        <p className="text-slate-500 mt-1">Configure global delivery parameters and rules</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Navigation Tabs */}
        <div className="space-y-2">
          {[
            { label: 'Delivery Rules', icon: Truck, active: true },
            { label: 'Security', icon: ShieldCheck, active: false },
            { label: 'Notifications', icon: Bell, active: false },
          ].map((item, i) => (
            <button
              key={i}
              className={cn(
                "w-full flex items-center gap-3 px-4 py-3 rounded-xl font-bold text-sm transition-all",
                item.active ? "bg-indigo-600 text-white shadow-lg shadow-indigo-100" : "text-slate-500 hover:bg-slate-100"
              )}
            >
              <item.icon size={18} />
              {item.label}
            </button>
          ))}
        </div>

        {/* Settings Content */}
        <div className="md:col-span-2 space-y-6">
          <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm space-y-8">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-slate-900">Delivery Rules</h2>
              {showSuccess && (
                <div className="flex items-center gap-2 text-emerald-600 text-sm font-bold animate-in fade-in slide-in-from-right-4">
                  <CheckCircle2 size={16} />
                  Settings saved
                </div>
              )}
            </div>

            <div className="space-y-6">
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <label className="font-bold text-slate-700">Max Delivery Attempts</label>
                  <span className="px-3 py-1 bg-slate-100 rounded-lg font-mono font-bold text-slate-900">{maxAttempts}</span>
                </div>
                <p className="text-sm text-slate-500">Number of times a driver can attempt delivery before the request is marked as failed.</p>
                <input 
                  type="range" 
                  min="1" 
                  max="10" 
                  value={maxAttempts}
                  onChange={(e) => setMaxAttempts(parseInt(e.target.value))}
                  className="w-full h-2 bg-slate-100 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
                <div className="flex justify-between text-xs text-slate-400 font-bold">
                  <span>1 ATTEMPT</span>
                  <span>10 ATTEMPTS</span>
                </div>
              </div>

              <div className="pt-6 border-t border-slate-100 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-bold text-slate-700">Auto-assign Drivers</p>
                    <p className="text-sm text-slate-500">Automatically assign the nearest driver to new requests.</p>
                  </div>
                  <div className="w-12 h-6 bg-indigo-600 rounded-full relative cursor-pointer">
                    <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full shadow-sm" />
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-bold text-slate-700">Require Proof of Delivery</p>
                    <p className="text-sm text-slate-500">Drivers must upload a photo or signature to complete delivery.</p>
                  </div>
                  <div className="w-12 h-6 bg-indigo-600 rounded-full relative cursor-pointer">
                    <div className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full shadow-sm" />
                  </div>
                </div>
              </div>
            </div>

            <div className="pt-8 flex justify-end">
              <button
                onClick={handleSave}
                disabled={updateConfig.isPending}
                className="inline-flex items-center gap-2 px-8 py-3 bg-slate-900 text-white rounded-xl font-bold shadow-lg shadow-slate-200 hover:bg-slate-800 transition-all active:scale-95 disabled:opacity-50"
              >
                <Save size={20} />
                {updateConfig.isPending ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>

          <div className="p-6 bg-indigo-50 border border-indigo-100 rounded-2xl flex items-start gap-4">
            <div className="p-2 bg-indigo-600 text-white rounded-lg">
              <AlertCircle size={20} />
            </div>
            <div>
              <p className="font-bold text-indigo-900">Pro Tip</p>
              <p className="text-sm text-indigo-700 leading-relaxed">
                Changes to delivery rules will only apply to new requests. Existing requests will follow the rules that were active at the time of creation.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
