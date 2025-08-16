#!/usr/bin/env python3
"""
Demo script for ElasticSearch + Gemini RAG system

This script demonstrates how to use the RAG system with example queries.
"""

import os
import sys

def print_demo_header():
    """Print demo header"""
    print("="*80)
    print("ElasticSearch + Gemini CLI RAG System Demo")
    print("="*80)
    print()

def print_setup_instructions():
    """Print setup instructions"""
    print("📋 Setup Instructions:")
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("2. Set up environment variables:")
    print("   cp .env.example .env")
    print("   # Edit .env file with your API keys")
    print()
    print("3. Start ElasticSearch:")
    print("   docker run -d --name elasticsearch \\")
    print("     -p 9200:9200 -p 9300:9300 \\")
    print("     -e \"discovery.type=single-node\" \\")
    print("     -e \"xpack.security.enabled=false\" \\")
    print("     elasticsearch:8.10.0")
    print()
    print("4. Setup sample data:")
    print("   python setup_sample_data.py")
    print()

def print_example_queries():
    """Print example queries"""
    print("🚀 Example Queries:")
    print()
    
    examples = [
        {
            "description": "Basic query about machine learning",
            "command": "python elasticsearch_gemini_rag.py \"機械学習について教えて\"",
            "expected": "Explains machine learning concepts based on retrieved documents"
        },
        {
            "description": "Query about Python programming",
            "command": "python elasticsearch_gemini_rag.py \"Pythonの特徴は何ですか？\"",
            "expected": "Describes Python features and applications"
        },
        {
            "description": "Query with specific index",
            "command": "python elasticsearch_gemini_rag.py \"深層学習\" --index knowledge",
            "expected": "Explains deep learning from knowledge base"
        },
        {
            "description": "Query with limited results and verbose output",
            "command": "python elasticsearch_gemini_rag.py \"RAG\" --num-docs 3 --verbose",
            "expected": "Explains RAG with detailed document information"
        },
        {
            "description": "Query with specific fields",
            "command": "python elasticsearch_gemini_rag.py \"データサイエンス\" --fields title,content",
            "expected": "Searches only in title and content fields"
        },
        {
            "description": "Save results to file",
            "command": "python elasticsearch_gemini_rag.py \"自然言語処理\" --output nlp_result.json",
            "expected": "Saves complete results to JSON file"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example['description']}")
        print(f"   Command: {example['command']}")
        print(f"   Expected: {example['expected']}")
        print()

def print_troubleshooting():
    """Print troubleshooting tips"""
    print("🔧 Troubleshooting:")
    print()
    print("Connection Issues:")
    print("• Test connections: python elasticsearch_gemini_rag.py --test")
    print("• Check ElasticSearch: curl http://localhost:9200")
    print("• Verify API key in .env file")
    print()
    print("No Results Found:")
    print("• Ensure sample data is loaded: python setup_sample_data.py")
    print("• Try different queries or broader terms")
    print("• Check index name: python elasticsearch_gemini_rag.py \"query\" --index knowledge")
    print()
    print("API Errors:")
    print("• Verify Gemini API key is valid")
    print("• Check internet connection")
    print("• Ensure API quota is not exceeded")
    print()

def print_advanced_usage():
    """Print advanced usage examples"""
    print("🎯 Advanced Usage:")
    print()
    print("Custom Configuration:")
    print("• Set custom ElasticSearch host: ELASTICSEARCH_HOST=remote-host")
    print("• Use authentication: ELASTICSEARCH_USERNAME=user ELASTICSEARCH_PASSWORD=pass")
    print("• Change Gemini model: GEMINI_MODEL=gemini-1.5-pro")
    print()
    print("Batch Processing:")
    print("• Process multiple queries with a shell script:")
    print("  for query in \"機械学習\" \"Python\" \"データサイエンス\"; do")
    print("    python elasticsearch_gemini_rag.py \"$query\" --output \"result_${query}.json\"")
    print("  done")
    print()
    print("Integration:")
    print("• Import as module: from elasticsearch_gemini_rag import ElasticSearchRAG")
    print("• Use in web applications, chatbots, or other tools")
    print()

def main():
    """Main demo function"""
    print_demo_header()
    
    # Check if basic files exist
    required_files = [
        "elasticsearch_gemini_rag.py",
        "requirements.txt",
        ".env.example",
        "README.md"
    ]
    
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("Please ensure all files are in the current directory.")
        return
    
    print("✓ All required files found")
    print()
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("⚠️  .env file not found. You'll need to create it from .env.example")
        print()
    else:
        print("✓ .env file found")
        print()
    
    print_setup_instructions()
    print_example_queries()
    print_troubleshooting()
    print_advanced_usage()
    
    print("="*80)
    print("Ready to start! Begin with: python setup_sample_data.py")
    print("Then try: python elasticsearch_gemini_rag.py \"機械学習について教えて\"")
    print("="*80)

if __name__ == "__main__":
    main()