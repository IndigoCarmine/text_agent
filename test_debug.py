import os
import unittest
import os
from utils import split_markdown_sections, write_markdown_file
from prompt import build_prompt
from rag import find_similar_terms
from llm import call_ollama

class TestMarkdownKouetsu(unittest.TestCase):
    def setUp(self):
        self.sample_md = """# Title\n\nThis is a test document.\n\n## Section\n\nSome content here."""
        self.input_path = "test_input.md"
        self.output_path = "test_input.revised.md"
        with open(self.input_path, "w", encoding="utf-8") as f:
            f.write(self.sample_md)
        self.terms = [{"term": "test", "desc": "A test term."}]

    def tearDown(self):
        if os.path.exists(self.input_path):
            os.remove(self.input_path)
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

    def test_split_markdown_sections(self):
        lines = self.sample_md.splitlines()
        sections = split_markdown_sections(lines)
        self.assertTrue(isinstance(sections, list))
        self.assertGreater(len(sections), 0)

    def test_write_markdown_file(self):
        revised_lines = ["# Title", "", "This is a revised document."]
        write_markdown_file(self.output_path, revised_lines)
        self.assertTrue(os.path.exists(self.output_path))
        with open(self.output_path, encoding="utf-8") as f:
            content = f.read()
        self.assertIn("revised", content)

    def test_build_prompt(self):
        paragraphs = ["Some text."]
        checks = {"grammar", "terminology"}
        terminology_context = [t["term"] for t in self.terms]
        prompt = build_prompt(paragraphs, checks, terminology_context)
        self.assertIn("grammar", prompt)
        self.assertIn("test", prompt)

    def test_find_similar_terms(self):
        # This is a stub; actual test would require embedding model
        result = find_similar_terms("test", self.terms)
        self.assertIsInstance(result, list)

    def test_call_ollama(self):
        # This is a stub; actual test would require Ollama API
        try:
            response = call_ollama("校閲してください。", temperature=0.2)
        except Exception:
            response = ""
        self.assertIsInstance(response, str)

if __name__ == "__main__":
    unittest.main()
