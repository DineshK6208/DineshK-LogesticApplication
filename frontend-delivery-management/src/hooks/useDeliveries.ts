import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { deliveryApi } from '../api/deliveries';
import { 
  CreateItemRequestPayload, 
  PaymentPayload, 
  TrackingUpdatePayload, 
  DeliveryAttemptPayload, 
  DeliveryConfig 
} from '../types/deliveries';

export const useItemRequests = () => {
  return useQuery({
    queryKey: ['itemRequests'],
    queryFn: deliveryApi.getItemRequests,
  });
};

export const useItemRequest = (id: number) => {
  return useQuery({
    queryKey: ['itemRequest', id],
    queryFn: () => deliveryApi.getItemRequest(id),
    enabled: !!id,
  });
};

export const useCreateItemRequest = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateItemRequestPayload) => deliveryApi.createItemRequest(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['itemRequests'] });
    },
  });
};

export const useProcessPayment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: PaymentPayload }) => 
      deliveryApi.processPayment(id, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['itemRequest', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['itemRequests'] });
    },
  });
};

export const useTracking = (id: number) => {
  return useQuery({
    queryKey: ['tracking', id],
    queryFn: () => deliveryApi.getTracking(id),
    enabled: !!id,
  });
};

export const useUpdateTracking = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, payload }: { id: number; payload: TrackingUpdatePayload }) => 
      deliveryApi.updateTracking(id, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['tracking', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['itemRequest', variables.id] });
    },
  });
};

export const useCreateAttempt = () => {
  return useMutation({
    mutationFn: (payload: DeliveryAttemptPayload) => deliveryApi.createAttempt(payload),
  });
};

export const useUploadProof = () => {
  return useMutation({
    mutationFn: ({ attemptId, formData }: { attemptId: number; formData: FormData }) => 
      deliveryApi.uploadProof(attemptId, formData),
  });
};

export const useDeliveryConfig = () => {
  return useQuery({
    queryKey: ['deliveryConfig'],
    queryFn: deliveryApi.getDeliveryConfig,
  });
};

export const useUpdateDeliveryConfig = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: DeliveryConfig) => deliveryApi.updateDeliveryConfig(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deliveryConfig'] });
    },
  });
};
