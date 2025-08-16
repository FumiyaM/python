#!/usr/bin/env python3
"""
Example script demonstrating ElasticSearch RAG with Gemini

This script shows how to:
1. Set up sample data in ElasticSearch
2. Run example queries using the RAG system
3. Display formatted results
"""

import json
import os
import sys
import time
from typing import Dict, Any

# Add the current directory to Python path to import our RAG module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from elasticsearch_gemini_rag import ElasticSearchRAG
    from elasticsearch import Elasticsearch
except ImportError as e:
    print(f"Error: {e}")
    print("Please ensure the main script and dependencies are available")
    sys.exit(1)


class RAGExample:
    """Example implementation of ElasticSearch RAG with Gemini"""
    
    def __init__(self):
        self.es_host = "localhost"
        self.es_port = 9200
        self.sample_index = "sample_docs"
        
    def setup_sample_data(self) -> bool:
        """Setup sample documents in ElasticSearch"""
        try:
            # Connect to ElasticSearch
            es = Elasticsearch([{'host': self.es_host, 'port': self.es_port}])
            
            if not es.ping():
                print("Error: Cannot connect to ElasticSearch")
                print("Please ensure ElasticSearch is running on localhost:9200")
                return False
            
            print("Setting up sample data in ElasticSearch...")
            
            # Sample documents
            sample_docs = [
                {
                    "id": "1",
                    "title": "Python プログラミング入門",
                    "content": "Pythonは初心者にも学びやすいプログラミング言語です。データ分析、Web開発、AI開発など様々な分野で使用されています。シンプルな文法と豊富なライブラリにより、効率的な開発が可能です。",
                    "category": "技術・プログラミング",
                    "tags": ["Python", "プログラミング", "初心者", "データ分析"],
                    "difficulty": "初級",
                    "estimated_time": "2-3ヶ月"
                },
                {
                    "id": "2", 
                    "title": "機械学習の基礎",
                    "content": "機械学習は人工知能の一分野で、データからパターンを学習してタスクを実行する技術です。教師あり学習、教師なし学習、強化学習などの手法があり、各々が異なる問題解決アプローチを提供します。",
                    "category": "AI・機械学習",
                    "tags": ["機械学習", "AI", "データサイエンス", "アルゴリズム"],
                    "difficulty": "中級",
                    "estimated_time": "6-12ヶ月"
                },
                {
                    "id": "3",
                    "title": "ElasticSearchの活用",
                    "content": "ElasticSearchは分散型の検索・分析エンジンです。大量のデータを高速に検索でき、ログ分析やWebサイトの検索機能、リアルタイム分析などに使用されます。RESTful APIを通じて操作できます。",
                    "category": "技術・データベース",
                    "tags": ["ElasticSearch", "検索エンジン", "データベース", "分析"],
                    "difficulty": "中級",
                    "estimated_time": "3-6ヶ月"
                },
                {
                    "id": "4",
                    "title": "自然言語処理入門",
                    "content": "自然言語処理（NLP）は、コンピューターが人間の言語を理解し処理する技術です。テキスト分析、感情分析、機械翻訳、チャットボットなどの応用があります。最近ではTransformerモデルが注目されています。",
                    "category": "AI・機械学習",
                    "tags": ["NLP", "自然言語処理", "テキスト分析", "Transformer"],
                    "difficulty": "上級",
                    "estimated_time": "12ヶ月以上"
                },
                {
                    "id": "5",
                    "title": "Web開発の基本",
                    "content": "Web開発にはフロントエンド（HTML、CSS、JavaScript）とバックエンド（Python、Java、Node.jsなど）の技術が必要です。最近ではReact、Vue.js、Angularなどのフレームワークが人気です。",
                    "category": "技術・Web開発",
                    "tags": ["Web開発", "HTML", "CSS", "JavaScript", "React"],
                    "difficulty": "初級",
                    "estimated_time": "3-6ヶ月"
                }
            ]
            
            # Insert documents
            for doc in sample_docs:
                es.index(index=self.sample_index, id=doc["id"], body=doc)
                print(f"  → Inserted: {doc['title']}")
            
            # Refresh index to make documents searchable
            es.indices.refresh(index=self.sample_index)
            
            print(f"Successfully set up {len(sample_docs)} sample documents!")
            return True
            
        except Exception as e:
            print(f"Error setting up sample data: {e}")
            return False
    
    def run_example_queries(self) -> bool:
        """Run example queries to demonstrate the RAG system"""
        try:
            # Check if Gemini API key is available
            gemini_api_key = os.getenv('GEMINI_API_KEY')
            if not gemini_api_key:
                print("Warning: GEMINI_API_KEY environment variable not set")
                print("Please set your Gemini API key to run the full example")
                print("Example: export GEMINI_API_KEY='your-api-key-here'")
                return False
            
            # Initialize RAG system
            print("\nInitializing ElasticSearch RAG system...")
            rag = ElasticSearchRAG(
                es_host=self.es_host,
                es_port=self.es_port,
                gemini_api_key=gemini_api_key
            )
            
            # Example queries
            example_queries = [
                "Pythonプログラミングを学ぶにはどうすればいいですか？",
                "機械学習と自然言語処理の関係について教えて",
                "Web開発を始めるのに必要な技術は何ですか？",
                "ElasticSearchはどのような用途に使われますか？"
            ]
            
            print("\n" + "="*80)
            print("RAG Example Queries")
            print("="*80)
            
            for i, query in enumerate(example_queries, 1):
                print(f"\n--- Example {i} ---")
                print(f"Query: {query}")
                print("-" * 40)
                
                try:
                    # Process query
                    result = rag.process_query(query, index=self.sample_index, max_results=3)
                    
                    print(f"Search Results: {result['num_results']} documents found")
                    print("\nGenerated Response:")
                    print(result['response'])
                    
                    # Show search result titles for reference
                    if result['search_results']:
                        print("\nSource Documents:")
                        for j, sr in enumerate(result['search_results'], 1):
                            title = sr['source'].get('title', 'Unknown')
                            score = sr['score']
                            print(f"  {j}. {title} (score: {score:.2f})")
                    
                except Exception as e:
                    print(f"Error processing query: {e}")
                
                print("\n" + "="*80)
                
                # Small delay between queries
                time.sleep(1)
            
            return True
            
        except Exception as e:
            print(f"Error running example queries: {e}")
            return False
    
    def show_search_only_example(self) -> bool:
        """Show search-only example (without Gemini)"""
        try:
            print("\n--- Search-Only Example (without Gemini) ---")
            
            # Initialize without Gemini
            es = Elasticsearch([{'host': self.es_host, 'port': self.es_port}])
            
            query = "Python データ分析"
            print(f"Searching for: '{query}'")
            
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["title", "content", "tags"],
                        "type": "best_fields"
                    }
                },
                "size": 3
            }
            
            response = es.search(index=self.sample_index, body=search_body)
            
            print(f"\nFound {len(response['hits']['hits'])} results:")
            for i, hit in enumerate(response['hits']['hits'], 1):
                source = hit['_source']
                print(f"\n{i}. {source['title']} (score: {hit['_score']:.2f})")
                print(f"   Category: {source['category']}")
                print(f"   Content: {source['content'][:100]}...")
                print(f"   Tags: {', '.join(source['tags'])}")
            
            return True
            
        except Exception as e:
            print(f"Error in search-only example: {e}")
            return False

