def recommend_interim_care(initial_case: str, answers: list[str], mcp_context: str = "") -> str:
    joined = " ".join([initial_case, *answers]).lower()
    red_flags = ["douleur thoracique", "difficulte respiratoire", "difficulté respiratoire", "confusion", "sang", "malaise", "forte fièvre"]

    if any(flag in joined for flag in red_flags):
        base = (
            "Recommandation intermédiaire prudente : surveillance rapprochée et consultation médicale rapide, "
            "en particulier si les symptômes persistent ou s'aggravent."
        )
    else:
        base = (
            "Recommandation intermédiaire générale : repos, hydratation, surveillance de l'évolution, "
            "et consultation en cas d'aggravation ou d'apparition de signes d'alerte."
        )

    if mcp_context:
        return f"{base}\n\nRéférence MCP utilisée : {mcp_context}"
    return base