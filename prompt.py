# prompt.py
"""
Prompt generation for Markdown校閲ツール.
Builds LLM prompt based on enabled checks and (optionally) terminology context.
"""
from typing import List, Set, Optional

def build_prompt(paragraphs: List[str], checks: Set[str], terminology_context: Optional[List[str]] = None) -> str:
    instructions = []
    if 'typo' in checks:
        instructions.append('誤字脱字・スペルミスを修正してください。')
    if 'grammar' in checks:
        instructions.append('文法ミスを修正してください。')
    if 'academic' in checks:
        instructions.append('学術論文にふさわしい表現にしてください。')
    if 'terminology' in checks:
        instructions.append('専門用語の統一を行ってください。')
    if 'logic' in checks:
        instructions.append(r'論理的な整合性を確認て、不足している部分には{{TODO::説明}}のように説明をを追加してください。')
    instructions.append('不要な文体改変は禁止です。')
    if terminology_context:
        instructions.append(f'以下の専門用語リストを参考にしてください: {", ".join(terminology_context)}')
    prompt = '\n'.join(instructions) + '\n\n' + '\n'.join(paragraphs)
    return prompt
