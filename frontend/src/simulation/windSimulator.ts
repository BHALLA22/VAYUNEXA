export type WindScenario = "normal" | "gust" | "high";

export interface WindSimulationState {
  speed: number;
  direction: number;
  phase: number;
  scenario: WindScenario;
}

const normalProfile = [
  8,
  8.6,
  9.2,
  10.1,
  11.2,
  12.4,
  13.1,
  12.2,
  11.4,
  10.6,
  9.8,
  9.1,
];

const gustProfile = [
  8,
  8.8,
  10.2,
  12.5,
  15.2,
  17.5,
  16.1,
  13.8,
  11.7,
  10.4,
];

const highWindProfile = [
  13,
  14,
  15,
  16,
  17,
  18,
  17,
  16,
  15,
  14,
];

export function getWindProfile(
  scenario: WindScenario,
): number[] {
  switch (scenario) {
    case "gust":
      return gustProfile;
    case "high":
      return highWindProfile;
    default:
      return normalProfile;
  }
}

export function getWindAtStep(
  scenario: WindScenario,
  step: number,
): number {
  const profile = getWindProfile(scenario);
  return profile[step % profile.length];
}

export function getWindDirection(
  step: number,
): number {
  return Math.round(
    220 + Math.sin(step * 0.35) * 18,
  );
}
