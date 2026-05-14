from backend.app.llm import call_openai

QUESTIONS = [
    "Depuis quand les symptômes ont-ils commencé ?",
    "Quelle est l'intensité des symptômes sur une échelle de 1 à 10 ?",
    "Avez-vous de la fièvre, une gêne respiratoire ou une douleur importante ?",
    "Avez-vous des antécédents médicaux, allergies ou traitements en cours ?",
    "Les symptômes s'aggravent-ils ou y a-t-il des signes inhabituels ?",
]

def ask_patient(question_count: int) -> str:
    return QUESTIONS[question_count]

def generate_dynamic_question(case: str, previous_answers: list[str], question_number: int) -> str:
    """Génère une question personnalisée avec OpenAI selon le contexte."""
    
    if question_number >= len(QUESTIONS):
        return QUESTIONS[-1]
    
    base_question = QUESTIONS[question_number]
    
    if not previous_answers:
        return base_question
    
    context = " ".join(previous_answers).lower()
    
    # Questions contextuelles enrichies
    if question_number == 2 and ("fièvre" in context or "fievre" in context or "chaud" in context):
        return "À quelle température est montée la fièvre ? Dure-t-elle depuis plus de 3 jours ?"
    
    if question_number == 2 and ("toux" in context or "respiratoire" in context):
        return "La toux est-elle sèche ou grasse ? Avez-vous du mucus coloré ?"
    
    if question_number == 2 and ("yeux" in context or "rouge" in context or "vision" in context):
        return "Les yeux sont-ils douloureux, démangent-ils ou y a-t-il un écoulement ?"
    
    if question_number == 4 and ("aggravation" in context or "pire" in context):
        return "Quels signes nouveaux sont apparus depuis le début ?"
    
    # Fallback: demander à OpenAI de personnaliser
    system_prompt = (
        "Tu es un médecin généraliste. Tu poses une question de suivi concise "
        "et pertinente basée sur les symptômes déjà mentionnés. Maximum 15 mots."
    )
    user_prompt = (
        f"Cas: {case}. Réponses déjà données: {' | '.join(previous_answers)}.\n"
        f"Question de base: {base_question}\n"
        "Adapte cette question au contexte ou pose une question de suivi plus ciblée."
    )
    
    llm_result = call_openai(system_prompt, user_prompt, temperature=0.4)
    if llm_result:
        return llm_result.strip().strip('"')
    
    return base_question