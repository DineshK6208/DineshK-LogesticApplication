import React from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useItemRequest, useUpdateTracking, useCreateAttempt, useUploadProof } from '../hooks/useDeliveries';
import { 
  ArrowLeft, 
  Package, 
  MapPin, 
  Truck, 
  CheckCircle2, 
  Clock, 
  CreditCard, 
  AlertCircle,
  Phone,
  User,
  History,
  Camera,
  Signature
} from 'lucide-react';
import { cn } from '../lib/utils';
import { format } from 'date-fns';
import { motion } from 'motion/react';

export default function RequestDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: request, isLoading, error } = useItemRequest(Number(id));
  const updateTracking = useUpdateTracking();
  const [isDriverMode, setIsDriverMode] = React.useState(false);

  if (isLoading) return <div className="animate-pulse space-y-8">
    <div className="h-12 bg-slate-200 rounded-xl w-1/3"></div>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      <div className="h-64 bg-slate-200 rounded-2xl md:col-span-2"></div>
      <div className="h-64 bg-slate-200 rounded-2xl"></div>
    </div>
  </div>;

  if (error || !request) return (
    <div className="p-8 bg-red-50 border border-red-100 rounded-2xl text-red-700">
      <p>Request not found.</p>
      <Link to="/" className="text-indigo-600 font-bold mt-4 inline-block">Back to Dashboard</Link>
    </div>
  );

  const handleStatusUpdate = async (status: 'pending' | 'in_transit' | 'delivered') => {
    try {
      await updateTracking.mutateAsync({
        id: request.id,
        payload: {
          status,
          current_location: status === 'delivered' ? 'Delivered to receiver' : 'In transit',
          delivery_latitude: 40.7128, // Mock coordinates
          delivery_longitude: -74.0060,
        }
      });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <Link to="/" className="p-2 hover:bg-slate-100 rounded-xl transition-colors">
            <ArrowLeft size={24} className="text-slate-600" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Request #{request.request_number}</h1>
            <p className="text-slate-500">Created on {format(new Date(request.created_at), 'MMMM dd, yyyy')}</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setIsDriverMode(!isDriverMode)}
            className={cn(
              "px-6 py-2.5 rounded-xl font-bold transition-all",
              isDriverMode ? "bg-indigo-600 text-white" : "bg-white border border-slate-200 text-slate-700"
            )}
          >
            {isDriverMode ? 'Exit Driver Mode' : 'Driver Controls'}
          </button>
          {request.status === 'pending_payment' && (
            <Link 
              to={`/payment/${request.id}`}
              className="px-6 py-2.5 bg-emerald-600 text-white rounded-xl font-bold shadow-lg shadow-emerald-200 hover:bg-emerald-700 transition-all"
            >
              Pay Now
            </Link>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Details & Items */}
        <div className="lg:col-span-2 space-y-8">
          {/* Tracking Timeline */}
          <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm">
            <h2 className="text-xl font-bold text-slate-900 mb-8 flex items-center gap-2">
              <Truck className="text-indigo-600" size={24} />
              Delivery Tracking
            </h2>
            
            <div className="relative">
              <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-100" />
              <div className="space-y-10">
                {[
                  { label: 'Delivered', status: 'delivered', icon: CheckCircle2, time: request.tracking?.status === 'delivered' ? request.tracking.last_updated : null },
                  { label: 'In Transit', status: 'in_transit', icon: Truck, time: request.tracking?.status === 'in_transit' || request.tracking?.status === 'delivered' ? request.tracking.last_updated : null },
                  { label: 'Order Placed', status: 'pending', icon: Clock, time: request.created_at },
                ].map((step, i) => {
                  const isCompleted = !!step.time;
                  const Icon = step.icon;
                  return (
                    <div key={i} className="relative flex items-start gap-8 pl-10">
                      <div className={cn(
                        "absolute left-0 w-8 h-8 rounded-full flex items-center justify-center z-10 border-4 border-white",
                        isCompleted ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-400"
                      )}>
                        <Icon size={14} />
                      </div>
                      <div className="flex-1">
                        <p className={cn("font-bold", isCompleted ? "text-slate-900" : "text-slate-400")}>{step.label}</p>
                        {step.time && <p className="text-sm text-slate-500">{format(new Date(step.time), 'MMM dd, HH:mm')}</p>}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {isDriverMode && request.status !== 'delivered' && (
              <div className="mt-12 p-6 bg-slate-50 rounded-2xl border border-slate-200">
                <h3 className="font-bold text-slate-900 mb-4">Driver Actions</h3>
                <div className="flex flex-wrap gap-4">
                  <button 
                    onClick={() => handleStatusUpdate('in_transit')}
                    className="px-6 py-2 bg-indigo-600 text-white rounded-xl text-sm font-bold shadow-md shadow-indigo-100"
                  >
                    Start Delivery
                  </button>
                  <button 
                    onClick={() => handleStatusUpdate('delivered')}
                    className="px-6 py-2 bg-emerald-600 text-white rounded-xl text-sm font-bold shadow-md shadow-emerald-100"
                  >
                    Mark as Delivered
                  </button>
                  <Link 
                    to={`/attempt/${request.id}`}
                    className="px-6 py-2 bg-white border border-slate-200 text-slate-700 rounded-xl text-sm font-bold"
                  >
                    Log Attempt
                  </Link>
                </div>
              </div>
            )}
          </div>

          {/* Items List */}
          <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm">
            <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
              <Package className="text-indigo-600" size={24} />
              Items Requested
            </h2>
            <div className="divide-y divide-slate-100">
              {request.items.map((item, i) => (
                <div key={i} className="py-4 flex justify-between items-center">
                  <div>
                    <p className="font-bold text-slate-900">{item.name}</p>
                    <p className="text-sm text-slate-500">{item.description}</p>
                    <p className="text-xs text-slate-400 mt-1">Qty: {item.quantity} × ${item.unit_price.toFixed(2)}</p>
                  </div>
                  <span className="font-bold text-slate-900">${(item.quantity * item.unit_price).toFixed(2)}</span>
                </div>
              ))}
            </div>
            <div className="mt-6 pt-6 border-t border-slate-100 flex justify-between items-center">
              <span className="text-slate-500 font-bold">Total Amount</span>
              <span className="text-2xl font-bold text-indigo-600">${request.total_amount.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {/* Right Column: Receiver & Payment */}
        <div className="space-y-8">
          {/* Receiver Info */}
          <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm">
            <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
              <User className="text-indigo-600" size={24} />
              Receiver
            </h2>
            <div className="space-y-6">
              <div className="flex items-start gap-4">
                <div className="p-2 bg-slate-50 rounded-lg text-slate-400">
                  <User size={20} />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Name</p>
                  <p className="font-bold text-slate-900">{request.receiver.receiver_name}</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="p-2 bg-slate-50 rounded-lg text-slate-400">
                  <Phone size={20} />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Contact</p>
                  <p className="font-bold text-slate-900">{request.receiver.contact_number}</p>
                </div>
              </div>
              <div className="flex items-start gap-4">
                <div className="p-2 bg-slate-50 rounded-lg text-slate-400">
                  <MapPin size={20} />
                </div>
                <div>
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Address</p>
                  <p className="font-bold text-slate-900 leading-tight">
                    {request.receiver.delivery_address}<br />
                    {request.receiver.city}, {request.receiver.state} {request.receiver.postal_code}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Payment Info */}
          <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm">
            <h2 className="text-xl font-bold text-slate-900 mb-6 flex items-center gap-2">
              <CreditCard className="text-indigo-600" size={24} />
              Payment
            </h2>
            {request.payment ? (
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">Method</span>
                  <span className="font-bold text-slate-900 uppercase">{request.payment.payment_method}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-500">Status</span>
                  <span className="px-3 py-1 bg-emerald-100 text-emerald-700 rounded-full text-xs font-bold">
                    {request.payment.status}
                  </span>
                </div>
                {request.payment.transaction_id && (
                  <div className="pt-4 border-t border-slate-100">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-wider">Transaction ID</p>
                    <p className="text-sm font-mono text-slate-600 break-all">{request.payment.transaction_id}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-4">
                <div className="w-12 h-12 bg-amber-50 rounded-full flex items-center justify-center text-amber-600 mx-auto mb-3">
                  <AlertCircle size={24} />
                </div>
                <p className="text-slate-500 text-sm">No payment information available yet.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
