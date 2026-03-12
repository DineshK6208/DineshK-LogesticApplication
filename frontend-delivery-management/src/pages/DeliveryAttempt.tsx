import React from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useItemRequest, useCreateAttempt, useUploadProof } from '../hooks/useDeliveries';
import { 
  ArrowLeft, 
  Camera, 
  Signature, 
  CheckCircle2, 
  XCircle, 
  AlertCircle,
  FileText,
  Upload
} from 'lucide-react';
import { cn } from '../lib/utils';

export default function DeliveryAttempt() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { data: request, isLoading } = useItemRequest(Number(id));
  const createAttempt = useCreateAttempt();
  const uploadProof = useUploadProof();

  const [status, setStatus] = React.useState<'success' | 'failed'>('success');
  const [reason, setReason] = React.useState('');
  const [notes, setNotes] = React.useState('');
  const [proofImage, setProofImage] = React.useState<File | null>(null);
  const [signature, setSignature] = React.useState<File | null>(null);

  if (isLoading) return <div className="animate-pulse h-64 bg-slate-100 rounded-2xl"></div>;
  if (!request) return <div>Request not found</div>;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const attempt = await createAttempt.mutateAsync({
        shipment: request.id,
        status,
        reason: status === 'failed' ? reason : undefined,
        notes,
      });

      if (proofImage || signature) {
        const formData = new FormData();
        if (proofImage) formData.append('proof_image', proofImage);
        if (signature) formData.append('signature', signature);
        await uploadProof.mutateAsync({ attemptId: attempt.id, formData });
      }

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
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Log Delivery Attempt</h1>
          <p className="text-slate-500">For Request #{request.request_number}</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm space-y-8">
          {/* Status Selection */}
          <div className="space-y-4">
            <label className="text-sm font-bold text-slate-700 uppercase tracking-wider">Attempt Status</label>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setStatus('success')}
                className={cn(
                  "flex items-center justify-center gap-3 p-4 rounded-xl border-2 transition-all font-bold",
                  status === 'success' 
                    ? "border-emerald-600 bg-emerald-50 text-emerald-700" 
                    : "border-slate-100 text-slate-400 hover:border-slate-200"
                )}
              >
                <CheckCircle2 size={20} />
                Successful
              </button>
              <button
                type="button"
                onClick={() => setStatus('failed')}
                className={cn(
                  "flex items-center justify-center gap-3 p-4 rounded-xl border-2 transition-all font-bold",
                  status === 'failed' 
                    ? "border-red-600 bg-red-50 text-red-700" 
                    : "border-slate-100 text-slate-400 hover:border-slate-200"
                )}
              >
                <XCircle size={20} />
                Failed
              </button>
            </div>
          </div>

          {status === 'failed' && (
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700 uppercase tracking-wider">Reason for Failure</label>
              <select 
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-red-500/20 focus:border-red-500 outline-none transition-all"
                required
              >
                <option value="">Select a reason...</option>
                <option value="Customer not available">Customer not available</option>
                <option value="Incorrect address">Incorrect address</option>
                <option value="Access denied">Access denied (Gated community/Building)</option>
                <option value="Customer refused delivery">Customer refused delivery</option>
                <option value="Other">Other</option>
              </select>
            </div>
          )}

          <div className="space-y-2">
            <label className="text-sm font-bold text-slate-700 uppercase tracking-wider">Notes</label>
            <textarea 
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all resize-none"
              placeholder="Add any additional details about the attempt..."
            />
          </div>

          {/* Proof Uploads */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4">
            <div className="space-y-3">
              <label className="text-sm font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
                <Camera size={16} />
                Proof Image
              </label>
              <div className="relative">
                <input 
                  type="file" 
                  accept="image/*"
                  onChange={(e) => setProofImage(e.target.files?.[0] || null)}
                  className="hidden" 
                  id="proof-image"
                />
                <label 
                  htmlFor="proof-image"
                  className={cn(
                    "flex flex-col items-center justify-center gap-2 p-6 border-2 border-dashed rounded-2xl cursor-pointer transition-all",
                    proofImage ? "border-emerald-500 bg-emerald-50" : "border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/30"
                  )}
                >
                  {proofImage ? (
                    <>
                      <CheckCircle2 className="text-emerald-500" size={32} />
                      <span className="text-xs font-bold text-emerald-700 truncate max-w-full px-2">{proofImage.name}</span>
                    </>
                  ) : (
                    <>
                      <Upload className="text-slate-400" size={32} />
                      <span className="text-xs font-bold text-slate-500">Upload Photo</span>
                    </>
                  )}
                </label>
              </div>
            </div>

            <div className="space-y-3">
              <label className="text-sm font-bold text-slate-700 uppercase tracking-wider flex items-center gap-2">
                <Signature size={16} />
                Signature
              </label>
              <div className="relative">
                <input 
                  type="file" 
                  accept="image/*"
                  onChange={(e) => setSignature(e.target.files?.[0] || null)}
                  className="hidden" 
                  id="signature-image"
                />
                <label 
                  htmlFor="signature-image"
                  className={cn(
                    "flex flex-col items-center justify-center gap-2 p-6 border-2 border-dashed rounded-2xl cursor-pointer transition-all",
                    signature ? "border-emerald-500 bg-emerald-50" : "border-slate-200 hover:border-indigo-400 hover:bg-indigo-50/30"
                  )}
                >
                  {signature ? (
                    <>
                      <CheckCircle2 className="text-emerald-500" size={32} />
                      <span className="text-xs font-bold text-emerald-700 truncate max-w-full px-2">{signature.name}</span>
                    </>
                  ) : (
                    <>
                      <FileText className="text-slate-400" size={32} />
                      <span className="text-xs font-bold text-slate-500">Upload Signature</span>
                    </>
                  )}
                </label>
              </div>
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end gap-4">
          <Link to={`/request/${id}`} className="px-6 py-3 text-slate-600 font-bold hover:bg-slate-100 rounded-xl transition-all">
            Cancel
          </Link>
          <button
            type="submit"
            disabled={createAttempt.isPending}
            className="px-10 py-3 bg-slate-900 text-white rounded-xl font-bold shadow-lg shadow-slate-200 hover:bg-slate-800 transition-all active:scale-95 disabled:opacity-50"
          >
            {createAttempt.isPending ? 'Saving...' : 'Save Attempt'}
          </button>
        </div>
      </form>
    </div>
  );
}
