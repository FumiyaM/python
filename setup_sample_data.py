#!/usr/bin/env python3
"""
Sample data setup script for ElasticSearch + Gemini RAG system

This script helps users set up sample data in ElasticSearch for testing
the RAG system.
"""

import json
import sys
from typing import List, Dict, Any

try:
    from elasticsearch import Elasticsearch
    from elasticsearch.helpers import bulk
except ImportError:
    print("Error: elasticsearch package not found. Please install requirements.txt")
    sys.exit(1)


def create_sample_documents() -> List[Dict[str, Any]]:
    """Create sample documents for testing"""
    return [
        {
            "_index": "knowledge",
            "_id": "1",
            "_source": {
                "title": "機械学習の基礎",
                "content": "機械学習は、コンピュータが明示的にプログラムされることなく学習する能力を与える人工知能の一分野です。データからパターンを見つけ出し、新しいデータに対して予測や判断を行うことができます。教師あり学習、教師なし学習、強化学習の3つの主要なタイプがあります。",
                "category": "AI",
                "tags": ["機械学習", "AI", "データサイエンス", "人工知能"],
                "difficulty": "初級",
                "language": "ja"
            }
        },
        {
            "_index": "knowledge",
            "_id": "2",
            "_source": {
                "title": "Pythonプログラミング入門",
                "content": "Pythonは、読みやすく書きやすい高水準プログラミング言語です。データサイエンス、機械学習、Web開発、自動化などの分野で広く使用されています。豊富なライブラリエコシステムと活発なコミュニティが特徴です。",
                "category": "プログラミング",
                "tags": ["Python", "プログラミング", "データサイエンス", "開発"],
                "difficulty": "初級",
                "language": "ja"
            }
        },
        {
            "_index": "knowledge",
            "_id": "3",
            "_source": {
                "title": "深層学習（ディープラーニング）",
                "content": "深層学習は、多層のニューラルネットワークを使用した機械学習の手法です。画像認識、自然言語処理、音声認識などの分野で革命的な成果を上げています。TensorFlow、PyTorch、Kerasなどのフレームワークが広く使用されています。",
                "category": "AI",
                "tags": ["深層学習", "ニューラルネットワーク", "AI", "機械学習"],
                "difficulty": "中級",
                "language": "ja"
            }
        },
        {
            "_index": "knowledge",
            "_id": "4",
            "_source": {
                "title": "データサイエンスとは",
                "content": "データサイエンスは、統計学、機械学習、プログラミング、ドメイン知識を組み合わせて、データから有意義な洞察を抽出する学際的な分野です。ビジネス意思決定の支援や新しい知見の発見に役立ちます。",
                "category": "データサイエンス",
                "tags": ["データサイエンス", "統計", "分析", "ビジネス"],
                "difficulty": "初級",
                "language": "ja"
            }
        },
        {
            "_index": "knowledge",
            "_id": "5",
            "_source": {
                "title": "自然言語処理（NLP）",
                "content": "自然言語処理は、コンピュータが人間の言語を理解し、処理する技術です。テキスト分析、機械翻訳、感情分析、チャットボットなどの応用があります。最近では、TransformerアーキテクチャやGPTなどの大規模言語モデルが注目されています。",
                "category": "AI",
                "tags": ["自然言語処理", "NLP", "テキスト分析", "AI"],
                "difficulty": "中級",
                "language": "ja"
            }
        },
        {
            "_index": "knowledge",
            "_id": "6",
            "_source": {
                "title": "ElasticSearchの基本",
                "content": "ElasticSearchは、分散型の検索・分析エンジンです。リアルタイムでの全文検索、ログ分析、メトリクス分析などに使用されます。RESTful APIを提供し、JSON形式でデータを扱います。スケーラビリティと高いパフォーマンスが特徴です。",
                "category": "データベース",
                "tags": ["ElasticSearch", "検索エンジン", "分析", "データベース"],
                "difficulty": "初級",
                "language": "ja"
            }
        },
        {
            "_index": "knowledge",
            "_id": "7",
            "_source": {
                "title": "RAG（Retrieval Augmented Generation）",
                "content": "RAGは、情報検索と生成AIを組み合わせた手法です。関連する文書を検索し、その内容をコンテキストとして大規模言語モデルに与えることで、より正確で根拠のある回答を生成できます。知識ベースの更新が容易で、幻覚（hallucination）の問題を軽減できます。",
                "category": "AI",
                "tags": ["RAG", "情報検索", "生成AI", "LLM"],
                "difficulty": "中級",
                "language": "ja"
            }
        },
        {
            "_index": "knowledge",
            "_id": "8",
            "_source": {
                "title": "Google Gemini API",
                "content": "Google Gemini APIは、Googleが開発した最新の生成AIモデルです。テキスト生成、画像理解、コード生成など、マルチモーダルな機能を提供します。高い性能と柔軟性を持ち、様々なアプリケーションに統合できます。",
                "category": "API",
                "tags": ["Gemini", "Google", "生成AI", "API"],
                "difficulty": "初級",
                "language": "ja"
            }
        }
    ]


