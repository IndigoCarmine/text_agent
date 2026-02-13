# config.py
"""
Configuration management for Markdown proofreading tool.
Handles CLI arguments, Ollama params, RAG/FAISS settings, and file paths.
"""
import argparse
import json
from pathlib import Path


class Config:
    def __init__(self):
        self.args = self.parse_args()
        self.ollama_url = self.args.ollama_url
        self.ollama_model = self.args.ollama_model
        self.temperature = self.args.temperature
        self.input_file = Path(self.args.input_file)
        self.output_file = Path(self.args.output_file) if self.args.output_file else self.input_file
        self.checks = set(self.args.checks)
        self.terminology_path = Path(self.args.terminology) if self.args.terminology else None
        self.sim_threshold = self.args.sim_threshold
        self.repeat = self.args.repeat

    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description="Markdown 校閲ツール (Ollama + RAG)")
        parser.add_argument("-i", "--input-file", help="入力Markdownファイル", required=True)
        parser.add_argument("-o", "--output-file", help="出力ファイル名 (省略時は上書き保存)")
        parser.add_argument(
            "-c",
            "--checks",
            nargs="+",
            required=True,
            choices=["typo", "grammar", "academic", "terminology", "logic", "logicflow"],
            help="有効化するチェック観点",
        )
        parser.add_argument(
            "--ollama-url", default="http://192.168.11.63:11434/api/generate", help="Ollama APIエンドポイント"
        )
        parser.add_argument("--ollama-model", default="gemma3-32000", help="Ollamaモデル名")
        parser.add_argument("--temperature", type=float, default=0.2, help="Ollama温度パラメータ")
        parser.add_argument("--terminology", help="専門用語JSONファイル (terminology有効時必須)")
        parser.add_argument("--sim-threshold", type=float, default=0.7, help="用語類似度閾値 (terminology有効時)")
        parser.add_argument("--logicflow", action="store_true", help="要約→LogicCheck→修正の新機能フローを使う")
        parser.add_argument("--repeat", type=int, default=1, help="校閲回数 (デフォルト1回)")
        return parser.parse_args()

    def load_terminology(self):
        if not self.terminology_path:
            return []
        with open(self.terminology_path, encoding="utf-8") as f:
            return json.load(f)
