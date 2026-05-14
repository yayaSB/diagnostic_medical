from backend.app.llm import call_openai

def recommend_interim_care(initial_case: str, answers: list[str], mcp_context: str = "") -> str:
    """Génère une recommandation personnalisée avec OpenAI selon le contexte."""
    
    joined = " ".join([initial_case, *answers]).lower()
    
    # Détection basique pour cas urgents (red flags)
    urgent_flags = ["douleur thoracique", "difficulte respiratoire", "difficulté respiratoire", 
                    "confusion", "sang", "malaise important", "forte fièvre", "perte de vision",
                    "douleur intense", "saignement"]
    
    is_urgent = any(flag in joined for flag in urgent_flags)
    
    # Appel OpenAI pour recommandation personnalisée
    system_prompt = (
        "Tu es un assistant médical pédagogique. Tu rédiges UNE SEULE recommandation "
        "intermédiaire concise (2-3 phrases max), personnalisée au cas du patient. "
        "Tu ne répètes pas les symptômes, tu donnes des conseils concrets. "
        "Si c'est urgent, tu insistes sur la consultation rapide. Sinon, repos/surveillance."
    )
    
    user_prompt = (
        f"Cas: {initial_case}\n"
        f"Réponses: {' | '.join(answers)}\n"
        f"Contexte médical: {mcp_context[:300]}\n\n"
        f"Urgence détectée: {'OUI' if is_urgent else 'NON'}\n\n"
        "Rédige une recommandation intermédiaire UNIQUE et SPÉCIFIQUE:"
    )
    
    llm_result = call_openai(system_prompt, user_prompt, temperature=0.3)
    if llm_result:
        return llm_result.strip()
    
    # Fallback local amélioré
    if is_urgent:
        return (
            "⚠️ Recommandation urgente : consultation médicale rapide recommandée "
            "en raison de signes potentiellement graves. Ne pas attendre."
        )
    
    return (
        f"Recommandation pour '{initial_case[:30]}...' : "
        "repos, hydratation, surveillance attentive. "
        "Consulter si aggravation ou nouveaux symptômes."
    )