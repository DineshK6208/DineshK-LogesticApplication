import React from 'react';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { useCreateItemRequest } from '../hooks/useDeliveries';
import { useNavigate } from 'react-router-dom';
import { 
  Plus, 
  Trash2, 
  ArrowRight, 
  ArrowLeft, 
  Package, 
  User, 
  MapPin, 
  FileText,
  CheckCircle2
} from 'lucide-react';
import { cn } from '../lib/utils';
import { motion, AnimatePresence } from 'motion/react';

const schema = z.object({
  notes: z.string().min(5, 'Notes must be at least 5 characters'),
  items: z.array(z.object({
    name: z.string().min(2, 'Item name is required'),
    description: z.string().optional(),
    quantity: z.number().min(1, 'Quantity must be at least 1'),
    unit_price: z.number().min(0.01, 'Price must be greater than 0'),
  })).min(1, 'At least one item is required'),
  receiver: z.object({
    receiver_name: z.string().min(2, 'Receiver name is required'),
    contact_number: z.string().min(10, 'Valid contact number is required'),
    delivery_address: z.string().min(5, 'Address is required'),
    city: z.string().min(2, 'City is required'),
    state: z.string().min(2, 'State is required'),
    postal_code: z.string().min(5, 'Valid postal code is required'),
  }),
});

type FormValues = z.infer<typeof schema>;

const steps = [
  { id: 'items', title: 'Items', icon: Package },
  { id: 'receiver', title: 'Receiver', icon: User },
  { id: 'review', title: 'Review', icon: FileText },
];

