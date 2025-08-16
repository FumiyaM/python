#!/usr/bin/env python3
"""
ElasticSearch + Gemini CLI RAG (Retrieval Augmented Generation) Script

This script implements a RAG system that:
1. Retrieves relevant documents from ElasticSearch
2. Uses those documents as context for Google Gemini API generation
3. Provides a command-line interface for querying

Author: Gemini CLI RAG Implementation
"""

import argparse
import json
import os
import sys
from typing import List, Dict, Any, Optional

try:
    from elasticsearch import Elasticsearch
    import google.generativeai as genai
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Missing required dependencies. Please install requirements: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)


class ElasticSearchRAG:
    """ElasticSearch + Gemini RAG implementation"""
    
    def __init__(self, 
                 es_host: str = "localhost",
                 es_port: int = 9200,
                 es_username: Optional[str] = None,
                 es_password: Optional[str] = None,
                 gemini_api_key: Optional[str] = None,
                 gemini_model: str = "gemini-1.5-flash"):
        """
        Initialize the RAG system
        
        Args:
            es_host: ElasticSearch host
            es_port: ElasticSearch port
            es_username: ElasticSearch username (optional)
            es_password: ElasticSearch password (optional)
            gemini_api_key: Google Gemini API key
            gemini_model: Gemini model to use
        """
        self.es_host = es_host
        self.es_port = es_port
        self.gemini_model = gemini_model
        
        # Initialize ElasticSearch client
        if es_username and es_password:
            self.es = Elasticsearch(
                [{"host": es_host, "port": es_port}],
                http_auth=(es_username, es_password),
                verify_certs=False
            )
        else:
            self.es = Elasticsearch([{"host": es_host, "port": es_port}])
        
        # Initialize Gemini
        if gemini_api_key:
            genai.configure(api_key=gemini_api_key)
            self.model = genai.GenerativeModel(gemini_model)
        else:
            raise ValueError("Gemini API key is required")
    
    def test_connections(self) -> bool:
        """Test connections to ElasticSearch and Gemini"""
        try:
            # Test ElasticSearch
            if not self.es.ping():
                print("Error: Cannot connect to ElasticSearch")
                return False
            print("✓ ElasticSearch connection successful")
            
            # Test Gemini
            test_response = self.model.generate_content("Hello")
            print("✓ Gemini API connection successful")
            return True
            
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def search_documents(self, 
                        query: str, 
                        index: str = "_all",
                        size: int = 5,
                        fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents in ElasticSearch
        
        Args:
            query: Search query
            index: ElasticSearch index to search
            size: Number of documents to retrieve
            fields: Specific fields to return
            
        Returns:
            List of relevant documents
        """
        try:
            # Build search body
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": fields or ["*"],
                        "type": "best_fields",
                        "fuzziness": "AUTO"
                    }
                },
                "size": size,
                "_source": fields or True
            }
            
            # Execute search
            response = self.es.search(index=index, body=search_body)
            
            # Extract documents
            documents = []
            for hit in response['hits']['hits']:
                doc = {
                    'score': hit['_score'],
                    'index': hit['_index'],
                    'id': hit['_id'],
                    'source': hit['_source']
                }
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"Error searching ElasticSearch: {e}")
            return []
    
    def format_context(self, documents: List[Dict[str, Any]]) -> str:
        """Format retrieved documents as context for Gemini"""
        if not documents:
            return "No relevant documents found."
        
        context_parts = ["Retrieved context documents:"]
        for i, doc in enumerate(documents, 1):
            source = doc['source']
            score = doc['score']
            
            # Create a readable representation of the document
            doc_text = f"\nDocument {i} (relevance: {score:.2f}):\n"
            
            # Handle different document structures
            if isinstance(source, dict):
                for key, value in source.items():
                    if isinstance(value, (str, int, float)):
                        doc_text += f"{key}: {value}\n"
                    elif isinstance(value, list):
                        doc_text += f"{key}: {', '.join(map(str, value))}\n"
            else:
                doc_text += str(source)
            
            context_parts.append(doc_text)
        
        return "\n".join(context_parts)
    
    def generate_response(self, query: str, context: str) -> str:
        """Generate response using Gemini with context"""
        try:
            prompt = f"""
You are an AI assistant that answers questions based on provided context documents.

Context:
{context}

User Question: {query}

Please provide a comprehensive answer based on the context above. If the context doesn't contain relevant information, please say so. Be accurate and cite specific information from the context when possible.

Answer:
"""
            
            response = self.model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            return f"Error generating response: {e}"
    
    def rag_query(self, 
                  query: str, 
                  index: str = "_all",
                  num_docs: int = 5,
                  fields: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Perform complete RAG query: retrieve + generate
        
        Args:
            query: User query
            index: ElasticSearch index to search
            num_docs: Number of documents to retrieve
            fields: Specific fields to search/return
            
        Returns:
            Dictionary containing retrieved documents and generated response
        """
        print(f"🔍 Searching for documents related to: '{query}'")
        
        # Retrieve relevant documents
        documents = self.search_documents(query, index, num_docs, fields)
        
        if documents:
            print(f"📄 Found {len(documents)} relevant documents")
        else:
            print("❌ No relevant documents found")
        
        # Format context
        context = self.format_context(documents)
        
        print("🤖 Generating response with Gemini...")
        
        # Generate response
        response = self.generate_response(query, context)
        
        return {
            "query": query,
            "documents": documents,
            "context": context,
            "response": response
        }


def load_config() -> Dict[str, Any]:
    """Load configuration from environment variables and .env file"""
    load_dotenv()
    
    config = {
        "es_host": os.getenv("ELASTICSEARCH_HOST", "localhost"),
        "es_port": int(os.getenv("ELASTICSEARCH_PORT", 9200)),
        "es_username": os.getenv("ELASTICSEARCH_USERNAME"),
        "es_password": os.getenv("ELASTICSEARCH_PASSWORD"),
        "gemini_api_key": os.getenv("GEMINI_API_KEY"),
        "gemini_model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    }
    
    return config


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="ElasticSearch + Gemini RAG CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python elasticsearch_gemini_rag.py "What is machine learning?"
  python elasticsearch_gemini_rag.py "Python programming" --index my_docs --num-docs 3
  python elasticsearch_gemini_rag.py "data science" --fields title,content --verbose
        """
    )
    
    parser.add_argument("query", help="Query to search and generate response for")
    parser.add_argument("--index", default="_all", help="ElasticSearch index to search (default: _all)")
    parser.add_argument("--num-docs", type=int, default=5, help="Number of documents to retrieve (default: 5)")
    parser.add_argument("--fields", help="Comma-separated list of fields to search/return")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--test", action="store_true", help="Test connections only")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--output", help="Save result to JSON file")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    # Override with command line arguments if provided
    if not config["gemini_api_key"]:
        print("Error: GEMINI_API_KEY environment variable is required")
        print("Please set it in your environment or .env file")
        sys.exit(1)
    
    try:
        # Initialize RAG system
        rag = ElasticSearchRAG(
            es_host=config["es_host"],
            es_port=config["es_port"],
            es_username=config["es_username"],
            es_password=config["es_password"],
            gemini_api_key=config["gemini_api_key"],
            gemini_model=config["gemini_model"]
        )
        
        # Test connections if requested
        if args.test:
            if rag.test_connections():
                print("All connections successful!")
                sys.exit(0)
            else:
                sys.exit(1)
        
        # Parse fields if provided
        fields = None
        if args.fields:
            fields = [f.strip() for f in args.fields.split(",")]
        
        # Perform RAG query
        result = rag.rag_query(
            query=args.query,
            index=args.index,
            num_docs=args.num_docs,
            fields=fields
        )
        
        # Display results
        print("\n" + "="*80)
        print("QUERY RESULTS")
        print("="*80)
        print(f"Query: {result['query']}")
        print(f"Documents found: {len(result['documents'])}")
        print("\n" + "-"*40)
        print("GENERATED RESPONSE:")
        print("-"*40)
        print(result['response'])
        
        if args.verbose:
            print("\n" + "-"*40)
            print("RETRIEVED DOCUMENTS:")
            print("-"*40)
            for i, doc in enumerate(result['documents'], 1):
                print(f"\nDocument {i}:")
                print(f"  Index: {doc['index']}")
                print(f"  ID: {doc['id']}")
                print(f"  Score: {doc['score']:.3f}")
                print(f"  Content: {json.dumps(doc['source'], indent=2, ensure_ascii=False)}")
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\nResults saved to: {args.output}")
    
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()