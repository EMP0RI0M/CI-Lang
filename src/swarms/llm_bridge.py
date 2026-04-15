import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

class OpenRouterBridge:
    """
    Acts as the 'Auditory Cortex' for the FluxVM swarm.
    Translates swarm reports into prompts and processes LLM advice.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = os.getenv("OPENROUTER_MODEL", "minimax/minimax-m2.5:free")
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def chat(self, prompt):
        if not self.api_key:
            return "Error: No API Key found."

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are the LLM_TEACHER of a Chaos Intelligence Swarm. Your task is to provide stability advice. "
                               "Return only a single numeric value between 0.0 and 1.0 representing the recommended cooling/volatility, "
                               "or a Command Code: 10.0 (RESET), 11.0 (INJECT CHAOS), 12.0 (FREEZE). "
                               "Reply with ONLY the number."
                },
                {"role": "user", "content": prompt}
            ]
        }

        try:
            response = requests.post(self.url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            print(f"[LLM_BRIDGE RAW]: '{content}'")
            
            # Extract just the number in case the model is talkative
            import re
            match = re.search(r"[-+]?\d*\.\d+|\d+", content)
            if match:
                return float(match.group())
            return 0.0
        except Exception as e:
            print(f"[LLM_BRIDGE ERROR]: {e}")
            return 0.0
