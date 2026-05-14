import React, { useState, useRef, useMemo } from "react";
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
  FileDown,
  History,
  Search,
  X,
  Globe,
  BarChart3,
  GitCompare,
  Camera,
  Upload,
  AlertTriangle,
  AlertCircle,
  CheckCircle,
  BookOpen,
  ExternalLink,
} from "lucide-react";
import "./styles.css";

const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const translations = {
  fr: {
    title: "Orientation clinique",
    subtitle: "Multi-agents",
    start: "Démarrer la consultation",
    casePlaceholder: "Exemple : Patient avec toux, fatigue...",
    question: "Question",
    send: "Envoyer la réponse",
    physicianReview: "Revue du médecin traitant",
    treatmentPlaceholder: "Traitement ou conduite à tenir...",
    validate: "Valider la revue",
    finalReport: "Rapport final",
    newConsultation: "Nouvelle consultation",
    status: "Statut",
    questions: "Questions",
    safetyNote: "Ce système ne remplace pas une consultation médicale.",
    inProgress: "En cours",
    completed: "Terminée",
    waitingPhysician: "Attente médecin",
    diagnosticSummary: "Synthèse clinique préliminaire",
    interimCare: "Recommandation intermédiaire",
    mcpContext: "Contexte de recherche MCP",
    exportPDF: "Exporter PDF",
    history: "Historique",
    compare: "Comparer",
    dashboard: "Tableau de bord",
    urgency: "Score d'urgence",
    sources: "Sources médicales",
    imageUpload: "Ajouter une photo",
    stopEarly: "Arrêt précoce détecté",
  },
  en: {
    title: "Clinical Orientation",
    subtitle: "Multi-agent",
    start: "Start consultation",
    casePlaceholder: "Example: Patient with cough, fatigue...",
    question: "Question",
    send: "Send answer",
    physicianReview: "Physician review",
    treatmentPlaceholder: "Treatment or course of action...",
    validate: "Validate review",
    finalReport: "Final report",
    newConsultation: "New consultation",
    status: "Status",
    questions: "Questions",
    safetyNote: "This system does not replace a medical consultation.",
    inProgress: "In progress",
    completed: "Completed",
    waitingPhysician: "Waiting physician",
    diagnosticSummary: "Preliminary clinical summary",
    interimCare: "Interim recommendation",
    mcpContext: "MCP research context",
    exportPDF: "Export PDF",
    history: "History",
    compare: "Compare",
    dashboard: "Dashboard",
    urgency: "Urgency score",
    sources: "Medical sources",
    imageUpload: "Add a photo",
    stopEarly: "Early stop detected",
  },
  es: {
    title: "Orientación clínica",
    subtitle: "Multi-agente",
    start: "Iniciar consulta",
    casePlaceholder: "Ejemplo: Paciente con tos, fatiga...",
    question: "Pregunta",
    send: "Enviar respuesta",
    physicianReview: "Revisión médica",
    treatmentPlaceholder: "Tratamiento o conducta a seguir...",
    validate: "Validar revisión",
    finalReport: "Informe final",
    newConsultation: "Nueva consulta",
    status: "Estado",
    questions: "Preguntas",
    safetyNote: "Este sistema no sustituye una consulta médica.",
    inProgress: "En curso",
    completed: "Completada",
    waitingPhysician: "Esperando médico",
    diagnosticSummary: "Resumen clínico preliminar",
    interimCare: "Recomendación intermedia",
    mcpContext: "Contexto de investigación MCP",
    exportPDF: "Exportar PDF",
    history: "Historial",
    compare: "Comparar",
    dashboard: "Panel",
    urgency: "Puntuación de urgencia",
    sources: "Fuentes médicas",
    imageUpload: "Añadir foto",
    stopEarly: "Detención temprana detectada",
  },
  ar: {
    title: "التوجيه السريري",
    subtitle: "متعدد الوكلاء",
    start: "بدء الاستشارة",
    casePlaceholder: "مثال: مريض بسعال، تعب...",
    question: "سؤال",
    send: "إرسال الإجابة",
    physicianReview: "مراجعة الطبيب",
    treatmentPlaceholder: "العلاج أو سلوك...",
    validate: "التحقق من المراجعة",
    finalReport: "التقرير النهائي",
    newConsultation: "استشارة جديدة",
    status: "الحالة",
    questions: "الأسئلة",
    safetyNote: "هذا النظام لا يحل محل استشارة طبية.",
    inProgress: "قيد التقدم",
    completed: "مكتملة",
    waitingPhysician: "في انتظار الطبيب",
    diagnosticSummary: "الملخص السريري الأولي",
    interimCare: "التوصية المؤقتة",
    mcpContext: "سياق البحث MCP",
    exportPDF: "تصدير PDF",
    history: "السجل",
    compare: "مقارنة",
    dashboard: "لوحة القيادة",
    urgency: "درجة الخطورة",
    sources: "المصادر الطبية",
    imageUpload: "إضافة صورة",
    stopEarly: "تم الكشف عن توقف مبكر",
  },
};

