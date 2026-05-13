import React, { useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  ArrowRight,
  CheckCircle2,
  ClipboardPlus,
  FileText,
  HeartPulse,
  Loader2,
  RefreshCw,
  ShieldCheck,
  Stethoscope,
  UserRound,
} from "lucide-react";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const steps = [
  { key: "case", label: "Cas initial", icon: ClipboardPlus },
  { key: "questions", label: "Questions", icon: UserRound },
  { key: "review", label: "Medecin", icon: Stethoscope },
  { key: "report", label: "Rapport", icon: FileText },
];

function getActiveStep(data) {
  if (!data) return "case";
  const interrupt = data.interrupt;
  if (interrupt?.type === "patient_question") return "questions";
  if (interrupt?.type === "physician_review") return "review";
  if (data.state?.final_report) return "report";
  return "questions";
}

function Stepper({ activeStep }) {
  const activeIndex = steps.findIndex((step) => step.key === activeStep);

  return (
    <div className="stepper" aria-label="Progression">
      {steps.map((step, index) => {
        const Icon = step.icon;
        const isActive = step.key === activeStep;
        const isDone = index < activeIndex;
        return (
          <div className={`step ${isActive ? "active" : ""} ${isDone ? "done" : ""}`} key={step.key}>
            <span className="stepIcon">{isDone ? <CheckCircle2 size={18} /> : <Icon size={18} />}</span>
            <span>{step.label}</span>
          </div>
        );
      })}
    </div>
  );
}

function StatusCard({ data }) {
  const answers = data?.state?.patient_answers?.length || 0;
  const status = data?.status === "completed" ? "Terminee" : data ? "En cours" : "Nouvelle";

  return (
    <aside className="statusPanel">
      <div className="brandBlock">
        <div className="brandMark">
          <HeartPulse size={28} />
        </div>
        <div>
          <p className="eyebrow">Multi-agents</p>
          <h1>Orientation clinique</h1>
        </div>
      </div>

      <div className="metricGrid">
        <div className="metric">
          <span>Status</span>
          <strong>{status}</strong>
        </div>
        <div className="metric">
          <span>Questions</span>
          <strong>{answers}/5</strong>
        </div>
      </div>

      <div className="safetyNote">
        <ShieldCheck size={18} />
        <p>Ce systeme ne remplace pas une consultation medicale.</p>
      </div>
    </aside>
  );
}

function CaseForm({ onStart, loading }) {
  const [initialCase, setInitialCase] = useState("");

  return (
    <section className="workPanel enter">
      <div className="panelHeader">
        <div>
          <p className="eyebrow">Etape 1</p>
          <h2>Saisir le cas patient</h2>
        </div>
        <Activity size={24} />
      </div>

      <textarea
        value={initialCase}
        onChange={(event) => setInitialCase(event.target.value)}
        placeholder="Exemple : Patient avec toux, fatigue et nez qui coule depuis 2 jours, sans gene respiratoire."
      />

      <button className="primaryButton" disabled={!initialCase.trim() || loading} onClick={() => onStart(initialCase)}>
        {loading ? <Loader2 className="spin" size={18} /> : <ArrowRight size={18} />}
        Demarrer la consultation
      </button>
    </section>
  );
}

function QuestionForm({ data, onResume, loading }) {
  const [answer, setAnswer] = useState("");
  const interrupt = data.interrupt;
  const answers = data.state?.patient_answers || [];

  return (
    <section className="workPanel enter">
      <div className="panelHeader">
        <div>
          <p className="eyebrow">Question {interrupt.question_number}/5</p>
          <h2>{interrupt.question}</h2>
        </div>
        <UserRound size={24} />
      </div>

      <div className="progressTrack">
        <span style={{ width: `${((interrupt.question_number - 1) / 5) * 100}%` }} />
      </div>

      {answers.length > 0 && (
        <div className="answerList">
          {answers.map((item, index) => (
            <div className="answerItem" key={`${item}-${index}`}>
              <span>Q{index + 1}</span>
              <p>{item}</p>
            </div>
          ))}
        </div>
      )}

      <input
        value={answer}
        onChange={(event) => setAnswer(event.target.value)}
        placeholder="Votre reponse"
        onKeyDown={(event) => {
          if (event.key === "Enter" && answer.trim() && !loading) {
            onResume(answer);
            setAnswer("");
          }
        }}
      />

      <button
        className="primaryButton"
        disabled={!answer.trim() || loading}
        onClick={() => {
          onResume(answer);
          setAnswer("");
        }}
      >
        {loading ? <Loader2 className="spin" size={18} /> : <ArrowRight size={18} />}
        Envoyer la reponse
      </button>
    </section>
  );
}

