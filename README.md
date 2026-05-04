# Projet Multi-Agents Médical avec LangGraph

Application académique d'orientation clinique préliminaire basée sur LangGraph, FastAPI, MCP et Streamlit.

> Ce système ne remplace pas une consultation médicale.

## Objectif

Le projet simule un workflow multi-agents médical :

1. un utilisateur saisit un cas patient ;
2. le Diagnostic Agent pose 5 questions successives ;
3. le système génère une synthèse clinique préliminaire ;
4. une recommandation intermédiaire prudente est proposée ;
5. un médecin traitant intervient via Human-in-the-Loop ;
6. le Report Agent produit un rapport final structuré.

## Architecture

```text
backend/
  app/
    graph.py
    state.py
    api.py
    nodes/
      supervisor.py
      diagnostic_agent.py
      physician_review.py
      report_agent.py
    tools/
      patient_tools.py
      care_tools.py
      mcp_client.py
  langgraph.json
  requirements.txt
mcp_server/
  server.py
  data/red_flags.md
frontend/
  streamlit_app.py
README.md
```

## Agents

- `Supervisor` : orchestre les transitions du graphe.
- `Diagnostic Agent` : pose 5 questions, collecte les réponses, produit la synthèse clinique préliminaire.
- `Physician Review` : interruption Human-in-the-Loop pour la validation du médecin traitant.
- `Report Agent` : génère le rapport final.

## Endpoints FastAPI

- `POST /sessions/start`
- `POST /consultation/start`
- `POST /consultation/resume`
- `GET /consultation/{thread_id}`
- `GET /consultation/{thread_id}/report`

## Installation

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Lancer l'API

```bash
cd backend
uvicorn app.api:app --reload --port 8000
```

Documentation API :

```text
http://127.0.0.1:8000/docs
```

## Lancer le frontend

Dans un deuxième terminal :

```bash
cd frontend
streamlit run streamlit_app.py
```

## Lancer le serveur MCP

```bash
python mcp_server/server.py
```

L'outil MCP exposé est `red_flags_reference`, utilisé comme référence de signes d'alerte généraux.

## Test LangGraph Studio

Depuis le dossier `backend` :

```bash
langgraph dev
```

Le fichier `backend/langgraph.json` déclare le graphe :

```text
medical_orientation -> ./app/graph.py:graph
```

Points à vérifier dans Studio :

- transition `START -> supervisor -> diagnostic_agent` ;
- 5 interruptions patient ;
- génération de la recommandation intermédiaire ;
- interruption `physician_review` ;
- génération du rapport final ;
- transition finale vers `END`.

## Jeux de tests

### Cas 1 : syndrome respiratoire simple

Cas initial : toux, nez qui coule, fatigue légère depuis 2 jours, pas de gêne respiratoire.

Résultat attendu : 5 questions, recommandation repos/hydratation/surveillance, revue médecin, rapport final.

### Cas 2 : cas avec red flags

Cas initial : fièvre élevée persistante avec difficulté respiratoire et douleur thoracique.

Résultat attendu : 5 questions, recommandation de consultation rapide, revue médecin prioritaire, rapport final prudent.

### Cas 3 : cas bénin

Cas initial : léger mal de tête après une journée de travail, pas de fièvre, pas d'autre symptôme.

Résultat attendu : 5 questions, recommandation générale de repos/surveillance, revue médecin, rapport final.

## Captures d'écran

Ajouter ici les captures demandées dans Classroom :

### LangGraph Studio

![Capture LangGraph Studio](docs/screenshots/langgraph-studio.png)

### API FastAPI

![Capture FastAPI](docs/screenshots/fastapi-docs.png)

### Frontend Streamlit

![Capture Frontend](docs/screenshots/frontend.png)

### Rapport final

![Capture Rapport final](docs/screenshots/final-report.png)

## Commandes Git recommandées

```bash
git init
git add .
git commit -m "Initial project structure"
git commit -m "Add LangGraph medical workflow"
git commit -m "Expose FastAPI consultation endpoints"
git commit -m "Add MCP reference tool and Streamlit frontend"
git commit -m "Document setup, tests and screenshots"
```

## Création du repository GitHub privé

Créer un repository privé GitHub pour le groupe, puis ajouter le collaborateur demandé par le professeur.

Avec GitHub CLI, la création du dépôt peut se faire ainsi :

```bash
gh repo create NOM_DU_REPO --private --source . --remote origin --push
```

Pour l'ajout du collaborateur, utiliser l'interface GitHub :

```text
Repository -> Settings -> Collaborators -> Add people -> m.youssfi@enset-media.ac.ma
```

Si le username GitHub du professeur est connu, l'ajout peut aussi être fait avec :

```bash
gh api -X PUT repos/OWNER/NOM_DU_REPO/collaborators/USERNAME_GITHUB -f permission=push
```

Déposer ensuite le lien du repository dans Classroom.
