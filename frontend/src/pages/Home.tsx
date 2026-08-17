/** VAYUNEXA: turbine-led spatial command center with restrained aerospace glass. */
import { useEffect, useMemo, useRef, useState, type ComponentType } from "react";
import { Activity, BarChart3, BrainCircuit, CheckCircle2, ChevronRight, Compass, Cpu, Droplets, FlaskConical, Gauge, Leaf, LayoutDashboard, Maximize2, MoveRight, Radio, RotateCcw, Send, ServerCog, Settings2, ShieldCheck, Sparkles, Thermometer, Waves, Wind, Zap } from "lucide-react";
import { getWindAtStep, getWindDirection } from "@/simulation/windSimulator";
import { optimizeFlaps } from "@/simulation/flapOptimizer";
import { simulatePower } from "@/simulation/powerModel";
import { getLatestTelemetry, getTodayEnergy, getWeather, getOptimizationRecommendation } from "@/services/api";

type Icon = ComponentType<{ size?: number; strokeWidth?: number }>;
type Telemetry = { wind: number; direction: number; rpm: number; power: number; energy: number; temperature: number; humidity: number };

const nav = [["Dashboard", LayoutDashboard], ["Live Turbine", Wind], ["Analytics", BarChart3], ["AI Intelligence", BrainCircuit], ["Experiment", FlaskConical], ["System", ServerCog], ["Settings", Settings2]] as [string, Icon][];
const adaptive = [19,26,25,37,34,48,39,50,42,58,56,61,55,67,58,65,61,72,70,77,72,69,75,70,66,58,55,51,46,43,35,31];
const fixed = [16,19,20,27,25,35,31,39,33,44,40,47,45,55,49,54,50,60,56,62,58,52,54,50,46,41,39,35,29,26,23,20];
const path = (values: number[]) => values.map((v, i) => `${i ? "L" : "M"}${(i / (values.length - 1) * 560).toFixed(1)} ${(110 - v / 84 * 110).toFixed(1)}`).join(" ");

function Metric({ icon: I, label, value, unit, className }: { icon: Icon; label: string; value: string; unit?: string; className: string }) {
  return <div className={`metric-callout ${className}`}><div className="metric-icon"><I size={21} strokeWidth={1.6} /></div><div><p>{label}</p><strong>{value}<span>{unit}</span></strong></div></div>;
}
function Kpi({ icon: I, label, value, unit, tone = "cyan" }: { icon: Icon; label: string; value: string; unit?: string; tone?: string }) {
  return <div className="small-kpi"><div className={`small-kpi-icon ${tone}`}><I size={18} /></div><div><p>{label}</p><strong className={tone}>{value}<span>{unit}</span></strong></div></div>;
}
function Flow({ icon: I, label, active = false }: { icon: Icon; label: string; active?: boolean }) {
  return <div className={`flow-node ${active ? "active" : ""}`}><div><I size={18} strokeWidth={1.45} /></div><span>{label}</span></div>;
}

