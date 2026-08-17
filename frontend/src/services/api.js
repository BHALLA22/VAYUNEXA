const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";

const API_KEY =
  import.meta.env.VITE_API_KEY ||
  "dev-token-change-me";

async function request(endpoint, options = {}) {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      "x-api-key": API_KEY,
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      `API ${response.status}: ${errorText}`,
    );
  }

  return response.json();
}

// Latest telemetry
export async function getLatestTelemetry(
  deviceId = "VAYU-001",
) {
  return request(
    `/telemetry/latest?device_id=${encodeURIComponent(deviceId)}`,
  );
}

// AI prediction
export async function getAIPrediction(
  deviceId = "VAYU-001",
) {
  return request(
    `/ai/prediction?device_id=${encodeURIComponent(deviceId)}`,
  );
}

// Automatic flap control
export async function getAutoControl(
  deviceId = "VAYU-001",
) {
  return request("/control/auto", {
    method: "POST",
    body: JSON.stringify({
      device_id: deviceId,
    }),
  });
}

// Manual flap control
export async function sendManualControl(
  deviceId,
  flap1,
  flap2,
  flap3,
) {
  return request("/control/command", {
    method: "POST",
    body: JSON.stringify({
      device_id: deviceId,
      flap_angle_1: flap1,
      flap_angle_2: flap2,
      flap_angle_3: flap3,
      source: "manual",
    }),
  });
}

// Today's energy
export async function getTodayEnergy(
  deviceId = "VAYU-001",
) {
  return request(
    `/energy/today?device_id=${encodeURIComponent(deviceId)}`,
  );
}

// Current weather
export async function getWeather() {
  return request("/weather/current");
}

// Weather forecast - default 96 hours
export async function getWeatherForecast(
  hours = 96,
) {
  return request(`/weather/forecast?hours=${hours}`);
}

// AI optimization recommendation
export async function getOptimizationRecommendation(
  deviceId = "VAYU-001",
) {
  return request(
    `/optimization/recommendation?device_id=${encodeURIComponent(deviceId)}`,
  );
}

// Energy history
export async function getEnergyHistory(
  deviceId = "VAYU-001",
  days = 7,
) {
  return request(
    `/energy/history?device_id=${encodeURIComponent(deviceId)}&days=${days}`,
  );
}

// Fixed vs adaptive comparison
export async function getEnergyComparison(
  deviceId = "VAYU-001",
  days = 7,
) {
  return request(
    `/energy/comparison?device_id=${encodeURIComponent(deviceId)}&days=${days}`,
  );
}

// Backend health
export async function checkBackendHealth() {
  try {
    await request("/health");
    return true;
  } catch {
    return false;
  }
}

export { API_BASE_URL };