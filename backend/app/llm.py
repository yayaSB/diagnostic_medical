import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def call_openai(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key in {"remplace_par_ta_vraie_cle", "sk-votre-cle-api-ici"}:
        return None

    try:
        from langchain_openai import ChatOpenAI
    except ImportError:
        return None

    try:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=api_key,
            timeout=8,
            max_retries=0,
        )
        response = llm.invoke(
            [
                ("system", system_prompt),
                ("human", user_prompt),
            ]
        )
        return str(response.content)
    except Exception:
        return None
