import type {
  Telemetry,
  AIRecommendation,
  AutoControlResponse,
} from "../types/api";

const API_BASE =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";

const API_KEY =
  import.meta.env.VITE_API_KEY ||
  "dev-token-change-me";

const headers = {
  "Content-Type": "application/json",
  "x-api-key": API_KEY,
};

async function request<T>(
  url: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(
    `${API_BASE}${url}`,
    {
      ...options,
      headers: {
        ...headers,
        ...(options.headers || {}),
      },
    },
  );

  if (!response.ok) {
    const text = await response.text();

    throw new Error(
      `API ${response.status}: ${text}`,
    );
  }

  return response.json();
}


/* =========================================================
   LATEST TELEMETRY
========================================================= */

export async function getLatestTelemetry(
  deviceId = "VAYU-001",
): Promise<Telemetry> {
  return request<Telemetry>(
    `/telemetry/latest?device_id=${encodeURIComponent(
      deviceId,
    )}`,
  );
}


/* =========================================================
   AI PREDICTION
========================================================= */

export async function getAIPrediction(
  deviceId = "VAYU-001",
): Promise<AIRecommendation> {
  return request<AIRecommendation>(
    `/ai/prediction?device_id=${encodeURIComponent(
      deviceId,
    )}`,
  );
}


/* =========================================================
   AI AUTO CONTROL
========================================================= */

export async function runAutoControl(
  deviceId = "VAYU-001",
): Promise<AutoControlResponse> {
  return request<AutoControlResponse>(
    "/control/auto",
    {
      method: "POST",

      body: JSON.stringify({
        device_id: deviceId,
      }),
    },
  );
}


/* =========================================================
   MANUAL CONTROL
========================================================= */

export async function sendManualControl(
  deviceId: string,
  flap1: number,
  flap2: number,
  flap3: number,
): Promise<unknown> {
  return request(
    "/control/command",
    {
      method: "POST",

      body: JSON.stringify({
        device_id: deviceId,

        flap_angle_1: flap1,
        flap_angle_2: flap2,
        flap_angle_3: flap3,

        source: "manual",
      }),
    },
  );
}


/* =========================================================
   HEALTH CHECK
========================================================= */

export async function checkBackendHealth(): Promise<boolean> {
  try {
    await request("/health");
    return true;
  } catch {
    return false;
  }
}


export { API_BASE };