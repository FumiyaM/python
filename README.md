# ElasticSearch + Gemini CLI RAG System

Google Gemini CLIを用いたElasticSearch Agent RAGスクリプトの実装です。このシステムは、ElasticSearchから関連文書を検索し、その結果をGemini APIのコンテキストとして使用して、高品質な回答を生成します。

## 概要

このRAG（Retrieval Augmented Generation）システムは以下の機能を提供します：

1. **文書検索**: ElasticSearchから関連する文書を検索
2. **コンテキスト生成**: 検索結果を構造化されたコンテキストとして整理
3. **回答生成**: GeminiAPIを使用してコンテキストに基づいた回答を生成
4. **CLI interface**: コマンドラインから簡単に利用可能

## 必要な環境

- Python 3.8以上
- ElasticSearch 8.0以上
- Google Gemini API アクセス

## セットアップ手順

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env.example`を`.env`にコピーして、必要な設定を行います：

```bash
cp .env.example .env
```

`.env`ファイルを編集して以下を設定：

```env
# ElasticSearch設定
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_USERNAME=your_username  # 認証が必要な場合
ELASTICSEARCH_PASSWORD=your_password  # 認証が必要な場合

# Gemini API設定
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
```

### 3. Gemini API キーの取得

1. [Google AI Studio](https://makersuite.google.com/app/apikey)にアクセス
2. APIキーを生成
3. `.env`ファイルの`GEMINI_API_KEY`に設定

### 4. ElasticSearchの準備

ElasticSearchが起動していることを確認してください：

```bash
# Dockerを使用する場合
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  elasticsearch:8.10.0

# または、ローカルにインストールされている場合
elasticsearch
```

## 使用方法

### 基本的な使用

```bash
python elasticsearch_gemini_rag.py "機械学習とは何ですか？"
```

### オプション付きの使用

```bash
# 特定のインデックスを指定
python elasticsearch_gemini_rag.py "Python プログラミング" --index my_documents

# 検索する文書数を指定
python elasticsearch_gemini_rag.py "データサイエンス" --num-docs 3

# 特定のフィールドのみを検索対象に
python elasticsearch_gemini_rag.py "機械学習" --fields title,content,description

# 詳細出力を有効にする
python elasticsearch_gemini_rag.py "人工知能" --verbose

# 結果をJSONファイルに保存
python elasticsearch_gemini_rag.py "deep learning" --output result.json
```

### 接続テスト

```bash
python elasticsearch_gemini_rag.py --test
```

## コマンドラインオプション

| オプション | 説明 | デフォルト |
|-----------|------|-----------|
| `query` | 検索・生成したいクエリ（必須） | - |
| `--index` | 検索対象のElasticSearchインデックス | `_all` |
| `--num-docs` | 取得する文書数 | `5` |
| `--fields` | 検索対象フィールド（カンマ区切り） | 全フィールド |
| `--test` | 接続テストのみ実行 | - |
| `--verbose` | 詳細出力を表示 | - |
| `--output` | 結果をJSONファイルに保存 | - |

## サンプルデータの準備

### ElasticSearchにサンプルデータを投入

```bash
# サンプルドキュメントの投入例
curl -X POST "localhost:9200/knowledge/_doc/1" -H 'Content-Type: application/json' -d'
{
  "title": "機械学習の基礎",
  "content": "機械学習は、コンピュータが明示的にプログラムされることなく学習する能力を与える人工知能の一分野です。",
  "category": "AI",
  "tags": ["機械学習", "AI", "データサイエンス"]
}
'

curl -X POST "localhost:9200/knowledge/_doc/2" -H 'Content-Type: application/json' -d'
{
  "title": "Pythonプログラミング",
  "content": "Pythonは、読みやすく書きやすい高水準プログラミング言語です。データサイエンスや機械学習の分野で広く使用されています。",
  "category": "プログラミング",
  "tags": ["Python", "プログラミング", "データサイエンス"]
}
'
```

## 実行例

### 基本的なクエリ

```bash
$ python elasticsearch_gemini_rag.py "機械学習について教えて"

🔍 Searching for documents related to: '機械学習について教えて'
📄 Found 2 relevant documents
🤖 Generating response with Gemini...

================================================================================
QUERY RESULTS
================================================================================
Query: 機械学習について教えて
Documents found: 2

----------------------------------------
GENERATED RESPONSE:
----------------------------------------
機械学習は、コンピュータが明示的にプログラムされることなく学習する能力を与える人工知能の一分野です。

提供されたコンテキストによると、機械学習は以下のような特徴があります：

1. **自動学習能力**: コンピュータが明示的にプログラムされることなく、データから学習することができます
2. **AI分野の一部**: 人工知能の重要な分野の一つです
3. **実用的な応用**: データサイエンスの分野で広く活用されています

また、機械学習の実装や学習においては、Pythonプログラミング言語が広く使用されています。Pythonは読みやすく書きやすい高水準言語であり、データサイエンスや機械学習の開発に適しているためです。
```

### 詳細出力付きの実行

```bash
$ python elasticsearch_gemini_rag.py "Python" --verbose --num-docs 2

🔍 Searching for documents related to: 'Python'
📄 Found 2 relevant documents
🤖 Generating response with Gemini...

================================================================================
QUERY RESULTS
================================================================================
Query: Python
Documents found: 2

----------------------------------------
GENERATED RESPONSE:
----------------------------------------
Pythonは、読みやすく書きやすい高水準プログラミング言語です...

----------------------------------------
RETRIEVED DOCUMENTS:
----------------------------------------

Document 1:
  Index: knowledge
  ID: 2
  Score: 1.234
  Content: {
    "title": "Pythonプログラミング",
    "content": "Pythonは、読みやすく書きやすい高水準プログラミング言語です...",
    "category": "プログラミング",
    "tags": ["Python", "プログラミング", "データサイエンス"]
  }
```

## トラブルシューティング

### よくある問題と解決方法

1. **ElasticSearchに接続できない**
   ```
   Error: Cannot connect to ElasticSearch
   ```
   - ElasticSearchが起動しているか確認
   - ポート9200がアクセス可能か確認
   - 認証情報が正しいか確認

2. **Gemini APIエラー**
   ```
   Error generating response: API key invalid
   ```
   - APIキーが正しく設定されているか確認
   - APIキーの権限を確認

3. **依存関係のエラー**
   ```
   ModuleNotFoundError: No module named 'elasticsearch'
   ```
   - `pip install -r requirements.txt`を実行

## 開発・カスタマイズ

### スクリプトの拡張

`elasticsearch_gemini_rag.py`を編集することで、以下のカスタマイズが可能です：

- 検索クエリの精度向上
- Geminiプロンプトの調整
- 出力フォーマットの変更
- 追加の前処理・後処理

### 新しい機能の追加

- Web UIの追加
- 複数の検索エンジン対応
- 結果のキャッシュ機能
- バッチ処理機能

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。

## 貢献

プルリクエストやイシューの報告を歓迎します。改善提案がありましたら、お気軽にお知らせください。

## 参考資料

- [ElasticSearch Python Client](https://elasticsearch-py.readthedocs.io/)
- [Google Generative AI Python SDK](https://ai.google.dev/tutorials/python_quickstart)
- [RAG (Retrieval Augmented Generation) について](https://ai.facebook.com/blog/retrieval-augmented-generation-streamlining-the-creation-of-intelligent-natural-language-processing-models/)