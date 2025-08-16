#!/usr/bin/env python3
"""
ElasticSearch Agent RAG with Google Gemini CLI

This script implements a Retrieval Augmented Generation (RAG) system that:
1. Searches data from ElasticSearch
2. Uses the retrieved data as context for Google Gemini to generate responses

Requirements:
- ElasticSearch server running
- Google Cloud credentials configured for Gemini API
- Required Python packages installed (see requirements.txt)
"""

import json
import os
import sys
import argparse
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

try:
    from elasticsearch import Elasticsearch
    import google.generativeai as genai
    import requests
except ImportError as e:
    print(f"Error: Missing required package: {e}")
    print("Please install dependencies with: pip install -r requirements.txt")
    sys.exit(1)


class ElasticSearchRAG:
    """ElasticSearch RAG Agent with Gemini integration"""
    
    def __init__(self, 
                 es_host: str = "localhost",
                 es_port: int = 9200,
                 es_username: str = None,
                 es_password: str = None,
                 gemini_api_key: str = None,
                 gemini_model: str = "gemini-pro"):
        """
        Initialize the RAG agent
        
        Args:
            es_host: ElasticSearch host
            es_port: ElasticSearch port
            es_username: ElasticSearch username (optional)
            es_password: ElasticSearch password (optional)
            gemini_api_key: Google Gemini API key
            gemini_model: Gemini model to use
        """
        self.logger = self._setup_logging()
        
        # Initialize ElasticSearch connection
        self.es = self._init_elasticsearch(es_host, es_port, es_username, es_password)
        
        # Initialize Gemini
        self.gemini_model_name = gemini_model
        self._init_gemini(gemini_api_key)
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def _init_elasticsearch(self, host: str, port: int, username: str, password: str) -> Elasticsearch:
        """Initialize ElasticSearch connection"""
        try:
            # Build connection URL
            if username and password:
                es = Elasticsearch(
                    [f"http://{host}:{port}"],
                    http_auth=(username, password),
                    http_compress=True,
                    request_timeout=30
                )
            else:
                es = Elasticsearch(
                    [f"http://{host}:{port}"],
                    http_compress=True,
                    request_timeout=30
                )
            
            # Test connection
            if es.ping():
                self.logger.info(f"Successfully connected to ElasticSearch at {host}:{port}")
            else:
                raise ConnectionError("Failed to connect to ElasticSearch")
                
            return es
        except Exception as e:
            self.logger.error(f"Failed to connect to ElasticSearch: {e}")
            raise
    
    def _init_gemini(self, api_key: str):
        """Initialize Gemini API"""
        try:
            if not api_key:
                api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY environment variable or pass api_key parameter")
            
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel(self.gemini_model_name)
            
            self.logger.info(f"Successfully initialized Gemini model: {self.gemini_model_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {e}")
            raise
    
    def search_elasticsearch(self, query: str, index: str = "_all", size: int = 5) -> List[Dict[str, Any]]:
        """
        Search ElasticSearch for relevant documents
        
        Args:
            query: Search query
            index: ElasticSearch index to search (default: all indices)
            size: Number of results to return
            
        Returns:
            List of search results
        """
        try:
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["*"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                },
                "size": size,
                "_source": True,
                "highlight": {
                    "fields": {
                        "*": {}
                    }
                }
            }
            
            self.logger.info(f"Searching ElasticSearch with query: '{query}' in index: '{index}'")
            response = self.es.search(index=index, body=search_body)
            
            results = []
            for hit in response['hits']['hits']:
                result = {
                    'index': hit['_index'],
                    'id': hit['_id'],
                    'score': hit['_score'],
                    'source': hit['_source'],
                    'highlights': hit.get('highlight', {})
                }
                results.append(result)
            
            self.logger.info(f"Found {len(results)} results")
            return results
            
        except Exception as e:
            self.logger.error(f"ElasticSearch query failed: {e}")
            raise
    
    def format_context(self, search_results: List[Dict[str, Any]]) -> str:
        """
        Format search results as context for Gemini
        
        Args:
            search_results: Results from ElasticSearch
            
        Returns:
            Formatted context string
        """
        if not search_results:
            return "No relevant information found."
        
        context_parts = ["以下は検索された関連情報です:\n"]
        
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"=== 結果 {i} (スコア: {result['score']:.2f}) ===")
            context_parts.append(f"インデックス: {result['index']}")
            context_parts.append(f"ID: {result['id']}")
            
            # Format source data
            source = result['source']
            for key, value in source.items():
                if isinstance(value, (str, int, float)):
                    context_parts.append(f"{key}: {value}")
                elif isinstance(value, (list, dict)):
                    context_parts.append(f"{key}: {json.dumps(value, ensure_ascii=False, indent=2)}")
            
            # Add highlights if available
            if result['highlights']:
                context_parts.append("ハイライト:")
                for field, highlights in result['highlights'].items():
                    context_parts.append(f"  {field}: {' ... '.join(highlights)}")
            
            context_parts.append("")  # Empty line between results
        
        return "\n".join(context_parts)
    
    def generate_response(self, user_query: str, context: str) -> str:
        """
        Generate response using Gemini with retrieved context
        
        Args:
            user_query: User's original query
            context: Context from ElasticSearch results
            
        Returns:
            Generated response from Gemini
        """
        try:
            prompt = f"""あなたは親切で知識豊富なAIアシスタントです。以下の文脈情報を参考にして、ユーザーの質問に答えてください。

文脈情報:
{context}

ユーザーの質問: {user_query}

上記の文脈情報を参考にして、ユーザーの質問に対して正確で役に立つ回答を日本語で提供してください。文脈情報に関連する内容がない場合は、その旨を伝えてください。"""

            self.logger.info("Generating response with Gemini...")
            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                self.logger.info("Successfully generated response")
                return response.text
            else:
                return "申し訳ありませんが、回答を生成できませんでした。"
                
        except Exception as e:
            self.logger.error(f"Failed to generate response with Gemini: {e}")
            return f"エラーが発生しました: {str(e)}"
    
    def process_query(self, user_query: str, index: str = "_all", max_results: int = 5) -> Dict[str, Any]:
        """
        Process a complete RAG query: search + generate
        
        Args:
            user_query: User's query
            index: ElasticSearch index to search
            max_results: Maximum number of search results to use
            
        Returns:
            Dictionary containing search results and generated response
        """
        try:
            # Step 1: Search ElasticSearch
            search_results = self.search_elasticsearch(user_query, index, max_results)
            
            # Step 2: Format context
            context = self.format_context(search_results)
            
            # Step 3: Generate response with Gemini
            response = self.generate_response(user_query, context)
            
            return {
                'query': user_query,
                'timestamp': datetime.now().isoformat(),
                'search_results': search_results,
                'context': context,
                'response': response,
                'num_results': len(search_results)
            }
            
        except Exception as e:
            self.logger.error(f"Failed to process query: {e}")
            raise

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='ElasticSearch RAG with Gemini CLI')
    parser.add_argument('query', help='Search query')
    parser.add_argument('--es-host', default='localhost', help='ElasticSearch host')
    parser.add_argument('--es-port', type=int, default=9200, help='ElasticSearch port')
    parser.add_argument('--es-username', help='ElasticSearch username')
    parser.add_argument('--es-password', help='ElasticSearch password')
    parser.add_argument('--index', default='_all', help='ElasticSearch index to search')
    parser.add_argument('--max-results', type=int, default=5, help='Maximum search results')
    parser.add_argument('--gemini-api-key', help='Gemini API key (or set GEMINI_API_KEY env var)')
    parser.add_argument('--gemini-model', default='gemini-pro', help='Gemini model to use')
    parser.add_argument('--output', help='Output file to save results (JSON format)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize RAG system
        rag = ElasticSearchRAG(
            es_host=args.es_host,
            es_port=args.es_port,
            es_username=args.es_username,
            es_password=args.es_password,
            gemini_api_key=args.gemini_api_key,
            gemini_model=args.gemini_model
        )
        
        # Process query
        result = rag.process_query(args.query, args.index, args.max_results)
        
        # Output results
        print("=" * 80)
        print(f"クエリ: {result['query']}")
        print(f"検索結果数: {result['num_results']}")
        print("=" * 80)
        print("\n回答:")
        print(result['response'])
        print("\n" + "=" * 80)
        
        # Save to file if specified
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"詳細結果を {args.output} に保存しました。")
            
    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()