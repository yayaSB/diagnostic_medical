from app.llm import call_openai


def _fallback_question(initial_case: str, previous_answers: list[str], question_number: int) -> str:
    text = " ".join([initial_case, *previous_answers]).lower()

    if question_number == 1:
        if any(word in text for word in ["toux", "respir", "gorge", "rhume"]):
            return "Depuis quand avez-vous ces symptomes respiratoires et ont-ils commence brutalement ou progressivement ?"
        if any(word in text for word in ["ventre", "abdominal", "diarrhee", "vomissement", "nausee"]):
            return "Depuis quand avez-vous les symptomes digestifs et sont-ils associes a des vomissements ou une diarrhee ?"
        if any(word in text for word in ["tete", "migraine", "vertige"]):
            return "Depuis quand avez-vous mal a la tete et la douleur est-elle inhabituelle pour vous ?"
        return "Depuis quand les symptomes ont-ils commence et comment ont-ils evolue ?"

    if question_number == 2:
        return "Quelle est l'intensite actuelle des symptomes sur une echelle de 1 a 10 ?"

    if question_number == 3:
        if any(word in text for word in ["toux", "respir", "thorac", "poitrine"]):
            return "Avez-vous une difficulte respiratoire, une douleur thoracique, une fievre elevee ou des crachats inhabituels ?"
        if any(word in text for word in ["ventre", "abdominal", "diarrhee", "vomissement"]):
            return "Avez-vous du sang dans les selles, une douleur abdominale intense, une fievre elevee ou des signes de deshydratation ?"
        return "Avez-vous de la fievre, une douleur importante, un malaise, une confusion ou un autre signe d'alerte ?"

    if question_number == 4:
        return "Avez-vous des antecedents medicaux, allergies, grossesse possible ou traitements en cours importants ?"

    return "Qu'est-ce qui aggrave ou soulage les symptomes, et y a-t-il un element recent particulier a signaler ?"


def ask_patient(
    initial_case: str,
    previous_questions: list[str],
    previous_answers: list[str],
    question_number: int,
    mcp_context: str,
) -> tuple[str, str]:
    dialog = "\n".join(
        f"Q{i + 1}: {question}\nR{i + 1}: {previous_answers[i]}"
        for i, question in enumerate(previous_questions)
    )
    ai_question = call_openai(
        system_prompt=(
            "Tu es un agent d'orientation clinique preliminaire. "
            "Tu poses une seule question patient a la fois. "
            "La question doit etre personnalisee selon le cas et les reponses precedentes. "
            "Tu ne poses pas de diagnostic et tu restes prudent."
        ),
        user_prompt=(
            f"Cas initial du patient:\n{initial_case}\n\n"
            f"Questions et reponses deja obtenues:\n{dialog or 'Aucune pour le moment.'}\n\n"
            f"Reference de securite:\n{mcp_context}\n\n"
            f"Genere la question numero {question_number}/5. "
            "Retourne uniquement la question, sans introduction, sans liste et sans explication. "
            "Evite de repeter une question deja posee."
        ),
        temperature=0.35,
    )

    if ai_question:
        question = ai_question.strip().strip('"')
        if question and question not in previous_questions:
            return question, "ai"

    return _fallback_question(initial_case, previous_answers, question_number), "fallback"
