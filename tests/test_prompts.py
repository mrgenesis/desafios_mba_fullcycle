"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path
import re

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

class TestPrompts:
    @pytest.fixture(scope="session")
    def the_prompt(self):
        """Carrega o prompt para os testes."""
        return (load_prompts("prompts/bug_to_user_story_v2.yml"))["bug_to_user_story_v2"]
    
    def test_prompt_has_system_prompt(self, the_prompt):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in the_prompt
        assert the_prompt["system_prompt"].strip()

    def test_prompt_has_role_definition(self, the_prompt):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        persona_palavras_chave = ["você é", "sua função é", "seu papel é"]
        system_prompt = the_prompt["system_prompt"].lower()
        assert any(palavra in system_prompt for palavra in persona_palavras_chave)

    def test_prompt_mentions_format(self, the_prompt):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = the_prompt["system_prompt"].lower()
        keywords = [
            "formato de saída",
            "user story",
            "critérios de aceitação",
            "como um",  # padrão de user story
        ]
        assert any(k in system_prompt for k in keywords), (
            "O prompt não especifica um formato claro (Markdown ou User Story)."
        )

    def test_prompt_has_few_shot_examples(self, the_prompt):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = the_prompt["system_prompt"].lower()
        word = r"^#{1,6}\sexemplos"
        assert re.search(word, system_prompt, flags=re.MULTILINE), (
            "O prompt não contém exemplos de entrada/saída (técnica Few-shot)."
        )

    def test_prompt_no_todos(self, the_prompt):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        full_text = "\n".join(
            str(value) for value in the_prompt.values()
        ).lower()
        assert "[todo]" not in full_text, (
            "O prompt contém '[TODO]' — remova ou finalize antes de publicar."
        )

    def test_minimum_techniques(self, the_prompt):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = the_prompt.get("techniques_applied", [])
        assert isinstance(techniques, list), (
            "O campo 'techniques_applied' deve ser uma lista."
        )
        assert len(techniques) >= 2, (
            f"Esperado pelo menos 2 técnicas, mas encontrei {len(techniques)}."
        )

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])