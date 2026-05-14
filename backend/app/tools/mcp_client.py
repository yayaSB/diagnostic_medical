def get_red_flags_reference() -> str:
    return (
        "Signes d'alerte généraux : douleur thoracique, difficulté respiratoire, "
        "confusion, malaise important, saignement, forte fièvre persistante."
    )

def search_medical_context(symptoms: str, answers: list[str]) -> str:
    """Simule une recherche MCP/contextuelle selon les symptômes."""
    
    joined = " ".join([symptoms, *answers]).lower()
    
    contexts = []
    
    if any(w in joined for w in ["yeux", "rouge", "vision", "larme"]):
        contexts.append(
            "Contexte ophtalmologique: possible conjonctivite, kératite, "
            "allergie oculaire ou irritation. Surveiller: douleur oculaire intense, "
            "perte de vision, photophobie, écoulement purulent."
        )
    
    if any(w in joined for w in ["toux", "gorge", "nez", "fièvre"]):
        contexts.append(
            "Contexte ORL/respiratoire: possible rhume, grippe, COVID-19, "
            "bronchite ou sinusite. Surveiller: dyspnée, fièvre >39°C, "
            "durée >7 jours, douleur thoracique."
        )
    
    if any(w in joined for w in ["ventre", "diahrrée", "nausée", "vomir", "manger"]):
        contexts.append(
            "Contexte gastro-entérologique: possible gastro-entérite, "
            "intoxication alimentaire ou syndrome grippal. Surveiller: "
            "déshydratation, sang dans les selles, douleur intense."
        )
    
    if any(w in joined for w in ["tête", "migraine", "mal de crâne"]):
        contexts.append(
            "Contexte neurologique: possible céphalée tensionnelle, "
            "migraine ou sinusite. Surveiller: céphalée brutale 'comme jamais', "
            "troubles visuels, raideur de la nuque."
        )
    
    if any(w in joined for w in ["peau", "rougeur", "démange", "bouton"]):
        contexts.append(
            "Contexte dermatologique: possible allergie, infection cutanée "
            "ou éruption virale. Surveiller: extension rapide, fièvre, "
            "bulles, signes d'infection."
        )
    
    if not contexts:
        contexts.append(
            "Contexte général: symptômes non spécifiques. Surveiller: "
            "apparition de signes d'alerte, persistance >3 jours, aggravation."
        )
    
    return "\n\n".join(contexts)