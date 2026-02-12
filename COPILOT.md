Markdown文書校閲ツール（Ollama + Langchain + sklearn）実装サマリ

Python環境にはUVを使うこと

概要
ローカルOllamaを用いたMarkdown文書校閲CLIツール
校閲観点（typo, grammar, academic, terminology, logic）はCLI引数で選択式
terminology有効時のみ、用語JSON＋Embedding＋sklearn近傍探索（RAG）で関連用語をプロンプトに注入
セクション単位バッチ処理、1行単位LLM呼び出し禁止
出力は修正文のみを別ファイル（例: input.revised.md）に保存
モジュール分離・拡張性重視
ディレクトリ構成・主なファイル
main.py … CLI制御・全体オーケストレーション
config.py … CLI引数・パラメータ管理
utils.py … Markdown分割・ファイルI/O
prompt.py … 校閲観点・用語注入に応じたプロンプト生成
rag.py … Langchain＋sentence-transformers＋sklearnによる用語類似検索
llm.py … Ollama API呼び出し
requirements.txt … 必要パッケージ（requests, sentence-transformers, scikit-learn, langchain）
技術ポイント
sklearn.NearestNeighborsでEmbedding類似検索（faiss不要、Windows対応）
Langchain導入済み（今後の拡張も容易）
校閲観点はCLIで複数指定可、不要な文体改変は禁止
用語JSONは[{\"term\": \"...\", ...}, ...]形式
Ollama APIは低temperature（0.2）で呼び出し、出力は修正文のみ
注意・今後のTODO
faiss非対応環境でも動作
Langchainのさらなる活用やプロンプトテンプレート拡張も容易
異常系（API失敗、用語JSON不備等）はprintでエラー通知
テスト・追加機能は未実装
この内容をもとに、次のセッションで再開・引き継ぎが可能です。

GPT-4.1 • 0x