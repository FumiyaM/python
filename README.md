# ElasticSearch Agent RAG with Google Gemini CLI

Google Gemini CLIを使用してElasticSearchに対するRAG（Retrieval Augmented Generation）を実装するPythonスクリプトです。

## 概要

このスクリプトは以下の機能を提供します：

1. **ElasticSearch検索**: ユーザーのクエリに基づいてElasticSearchから関連データを検索
2. **コンテキスト生成**: 検索結果を構造化されたコンテキストとして整理
3. **Gemini生成**: 検索結果をコンテキストとしてGoogle Geminiに渡し、自然言語での回答を生成
4. **CLI インターフェース**: コマンドラインから簡単に使用可能

## セットアップ

### 前提条件

1. **Python 3.8以上**
2. **ElasticSearchサーバー** (ローカルまたはリモート)
3. **Google Cloud Platform アカウント** (Gemini API使用のため)

### 1. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 2. ElasticSearchの準備

#### ローカルでElasticSearchを起動する場合:

```bash
# Dockerを使用する場合
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  elasticsearch:8.11.0

# ElasticSearchが起動したかを確認
curl http://localhost:9200
```

#### サンプルデータの投入:

```bash
# サンプル文書を投入
curl -X PUT "localhost:9200/sample_docs/1" -H 'Content-Type: application/json' -d'
{
  "title": "Python プログラミング入門",
  "content": "Pythonは初心者にも学びやすいプログラミング言語です。データ分析、Web開発、AI開発など様々な分野で使用されています。",
  "category": "技術",
  "tags": ["Python", "プログラミング", "初心者"]
}
'

curl -X PUT "localhost:9200/sample_docs/2" -H 'Content-Type: application/json' -d'
{
  "title": "機械学習の基礎",
  "content": "機械学習は人工知能の一分野で、データからパターンを学習してタスクを実行する技術です。教師あり学習、教師なし学習、強化学習などの手法があります。",
  "category": "AI・機械学習",
  "tags": ["機械学習", "AI", "データサイエンス"]
}
'

curl -X PUT "localhost:9200/sample_docs/3" -H 'Content-Type: application/json' -d'
{
  "title": "ElasticSearchとは",
  "content": "ElasticSearchは分散型の検索・分析エンジンです。大量のデータを高速に検索でき、ログ分析やWebサイトの検索機能などに使用されます。",
  "category": "技術",
  "tags": ["ElasticSearch", "検索", "データベース"]
}
'
```

### 3. Google Gemini APIの設定

