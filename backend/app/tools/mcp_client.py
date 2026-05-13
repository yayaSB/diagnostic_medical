import httpx

class MCPClient:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_medical_guidelines(self, condition: str) -> str:
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/guidelines",
                json={"condition": condition}
            )
            response.raise_for_status()
            return response.json().get("guidelines", "Guidelines non disponibles")
        except Exception as e:
            return f"Erreur MCP: {str(e)}"
    
    async def check_drug_interactions(self, medications: list) -> str:
        try:
            response = await self.client.post(
                f"{self.base_url}/tools/drug-interactions",
                json={"medications": medications}
            )
            response.raise_for_status()
            return response.json().get("interactions", "Aucune interaction detectee")
        except Exception as e:
            return f"Erreur MCP: {str(e)}"
    
    async def close(self):
        await self.client.aclose()

mcp_client = MCPClient()