function PhysicianReview({ data, onResume, loading }) {
  const [treatment, setTreatment] = useState("");
  const interrupt = data.interrupt;

  return (
    <section className="workPanel enter">
      <div className="panelHeader">
        <div>
          <p className="eyebrow">Human-in-the-Loop</p>
          <h2>Revue du medecin traitant</h2>
        </div>
        <Stethoscope size={24} />
      </div>

      <div className="clinicalBox">
        <h3>Synthese clinique preliminaire</h3>
        <p>{interrupt.diagnostic_summary}</p>
      </div>

      <div className="clinicalBox accent">
        <h3>Recommandation intermediaire</h3>
        <p>{interrupt.interim_care}</p>
      </div>

      <textarea
        value={treatment}
        onChange={(event) => setTreatment(event.target.value)}
        placeholder="Traitement ou conduite a tenir proposee par le medecin..."
      />

      <button className="primaryButton" disabled={!treatment.trim() || loading} onClick={() => onResume(treatment)}>
        {loading ? <Loader2 className="spin" size={18} /> : <CheckCircle2 size={18} />}
        Valider la revue
      </button>
    </section>
  );
}

function ReportView({ data, onReset }) {
  const report = data.state?.final_report || "";
  const formattedReport = useMemo(
    () =>
      report
        .split("\n")
        .filter(Boolean)
        .map((line, index) => {
          if (line.startsWith("# ")) return <h2 key={index}>{line.replace("# ", "")}</h2>;
          if (line.startsWith("## ")) return <h3 key={index}>{line.replace("## ", "")}</h3>;
          return <p key={index}>{line}</p>;
        }),
    [report],
  );

  return (
    <section className="workPanel reportPanel enter">
      <div className="panelHeader">
        <div>
          <p className="eyebrow">Etape finale</p>
          <h2>Rapport final</h2>
        </div>
        <FileText size={24} />
      </div>

      <article className="report">{formattedReport}</article>

      <button className="secondaryButton" onClick={onReset}>
        <RefreshCw size={18} />
        Nouvelle consultation
      </button>
    </section>
  );
}

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const activeStep = getActiveStep(data);

  async function request(path, options) {
    setLoading(true);
    setError("");
    try {
      const response = await fetch(`${API_URL}${path}`, {
        headers: { "Content-Type": "application/json" },
        ...options,
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Erreur API");
      }
      setData(payload);
    } catch (event) {
      setError(event.message || "Impossible de contacter l'API FastAPI");
    } finally {
      setLoading(false);
    }
  }

  function startConsultation(initialCase) {
    request("/consultation/start", {
      method: "POST",
      body: JSON.stringify({ initial_case: initialCase }),
    });
  }

  function resumeConsultation(answer) {
    request("/consultation/resume", {
      method: "POST",
      body: JSON.stringify({ thread_id: data.thread_id, answer }),
    });
  }

  function reset() {
    setData(null);
    setError("");
  }

  return (
    <main className="appShell">
      <StatusCard data={data} />
      <div className="mainColumn">
        <Stepper activeStep={activeStep} />
        {error && <div className="errorBox">{error}</div>}

        {!data && <CaseForm onStart={startConsultation} loading={loading} />}
        {data?.interrupt?.type === "patient_question" && (
          <QuestionForm data={data} onResume={resumeConsultation} loading={loading} />
        )}
        {data?.interrupt?.type === "physician_review" && (
          <PhysicianReview data={data} onResume={resumeConsultation} loading={loading} />
        )}
        {data?.state?.final_report && <ReportView data={data} onReset={reset} />}
      </div>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
