from mcp.server.fastmcp import FastMCP

mcp = FastMCP("medical-reference-tools")


@mcp.tool()
def red_flags_reference() -> str:
    """Return general safety red flags used by the diagnostic agent."""
    return (
        "Signes d'alerte généraux : douleur thoracique, difficulté respiratoire, "
        "confusion, malaise important, saignement, forte fièvre persistante."
    )


if __name__ == "__main__":
    mcp.run()