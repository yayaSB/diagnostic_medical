def calculate_urgency_score(case: str, answers: list[str]) -> dict:
    """Calcule un score d'urgence 0-100 avec code couleur."""
    
    joined = " ".join([case, *answers]).lower()
    score = 0
    flags = []
    
    # Critères rouges (+40 chacun)
    red_flags = {
        "perte de conscience": "Perte de conscience",
        "difficulte respiratoire": "Dyspnée",
        "douleur thoracique": "Douleur thoracique",
        "saignement": "Saignement actif",
        "arret cardiaque": "Arrêt cardiaque",
    }
    
    for keyword, label in red_flags.items():
        if keyword in joined:
            score += 40
            flags.append({"level": "red", "label": label})
    
    # Critères orange (+20 chacun)
    orange_flags = {
        "fievre": "Fièvre",
        "vomissement": "Vomissements",
        "douleur intense": "Douleur intense",
        "confusion": "Confusion",
        "malaise": "Malaise",
    }
    
    for keyword, label in orange_flags.items():
        if keyword in joined:
            score += 20
            flags.append({"level": "orange", "label": label})
    
    # Critères jaunes (+10 chacun)
    yellow_flags = {
        "toux": "Toux",
        "fatigue": "Fatigue",
        "nausée": "Nausées",
        "mal de tete": "Céphalée",
    }
    
    for keyword, label in yellow_flags.items():
        if keyword in joined:
            score += 10
            flags.append({"level": "yellow", "label": label})
    
    # Cap à 100
    score = min(score, 100)
    
    # Code couleur
    if score >= 60:
        color = "red"
        label = "URGENT"
        action = "Consultation immédiate recommandée"
    elif score >= 30:
        color = "orange"
        label = "MODÉRÉ"
        action = "Consultation rapide (24h)"
    elif score >= 10:
        color = "yellow"
        label = "FAIBLE"
        action = "Surveillance et consultation si aggravation"
    else:
        color = "green"
        label = "MINIME"
        action = "Auto-soins, consulter si persistance >3 jours"
    
    return {
        "score": score,
        "color": color,
        "label": label,
        "action": action,
        "flags": flags
    }