export type SimulationPhase =
  | "idle"
  | "normal"
  | "strong"
  | "gust"
  | "recovery"
  | "stopped";

export interface SimulationState {
  running: boolean;
  emergencyStopped: boolean;
  phase: SimulationPhase;
  step: number;
}

export const DEMO_PHASES: Array<{
  phase: Exclude<SimulationPhase, "idle" | "stopped">;
  durationSteps: number;
}> = [
  { phase: "normal", durationSteps: 6 },
  { phase: "strong", durationSteps: 6 },
  { phase: "gust", durationSteps: 6 },
  { phase: "recovery", durationSteps: 6 },
];

export function getPhaseForStep(step: number): SimulationPhase {
  let cursor = 0;

  for (const entry of DEMO_PHASES) {
    if (step < cursor + entry.durationSteps) {
      return entry.phase;
    }

    cursor += entry.durationSteps;
  }

  return "recovery";
}

export function getScenarioForPhase(
  phase: SimulationPhase,
): "normal" | "gust" | "high" {
  switch (phase) {
    case "gust":
      return "gust";

    case "strong":
      return "high";

    case "recovery":
      return "normal";

    case "normal":
    default:
      return "normal";
  }
}