1. [Google Cloud Console](https://console.cloud.google.com/)でプロジェクトを作成
2. Gemini API (Generative AI API)を有効化
3. APIキーを取得
4. 環境変数を設定:

```bash
export GEMINI_API_KEY="your-api-key-here"
```

または、`.env`ファイルを作成:

```bash
# .env ファイル
GEMINI_API_KEY=your-api-key-here
```

## 使用方法

### 基本的な使用方法

```bash
# 基本的なクエリ実行
python elasticsearch_gemini_rag.py "Pythonプログラミングについて教えて"

# 特定のインデックスを指定
python elasticsearch_gemini_rag.py "機械学習とは何ですか" --index sample_docs

# 検索結果数を指定
python elasticsearch_gemini_rag.py "ElasticSearchの特徴は？" --max-results 3

# 結果をJSONファイルに保存
python elasticsearch_gemini_rag.py "AIについて" --output result.json

# 詳細ログを表示
python elasticsearch_gemini_rag.py "データ分析" --verbose
```

### コマンドラインオプション

```bash
python elasticsearch_gemini_rag.py [クエリ] [オプション]

必須引数:
  query                  検索クエリ

オプション引数:
  --es-host              ElasticSearchホスト (デフォルト: localhost)
  --es-port              ElasticSearchポート (デフォルト: 9200)
  --es-username          ElasticSearchユーザー名
  --es-password          ElasticSearchパスワード
  --index                検索対象インデックス (デフォルト: _all)
  --max-results          最大検索結果数 (デフォルト: 5)
  --gemini-api-key       Gemini APIキー (環境変数GEMINI_API_KEYでも可)
  --gemini-model         Geminiモデル名 (デフォルト: gemini-pro)
  --output               結果保存先ファイル (JSON形式)
  --verbose, -v          詳細ログ表示
```

### プログラムでの使用例

```python
from elasticsearch_gemini_rag import ElasticSearchRAG

# RAGシステムを初期化
rag = ElasticSearchRAG(
    es_host="localhost",
    es_port=9200,
    gemini_api_key="your-api-key"
)

# クエリを処理
result = rag.process_query("Pythonについて教えて", index="sample_docs")

print("回答:", result['response'])
print("検索結果数:", result['num_results'])
```

## 実行例

### 例1: 基本的なクエリ

```bash
$ python elasticsearch_gemini_rag.py "Pythonプログラミングとは何ですか？"

================================================================================
クエリ: Pythonプログラミングとは何ですか？
検索結果数: 1
================================================================================

回答:
Pythonプログラミングとは、Python言語を使用したソフトウェア開発のことです。

検索結果によると、Pythonは初心者にも学びやすいプログラミング言語として位置づけられており、以下のような特徴があります：

**主な特徴:**
- 初心者にも学びやすい文法
- 多様な応用分野での活用が可能

**主な応用分野:**
- データ分析
- Web開発  
- AI開発

Pythonはそのシンプルで読みやすい構文により、プログラミング初心者から上級者まで幅広く使用されている人気の高いプログラミング言語です。
================================================================================
```

### 例2: 特定インデックスでの検索

```bash
$ python elasticsearch_gemini_rag.py "機械学習について詳しく" --index sample_docs --max-results 2

================================================================================
クエリ: 機械学習について詳しく
検索結果数: 1
================================================================================

回答:
機械学習は人工知能（AI）の重要な一分野です。

**機械学習の定義:**
機械学習は、データからパターンを自動的に学習して、特定のタスクを実行する技術です。

**主な学習手法:**
検索結果によると、機械学習には以下の主要な手法があります：

1. **教師あり学習** - ラベル付きデータを使用して学習
2. **教師なし学習** - ラベルなしデータからパターンを発見  
3. **強化学習** - 環境との相互作用を通じて学習

機械学習は現在、データサイエンス分野において中核的な技術として位置づけられており、様々な業界で実用的な応用が進んでいます。
================================================================================
```

## 設定ファイル

より複雑な設定を行いたい場合は、設定ファイルを作成できます：

```python
# config.py
ES_CONFIG = {
    'host': 'localhost',
    'port': 9200,
    'username': None,
    'password': None
}

GEMINI_CONFIG = {
    'api_key': None,  # 環境変数から取得
    'model': 'gemini-pro'
}

SEARCH_CONFIG = {
    'default_index': 'documents',
    'max_results': 5,
    'fuzziness': 'AUTO'
}
```

## トラブルシューティング

### よくある問題と解決方法

1. **ElasticSearchに接続できない**
   ```bash
   # ElasticSearchが起動しているか確認
   curl http://localhost:9200
   ```

2. **Gemini API認証エラー**
   ```bash
   # APIキーが正しく設定されているか確認
   echo $GEMINI_API_KEY
   ```

3. **検索結果が空**
   ```bash
   # インデックスにデータが存在するか確認
   curl http://localhost:9200/_cat/indices
   ```

4. **依存関係エラー**
   ```bash
   # 依存関係を再インストール
   pip install -r requirements.txt --upgrade
   ```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

プルリクエストやIssueは歓迎します。改善提案がありましたら、お気軽にお知らせください。

## 関連リンク

- [ElasticSearch公式ドキュメント](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Google Gemini API ドキュメント](https://ai.google.dev/docs)
- [Python ElasticSearch クライアント](https://elasticsearch-py.readthedocs.io/)