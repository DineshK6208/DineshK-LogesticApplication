import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useItemRequest, useProcessPayment } from '../hooks/useDeliveries';
import { 
  ArrowLeft, 
  CreditCard, 
  Wallet, 
  Truck, 
  CheckCircle2, 
  ShieldCheck,
  AlertCircle,
  Clock
} from 'lucide-react';
import { cn } from '../lib/utils';
import { PaymentMethod } from '../types/deliveries';

export default function PaymentPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: request, isLoading } = useItemRequest(Number(id));
  const processPayment = useProcessPayment();
  const [method, setMethod] = React.useState<PaymentMethod>('online');

  if (isLoading) return <div className="animate-pulse h-64 bg-slate-100 rounded-2xl"></div>;
  if (!request) return <div>Request not found</div>;

  const handlePayment = async () => {
    try {
      await processPayment.mutateAsync({
        id: request.id,
        payload: {
          payment_method: method,
          transaction_id: method === 'online' ? `txn_${Math.random().toString(36).substring(7)}` : undefined,
        }
      });
      navigate(`/request/${request.id}`);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8 flex items-center gap-4">
        <Link to={`/request/${id}`} className="p-2 hover:bg-slate-100 rounded-xl transition-colors">
          <ArrowLeft size={24} className="text-slate-600" />
        </Link>
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Checkout</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm space-y-4">
            <h2 className="text-lg font-bold text-slate-900">Select Payment Method</h2>
            <div className="space-y-3">
              {[
                { id: 'online', label: 'Online Payment', icon: CreditCard, desc: 'Credit/Debit Card, UPI' },
                { id: 'wallet', label: 'Swift Wallet', icon: Wallet, desc: 'Use your SwiftDrop balance' },
                { id: 'cod', label: 'Cash on Delivery', icon: Truck, desc: 'Pay when you receive' },
              ].map((item) => (
                <button
                  key={item.id}
                  onClick={() => setMethod(item.id as PaymentMethod)}
                  className={cn(
                    "w-full flex items-center gap-4 p-4 rounded-xl border-2 transition-all text-left",
                    method === item.id 
                      ? "border-indigo-600 bg-indigo-50/50" 
                      : "border-slate-100 hover:border-slate-200"
                  )}
                >
                  <div className={cn(
                    "p-2 rounded-lg",
                    method === item.id ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-500"
                  )}>
                    <item.icon size={20} />
                  </div>
                  <div className="flex-1">
                    <p className="font-bold text-slate-900">{item.label}</p>
                    <p className="text-xs text-slate-500">{item.desc}</p>
                  </div>
                  {method === item.id && <CheckCircle2 className="text-indigo-600" size={20} />}
                </button>
              ))}
            </div>
          </div>

          <div className="bg-indigo-900 p-6 rounded-2xl text-white shadow-xl shadow-indigo-200">
            <div className="flex items-center gap-3 mb-4">
              <ShieldCheck className="text-indigo-300" size={24} />
              <span className="font-bold">Secure Checkout</span>
            </div>
            <p className="text-indigo-100 text-sm leading-relaxed">
              Your payment information is encrypted and processed securely. We never store your card details.
            </p>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm space-y-6">
            <h2 className="text-lg font-bold text-slate-900">Order Summary</h2>
            <div className="space-y-3">
              <div className="flex justify-between text-slate-500">
                <span>Request #</span>
                <span className="font-medium text-slate-900">{request.request_number}</span>
              </div>
              <div className="flex justify-between text-slate-500">
                <span>Items Total</span>
                <span className="font-medium text-slate-900">${request.total_amount.toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-slate-500">
                <span>Delivery Fee</span>
                <span className="font-medium text-slate-900 text-emerald-600">FREE</span>
              </div>
              <div className="pt-4 border-t border-slate-100 flex justify-between items-center">
                <span className="text-lg font-bold text-slate-900">Total</span>
                <span className="text-2xl font-bold text-indigo-600">${request.total_amount.toFixed(2)}</span>
              </div>
            </div>

            <button
              onClick={handlePayment}
              disabled={processPayment.isPending}
              className="w-full py-4 bg-indigo-600 text-white rounded-xl font-bold shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition-all active:scale-95 disabled:opacity-50"
            >
              {processPayment.isPending ? 'Processing...' : `Pay $${request.total_amount.toFixed(2)}`}
            </button>

            <div className="flex items-center justify-center gap-2 text-slate-400 text-xs">
              <Clock size={14} />
              <span>Payment expires in 15:00</span>
            </div>
          </div>

          <div className="p-4 bg-amber-50 border border-amber-100 rounded-xl flex items-start gap-3">
            <AlertCircle className="text-amber-600 shrink-0" size={20} />
            <p className="text-xs text-amber-800">
              By clicking "Pay", you agree to SwiftDrop's Terms of Service and Refund Policy.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
