# Rapport de projet : Système multi-agents médical avec LangGraph

## 1. Présentation générale

Ce projet est une application académique qui simule un workflow d'orientation clinique préliminaire avec un système multi-agents. Il utilise **LangGraph** pour orchestrer les agents, **FastAPI** pour exposer le backend, **MCP** pour fournir un outil externe de référence, **OpenAI via LangChain** pour générer les textes cliniques, et **React + Vite** pour l'interface utilisateur.

> **Mention obligatoire :** Ce système ne remplace pas une consultation médicale.

Le système ne fournit pas de diagnostic définitif. Il produit une synthèse clinique préliminaire, une recommandation intermédiaire prudente, puis un rapport final après validation humaine par un médecin traitant.

---

## 2. Objectifs du projet

- Modéliser un workflow multi-agents avec LangGraph  
- Gérer un état partagé entre les agents  
- Intégrer des tools pour les questions patient et les recommandations  
- Ajouter une étape **Human-in-the-Loop**  
- Exposer le workflow via FastAPI  
- Intégrer MCP  
- Connecter un frontend React  
- Tester le graphe dans LangGraph Studio  
- Documenter le projet avec captures d’écran  

---

## 3. Technologies utilisées

| Partie | Technologie |
|------|--------|
| Orchestration | LangGraph |
| LLM | LangChain + OpenAI |
| Backend | FastAPI |
| Human-in-the-loop | Interruptions LangGraph |
| MCP | Serveur externe |
| Frontend | React + Vite |
| UI | Lucide React |
| Export | jsPDF, html2canvas |
| Charts | Chart.js |
| Docs API | Swagger UI |
| Versioning | Git, GitHub |

---

## 4. Architecture du projet

```text
project/
├── backend/
│   ├── app/
│   │   ├── api.py
│   │   ├── graph.py
│   │   ├── llm.py
│   │   ├── state.py
│   │   ├── nodes/
│   │   │   ├── supervisor.py
│   │   │   ├── diagnostic_agent.py
│   │   │   ├── physician_review.py
│   │   │   └── report_agent.py
│   │   └── tools/
│   │       ├── patient_tools.py
│   │       ├── care_tools.py
│   │       ├── mcp_client.py
│   │       ├── urgency_scorer.py
│   │       └── medical_sources.py
│   ├── langgraph.json
│   └── requirements.txt
├── mcp_server/
│   └── server.py
├── frontend/
│   ├── src/
│   │   ├── i18n.js
│   │   └── components/
│   │       ├── ExportPDF.jsx
│   │       ├── HistoryPanel.jsx
│   │       ├── CompareView.jsx
│   │       ├── Dashboard.jsx
│   │       ├── LanguageSelector.jsx
│   │       ├── ImageUpload.jsx
│   │       ├── UrgencyBadge.jsx
│   │       └── MedicalSources.jsx
└── README.md
```

## 5. Architecture du projet

flowchart TD
A[START] --> B[Supervisor]
B --> C[Diagnostic Agent]
C --> D[Questions dynamiques IA]
D --> E[Synthèse + Recommandation]
E --> F[Physician Review]
F --> G[Report Agent]
G --> H[END]

## Étapes du workflow

- Cas initial patient  
- Questions dynamiques IA  
- Synthèse clinique + diagnostic différentiel  
- Recommandation intermédiaire  
- Intervention médecin (HITL)  
- Rapport final structuré  

---

## 6. État partagé LangGraph

- messages  
- next  
- thread_id  
- initial_case  
- questions  
- patient_answers  
- question_count  
- interim_care  
- diagnostic_summary  
- physician_treatment  
- physician_notes  
- final_report  
- mcp_context  
- mcp_search  
- urgency  

---

## 7. Description des agents

### 7.1 Supervisor
Orchestre le workflow et contrôle la progression des étapes.

---

### 7.2 Diagnostic Agent
- Pose 5 questions dynamiques IA  
- Analyse les réponses patient  
- Génère une synthèse clinique  
- Appelle MCP  
- Produit une recommandation intermédiaire  

---

### 7.3 Physician Review (HITL)
Étape Human-in-the-loop :

- synthèse clinique  
- recommandation  
- score d’urgence  
- contexte MCP  
- décision médicale  

---

### 7.4 Report Agent
Génère un rapport final structuré en **8 sections**.

---

## 8. Tools internes

### generate_dynamic_question
Questions adaptées au contexte patient.

---

### recommend_interim_care
Recommandations médicales intermédiaires.

---

### search_medical_context
Recherche MCP selon le type de symptômes :

- respiratoire  
- ophtalmologique  
- digestif  
- neurologique  
- dermatologique  

---

### calculate_urgency_score
Score d’urgence :

- 🔴 60–100 : urgent  
- 🟠 30–59 : rapide  
- 🟡 10–29 : surveillance  
- 🟢 0–9 : mineur  

---

### get_medical_sources
Sources médicales (HAS, etc.)

---

## 9. Intégration OpenAI

Configuration :

```env
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4o-mini
```

## Fonctionnalités

- questions dynamiques  
- synthèse clinique  
- rapport final  
- recommandations  
- analyse d’image  

Fallback local si clé absente.

---

## 10. Intégration MCP

Serveur MCP :

- `red_flags_reference`

### Signes d’alerte :

- douleur thoracique  
- dyspnée  
- confusion  
- malaise  
- saignement  
- fièvre persistante  

---

## 11. API FastAPI

| Méthode | Endpoint |
|--------|---------|
| POST | /consultation/start |
| POST | /consultation/resume |
| POST | /consultation/{id}/physician-review |
| GET | /consultation/{id} |
| GET | /consultation/{id}/report |
| POST | /analyze-image |

---

## 12. Frontend

### Fonctionnalités

- cas initial patient  
- questions dynamiques IA  
- score d’urgence  
- revue médecin (HITL)  
- rapport final  
- export PDF  
- historique  
- dashboard  
- multi-langue  

---

## 13. Installation

### Backend

```bash
cd backend
uv venv
.venv\Scripts\activate
uv sync

## Frontend
cd frontend  
npm install  

---

## 14. Exécution

### Backend
uvicorn app.api:app --reload --port 8000  

### Frontend
npm run dev  

### MCP Server
python mcp_server/server.py  

---

## 15. Tests réalisés
- consultation complète  
- questions dynamiques  
- score urgence  
- MCP contextuel  
- HITL médecin  
- rapport final  

---

## 16. Cas de test

### Cas respiratoire
Toux + fatigue → surveillance  

### Cas grave
Fièvre + douleur thoracique → urgence  

### Cas ophtalmologique
Yeux rouges → contexte MCP ophtalmologique  

---

## 17. Captures d’écran
À ajouter dans `docs/screenshots/`

---

## 18. Sécurité et éthique
- pas un dispositif médical  
- pas de diagnostic définitif  
- validation humaine obligatoire  
- prudence systématique  

---

## 19. Git
git add .  
git commit -m "update"  
git push  

---

## 20. Conclusion

Système multi-agents médical pédagogique basé sur :

- LangGraph  
- FastAPI  
- MCP  
- OpenAI  
- React  

Avec :

- IA dynamique  
- score d’urgence  
- HITL médecin  
- rapport structuré  
- export PDF & dashboard  