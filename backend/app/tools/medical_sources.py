def get_medical_sources(symptoms: str) -> list:
    """Retourne des liens vers guidelines selon les symptômes."""
    
    sources = []
    s = symptoms.lower()
    
    if any(w in s for w in ["yeux", "conjonctiv", "kératit"]):
        sources.append({
            "title": "Conjonctivite - HAS",
            "url": "https://www.has-sante.fr/jcms/c_2875743/fr/conjonctivite-aigue-de-l-adulte-et-de-l-enfant",
            "type": "guideline"
        })
        sources.append({
            "title": "Kératite - Orphanet",
            "url": "https://www.orpha.net/consor/cgi-bin/OC_Exp.php?Lng=FR&Expert=280104",
            "type": "reference"
        })
    
    if any(w in s for w in ["toux", "bronchit", "pneumoni"]):
        sources.append({
            "title": "Bronchite aiguë - HAS",
            "url": "https://www.has-sante.fr/jcms/c_2875745/fr/bronchite-aigue",
            "type": "guideline"
        })
    
    if any(w in s for w in ["tête", "migraine", "céphalée"]):
        sources.append({
            "title": "Céphalées - HAS",
            "url": "https://www.has-sante.fr/jcms/c_2875747/fr/cephalees",
            "type": "guideline"
        })
    
    if not sources:
        sources.append({
            "title": "Guide des urgences - SOS Médecins",
            "url": "https://www.sos-medecins.fr/",
            "type": "general"
        })
    
    return sources