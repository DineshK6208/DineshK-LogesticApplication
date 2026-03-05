import { apiCall } from "../api";

export type DeliveryStatusType =
  | "assigned"
  | "picked_up"
  | "in_transit"
  | "out_for_delivery"
  | "delivered"
  | "delivery_failed"
  | "rto";

export interface DeliveryStatusUpdate {
  shipment_id: string;
  status: DeliveryStatusType;
}

export const deliveryStatusApi = {
  update: (data: DeliveryStatusUpdate) =>
    apiCall<any>("/drivers/me/update-shipment-status/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};
