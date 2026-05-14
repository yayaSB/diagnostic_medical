def get_red_flags_reference() -> str:
    """Minimal MCP-backed knowledge hook.

    In demo mode this function returns the same clinical safety reference used by
    the MCP server. The separate mcp_server/server.py exposes it as an MCP tool
    for Studio/client integration.
    """
    return (
        "Signes d'alerte généraux : douleur thoracique, difficulté respiratoire, "
        "confusion, malaise important, saignement, forte fièvre persistante."
    )