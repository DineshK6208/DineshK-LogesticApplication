import React from 'react';
import { useItemRequests } from '../hooks/useDeliveries';
import { Link } from 'react-router-dom';
import { 
  Search, 
  Filter, 
  Plus, 
  ChevronRight, 
  Package, 
  Clock, 
  CheckCircle2, 
  Truck, 
  AlertCircle,
  CreditCard
} from 'lucide-react';
import { cn } from '../lib/utils';
import { format } from 'date-fns';
import { RequestStatus } from '../types/deliveries';

const statusConfig: Record<RequestStatus, { label: string; color: string; icon: any }> = {
  pending_payment: { label: 'Pending Payment', color: 'bg-amber-100 text-amber-700 border-amber-200', icon: CreditCard },
  paid: { label: 'Paid', color: 'bg-blue-100 text-blue-700 border-blue-200', icon: CheckCircle2 },
  in_delivery: { label: 'In Delivery', color: 'bg-indigo-100 text-indigo-700 border-indigo-200', icon: Truck },
  delivered: { label: 'Delivered', color: 'bg-emerald-100 text-emerald-700 border-emerald-200', icon: CheckCircle2 },
  cancelled: { label: 'Cancelled', color: 'bg-slate-100 text-slate-700 border-slate-200', icon: AlertCircle },
};

export default function Dashboard() {
  const { data: requests, isLoading, error } = useItemRequests();
  const [searchQuery, setSearchQuery] = React.useState('');

  const filteredRequests = requests?.filter(req => 
    req.request_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
    req.receiver.receiver_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
    </div>
  );

  if (error) return (
    <div className="p-8 bg-red-50 border border-red-100 rounded-2xl text-red-700 flex items-center gap-3">
      <AlertCircle />
      <p>Failed to load requests. Please try again later.</p>
    </div>
  );

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Deliveries</h1>
          <p className="text-slate-500 mt-1">Manage and track your item requests</p>
        </div>
        <Link 
          to="/create" 
          className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-indigo-600 text-white rounded-xl font-semibold shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition-all active:scale-95"
        >
          <Plus size={20} />
          Create Request
        </Link>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: 'Total Requests', value: requests?.length || 0, icon: Package, color: 'text-blue-600', bg: 'bg-blue-50' },
          { label: 'In Delivery', value: requests?.filter(r => r.status === 'in_delivery').length || 0, icon: Truck, color: 'text-indigo-600', bg: 'bg-indigo-50' },
          { label: 'Pending Payment', value: requests?.filter(r => r.status === 'pending_payment').length || 0, icon: Clock, color: 'text-amber-600', bg: 'bg-amber-50' },
          { label: 'Delivered', value: requests?.filter(r => r.status === 'delivered').length || 0, icon: CheckCircle2, color: 'text-emerald-600', bg: 'bg-emerald-50' },
        ].map((stat, i) => (
          <div key={i} className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
            <div className="flex items-center justify-between">
              <div className={cn("p-3 rounded-xl", stat.bg)}>
                <stat.icon className={stat.color} size={24} />
              </div>
              <span className="text-2xl font-bold text-slate-900">{stat.value}</span>
            </div>
            <p className="text-slate-500 text-sm mt-4 font-medium">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Search & Filter */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400" size={20} />
          <input 
            type="text" 
            placeholder="Search by request # or receiver name..."
            className="w-full pl-12 pr-4 py-3 bg-white border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <button className="inline-flex items-center gap-2 px-6 py-3 bg-white border border-slate-200 rounded-xl text-slate-700 font-medium hover:bg-slate-50 transition-colors">
          <Filter size={20} />
          Filter
        </button>
      </div>

      {/* Requests Table/List */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/50 border-b border-slate-100">
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Request Details</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Receiver</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider text-right">Amount</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {filteredRequests?.map((request) => {
                const status = statusConfig[request.status];
                const StatusIcon = status.icon;
                return (
                  <tr key={request.id} className="hover:bg-slate-50/50 transition-colors group">
                    <td className="px-6 py-5">
                      <div className="flex flex-col">
                        <span className="font-bold text-slate-900">#{request.request_number}</span>
                        <span className="text-xs text-slate-400 mt-1">
                          {format(new Date(request.created_at), 'MMM dd, yyyy • HH:mm')}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-5">
                      <div className="flex flex-col">
                        <span className="text-slate-700 font-medium">{request.receiver.receiver_name}</span>
                        <span className="text-xs text-slate-400">{request.receiver.city}, {request.receiver.state}</span>
                      </div>
                    </td>
                    <td className="px-6 py-5">
                      <span className={cn(
                        "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border",
                        status.color
                      )}>
                        <StatusIcon size={14} />
                        {status.label}
                      </span>
                    </td>
                    <td className="px-6 py-5 text-right">
                      <span className="font-bold text-slate-900">
                        ${request.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </span>
                    </td>
                    <td className="px-6 py-5 text-right">
                      <Link 
                        to={`/request/${request.id}`}
                        className="inline-flex items-center justify-center w-10 h-10 rounded-xl text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-all"
                      >
                        <ChevronRight size={20} />
                      </Link>
                    </td>
                  </tr>
                );
              })}
              {filteredRequests?.length === 0 && (
                <tr>
                  <td colSpan={5} className="px-6 py-12 text-center text-slate-500">
                    No requests found matching your search.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
