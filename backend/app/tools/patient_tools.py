QUESTIONS = [
    "Depuis quand les symptômes ont-ils commencé ?",
    "Quelle est l'intensité des symptômes sur une échelle de 1 à 10 ?",
    "Avez-vous de la fièvre, une gêne respiratoire ou une douleur importante ?",
    "Avez-vous des antécédents médicaux, allergies ou traitements en cours ?",
    "Les symptômes s'aggravent-ils ou y a-t-il des signes inhabituels ?",
]


def ask_patient(question_count: int) -> str:
    return QUESTIONS[question_count]
