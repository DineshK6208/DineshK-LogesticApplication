import axios from 'axios';
import { 
  ItemRequest, 
  CreateItemRequestPayload, 
  PaymentPayload, 
  Tracking, 
  TrackingUpdatePayload, 
  DeliveryAttemptPayload, 
  DeliveryConfig 
} from '../types/deliveries';

// In a real app, this would be an environment variable
const API_BASE_URL = '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const deliveryApi = {
  // Item Requests
  getItemRequests: async (): Promise<ItemRequest[]> => {
    const response = await api.get('/item-requests/');
    return response.data;
  },
  
  getItemRequest: async (id: number): Promise<ItemRequest> => {
    const response = await api.get(`/item-requests/${id}/`);
    return response.data;
  },
  
  createItemRequest: async (payload: CreateItemRequestPayload): Promise<ItemRequest> => {
    const response = await api.post('/item-requests/', payload);
    return response.data;
  },
  
  // Payment
  processPayment: async (id: number, payload: PaymentPayload): Promise<any> => {
    const response = await api.post(`/item-requests/${id}/pay/`, payload);
    return response.data;
  },
  
  // Tracking
  getTracking: async (id: number): Promise<Tracking> => {
    const response = await api.get(`/item-requests/${id}/tracking/`);
    return response.data;
  },
  
  updateTracking: async (id: number, payload: TrackingUpdatePayload): Promise<Tracking> => {
    const response = await api.patch(`/item-requests/${id}/tracking/`, payload);
    return response.data;
  },
  
  // Attempts
  createAttempt: async (payload: DeliveryAttemptPayload): Promise<any> => {
    const response = await api.post('/attempts/', payload);
    return response.data;
  },
  
  uploadProof: async (attemptId: number, formData: FormData): Promise<any> => {
    const response = await api.patch(`/attempts/${attemptId}/upload-proof/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },
  
  // Config
  getDeliveryConfig: async (): Promise<DeliveryConfig> => {
    const response = await api.get('/delivery-config/');
    return response.data;
  },
  
  updateDeliveryConfig: async (payload: DeliveryConfig): Promise<DeliveryConfig> => {
    const response = await api.put('/delivery-config/', payload);
    return response.data;
  },
};
