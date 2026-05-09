import os
from groq import Groq
from assistant.core.config import LLM_TEMPERATURE

# Config Groq
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL   = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_MAX_TOKENS = int(os.environ.get("GROQ_MAX_TOKENS", "700"))
GROQ_TOP_P      = float(os.environ.get("GROQ_TOP_P", "0.9"))

_client = Groq(api_key=GROQ_API_KEY)


def llm_chat(system: str, user: str) -> str:
    """
    Appel à Groq Cloud (remplacement d'Ollama).
    Conserve la même signature : llm_chat(system, user) -> str
    """
    response = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        temperature=float(LLM_TEMPERATURE),
        max_tokens=GROQ_MAX_TOKENS,
        top_p=GROQ_TOP_P,
        stream=False,
    )

    text = response.choices[0].message.content

    if not text or not text.strip():
        raise RuntimeError("Réponse vide renvoyée par Groq.")

    return text.strip()