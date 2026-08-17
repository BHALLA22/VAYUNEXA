export interface Telemetry {
  device_id: string;
  timestamp: string;

  wind_speed: number;
  wind_direction: number;
  rpm: number;

  voltage: number;
  current: number;
  power: number;

  flap_angle_1: number;
  flap_angle_2: number;
  flap_angle_3: number;

  temperature: number;
  humidity: number;

  mode: string;
  servo_energy_wh: number;
}

export interface AIRecommendation {
  device_id: string;

  recommended_angle: number;
  current_angle: number;

  current_predicted_power_w: number;
  predicted_power_w: number;

  expected_power_gain_percent: number;

  candidates: Array<{
    angle: number;
    predicted_power_w: number;
  }>;

  model_version: string;
  controller_type: string;

  confidence?: number;
  is_experimental?: boolean;

  reason?: string;
}

export interface AutoControlResponse {
  status: string;
  device_id: string;

  source: string;
  control_mode: string;

  current_angles: {
    flap_1: number;
    flap_2: number;
    flap_3: number;
  };

  target_angles: {
    flap_1: number;
    flap_2: number;
    flap_3: number;
  };

  reason: string;

  expected_power_gain_percent: number;

  safety_status: string;

  message: string;
}

export interface WeatherData {
  temperature?: number;
  humidity?: number;
  wind_speed?: number;
  wind_direction?: number;
  precipitation?: number;
  cloud_cover?: number;
}

export interface ForecastDay {
  date: string;
  wind_speed?: number;
  predicted_power?: number;
  temperature?: number;
}