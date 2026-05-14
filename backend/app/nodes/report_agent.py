from app.llm import call_openai
from app.state import MedicalState


def _fallback_report(state: MedicalState) -> str:
    return f"""# Rapport final d'orientation clinique

## Cas initial
{state.get("initial_case", "Non renseigné")}

## Synthèse clinique préliminaire
{state.get("diagnostic_summary", "Non disponible")}

## Recommandation intermédiaire
{state.get("interim_care", "Non disponible")}

## Revue du médecin traitant
{state.get("physician_treatment", "Non renseigné")}

## Mention éthique
Ce système ne remplace pas une consultation médicale.
"""


def report_agent(state: MedicalState) -> MedicalState:
    report = call_openai(
        system_prompt=(
            "Tu es un agent de génération de rapport médical pédagogique. "
            "Tu produis un rapport final structuré en Markdown. "
            "Tu ne dois pas présenter le résultat comme un diagnostic définitif."
        ),
        user_prompt=(
            "Rédige un rapport final d'orientation clinique en français avec les sections : "
            "Cas initial, Synthèse clinique préliminaire, Recommandation intermédiaire, "
            "Revue du médecin traitant, Mention éthique.\n\n"
            f"Cas initial:\n{state.get('initial_case', 'Non renseigné')}\n\n"
            f"Synthèse clinique préliminaire:\n{state.get('diagnostic_summary', 'Non disponible')}\n\n"
            f"Recommandation intermédiaire:\n{state.get('interim_care', 'Non disponible')}\n\n"
            f"Revue du médecin traitant:\n{state.get('physician_treatment', 'Non renseigné')}\n\n"
            "La mention éthique exacte doit apparaître : "
            "Ce système ne remplace pas une consultation médicale."
        ),
    ) or _fallback_report(state)
    return {"final_report": report}
