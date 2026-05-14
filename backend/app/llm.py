import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from multiple locations
env_paths = [
    Path(__file__).resolve().parents[1] / ".env",      # backend/.env
    Path(__file__).resolve().parents[2] / ".env",      # root/.env
    Path.cwd() / ".env",                                # cwd/.env
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ .env loaded: {env_path}")
        break
else:
    print("⚠️ No .env found")

def call_openai(system_prompt: str, user_prompt: str, temperature: float = 0.2) -> str | None:
    """Call OpenAI API via LangChain."""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("❌ OPENAI_API_KEY missing")
        return None
    
    if len(api_key) < 20:
        print(f"❌ Key too short: {len(api_key)} chars")
        return None
    
    if api_key in {"remplace_par_ta_vraie_cle", "sk-votre-cle-api-ici", ""}:
        print("❌ Key is placeholder")
        return None

    try:
        from langchain_openai import ChatOpenAI
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return None

    try:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        llm = ChatOpenAI(model=model, temperature=temperature, api_key=api_key)
        response = llm.invoke(
            [
                ("system", system_prompt),
                ("human", user_prompt),
            ]
        )
        print(f"✅ OpenAI response: {str(response.content)[:100]}...")
        return str(response.content)
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return None


def call_openai_dual(system_prompt: str, user_prompt: str) -> dict:
    """Call GPT and return with confidence."""
    result = call_openai(system_prompt, user_prompt, temperature=0.2)
    return {
        "model": "gpt-4o-mini",
        "response": result,
        "confidence": 0.85 if result else 0
    }


def call_claude(system_prompt: str, user_prompt: str) -> dict:
    """Simulate Claude (or call real Anthropic if key available)."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if api_key and len(api_key) > 20:
        try:
            import requests
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                },
                json={
                    "model": "claude-3-haiku-20240307",
                    "max_tokens": 500,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}]
                }
            )
            result = response.json()["content"][0]["text"]
            return {
                "model": "claude-3-haiku",
                "response": result,
                "confidence": 0.82 if result else 0
            }
        except Exception as e:
            print(f"⚠️ Claude error: {e}, falling back")
    
    # Fallback: use GPT with different temperature to simulate different opinion
    result = call_openai(system_prompt, user_prompt, temperature=0.8)
    return {
        "model": "claude-3-haiku (simulated)",
        "response": result,
        "confidence": 0.80 if result else 0
    }


def consensus_medical(case: str, questions: list, answers: list) -> dict:
    """Get two opinions and make consensus."""
    
    qa_text = "\n".join([f"Q: {q}\nA: {a}" for q, a in zip(questions, answers)])
    
    prompt = (
        f"Cas: {case}\n\n{qa_text}\n\n"
        "Donne un diagnostic différentiel (2-3 hypothèses) avec niveau de confiance pour chacune. "
        "Format: 1. [Hypothèse] - Confiance: [élevée/modérée/faible]. Maximum 5 phrases."
    )
    
    system = "Tu es un médecin généraliste. Sois concis, structuré, prudent."
    
    avis1 = call_openai_dual(system, prompt)
    avis2 = call_claude(system, prompt)
    
    # Simple consensus: keyword overlap
    if avis1.get("response") and avis2.get("response"):
        words1 = set(avis1["response"].lower().split())
        words2 = set(avis2["response"].lower().split())
        common = words1 & words2
        all_words = words1 | words2
        overlap = len(common) / max(len(all_words), 1)
    else:
        overlap = 0
    
    return {
        "avis_gpt": avis1,
        "avis_claude": avis2,
        "consensus": overlap > 0.25,
        "agreement_score": round(overlap * 100, 1),
        "recommendation": avis1.get("response", "") if (avis1.get("confidence", 0) > avis2.get("confidence", 0)) else avis2.get("response", "")
    }