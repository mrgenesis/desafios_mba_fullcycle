"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        print_section_header(f"Fazendo push do prompt '{prompt_name}' para o LangSmith Hub...")

        # Tags e descrição
        tags = prompt_data.get('tags', [])
        system_prompt = prompt_data["system_prompt"]
        user_prompt = prompt_data["user_prompt"]
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", user_prompt)
        ])
        
        # Fazer push para o Hub (PÚBLICO)
        hub.push(
            repo_full_name='mrgenesis/'+prompt_name,
            object=prompt_template,
            tags=tags,
            new_repo_is_public=True,
        )

        print(f"✅ Prompt '{prompt_name}' publicado com sucesso!")
        return True

    except Exception as e:
        print(f"❌ Erro ao publicar o prompt '{prompt_name}': {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    errors = []

    required_fields = ['description', 'system_prompt', 'version', 'input_variables']
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    system_prompt = prompt_data.get('system_prompt', '').strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")

    if 'TODO' in system_prompt:
        errors.append("system_prompt ainda contém TODOs")

    techniques = prompt_data.get('techniques_applied', [])
    if len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)


def main():
    """Função principal"""
    if not check_env_vars(['LANGSMITH_API_KEY']):
        return 1

    prompt = load_yaml("prompts/bug_to_user_story_v2.yml")
    prompt_name, prompt_data = next(iter(prompt.items()))

    if not validate_prompt(prompt_data)[0]:
        print(f"❌ O arquivo de prompt está vazio ou mal formatado.")
        print(f"Erros encontrados: {validate_prompt(prompt_data)[1]}")
        return 1
    
    push_prompt_to_langsmith(prompt_name, prompt_data)

    return 0


if __name__ == "__main__":
    sys.exit(main())