export default function CreateRequest() {
  const [currentStep, setCurrentStep] = React.useState(0);
  const navigate = useNavigate();
  const createMutation = useCreateItemRequest();

  const { 
    register, 
    control, 
    handleSubmit, 
    watch,
    trigger,
    formState: { errors } 
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      items: [{ name: '', description: '', quantity: 1, unit_price: 0 }],
      receiver: { receiver_name: '', contact_number: '', delivery_address: '', city: '', state: '', postal_code: '' },
      notes: '',
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });

  const onSubmit = async (data: FormValues) => {
    try {
      const result = await createMutation.mutateAsync(data);
      navigate(`/request/${result.id}`);
    } catch (err) {
      console.error('Failed to create request', err);
    }
  };

  const nextStep = async () => {
    let fieldsToValidate: any[] = [];
    if (currentStep === 0) fieldsToValidate = ['items'];
    if (currentStep === 1) fieldsToValidate = ['receiver'];
    
    const isValid = await trigger(fieldsToValidate as any);
    if (isValid) setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
  };

  const prevStep = () => setCurrentStep(prev => Math.max(prev - 1, 0));

  const items = watch('items');
  const totalAmount = items.reduce((acc, item) => acc + (item.quantity * item.unit_price), 0);

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-12">
        <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Create Item Request</h1>
        <p className="text-slate-500 mt-2">Fill in the details to send a new delivery request</p>
      </div>

      {/* Stepper */}
      <div className="flex items-center justify-between mb-12 relative">
        <div className="absolute top-1/2 left-0 w-full h-0.5 bg-slate-100 -translate-y-1/2 z-0" />
        {steps.map((step, i) => {
          const Icon = step.icon;
          const isActive = i === currentStep;
          const isCompleted = i < currentStep;
          return (
            <div key={step.id} className="relative z-10 flex flex-col items-center gap-2">
              <div className={cn(
                "w-12 h-12 rounded-2xl flex items-center justify-center transition-all duration-300 border-2",
                isActive ? "bg-indigo-600 border-indigo-600 text-white shadow-lg shadow-indigo-200" : 
                isCompleted ? "bg-emerald-500 border-emerald-500 text-white" : 
                "bg-white border-slate-200 text-slate-400"
              )}>
                {isCompleted ? <CheckCircle2 size={24} /> : <Icon size={24} />}
              </div>
              <span className={cn(
                "text-xs font-bold uppercase tracking-wider",
                isActive ? "text-indigo-600" : "text-slate-400"
              )}>{step.title}</span>
            </div>
          );
        })}
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        <AnimatePresence mode="wait">
          {currentStep === 0 && (
            <motion.div
              key="step-items"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-slate-900">Items to Request</h2>
                  <button 
                    type="button"
                    onClick={() => append({ name: '', description: '', quantity: 1, unit_price: 0 })}
                    className="inline-flex items-center gap-2 text-sm font-bold text-indigo-600 hover:text-indigo-700"
                  >
                    <Plus size={18} />
                    Add Item
                  </button>
                </div>

                <div className="space-y-4">
                  {fields.map((field, index) => (
                    <div key={field.id} className="p-4 bg-slate-50 rounded-xl border border-slate-100 space-y-4 relative group">
                      {fields.length > 1 && (
                        <button 
                          type="button"
                          onClick={() => remove(index)}
                          className="absolute top-4 right-4 text-slate-400 hover:text-red-500 transition-colors"
                        >
                          <Trash2 size={18} />
                        </button>
                      )}
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-1.5">
                          <label className="text-sm font-semibold text-slate-700">Item Name</label>
                          <input 
                            {...register(`items.${index}.name`)}
                            className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"
                            placeholder="e.g. Laptop"
                          />
                          {errors.items?.[index]?.name && <p className="text-xs text-red-500">{errors.items[index]?.name?.message}</p>}
                        </div>
                        <div className="space-y-1.5">
                          <label className="text-sm font-semibold text-slate-700">Description</label>
                          <input 
                            {...register(`items.${index}.description`)}
                            className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"
                            placeholder="Optional"
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                        <div className="space-y-1.5">
                          <label className="text-sm font-semibold text-slate-700">Quantity</label>
                          <input 
                            type="number"
                            {...register(`items.${index}.quantity`, { valueAsNumber: true })}
                            className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"
                          />
                        </div>
                        <div className="space-y-1.5">
                          <label className="text-sm font-semibold text-slate-700">Unit Price ($)</label>
                          <input 
                            type="number"
                            step="0.01"
                            {...register(`items.${index}.unit_price`, { valueAsNumber: true })}
                            className="w-full px-4 py-2.5 bg-white border border-slate-200 rounded-lg focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"
                          />
                        </div>
                        <div className="hidden md:flex flex-col justify-end pb-2.5">
                          <span className="text-xs text-slate-400 font-medium uppercase tracking-wider">Line Total</span>
                          <span className="font-bold text-slate-900">
                            ${((watch(`items.${index}.quantity`) || 0) * (watch(`items.${index}.unit_price`) || 0)).toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="pt-6 border-t border-slate-100 flex justify-between items-center">
                  <span className="text-slate-500 font-medium">Total Amount</span>
                  <span className="text-2xl font-bold text-slate-900">${totalAmount.toFixed(2)}</span>
                </div>
              </div>
            </motion.div>
          )}

          {currentStep === 1 && (
            <motion.div
              key="step-receiver"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm space-y-6">
                <h2 className="text-xl font-bold text-slate-900 flex items-center gap-2">
                  <MapPin className="text-indigo-600" size={24} />
                  Delivery Details
                </h2>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-1.5">
                    <label className="text-sm font-semibold text-slate-700">Receiver Name</label>
                    <input 
                      {...register('receiver.receiver_name')}
                      className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"
                    />
                    {errors.receiver?.receiver_name && <p className="text-xs text-red-500">{errors.receiver.receiver_name.message}</p>}
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-semibold text-slate-700">Contact Number</label>
                    <input 
                      {...register('receiver.contact_number')}
                      className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all"
                    />
                    {errors.receiver?.contact_number && <p className="text-xs text-red-500">{errors.receiver.contact_number.message}</p>}
                  </div>
                </div>

                <div className="space-y-1.5">
                  <label className="text-sm font-semibold text-slate-700">Delivery Address</label>
                  <textarea 
                    {...register('receiver.delivery_address')}
                    rows={3}
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all resize-none"
                  />
                  {errors.receiver?.delivery_address && <p className="text-xs text-red-500">{errors.receiver.delivery_address.message}</p>}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="space-y-1.5">
                    <label className="text-sm font-semibold text-slate-700">City</label>
                    <input {...register('receiver.city')} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all" />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-semibold text-slate-700">State</label>
                    <input {...register('receiver.state')} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all" />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-sm font-semibold text-slate-700">Postal Code</label>
                    <input {...register('receiver.postal_code')} className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all" />
                  </div>
                </div>

                <div className="space-y-1.5 pt-4">
                  <label className="text-sm font-semibold text-slate-700">Special Instructions / Notes</label>
                  <textarea 
                    {...register('notes')}
                    rows={2}
                    className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 outline-none transition-all resize-none"
                    placeholder="e.g. Leave at the front door"
                  />
                </div>
              </div>
            </motion.div>
          )}

          {currentStep === 2 && (
            <motion.div
              key="step-review"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              className="space-y-6"
            >
              <div className="bg-white p-8 rounded-2xl border border-slate-100 shadow-sm space-y-8">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-slate-900">Review Request</h2>
                  <span className="px-4 py-1.5 bg-indigo-50 text-indigo-700 rounded-full text-sm font-bold">
                    Total: ${totalAmount.toFixed(2)}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-4">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Receiver</h3>
                    <div className="space-y-1">
                      <p className="font-bold text-slate-900">{watch('receiver.receiver_name')}</p>
                      <p className="text-slate-600">{watch('receiver.contact_number')}</p>
                      <p className="text-slate-600 text-sm mt-2">
                        {watch('receiver.delivery_address')}, {watch('receiver.city')}, {watch('receiver.state')} {watch('receiver.postal_code')}
                      </p>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Notes</h3>
                    <p className="text-slate-600 italic">"{watch('notes') || 'No special instructions provided'}"</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Items</h3>
                  <div className="divide-y divide-slate-100">
                    {watch('items').map((item, i) => (
                      <div key={i} className="py-3 flex justify-between items-center">
                        <div>
                          <p className="font-bold text-slate-900">{item.name}</p>
                          <p className="text-xs text-slate-500">Qty: {item.quantity} × ${item.unit_price.toFixed(2)}</p>
                        </div>
                        <span className="font-bold text-slate-700">${(item.quantity * item.unit_price).toFixed(2)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between pt-8">
          <button
            type="button"
            onClick={prevStep}
            disabled={currentStep === 0}
            className={cn(
              "inline-flex items-center gap-2 px-6 py-3 rounded-xl font-bold transition-all",
              currentStep === 0 ? "opacity-0 pointer-events-none" : "text-slate-600 hover:bg-slate-100"
            )}
          >
            <ArrowLeft size={20} />
            Back
          </button>

          {currentStep === steps.length - 1 ? (
            <button
              type="submit"
              disabled={createMutation.isPending}
              className="inline-flex items-center gap-2 px-8 py-3 bg-indigo-600 text-white rounded-xl font-bold shadow-lg shadow-indigo-200 hover:bg-indigo-700 transition-all active:scale-95 disabled:opacity-50"
            >
              {createMutation.isPending ? 'Creating...' : 'Submit Request'}
              <CheckCircle2 size={20} />
            </button>
          ) : (
            <button
              type="button"
              onClick={nextStep}
              className="inline-flex items-center gap-2 px-8 py-3 bg-slate-900 text-white rounded-xl font-bold shadow-lg shadow-slate-200 hover:bg-slate-800 transition-all active:scale-95"
            >
              Next Step
              <ArrowRight size={20} />
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