def main():
    """Main function to run the example"""
    print("ElasticSearch RAG with Gemini - Example Script")
    print("=" * 50)
    
    example = RAGExample()
    
    # Setup sample data
    if not example.setup_sample_data():
        print("Failed to setup sample data. Please check ElasticSearch connection.")
        return
    
    # Show search-only example first
    example.show_search_only_example()
    
    # Ask user if they want to run full RAG examples
    print("\n" + "="*50)
    print("To run full RAG examples with Gemini, you need to:")
    print("1. Set GEMINI_API_KEY environment variable")
    print("2. Ensure you have internet connection")
    print("3. Have valid Gemini API credits")
    
    try:
        user_input = input("\nRun full RAG examples? (y/N): ").strip().lower()
        if user_input in ['y', 'yes']:
            example.run_example_queries()
        else:
            print("Skipping full RAG examples.")
    except KeyboardInterrupt:
        print("\nExample script interrupted.")

    run_full_rag = False
    if args.run_full_rag:
        run_full_rag = True
    elif sys.stdin.isatty():
        try:
            user_input = input("\nRun full RAG examples? (y/N): ").strip().lower()
            if user_input in ['y', 'yes']:
                run_full_rag = True
            else:
                print("Skipping full RAG examples.")
        except KeyboardInterrupt:
            print("\nExample script interrupted.")
    else:
        print("Non-interactive environment detected. Skipping full RAG examples. Use --run-full-rag to force.")

    if run_full_rag:
        example.run_example_queries()
    print("\nExample script completed!")

if __name__ == "__main__":
    main()