const languages = [
  { code: "fr", flag: "🇫🇷", name: "Français" },
  { code: "en", flag: "🇬🇧", name: "English" },
  { code: "es", flag: "🇪🇸", name: "Español" },
  { code: "ar", flag: "🇸🇦", name: "العربية" },
];

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
          <div
            className={`step ${isActive ? "active" : ""} ${isDone ? "done" : ""}`}
            key={step.key}
          >
            <span className="stepIcon">
              {isDone ? <CheckCircle2 size={18} /> : <Icon size={18} />}
            </span>
            <span>{step.label}</span>
          </div>
        );
      })}
    </div>
  );
}

function StatusCard({ data, t }) {
  const answers = data?.state?.patient_answers?.length || 0;
  const status =
    data?.status === "completed"
      ? t.completed
      : data?.status === "waiting_physician"
      ? t.waitingPhysician
      : data
      ? t.inProgress
      : "Nouvelle";

  return (
    <aside className="statusPanel">
      <div className="brandBlock">
        <div className="brandMark">
          <HeartPulse size={28} />
        </div>
        <div>
          <p className="eyebrow">{t.subtitle}</p>
          <h1>{t.title}</h1>
        </div>
      </div>

      <div className="metricGrid">
        <div className="metric">
          <span>{t.status}</span>
          <strong>{status}</strong>
        </div>
        <div className="metric">
          <span>{t.questions}</span>
          <strong>
            {answers}/5
          </strong>
        </div>
      </div>

      <div className="safetyNote">
        <ShieldCheck size={18} />
        <p>{t.safetyNote}</p>
      </div>
    </aside>
  );
}

function CaseForm({ onStart, loading, t, onImageUpload }) {
  const [initialCase, setInitialCase] = useState("");
  const [imagePreview, setImagePreview] = useState(null);

  const handleImage = (file) => {
    if (!file) return;
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
      onImageUpload?.(reader.result);
    };
    reader.readAsDataURL(file);
  };

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
        placeholder={t.casePlaceholder}
        rows={4}
      />

      <div style={{ marginBottom: 15 }}>
        <div
          style={{
            border: "2px dashed #ddd",
            borderRadius: 12,
            padding: 15,
            textAlign: "center",
            cursor: "pointer",
          }}
        >
          {!imagePreview ? (
            <label style={{ cursor: "pointer", display: "block" }}>
              <Camera size={32} color="#999" style={{ margin: "0 auto 8px" }} />
              <span style={{ color: "#3498db" }}>{t.imageUpload}</span>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => handleImage(e.target.files[0])}
                style={{ display: "none" }}
              />
            </label>
          ) : (
            <div style={{ position: "relative" }}>
              <img
                src={imagePreview}
                style={{ maxWidth: "100%", maxHeight: 150, borderRadius: 8 }}
              />
              <button
                onClick={() => setImagePreview(null)}
                style={{
                  position: "absolute",
                  top: -10,
                  right: -10,
                  background: "#e74c3c",
                  color: "white",
                  border: "none",
                  borderRadius: "50%",
                  width: 28,
                  height: 28,
                  cursor: "pointer",
                }}
              >
                <X size={14} />
              </button>
            </div>
          )}
        </div>
      </div>

      <button
        className="primaryButton"
        disabled={!initialCase.trim() || loading}
        onClick={() => onStart(initialCase)}
      >
        {loading ? (
          <Loader2 className="spin" size={18} />
        ) : (
          <ArrowRight size={18} />
        )}
        {t.start}
      </button>
    </section>
  );
}

