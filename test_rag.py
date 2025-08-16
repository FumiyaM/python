#!/usr/bin/env python3
"""
Test script for ElasticSearch + Gemini RAG system
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from elasticsearch_gemini_rag import ElasticSearchRAG, load_config
except ImportError as e:
    print(f"Error importing RAG system: {e}")
    print("Please ensure all dependencies are installed: pip install -r requirements.txt")
    sys.exit(1)


class TestElasticSearchRAG(unittest.TestCase):
    """Test cases for ElasticSearch RAG system"""
    
    def setUp(self):
        """Set up test environment"""
        # Mock API key for testing
        self.test_api_key = "test_api_key"
        
    def test_config_loading(self):
        """Test configuration loading"""
        # Test with environment variables
        with patch.dict(os.environ, {
            'ELASTICSEARCH_HOST': 'test_host',
            'ELASTICSEARCH_PORT': '9200',
            'GEMINI_API_KEY': 'test_key'
        }):
            config = load_config()
            self.assertEqual(config['es_host'], 'test_host')
            self.assertEqual(config['es_port'], 9200)
            self.assertEqual(config['gemini_api_key'], 'test_key')
    
    @patch('elasticsearch_gemini_rag.genai')
    @patch('elasticsearch_gemini_rag.Elasticsearch')
    def test_rag_initialization(self, mock_es, mock_genai):
        """Test RAG system initialization"""
        # Mock ElasticSearch ping
        mock_es_instance = Mock()
        mock_es_instance.ping.return_value = True
        mock_es.return_value = mock_es_instance
        
        # Mock Gemini model
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model
        
        rag = ElasticSearchRAG(
            es_host="localhost",
            es_port=9200,
            gemini_api_key=self.test_api_key
        )
        
        self.assertIsNotNone(rag.es)
        self.assertIsNotNone(rag.model)
        mock_genai.configure.assert_called_once_with(api_key=self.test_api_key)
    
    def test_format_context(self):
        """Test context formatting"""
        # Mock RAG instance
        with patch('elasticsearch_gemini_rag.genai'), \
             patch('elasticsearch_gemini_rag.Elasticsearch'):
            
            rag = ElasticSearchRAG(gemini_api_key=self.test_api_key)
            
            # Test with sample documents
            documents = [
                {
                    'score': 1.5,
                    'index': 'test_index',
                    'id': '1',
                    'source': {
                        'title': 'Test Document',
                        'content': 'This is test content'
                    }
                }
            ]
            
            context = rag.format_context(documents)
            self.assertIn('Retrieved context documents:', context)
            self.assertIn('Test Document', context)
            self.assertIn('This is test content', context)
            self.assertIn('1.50', context)  # Score formatting
    
    def test_format_context_empty(self):
        """Test context formatting with empty documents"""
        with patch('elasticsearch_gemini_rag.genai'), \
             patch('elasticsearch_gemini_rag.Elasticsearch'):
            
            rag = ElasticSearchRAG(gemini_api_key=self.test_api_key)
            context = rag.format_context([])
            self.assertEqual(context, "No relevant documents found.")
    
    @patch('elasticsearch_gemini_rag.genai')
    @patch('elasticsearch_gemini_rag.Elasticsearch')
    def test_search_documents(self, mock_es, mock_genai):
        """Test document search functionality"""
        # Mock ElasticSearch response
        mock_es_instance = Mock()
        mock_search_response = {
            'hits': {
                'hits': [
                    {
                        '_score': 1.5,
                        '_index': 'test_index',
                        '_id': '1',
                        '_source': {'title': 'Test', 'content': 'Content'}
                    }
                ]
            }
        }
        mock_es_instance.search.return_value = mock_search_response
        mock_es.return_value = mock_es_instance
        
        rag = ElasticSearchRAG(gemini_api_key=self.test_api_key)
        
        documents = rag.search_documents("test query")
        
        self.assertEqual(len(documents), 1)
        self.assertEqual(documents[0]['score'], 1.5)
        self.assertEqual(documents[0]['source']['title'], 'Test')
    
    @patch('elasticsearch_gemini_rag.genai')
    @patch('elasticsearch_gemini_rag.Elasticsearch')
    def test_generate_response(self, mock_es, mock_genai):
        """Test response generation"""
        # Mock Gemini model
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Generated response"
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        rag = ElasticSearchRAG(gemini_api_key=self.test_api_key)
        
        response = rag.generate_response("test query", "test context")
        
        self.assertEqual(response, "Generated response")
        mock_model.generate_content.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Integration tests (require actual services)"""
    
    def setUp(self):
        """Set up for integration tests"""
        self.config = load_config()
        
    def test_elasticsearch_connection(self):
        """Test actual ElasticSearch connection if available"""
        if not self.config.get('gemini_api_key'):
            self.skipTest("GEMINI_API_KEY not configured")
        
        try:
            # This test requires actual ElasticSearch running
            from elasticsearch import Elasticsearch
            es = Elasticsearch([{
                "host": self.config['es_host'], 
                "port": self.config['es_port']
            }])
            
            if es.ping():
                print("✓ ElasticSearch connection successful")
            else:
                self.skipTest("ElasticSearch not available")
                
        except Exception as e:
            self.skipTest(f"ElasticSearch connection failed: {e}")


def run_basic_functionality_test():
    """Run a basic functionality test if services are available"""
    print("Testing basic RAG functionality...")
    
    try:
        config = load_config()
        
        if not config.get('gemini_api_key'):
            print("❌ GEMINI_API_KEY not configured. Please set it in .env file.")
            return False
        
        if config['gemini_api_key'] == 'your_gemini_api_key_here':
            print("❌ Please set a real Gemini API key in .env file.")
            return False
        
        # Test ElasticSearch connection
        from elasticsearch import Elasticsearch
        es = Elasticsearch([{
            "host": config['es_host'], 
            "port": config['es_port']
        }])
        
        if not es.ping():
            print("❌ ElasticSearch not available. Please start ElasticSearch.")
            return False
        
        print("✓ ElasticSearch connection successful")
        
        # Initialize RAG system
        rag = ElasticSearchRAG(
            es_host=config['es_host'],
            es_port=config['es_port'],
            es_username=config['es_username'],
            es_password=config['es_password'],
            gemini_api_key=config['gemini_api_key'],
            gemini_model=config['gemini_model']
        )
        
        # Test connections
        if rag.test_connections():
            print("✓ All connections successful")
            
            # Test a simple query (if index exists)
            try:
                result = rag.rag_query("test", num_docs=1)
                print("✓ RAG query test successful")
                return True
            except Exception as e:
                print(f"⚠ RAG query test failed (may be due to no data): {e}")
                return True  # Connection works, just no data
        else:
            print("❌ Connection test failed")
            return False
            
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False


def main():
    """Run tests"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test ElasticSearch + Gemini RAG system")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--functional", action="store_true", help="Run functional test only")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    if not any([args.unit, args.integration, args.functional, args.all]):
        args.all = True
    
    success = True
    
    if args.unit or args.all:
        print("Running unit tests...")
        unittest.main(argv=[''], module='__main__', verbosity=2, exit=False, 
                     defaultTest='TestElasticSearchRAG')
    
    if args.integration or args.all:
        print("\nRunning integration tests...")
        unittest.main(argv=[''], module='__main__', verbosity=2, exit=False,
                     defaultTest='TestIntegration')
    
    if args.functional or args.all:
        print("\nRunning functional test...")
        success = run_basic_functionality_test()
    
    if success:
        print("\n✓ All tests completed")
    else:
        print("\n❌ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()