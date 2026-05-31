"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

print_section_header("Buscando prompt do LangSmith Hub...")
check_env_vars(["LANGSMITH_ENDPOINT", "LANGSMITH_API_KEY"])

def pull_prompts_from_langsmith():
    prompt = hub.pull("leonanluppi/bug_to_user_story_v1")
    return prompt


def main():
    """Função principal"""
    prompt = pull_prompts_from_langsmith()
    system_prompt_text = prompt.messages[0].prompt.template
    user_prompt_text = prompt.messages[1].prompt.template

    data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_prompt_text,
            "user_prompt": user_prompt_text,
            "version": "v1",
            "created_at": "2025-01-15",
            "tags": ["bug-analysis", "user-story", "product-management"]
        }
    }
    save_yaml(data, Path("prompts/bug_to_user_story_v1.yml"))
    print("✅ Prompt salvo localmente em prompts/bug_to_user_story_v1.yml")
    return 0

if __name__ == "__main__":
    sys.exit(main())
