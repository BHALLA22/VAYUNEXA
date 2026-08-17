export interface FlapAngles {
  flap1: number;
  flap2: number;
  flap3: number;
}

export interface OptimizationResult {
  angles: FlapAngles;
  averageAngle: number;
  expectedPowerGainPercent: number;
  reason: string;
}

function clamp(
  value: number,
  min: number,
  max: number,
): number {
  return Math.max(min, Math.min(max, value));
}

export function optimizeFlaps(
  windSpeed: number,
  windDirection = 220,
  current: FlapAngles = {
    flap1: 18,
    flap2: 18,
    flap3: 18,
  },
): OptimizationResult {
  /*
   * Prototype deterministic controller.
   *
   * Wind bands:
   *   < 5 m/s   → low capture angle
   *   5–10 m/s  → moderate angle
   *   10–14 m/s → stronger adaptive angle
   *   14–18 m/s → protective/high-wind setting
   *   > 18 m/s  → aggressive protection
   *
   * Wind direction creates a small deterministic asymmetry
   * between the three flap angles.
   */

  const base = clamp(
    8 + windSpeed * 1.15,
    8,
    30,
  );

  const directionOffset =
    Math.sin((windDirection * Math.PI) / 180) * 2.0;

  const flap1 = clamp(
    Math.round(base + directionOffset - 1),
    0,
    35,
  );

  const flap2 = clamp(
    Math.round(base + directionOffset + 1),
    0,
    35,
  );

  const flap3 = clamp(
    Math.round(base - directionOffset),
    0,
    35,
  );

  const averageAngle =
    (flap1 + flap2 + flap3) / 3;

  /*
   * Prototype estimated gain.
   *
   * This is a model estimate for simulation,
   * NOT a measured hardware result.
   */
  const idealAngle = clamp(
    8 + windSpeed * 1.05,
    8,
    28,
  );

  const angleError =
    Math.abs(averageAngle - idealAngle);

  const expectedPowerGainPercent = clamp(
    10 - angleError * 0.8,
    0,
    10,
  );

  const reason =
    windSpeed < 5
      ? "Low wind: maintaining a conservative flap setting."
      : windSpeed < 10
        ? "Moderate wind: balancing aerodynamic capture and load."
        : windSpeed < 14
          ? "Strong wind: increasing flap angle for improved capture."
          : windSpeed < 18
            ? "High wind: adaptive angle increased while controlling load."
            : "Gust protection: limiting flap angle to reduce aerodynamic load.";

  /*
   * Keep current in the API contract now so the same optimizer
   * can later be replaced or extended with measured actuator state.
   */
  void current;

  return {
    angles: {
      flap1,
      flap2,
      flap3,
    },
    averageAngle,
    expectedPowerGainPercent: +expectedPowerGainPercent.toFixed(1),
    reason,
  };
}
