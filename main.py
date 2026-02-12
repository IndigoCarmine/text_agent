import os
import argparse
from config import Config
from utils import read_markdown_file, write_markdown_file, split_markdown_sections
from prompt import build_prompt
from llm import call_ollama
from rag import TerminologyRAG


def summarize_paragraph(paragraph, config, rag=None):
    """Summarize a paragraph into one sentence using LLM."""
    terminology_context = None
    if rag:
        terminology_context = rag.search(paragraph, threshold=config.sim_threshold)
    print("Summarizing paragraph:", paragraph)
    prompt = build_prompt([paragraph], {"summary"}, terminology_context)
    # summary用プロンプトを生成（build_prompt拡張が必要なら適宜修正）
    summary = call_ollama(prompt, config.ollama_model, config.ollama_url, config.temperature)
    return summary.strip() if summary else ""

def logic_check_summaries(summaries, config):
    """Check logic of all summaries together using LLM."""
    prompt = "以下は各段落の要約です。全体の論理的整合性を確認し、問題点があれば指摘してください。\n" + '\n'.join(f"- {s}" for s in summaries)
    result = call_ollama(prompt, config.ollama_model, config.ollama_url, config.temperature)
    return result.strip() if result else ""

def build_prompt_for_logic_check(paragraph, logic_result, config, rag=None):
    """LogicCheck結果をプロンプトに注入して段落修正用プロンプトを生成"""
    terminology_context = None
    if rag:
        terminology_context = rag.search(paragraph, threshold=config.sim_threshold)
    prompt = '''全文の論理的整合性に関するフィードバックと段落を与えます。フィードバックを踏まえて、段落を修正し、主張や言いたいことが明確かつ強調されるようにしてください。段落だけ返答しなさい。不必要な文体改変は禁止です。
[LogicCheckフィードバック]''' + logic_result + '''
[段落]''' + paragraph
    if terminology_context:
        prompt += f'\n[専門用語リスト] {", ".join(terminology_context)}'
    
    return prompt
def revise_paragraphs_with_logic_check(sections, config, rag=None):
    """新機能: 各段落を要約→まとめてLogicCheck→各段落修正の流れを実行"""
    all_summaries = []
    for heading, paragraphs in sections:
        for para in paragraphs:
            summary = summarize_paragraph(para, config, rag)
            all_summaries.append(summary)
    logic_result = logic_check_summaries(all_summaries, config)
    print("[LogicCheck結果]\n" + logic_result)
    revised_lines = []
    comments = []
    for heading, paragraphs in sections:
        revised_lines.append(heading)
        for para in paragraphs:
            terminology_context = None
            if rag:
                terminology_context = rag.search(para, threshold=config.sim_threshold)
            # LogicCheck結果をプロンプトに注入
            prompt = build_prompt_for_logic_check(para, logic_result, config, rag)
            revised = call_ollama(prompt, config.ollama_model, config.ollama_url, config.temperature)
            if revised is None:
                print('[Error] Ollama API呼び出し失敗')
                return
            # コメント生成: どんな観点で修正したか
            comment_prompt = f"次の修正文はどの観点（{', '.join(config.checks)}）で修正されたかを日本語で簡潔に列挙してください。\n---\n{para}\n---\n修正文:\n{revised.strip()}"
            comment = call_ollama(comment_prompt, config.ollama_model, config.ollama_url, config.temperature)
            comments.append(f"[{heading.strip()}] {comment.strip() if comment else ''}")
            for line in revised.strip().split('\n'):
                if line.strip():
                    revised_lines.append(line.strip())
    # コメントファイル出力
    comment_path = str(config.output_file) + ".comments.txt"
    i =0
    comment_new_path = comment_path
    while os.path.exists(comment_new_path):
        i +=1
        comment_new_path = f"{comment_path[:-4]}_{i}.txt"
    comment_path = comment_new_path
    with open(comment_path, "w", encoding="utf-8") as f:
        for c in comments:
            f.write(c + "\n")
    print(f"[OK] コメントファイル出力: {comment_path}")
    return revised_lines
# main.py
"""
CLI entry point for Markdown校閲ツール (Ollama + RAG)
"""




def main():

    config = Config()
    revised_lines = []

    # Prepare RAG if needed
    rag = None
    if 'terminology' in config.checks:
        terms = config.load_terminology()
        if not terms:
            print('[Error] terminologyチェック有効時は用語JSONが必要です')
            return
        rag = TerminologyRAG(terms)

    for _ in range(config.repeat):
        check(config, rag)



def check(config, rag):
    
    lines = read_markdown_file(str(config.input_file))
    sections = split_markdown_sections(lines)

    if config.checks == {"logicflow"}:
        print("[Info] 新機能: 段落要約→LogicCheck→段落修正フロー実行")
        revised_lines = revise_paragraphs_with_logic_check(sections, config, rag)
        write_markdown_file(str(config.output_file), revised_lines)
        print(f'[OK] 校閲済みファイル: {config.output_file}')
        return

    # 旧ロジック: 1パラグラフずつ通常校閲
    for heading, paragraphs in sections:
        revised_lines.append(heading)
        print(f'[Info] 校閲中: {heading.strip()}')
        if not paragraphs:
            continue
        for para in paragraphs:
            terminology_context = None
            if rag:
                terminology_context = rag.search(para, threshold=config.sim_threshold)
            prompt = build_prompt([para], config.checks, terminology_context)
            revised = call_ollama(prompt, config.ollama_model, config.ollama_url, config.temperature)
            if revised is None:
                print('[Error] Ollama API呼び出し失敗')
                return
            for line in revised.strip().split('\n'):
                if line.strip():
                    revised_lines.append(line.strip())

    write_markdown_file(str(config.output_file), revised_lines)
    print(f'[OK] 校閲済みファイル: {config.output_file}')

    for heading, paragraphs in sections:
        revised_lines.append(heading)
        print(f'[Info] 校閲中: {heading.strip()}')
        if not paragraphs:
            continue
        for para in paragraphs:
            terminology_context = None
            if rag:
                terminology_context = rag.search(para, threshold=config.sim_threshold)
            print("para:", para)
            prompt = build_prompt([para], config.checks, terminology_context)
            revised = call_ollama(prompt, config.ollama_model, config.ollama_url, config.temperature)
            if revised is None:
                print('[Error] Ollama API呼び出し失敗')
                return
            for line in revised.strip().split('\n'):
                if line.strip():
                    revised_lines.append(line.strip())

    write_markdown_file(str(config.output_file), revised_lines)
    print(f'[OK] 校閲済みファイル: {config.output_file}')

if __name__ == '__main__':
    main()