export default function Home() {
  const [activeNav, setActiveNav] = useState("Dashboard");
  const [mode, setMode] = useState<"AUTO" | "MANUAL">("AUTO");
  const [demoRunning, setDemoRunning] = useState(false);
  const [emergencyStop, setEmergencyStop] = useState(false);
  const [demoWind, setDemoWind] = useState<number | null>(null);
  const [selected, setSelected] = useState(0);
  const [flaps, setFlaps] = useState([18, 18, 18]);
  const [telemetry, setTelemetry] = useState<Telemetry>({
    wind: 8,
    direction: 220,
    rpm: 410,
    power: 42,
    energy: 1.82,
    temperature: 24.6,
    humidity: 56,
  });

  const simulationStep = useRef(0);

  useEffect(() => {
    let cancelled = false;

    const loadBackendData = async () => {
      try {
        const [latest, today, weather, recommendation] =
          await Promise.all([
            getLatestTelemetry("VAYU-001"),
            getTodayEnergy("VAYU-001"),
            getWeather(),
            getOptimizationRecommendation("VAYU-001"),
          ]);

        if (cancelled) return;

        setTelemetry({
          wind: latest.wind_speed,
          direction: latest.wind_direction ?? 0,
          rpm: Math.round(latest.rpm),
          power: latest.power,
          energy: +(today.net_energy_wh / 1000).toFixed(3),
          temperature:
            latest.temperature ??
            weather.temperature ??
            24.6,
          humidity:
            latest.humidity ??
            weather.humidity ??
            56,
        });

        setFlaps([
          latest.flap_angle_1,
          latest.flap_angle_2,
          latest.flap_angle_3,
        ]);

        if (mode === "AUTO") {
          const recommended = recommendation.recommended_angle;

          setFlaps([
            recommended,
            recommended,
            recommended,
          ]);
        }
      } catch (error) {
        console.warn(
          "VAYUNEXA backend unavailable — using simulation fallback.",
          error,
        );

        if (cancelled) return;

        const step = simulationStep.current++;
        const wind = getWindAtStep("normal", step);
        const direction = getWindDirection(step);

        setTelemetry(old => {
          const currentAngles: [number, number, number] = [
            flaps[0],
            flaps[1],
            flaps[2],
          ];

          const powerModel = simulatePower(
            wind,
            currentAngles,
          );

          return {
            wind,
            direction,
            rpm: Math.round(370 + wind * 5),
            power: powerModel.optimizedPowerWatts,
            energy: +(
              old.energy +
              powerModel.optimizedPowerWatts / 360000
            ).toFixed(3),
            temperature: +(
              24.4 +
              Math.sin(step * 0.3) * 0.7
            ).toFixed(1),
            humidity: Math.round(
              55 + Math.sin(step * 0.25) * 4,
            ),
          };
        });

        if (mode === "AUTO") {
          const result = optimizeFlaps(
            wind,
            direction,
            {
              flap1: flaps[0],
              flap2: flaps[1],
              flap3: flaps[2],
            },
          );

          setFlaps([
            result.angles.flap1,
            result.angles.flap2,
            result.angles.flap3,
          ]);
        }
      }
    };

    loadBackendData();

    const timer = window.setInterval(
      loadBackendData,
      5000,
    );

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const optimization = useMemo(
    () =>
      optimizeFlaps(
        demoWind ?? telemetry.wind,
        telemetry.direction,
        {
          flap1: flaps[0],
          flap2: flaps[1],
          flap3: flaps[2],
        },
      ),
    [telemetry.wind, telemetry.direction, flaps , demoWind],
  );

  const recommended = Math.round(
    optimization.averageAngle,
  );

  const powerSimulation = useMemo(
  () =>
    simulatePower(
      demoWind ?? telemetry.wind,
      [
        flaps[0],
        flaps[1],
        flaps[2],
      ],
    ),
  [telemetry.wind, flaps, demoWind],
);

  const adaptiveEnergyKwh = telemetry.energy;
  const baselineEnergyKwh =
    powerSimulation.powerGainPercent > 0
      ? adaptiveEnergyKwh /
        (1 + powerSimulation.powerGainPercent / 100)
      : adaptiveEnergyKwh;

  const projectedWeeklyEnergyKwh =
    (powerSimulation.optimizedPowerWatts * 24 * 7) /
    1000;

  const apply = () => {
  if (emergencyStop) return;

  setFlaps([
    optimization.angles.flap1,
    optimization.angles.flap2,
    optimization.angles.flap3,
    ]);

  setMode("AUTO");
  };
  const setFlap = (blade: number, value: number) => {
    setMode("MANUAL");
    setFlaps(old =>
      old.map((v, i) =>
        i === blade ? value : v,
      ),
    );
  };
  const startAIDemo = () => {
  setEmergencyStop(false);
  setDemoRunning(true);
  setMode("AUTO");

  setDemoWind(8);

  window.setTimeout(() => setDemoWind(12), 2500);
  window.setTimeout(() => setDemoWind(16), 5000);
  window.setTimeout(() => setDemoWind(18), 7500);
  window.setTimeout(() => setDemoWind(12), 10000);

  window.setTimeout(() => {
    setDemoWind(null);
    setDemoRunning(false);
  }, 12500);
};

const triggerWindGust = () => {
  if (emergencyStop) return;

  setDemoWind(18);

  window.setTimeout(() => {
    setDemoWind(null);
  }, 5000);
};

const triggerEmergencyStop = () => {
  setEmergencyStop(true);
  setDemoRunning(false);
  setDemoWind(null);
  setMode("MANUAL");
};
  return <main className="vayunexa-shell">
    <aside className="sidebar glass-edge">
      <div className="brand-lockup"><div className="brand-mark-fallback" aria-hidden="true"><Wind size={28} /></div><div><span className="brand-name">VAYU<span>NEXA</span></span><p>Adaptive Wind Intelligence</p></div></div>
      <nav className="main-nav" aria-label="Application navigation">{nav.map(([label, I]) => <button key={label} className={activeNav === label ? "nav-item active" : "nav-item"} onClick={() => setActiveNav(label)}><I size={20} strokeWidth={1.55} /><span>{label}</span>{activeNav === label && <ChevronRight size={15} />}</button>)}</nav>
      <div className="sidebar-status"><div className="status-light" /><div><strong>LIVE / ONLINE</strong><span>{mode} CONTROL</span></div></div><div className="sidebar-fade" aria-hidden="true" />
    </aside>

    <section className="workbench">
      <header className="topline"><div><span className="eyebrow">TURBINE / 01</span><span className="topline-divider" /><span className="live-copy"><i /> LIVE TELEMETRY</span></div><div className="top-actions"><button className="icon-button" aria-label="Reset turbine camera"><RotateCcw size={16} /></button><button className="icon-button" aria-label="Expand turbine view"><Maximize2 size={16} /></button><span className="last-sync">SYNCED 10:24:31 AM</span></div></header>
      <section className="turbine-stage" aria-label="Wind turbine digital twin">
        <div className="hero-image" /><div className="atmospheric-vignette" /><div className="airflow airflow-one"><Waves size={16} /><span /></div><div className="airflow airflow-two"><Waves size={15} /><span /></div>
        <div className="scene-heading"><span>DIGITAL TWIN</span><strong>Adaptive rotor control</strong></div><div className="turbine-overlay" aria-hidden="true"><div className="rotor"><span className="hub" /><i className="blade blade-a" style={{ ["--flap-angle" as string]: `${flaps[0]}deg` }}><span className="blade-flap" /></i><i className="blade blade-b" style={{ ["--flap-angle" as string]: `${flaps[1]}deg` }}><span className="blade-flap" /></i><i className="blade blade-c" style={{ ["--flap-angle" as string]: `${flaps[2]}deg` }}><span className="blade-flap" /></i></div></div>
        <Metric icon={Wind} label="WIND" value={telemetry.wind.toFixed(1)} unit=" m/s" className="callout-wind" /><Metric icon={Gauge} label="RPM" value={`${telemetry.rpm}`} className="callout-rpm" /><Metric icon={Zap} label="POWER" value={telemetry.power.toFixed(1)} unit=" W" className="callout-power" /><Metric icon={Leaf} label="ENERGY TODAY" value={telemetry.energy.toFixed(2)} unit=" kWh" className="callout-energy" /><Metric icon={Sparkles} label="FLAP" value={`${flaps[selected]}°`} className="callout-flap" />
      </section>
      <section className="analytics-deck glass-edge"><div className="deck-kpis"><Kpi icon={Zap} label="CURRENT POWER" value={telemetry.power.toFixed(1)} unit=" W" /><Kpi icon={Leaf} label="TODAY'S ENERGY" value={telemetry.energy.toFixed(2)} unit=" kWh" tone="green" /><Kpi icon={BarChart3} label="WEEKLY ENERGY" value={projectedWeeklyEnergyKwh.toFixed(2)} unit=" kWh" tone="white" /><Kpi icon={Activity} label="NET ENERGY GAIN" value={`+${powerSimulation.powerGainPercent.toFixed(1)}`} unit="%" tone="green" /></div><div className="analytics-main"><div className="chart-card"><div className="chart-head"><div><span>POWER (W)</span><strong>Adaptive production curve</strong></div><div className="chart-key"><b /><span>ADAPTIVE (AI)</span><i /><span>FIXED (BASELINE)</span></div></div><svg viewBox="0 0 560 130" role="img" aria-label="Power comparison chart" preserveAspectRatio="none">{[20,50,80,110].map(y => <line key={y} x1="0" x2="560" y1={y} y2={y} className="chart-grid" />)}<path d={path(fixed)} className="chart-line fixed" /><path d={path(adaptive)} className="chart-line adaptive" /></svg><div className="chart-times"><span>00:00</span><span>04:00</span><span>08:00</span><span>12:00</span><span>16:00</span><span>20:00</span><span>24:00</span></div></div><div className="comparison-card"><p>FIXED vs ADAPTIVE <span>(TODAY)</span></p><div className="bar-row"><span>{baselineEnergyKwh.toFixed(2)} kWh</span><span>{adaptiveEnergyKwh.toFixed(2)} kWh</span></div><div className="bars"><i className="fixed-bar" /><i className="adaptive-bar" /></div><strong>+{powerSimulation.powerGainPercent.toFixed(1)}<span>%</span></strong><em>MODELLED IMPROVEMENT</em></div></div></section>
      <footer className="status-rail glass-edge"><div><span className="footer-dot" /><small>SYSTEM STATUS</small><strong>All Systems Operational</strong></div><div><small>LAST UPDATE</small><strong>10:24:31 AM</strong></div><div><small>SYNC</small><strong className="cyan">REAL-TIME</strong></div><div><BrainCircuit size={16} /><small>CONTROL MODE</small><strong className="green">{mode}</strong></div><div><ShieldCheck size={16} /><small>SAFETY STATUS</small><strong className="green">NORMAL</strong></div></footer>
    </section>

    <aside className="intelligence-rail">
      <section className="optimizer-panel glass-edge"><div className="panel-title"><div className="brain-ring"><BrainCircuit size={20} /></div><div><span>AI FLAP OPTIMIZER</span><small>MODEL ONLINE</small></div><i className="panel-live" /></div><div className="optimizer-readings"><div><span>CURRENT FLAP ANGLE</span><strong>{flaps[selected]}°</strong></div><div><span>RECOMMENDED ANGLE</span><strong className="green">{recommended}°</strong></div><div><span>EXPECTED POWER IMPROVEMENT</span><strong className="green">+{powerSimulation.powerGainPercent.toFixed(1)}% <em>MODEL ESTIMATE</em></strong></div><div><span>CONFIDENCE</span><strong className="green">High</strong></div></div><div className="optimizer-reason"><span>REASON</span><p>Moderate winds with stable direction. Increasing flap angle improves lift-to-drag ratio and power capture.</p></div><div className="decision-flow"><div><span>CURRENT</span><strong>{flaps[selected]}°</strong></div><MoveRight size={20} /><div><span>AI</span><strong className="green">{recommended}°</strong></div><MoveRight size={20} /><div><span>SAFE</span><strong className="green"><CheckCircle2 size={25} /></strong></div></div><button className="apply-button" onClick={apply}><Sparkles size={15} /> APPLY SAFE RECOMMENDATION</button></section>
      <section className="blade-panel glass-edge"><div className="section-heading"><span>BLADE FLAP CONTROL</span><button onClick={() => setMode(mode === "AUTO" ? "MANUAL" : "AUTO")}>{mode === "AUTO" ? "AUTO ACTIVE" : "MANUAL"}</button></div><div className="blade-labels"><span>BLADE</span><span>CURRENT</span><span>TARGET</span><span>SERVO STATUS</span></div>{flaps.map((angle, i) => <div className={selected === i ? "blade-row selected" : "blade-row"} key={i}><button className="blade-name" onClick={() => setSelected(i)}>Blade {i + 1}</button><strong>{angle}°</strong><span className="target">{mode === "AUTO" ? recommended : angle}°</span><span className="servo-status"><i /> {mode === "AUTO" ? "LOCKED" : "READY"}</span>{mode === "MANUAL" && <input type="range" aria-label={`Set blade ${i + 1} flap angle`} min="0" max="35" value={angle} onChange={e => setFlap(i, Number(e.target.value))} />}</div>)}<div className="command-flow"><span><Send size={15} /> AI COMMAND</span><MoveRight size={14} /><span><ShieldCheck size={15} /> SAFETY CHECK</span><MoveRight size={14} /><span><Cpu size={15} /> SERVO</span><MoveRight size={14} /><span><Wind size={15} /> FLAP</span></div></section>
      <section className="system-flow glass-edge"><p>SYSTEM ARCHITECTURE</p><div className="flow-track"><Flow icon={Wind} label="WIND" active /><MoveRight /><Flow icon={Radio} label="SENSORS" active /><MoveRight /><Flow icon={Cpu} label="ESP8266" /><MoveRight /><Flow icon={BrainCircuit} label="AI OPTIMIZER" active /><MoveRight /><Flow icon={ShieldCheck} label="SAFETY" /><MoveRight /><Flow icon={Settings2} label="SERVOS" /><MoveRight /><Flow icon={Wind} label="FLAPS" /></div></section>
      <section className="weather-panel glass-edge"><p>WEATHER CONDITIONS</p><div className="weather-grid"><div><Compass /><span>WIND DIRECTION</span><strong>236° SW</strong><small>Southwest</small></div><div><Thermometer /><span>TEMPERATURE</span><strong>{telemetry.temperature}°C</strong></div><div><Droplets /><span>HUMIDITY</span><strong>{telemetry.humidity}%</strong></div></div><div className="weather-orb" aria-hidden="true" /></section>
    </aside>
  </main>;
}













