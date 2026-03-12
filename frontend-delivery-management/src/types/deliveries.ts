export type RequestStatus = 'pending_payment' | 'paid' | 'in_delivery' | 'delivered' | 'cancelled';
export type TrackingStatus = 'pending' | 'in_transit' | 'delivered';
export type AttemptStatus = 'success' | 'failed';
export type PaymentMethod = 'online' | 'cod' | 'wallet';

export interface Item {
  id?: number;
  name: string;
  description?: string;
  quantity: number;
  unit_price: number;
  line_total?: number;
}

export interface Receiver {
  receiver_name: string;
  contact_number: string;
  delivery_address: string;
  city: string;
  state: string;
  postal_code: string;
}

export interface Payment {
  id: number;
  payment_method: PaymentMethod;
  transaction_id?: string;
  amount: number;
  status: string;
  created_at: string;
}

export interface Tracking {
  id: number;
  status: TrackingStatus;
  current_location: string;
  last_updated: string;
  delivery_latitude?: number;
  delivery_longitude?: number;
}

export interface ItemRequest {
  id: number;
  request_number: string;
  status: RequestStatus;
  total_amount: number;
  notes: string;
  items: Item[];
  receiver: Receiver;
  payment?: Payment;
  tracking?: Tracking;
  created_at: string;
}

export interface CreateItemRequestPayload {
  notes: string;
  items: Item[];
  receiver: Receiver;
}

export interface PaymentPayload {
  payment_method: PaymentMethod;
  transaction_id?: string;
}

export interface TrackingUpdatePayload {
  status: TrackingStatus;
  current_location: string;
  delivery_latitude?: number;
  delivery_longitude?: number;
}

export interface DeliveryAttemptPayload {
  shipment: number;
  status: AttemptStatus;
  reason?: string;
  notes?: string;
}

export interface DeliveryConfig {
  max_delivery_attempts: number;
}
