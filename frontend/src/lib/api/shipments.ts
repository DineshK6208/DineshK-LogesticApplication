import { apiCall } from "../api";

export interface Shipment {
  id: string;
  tracking_number: string;
  status: string;
  origin_address: string;
  destination_address: string;
  customer_name?: string;
  customer_phone?: string;
  estimated_delivery_at?: string;
  weight?: string;
}

export const shipmentsApi = {
  getAssigned: () =>
    apiCall<Shipment[]>("/drivers/me/assigned-shipments/"),
};
