import { apiCall } from "../api";

export interface DriverProfile {
  id: string;
  is_available: boolean;
  kyc_status: string;
  license_number: string;
}

export const availabilityApi = {
  getStatus: () =>
    apiCall<DriverProfile>("/drivers/me/"),

  toggleOnline: (isAvailable: boolean) =>
    apiCall<DriverProfile>("/drivers/me/availability/", {
      method: "PATCH",
      body: JSON.stringify({ is_available: isAvailable }),
    }),
};