def setup_elasticsearch_index(es: Elasticsearch, index_name: str = "knowledge"):
    """Create ElasticSearch index with appropriate mappings"""
    
    # Check if index already exists
    if es.indices.exists(index=index_name):
        print(f"Index '{index_name}' already exists. Deleting...")
        es.indices.delete(index=index_name)
    
    # Create index with mappings
    mapping = {
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "standard",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "content": {
                    "type": "text",
                    "analyzer": "standard"
                },
                "category": {
                    "type": "keyword"
                },
                "tags": {
                    "type": "keyword"
                },
                "difficulty": {
                    "type": "keyword"
                },
                "language": {
                    "type": "keyword"
                }
            }
        },
        "settings": {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }
    
    es.indices.create(index=index_name, body=mapping)
    print(f"Created index '{index_name}' with mappings")


def insert_sample_data(es: Elasticsearch):
    """Insert sample documents into ElasticSearch"""
    documents = create_sample_documents()
    
    # Use bulk API for efficient insertion
    success, failed = bulk(es, documents)
    
    print(f"Successfully inserted {success} documents")
    if failed:
        print(f"Failed to insert {len(failed)} documents")
        for fail in failed:
            print(f"  - {fail}")
    
    # Refresh index to make documents searchable
    es.indices.refresh(index="knowledge")
    print("Index refreshed - documents are now searchable")


def test_search(es: Elasticsearch, query: str = "機械学習"):
    """Test search functionality"""
    print(f"\nTesting search with query: '{query}'")
    
    search_body = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["title^2", "content", "tags"],
                "type": "best_fields"
            }
        },
        "size": 3
    }
    
    response = es.search(index="knowledge", body=search_body)
    
    print(f"Found {response['hits']['total']['value']} total documents")
    print("Top results:")
    
    for i, hit in enumerate(response['hits']['hits'], 1):
        print(f"  {i}. {hit['_source']['title']} (score: {hit['_score']:.2f})")
        print(f"     Category: {hit['_source']['category']}")
        print(f"     Tags: {', '.join(hit['_source']['tags'])}")


def main():
    """Main setup function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Setup sample data for ElasticSearch RAG system")
    parser.add_argument("--host", default="localhost", help="ElasticSearch host")
    parser.add_argument("--port", type=int, default=9200, help="ElasticSearch port")
    parser.add_argument("--username", help="ElasticSearch username")
    parser.add_argument("--password", help="ElasticSearch password")
    parser.add_argument("--index", default="knowledge", help="Index name to create")
    parser.add_argument("--test-only", action="store_true", help="Only test connection, don't insert data")
    
    args = parser.parse_args()
    
    try:
        # Connect to ElasticSearch
        if args.username and args.password:
            es = Elasticsearch(
                [{"host": args.host, "port": args.port}],
                http_auth=(args.username, args.password),
                verify_certs=False
            )
        else:
            es = Elasticsearch([{"host": args.host, "port": args.port}])
        
        # Test connection
        if not es.ping():
            print("Error: Cannot connect to ElasticSearch")
            sys.exit(1)
        
        print(f"✓ Connected to ElasticSearch at {args.host}:{args.port}")
        
        if args.test_only:
            print("Connection test successful!")
            return
        
        # Setup index and insert data
        setup_elasticsearch_index(es, args.index)
        insert_sample_data(es)
        
        # Test search
        test_search(es)
        
        print("\n✓ Sample data setup complete!")
        print("\nYou can now test the RAG system with commands like:")
        print("  python elasticsearch_gemini_rag.py '機械学習について教えて'")
        print("  python elasticsearch_gemini_rag.py 'Pythonの特徴は？'")
        print("  python elasticsearch_gemini_rag.py 'RAGとは何ですか？'")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()