function QuestionForm({ data, onResume, loading, t }) {
  const [answer, setAnswer] = useState("");
  const interrupt = data.interrupt;
  const answers = data.state?.patient_answers || [];
  const urgency = data.urgency;

  const urgencyColors = {
    red: { bg: "#fee2e2", border: "#ef4444", text: "#991b1b" },
    orange: { bg: "#ffedd5", border: "#f97316", text: "#9a3412" },
    yellow: { bg: "#fef9c3", border: "#eab308", text: "#854d0e" },
    green: { bg: "#dcfce7", border: "#22c55e", text: "#166534" },
  };

  return (
    <section className="workPanel enter">
      <div className="panelHeader">
        <div>
          <p className="eyebrow">
            {t.question} {interrupt.question_number}/5
          </p>
          <h2>{interrupt.question}</h2>
        </div>
        <UserRound size={24} />
      </div>

      {urgency && (
        <div
          style={{
            background: urgencyColors[urgency.color]?.bg || "#f5f5f5",
            border: `2px solid ${urgencyColors[urgency.color]?.border || "#ddd"}`,
            borderRadius: 12,
            padding: "12px 16px",
            marginBottom: 15,
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          {urgency.color === "red" && <AlertTriangle size={24} color="#ef4444" />}
          {urgency.color === "orange" && <AlertCircle size={24} color="#f97316" />}
          {urgency.color === "yellow" && <AlertCircle size={24} color="#eab308" />}
          {urgency.color === "green" && <CheckCircle size={24} color="#22c55e" />}
          <div>
            <div style={{ fontWeight: "bold", color: urgencyColors[urgency.color]?.text }}>
              {urgency.label} ({urgency.score}/100)
            </div>
            <div style={{ fontSize: "0.85em", color: urgencyColors[urgency.color]?.text }}>
              {urgency.action}
            </div>
          </div>
        </div>
      )}

      <div className="progressTrack">
        <span
          style={{
            width: `${((interrupt.question_number - 1) / 5) * 100}%`,
          }}
        />
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
        {loading ? (
          <Loader2 className="spin" size={18} />
        ) : (
          <ArrowRight size={18} />
        )}
        {t.send}
      </button>
    </section>
  );
}

function PhysicianReview({ data, onResume, loading, t }) {
  const [treatment, setTreatment] = useState("");
  const [notes, setNotes] = useState("");
  const interrupt = data.interrupt;

  return (
    <section className="workPanel enter">
      <div className="panelHeader">
        <div>
          <p className="eyebrow">Human-in-the-Loop</p>
          <h2>{t.physicianReview}</h2>
        </div>
        <Stethoscope size={24} />
      </div>

      {data.stopEarly && (
        <div
          style={{
            background: "#fff3cd",
            border: "2px solid #ffc107",
            borderRadius: 12,
            padding: 15,
            marginBottom: 15,
          }}
        >
          <strong>⚠️ {t.stopEarly}</strong>
          <p style={{ margin: "5px 0 0" }}>{data.stopReason}</p>
        </div>
      )}

      <div className="clinicalBox">
        <h3>{t.diagnosticSummary}</h3>
        <p>{interrupt.diagnostic_summary}</p>
      </div>

      <div className="clinicalBox accent">
        <h3>{t.interimCare}</h3>
        <p>{interrupt.interim_care}</p>
      </div>

      {interrupt.mcp_context && (
        <div
          className="clinicalBox"
          style={{ background: "#e8f5e9", borderLeft: "4px solid #4caf50" }}
        >
          <h3>🔍 {t.mcpContext}</h3>
          <pre
            style={{
              whiteSpace: "pre-wrap",
              fontSize: "0.9em",
              lineHeight: 1.5,
            }}
          >
            {interrupt.mcp_context}
          </pre>
        </div>
      )}

      {data.sources && data.sources.length > 0 && (
        <div
          style={{
            marginTop: 15,
            padding: 15,
            background: "#f0f7ff",
            borderRadius: 8,
          }}
        >
          <h4
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              margin: "0 0 10px",
            }}
          >
            <BookOpen size={18} color="#3498db" />
            {t.sources}
          </h4>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {data.sources.map((source, i) => (
              <li key={i} style={{ marginBottom: 6 }}>
                <a
                  href={source.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    color: "#3498db",
                    textDecoration: "none",
                    display: "flex",
                    alignItems: "center",
                    gap: 5,
                  }}
                >
                  <ExternalLink size={14} />
                  [{source.type.toUpperCase()}] {source.title}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}

      <input
        value={treatment}
        onChange={(event) => setTreatment(event.target.value)}
        placeholder={t.treatmentPlaceholder}
      />

      <textarea
        value={notes}
        onChange={(event) => setNotes(event.target.value)}
        placeholder="Notes additionnelles (optionnel)"
        rows={3}
      />

      <button
        className="primaryButton"
        disabled={!treatment.trim() || loading}
        onClick={() => onResume(treatment, notes)}
      >
        {loading ? (
          <Loader2 className="spin" size={18} />
        ) : (
          <CheckCircle2 size={18} />
        )}
        {t.validate}
      </button>
    </section>
  );
}

function ReportView({ data, onReset, t }) {
  const report = data.state?.final_report || "";
  const [showCompare, setShowCompare] = useState(false);

  const formattedReport = useMemo(
    () =>
      report
        .split("\n")
        .filter(Boolean)
        .map((line, index) => {
          if (line.startsWith("# "))
            return <h2 key={index}>{line.replace("# ", "")}</h2>;
          if (line.startsWith("## "))
            return <h3 key={index}>{line.replace("## ", "")}</h3>;
          return <p key={index}>{line}</p>;
        }),
    [report]
  );

  const generatePDF = () => {
    import("jspdf").then(({ jsPDF }) => {
      const doc = new jsPDF();
      doc.setFillColor(44, 62, 80);
      doc.rect(0, 0, 210, 30, "F");
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(20);
      doc.text("Rapport d'Orientation Clinique", 105, 20, {
        align: "center",
      });

      doc.setTextColor(0, 0, 0);
      doc.setFontSize(11);
      const lines = report.split("\n");
      let y = 45;

      lines.forEach((line) => {
        if (y > 280) {
          doc.addPage();
          y = 20;
        }
        if (line.startsWith("#") || line.startsWith("=")) {
          doc.setFontSize(14);
          doc.setFont("helvetica", "bold");
          y += 5;
        } else {
          doc.setFontSize(11);
          doc.setFont("helvetica", "normal");
        }
        const cleanLine = line.replace(/[#=]/g, "").trim();
        if (cleanLine) {
          const splitLines = doc.splitTextToSize(cleanLine, 180);
          doc.text(splitLines, 15, y);
          y += splitLines.length * 6 + 2;
        }
      });

      doc.setFontSize(9);
      doc.setTextColor(128, 128, 128);
      doc.text(
        `Généré le ${new Date().toLocaleDateString("fr-FR")}`,
        105,
        290,
        { align: "center" }
      );
      doc.save(`rapport-${data.thread_id?.slice(0, 8)}.pdf`);
    });
  };

  return (
    <section className="workPanel reportPanel enter">
      <div className="panelHeader">
        <div>
          <p className="eyebrow">Etape finale</p>
          <h2>{t.finalReport}</h2>
        </div>
        <FileText size={24} />
      </div>

      <article className="report">{formattedReport}</article>

      <div
        style={{ display: "flex", gap: "10px", marginTop: "1rem", flexWrap: "wrap" }}
      >
        <button className="secondaryButton" onClick={generatePDF}>
          <FileDown size={18} />
          {t.exportPDF}
        </button>
        <button className="secondaryButton" onClick={() => setShowCompare(true)}>
          <GitCompare size={18} />
          {t.compare}
        </button>
        <button className="secondaryButton" onClick={onReset}>
          <RefreshCw size={18} />
          {t.newConsultation}
        </button>
      </div>
    </section>
  );
}

function HistoryPanel({ onLoadSession, currentThreadId }) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [history, setHistory] = useState([]);

  const loadHistory = () => {
    const saved = JSON.parse(localStorage.getItem("medical_history") || "[]");
    setHistory(saved);
  };

  const saveToHistory = (data) => {
    if (!data?.thread_id) return;
    const entry = {
      thread_id: data.thread_id,
      date: new Date().toISOString(),
      case: data.state?.initial_case || "Sans titre",
      status: data.status,
      has_report: !!data.state?.final_report,
    };
    const existing = JSON.parse(
      localStorage.getItem("medical_history") || "[]"
    );
    const filtered = existing.filter((h) => h.thread_id !== data.thread_id);
    const updated = [entry, ...filtered].slice(0, 50);
    localStorage.setItem("medical_history", JSON.stringify(updated));
    setHistory(updated);
  };

  useEffect(() => {
    loadHistory();
  }, []);

  const filtered = history.filter(
    (h) =>
      h.case.toLowerCase().includes(search.toLowerCase()) ||
      h.thread_id.includes(search)
  );

  const formatDate = (iso) => {
    return new Date(iso).toLocaleDateString("fr-FR", {
      day: "2-digit",
      month: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (!isOpen) {
    return (
      <button
        className="historyToggle"
        onClick={() => {
          loadHistory();
          setIsOpen(true);
        }}
        style={{
          position: "fixed",
          right: "20px",
          top: "20px",
          zIndex: 100,
          background: "#2c3e50",
          color: "white",
          border: "none",
          padding: "10px 15px",
          borderRadius: "8px",
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          gap: "8px",
        }}
      >
        <History size={20} />
        Historique ({history.length})
      </button>
    );
  }

  return (
    <div
      style={{
        position: "fixed",
        right: 0,
        top: 0,
        width: "350px",
        height: "100vh",
        background: "white",
        boxShadow: "-4px 0 15px rgba(0,0,0,0.1)",
        zIndex: 1000,
        display: "flex",
        flexDirection: "column",
      }}
    >
      <div
        style={{
          padding: "20px",
          borderBottom: "1px solid #eee",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h3 style={{ margin: 0 }}>Historique</h3>
        <button
          onClick={() => setIsOpen(false)}
          style={{ background: "none", border: "none", cursor: "pointer" }}
        >
          <X size={24} />
        </button>
      </div>

      <div style={{ padding: "15px" }}>
        <div style={{ position: "relative" }}>
          <Search
            size={16}
            style={{
              position: "absolute",
              left: "10px",
              top: "10px",
              color: "#999",
            }}
          />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Rechercher..."
            style={{
              width: "100%",
              padding: "8px 8px 8px 35px",
              borderRadius: "6px",
              border: "1px solid #ddd",
            }}
          />
        </div>
      </div>

      <div style={{ flex: 1, overflow: "auto", padding: "0 15px" }}>
        {filtered.map((entry) => (
          <div
            key={entry.thread_id}
            onClick={() => {
              onLoadSession(entry.thread_id);
              setIsOpen(false);
            }}
            style={{
              padding: "12px",
              marginBottom: "8px",
              borderRadius: "8px",
              border: "1px solid #eee",
              cursor: "pointer",
              background:
                entry.thread_id === currentThreadId ? "#e3f2fd" : "white",
              transition: "background 0.2s",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <span style={{ fontWeight: 500, fontSize: "0.9em" }}>
                {entry.case.length > 30
                  ? entry.case.slice(0, 30) + "..."
                  : entry.case}
              </span>
              {entry.has_report && <FileText size={16} color="#4caf50" />}
            </div>
            <div
              style={{ fontSize: "0.75em", color: "#666", marginTop: "4px" }}
            >
              {formatDate(entry.date)} ·{" "}
              {entry.status === "completed" ? "Terminé" : "En cours"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function Dashboard({ onClose }) {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const history = JSON.parse(
      localStorage.getItem("medical_history") || "[]"
    );

    const symptomTypes = {};
    const dailyCounts = {};
    const statusCounts = {
      completed: 0,
      in_progress: 0,
      waiting_physician: 0,
    };

    history.forEach((h) => {
      const case_lower = h.case.toLowerCase();
      let type = "Autre";
      if (
        case_lower.includes("yeux") ||
        case_lower.includes("vision")
      )
        type = "Ophtalmologique";
      else if (
        case_lower.includes("toux") ||
        case_lower.includes("gorge") ||
        case_lower.includes("respir")
      )
        type = "Respiratoire";
      else if (
        case_lower.includes("ventre") ||
        case_lower.includes("diahrrée") ||
        case_lower.includes("nausée")
      )
        type = "Digestif";
      else if (
        case_lower.includes("tête") ||
        case_lower.includes("migraine")
      )
        type = "Neurologique";
      else if (
        case_lower.includes("peau") ||
        case_lower.includes("rougeur")
      )
        type = "Dermatologique";

      symptomTypes[type] = (symptomTypes[type] || 0) + 1;

      const day = h.date.split("T")[0];
      dailyCounts[day] = (dailyCounts[day] || 0) + 1;

      statusCounts[h.status] = (statusCounts[h.status] || 0) + 1;
    });

    setStats({
      total: history.length,
      symptomTypes,
      dailyCounts,
      statusCounts,
    });
  }, []);

  if (!stats) return null;

  return (
    <div
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.5)",
        zIndex: 2000,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <div
        style={{
          background: "white",
          width: "90%",
          maxWidth: 900,
          height: "90%",
          borderRadius: 12,
          display: "flex",
          flexDirection: "column",
          padding: 30,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            marginBottom: 20,
          }}
        >
          <h2
            style={{
              margin: 0,
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            <BarChart3 size={28} /> Tableau de bord
          </h2>
          <button
            onClick={onClose}
            style={{ background: "none", border: "none", cursor: "pointer" }}
          >
            <X size={24} />
          </button>
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "1fr 1fr",
            gap: 20,
            flex: 1,
            overflow: "auto",
          }}
        >
          <div
            style={{
              background: "#f8f9fa",
              padding: 20,
              borderRadius: 8,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <h3>Types de symptômes</h3>
            <div style={{ fontSize: "3em", fontWeight: "bold", color: "#3498db" }}>
              {Object.keys(stats.symptomTypes).length}
            </div>
            <div style={{ color: "#666" }}>catégories identifiées</div>
            <ul style={{ marginTop: 15, textAlign: "left" }}>
              {Object.entries(stats.symptomTypes).map(([k, v]) => (
                <li key={k}>
                  {k}: {v}
                </li>
              ))}
            </ul>
          </div>

          <div
            style={{
              background: "#f8f9fa",
              padding: 20,
              borderRadius: 8,
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <h3>Statut des consultations</h3>
            <div style={{ display: "flex", gap: 20, marginTop: 15 }}>
              <div style={{ textAlign: "center" }}>
                <div
                  style={{
                    fontSize: "2em",
                    fontWeight: "bold",
                    color: "#2ecc71",
                  }}
                >
                  {stats.statusCounts.completed || 0}
                </div>
                <div style={{ fontSize: "0.8em", color: "#666" }}>Terminés</div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div
                  style={{
                    fontSize: "2em",
                    fontWeight: "bold",
                    color: "#f39c12",
                  }}
                >
                  {stats.statusCounts.in_progress || 0}
                </div>
                <div style={{ fontSize: "0.8em", color: "#666" }}>En cours</div>
              </div>
              <div style={{ textAlign: "center" }}>
                <div
                  style={{
                    fontSize: "2em",
                    fontWeight: "bold",
                    color: "#e74c3c",
                  }}
                >
                  {stats.statusCounts.waiting_physician || 0}
                </div>
                <div style={{ fontSize: "0.8em", color: "#666" }}>
                  Attente médecin
                </div>
              </div>
            </div>
          </div>

          <div
            style={{
              background: "#f8f9fa",
              padding: 20,
              borderRadius: 8,
              gridColumn: "1 / -1",
            }}
          >
            <h3>Activité quotidienne (7 derniers jours)</h3>
            <div
              style={{
                display: "flex",
                alignItems: "flex-end",
                gap: 10,
                height: 150,
                marginTop: 15,
              }}
            >
              {Object.entries(stats.dailyCounts)
                .slice(-7)
                .map(([day, count]) => (
                  <div
                    key={day}
                    style={{
                      flex: 1,
                      display: "flex",
                      flexDirection: "column",
                      alignItems: "center",
                      gap: 5,
                    }}
                  >
                    <div
                      style={{
                        width: "100%",
                        background: "#3498db",
                        borderRadius: "4px 4px 0 0",
                        height: `${Math.min(count * 20, 120)}px`,
                        minHeight: 5,
                      }}
                    />
                    <div style={{ fontSize: "0.7em", color: "#666" }}>
                      {day.slice(5)}
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>

        <div
          style={{
            marginTop: 20,
            textAlign: "center",
            fontSize: "1.2em",
            color: "#2c3e50",
          }}
        >
          Total: <strong>{stats.total}</strong> consultations
        </div>
      </div>
    </div>
  );
}

function LanguageSelector({ current, onChange }) {
  return (
    <select
      value={current}
      onChange={(e) => onChange(e.target.value)}
      style={{
        padding: "8px 12px",
        borderRadius: 6,
        border: "1px solid #ddd",
        background: "white",
        cursor: "pointer",
      }}
    >
      {languages.map((l) => (
        <option key={l.code} value={l.code}>
          {l.flag} {l.name}
        </option>
      ))}
    </select>
  );
}

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lang, setLang] = useState("fr");
  const [showDashboard, setShowDashboard] = useState(false);
  const [imageData, setImageData] = useState(null);
  const activeStep = getActiveStep(data);
  const historyRef = useRef(null);

  const t = translations[lang];

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
      return payload;
    } catch (event) {
      setError(event.message || "Impossible de contacter l'API FastAPI");
      return null;
    } finally {
      setLoading(false);
    }
  }

  function startConsultation(initialCase) {
    request("/consultation/start", {
      method: "POST",
      body: JSON.stringify({ patient_case: initialCase }),
    }).then((result) => {
      if (result && historyRef.current) {
        historyRef.current.saveToHistory(result);
      }
    });
  }

  function resumeConsultation(answer) {
    request("/consultation/resume", {
      method: "POST",
      body: JSON.stringify({ thread_id: data.thread_id, answer }),
    }).then((result) => {
      if (result && historyRef.current) {
        historyRef.current.saveToHistory(result);
      }
    });
  }

  function submitPhysicianReview(treatment, notes) {
    request(`/consultation/${data.thread_id}/physician-review`, {
      method: "POST",
      body: JSON.stringify({
        thread_id: data.thread_id,
        treatment: treatment,
        notes: notes || "",
      }),
    }).then((result) => {
      if (result && historyRef.current) {
        historyRef.current.saveToHistory(result);
      }
    });
  }

  function reset() {
    setData(null);
    setError("");
    setImageData(null);
  }

  return (
    <main className="appShell">
      <HistoryPanel
        ref={historyRef}
        onLoadSession={(id) => {
          fetch(`${API_URL}/consultation/${id}`)
            .then((r) => r.json())
            .then(setData);
        }}
        currentThreadId={data?.thread_id}
      />

      <div
        style={{
          position: "fixed",
          top: 20,
          left: 20,
          zIndex: 100,
          display: "flex",
          gap: 10,
        }}
      >
        <LanguageSelector current={lang} onChange={setLang} />
        <button
          onClick={() => setShowDashboard(true)}
          style={{
            padding: "8px 12px",
            borderRadius: 6,
            border: "1px solid #ddd",
            background: "white",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            gap: 5,
          }}
        >
          <BarChart3 size={16} />
          Dashboard
        </button>
      </div>

      {showDashboard && <Dashboard onClose={() => setShowDashboard(false)} />}

      <StatusCard data={data} t={t} />
      <div className="mainColumn">
        <Stepper activeStep={activeStep} />
        {error && <div className="errorBox">{error}</div>}

        {!data && (
          <CaseForm
            onStart={startConsultation}
            loading={loading}
            t={t}
            onImageUpload={setImageData}
          />
        )}
        {data?.interrupt?.type === "patient_question" && (
          <QuestionForm
            data={data}
            onResume={resumeConsultation}
            loading={loading}
            t={t}
          />
        )}
        {data?.interrupt?.type === "physician_review" && (
          <PhysicianReview
            data={data}
            onResume={submitPhysicianReview}
            loading={loading}
            t={t}
          />
        )}
        {data?.state?.final_report && (
          <ReportView data={data} onReset={reset} t={t} />
        )}
      </div>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);