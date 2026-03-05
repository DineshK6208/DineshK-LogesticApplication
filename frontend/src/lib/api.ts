// Central API configuration
const API_BASE = "/api";

async function apiCall<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem("auth_token");
  const tenantId = localStorage.getItem("tenant_id");

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((options?.headers as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (tenantId) {
    headers["X-Tenant-ID"] = tenantId;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    if (res.status === 401) {
      localStorage.removeItem("auth_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("tenant_id");
      localStorage.removeItem("user_role");
      window.location.href = "/login";
    }

    // Attempt to extract detail from various common error formats
    let errorMessage = "API request failed";
    try {
      const errorData = await res.json();
      errorMessage = errorData.detail || errorData.error || errorData.message ||
        (errorData.non_field_errors && errorData.non_field_errors[0]) ||
        JSON.stringify(errorData);
    } catch (e) {
      errorMessage = res.statusText || `Error ${res.status}`;
    }

    throw new Error(errorMessage);
  }
  return res.json();
}

export { apiCall, API_BASE };
