"""
Test script for LangGraph workflow
Chạy thử nghiệm để xem workflow hoạt động
"""
import os
from dotenv import load_dotenv
from backend.langgraph_orchestrator import build_search_graph, invoke_search

# Load environment
load_dotenv()

def test_medical_vietnamese():
    """Test case 1: Medical research in Vietnamese"""
    print("\n" + "="*80)
    print("TEST CASE 1: Medical Research (Vietnamese)")
    print("="*80)
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return
    
    # Build graph
    print("\n🔧 Building LangGraph...")
    graph = build_search_graph(
        gemini_api_key=gemini_key,
        pubmed_key=os.getenv("PUBMED_API_KEY"),
        scopus_key=os.getenv("SCOPUS_API_KEY"),
        semantic_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    )
    
    # Test query
    query = "Điều trị tăng huyết áp ở người cao tuổi"
    preferences = {
        'max_results': 15,
        'year_range': [2020, 2025],
        'sources': ['PubMed', 'Semantic Scholar']
    }
    
    # Execute
    print(f"\n🚀 Testing query: {query}")
    final_state = invoke_search(graph, query, preferences)
    
    # Results
    print("\n" + "="*80)
    print("📊 RESULTS")
    print("="*80)
    print(f"Total Articles: {len(final_state['final_results'])}")
    print(f"Quality Score: {final_state['quality_score']:.2f}")
    print(f"Refinement Count: {final_state['refinement_count']}")
    print(f"Metadata: {final_state['metadata']}")
    
    # Show first 3 articles
    print("\n📚 First 3 articles:")
    for i, article in enumerate(final_state['final_results'][:3], 1):
        print(f"\n{i}. {article.get('title', 'N/A')}")
        print(f"   Source: {article.get('source')}")
        print(f"   Year: {article.get('year')}")
        print(f"   DOI: {article.get('doi', 'N/A')}")


def test_engineering_english():
    """Test case 2: Engineering research in English"""
    print("\n" + "="*80)
    print("TEST CASE 2: Engineering Research (English)")
    print("="*80)
    
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return
    
    # Build graph
    print("\n🔧 Building LangGraph...")
    graph = build_search_graph(
        gemini_api_key=gemini_key,
        pubmed_key=os.getenv("PUBMED_API_KEY"),
        scopus_key=os.getenv("SCOPUS_API_KEY"),
        semantic_key=os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    )
    
    # Test query
    query = "Machine learning in healthcare"
    preferences = {
        'max_results': 10,
        'year_range': [2022, 2025],
        'sources': ['PubMed', 'Semantic Scholar']
    }
    
    # Execute
    print(f"\n🚀 Testing query: {query}")
    final_state = invoke_search(graph, query, preferences)
    
    # Results
    print("\n" + "="*80)
    print("📊 RESULTS")
    print("="*80)
    print(f"Total Articles: {len(final_state['final_results'])}")
    print(f"Quality Score: {final_state['quality_score']:.2f}")
    print(f"Refinement Count: {final_state['refinement_count']}")
    
    # Show sources breakdown
    sources_count = {}
    for article in final_state['final_results']:
        source = article.get('source')
        sources_count[source] = sources_count.get(source, 0) + 1
    
    print(f"\n📊 Sources breakdown:")
    for source, count in sources_count.items():
        print(f"   - {source}: {count} articles")


def test_deduplication():
    """Test case 3: Test deduplication mechanism"""
    print("\n" + "="*80)
    print("TEST CASE 3: Deduplication Test")
    print("="*80)
    
    from backend.async_apis import ArticleDeduplicator
    
    # Sample articles with duplicates
    articles = [
        {
            'title': 'Machine Learning in Healthcare',
            'doi': '10.1234/ml.2023.001',
            'source': 'PubMed',
            'year': 2023
        },
        {
            'title': 'Machine Learning in Healthcare',  # Duplicate title
            'doi': '10.1234/ml.2023.001',  # Same DOI
            'source': 'Scopus',
            'year': 2023
        },
        {
            'title': 'Deep Learning for Medical Diagnosis',
            'doi': '10.5678/dl.2024.002',
            'source': 'PubMed',
            'year': 2024
        },
        {
            'title': 'Deep Learning for Medical Diagnosis',  # Similar title
            'doi': 'N/A',  # No DOI
            'source': 'Semantic Scholar',
            'year': 2024
        },
        {
            'title': 'Artificial Intelligence in Radiology',
            'doi': 'N/A',
            'pmid': '12345678',
            'source': 'PubMed',
            'year': 2023
        },
        {
            'title': 'AI in Radiology (Different title)',
            'doi': 'N/A',
            'pmid': '12345678',  # Same PMID
            'source': 'Scopus',
            'year': 2023
        }
    ]
    
    print(f"\n📊 Before deduplication: {len(articles)} articles")
    
    dedup = ArticleDeduplicator()
    unique = dedup.deduplicate(articles)
    
    print(f"📊 After deduplication: {len(unique)} articles")
    print(f"🗑️  Removed: {len(articles) - len(unique)} duplicates")
    
    print("\n📚 Unique articles:")
    for i, article in enumerate(unique, 1):
        print(f"{i}. {article.get('title')[:60]}... ({article.get('source')})")


def test_cache():
    """Test case 4: Test caching mechanism"""
    print("\n" + "="*80)
    print("TEST CASE 4: Cache Test")
    print("="*80)
    
    from backend.async_apis import SearchCache
    
    cache = SearchCache(ttl_minutes=1)
    
    # Set cache
    cache.set('PubMed', 'test query', {'max': 10}, [{'title': 'Article 1'}])
    
    # Get cache (should hit)
    result = cache.get('PubMed', 'test query', {'max': 10})
    
    if result:
        print(f"✅ Cache HIT: Found {len(result)} articles")
    else:
        print("❌ Cache MISS")
    
    # Different query (should miss)
    result2 = cache.get('PubMed', 'different query', {'max': 10})
    
    if result2:
        print(f"✅ Cache HIT for different query")
    else:
        print("❌ Cache MISS for different query (expected)")


if __name__ == "__main__":
    print("\n🧪 LangGraph Workflow Test Suite")
    print("="*80)
    
    # Run tests
    try:
        # Test 1: Medical Vietnamese
        test_medical_vietnamese()
        
        # Test 2: Engineering English
        # test_engineering_english()
        
        # Test 3: Deduplication
        test_deduplication()
        
        # Test 4: Cache
        test_cache()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80)
        
    except KeyboardInterrupt:
        print("\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
