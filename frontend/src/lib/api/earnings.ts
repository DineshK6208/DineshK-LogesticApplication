import { apiCall } from "../api";

export interface Earning {
  id: string;
  amount: string;
  earning_type: string;
  calculated_at: string;
  shipment?: string;
}

export const earningsApi = {
  getAll: () =>
    apiCall<Earning[]>("/drivers/me/earnings/"),
};
