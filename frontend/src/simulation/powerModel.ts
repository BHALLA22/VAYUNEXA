export interface PowerSimulation {
  baselinePowerWatts: number;
  optimizedPowerWatts: number;
  powerGainWatts: number;
  powerGainPercent: number;
  baselineCp: number;
  optimizedCp: number;
  efficiencyPercent: number;
}

const AIR_DENSITY = 1.225;

/*
 * Prototype turbine geometry.
 * These are simulation assumptions, not measured hardware values.
 */
const ROTOR_AREA = 12.5;
const BASELINE_CP = 0.32;
const MAX_CP = 0.46;

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

function flapCpContribution(angle: number): number {
  /*
   * Optimal prototype flap region is around 20–26 degrees.
   * The farther away we move, the smaller the aerodynamic benefit.
   */
  const distance = Math.abs(angle - 23);

  return clamp(
    1 - distance / 23,
    0,
    1,
  );
}

export function simulatePower(
  windSpeed: number,
  flapAngles: [number, number, number],
): PowerSimulation {
  const velocityCubed = windSpeed ** 3;

  const baselinePower =
    0.5 *
    AIR_DENSITY *
    ROTOR_AREA *
    BASELINE_CP *
    velocityCubed;

  const flapQuality =
    flapAngles.reduce(
      (sum, angle) => sum + flapCpContribution(angle),
      0,
    ) / 3;

  /*
   * Move Cp smoothly between baseline and maximum
   * based on how close the three flap angles are
   * to the prototype optimum.
   */
  const optimizedCp =
    BASELINE_CP +
    (MAX_CP - BASELINE_CP) * flapQuality;

  const optimizedPower =
    0.5 *
    AIR_DENSITY *
    ROTOR_AREA *
    optimizedCp *
    velocityCubed;

  const powerGain =
    optimizedPower - baselinePower;

  const powerGainPercent =
    baselinePower > 0
      ? (powerGain / baselinePower) * 100
      : 0;

  return {
    baselinePowerWatts: +baselinePower.toFixed(2),
    optimizedPowerWatts: +optimizedPower.toFixed(2),
    powerGainWatts: +powerGain.toFixed(2),
    powerGainPercent: +powerGainPercent.toFixed(2),
    baselineCp: +BASELINE_CP.toFixed(3),
    optimizedCp: +optimizedCp.toFixed(3),
    efficiencyPercent: +((optimizedCp / 0.59) * 100).toFixed(1),
  };
}
