import { apiCall } from "../api";

export interface CreateAttemptPayload {
  shipment_id: string;
  status: "success" | "failed";
  reason?: string;
  notes?: string;
}

export const deliveryAttemptsApi = {
  create: (data: CreateAttemptPayload) =>
    apiCall<any>("/drivers/me/record-attempt/", {
      method: "POST",
      body: JSON.stringify(data),
    }),
};
