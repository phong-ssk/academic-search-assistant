"""
LangGraph Orchestrator
Xây dựng & compile workflow graph
"""
from langgraph.graph import StateGraph, END
from typing import Literal
from .state_schema import SearchState
from .nodes.analyze import analyze_query
from .nodes.plan import plan_strategy
from .nodes.optimize import optimize_queries
from .nodes.execute import execute_search
from .nodes.evaluate import evaluate_results
from .nodes.refine import refine_query
from .gemini_service import GeminiService
from .async_apis import AsyncSearchAPIs


def should_refine(state: SearchState) -> Literal["refine", "end"]:
    """
    Quyết định có refine hay không
    
    Điều kiện DỪNG:
    1. needs_refinement = False (kết quả tốt)
    2. refinement_count >= 2 (đã refine 2 lần)
    3. quality_score >= 0.7 (chất lượng tốt)
    """
    needs_refinement = state.get('needs_refinement', False)
    refinement_count = state.get('refinement_count', 0)
    quality_score = state.get('quality_score', 0.0)
    
    # Dừng nếu không cần refine
    if not needs_refinement:
        print(f"\n✅ Search completed successfully!")
        return "end"
    
    # Dừng nếu đã refine 2 lần
    if refinement_count >= 2:
        print(f"\n⚠️  Max refinement attempts reached (2)")
        return "end"
    
    # Dừng nếu quality tốt
    if quality_score >= 0.7:
        print(f"\n✅ Quality score {quality_score:.2f} is good enough")
        return "end"
    
    # Tiếp tục refine
    print(f"\n🔄 Refinement needed (attempt {refinement_count + 1}/2)")
    return "refine"


def build_search_graph(gemini_api_key: str, pubmed_key: str = None, 
                       scopus_key: str = None, semantic_key: str = None):
    """
    Build LangGraph workflow
    
    Flow:
    START → ANALYZE → PLAN → OPTIMIZE → EXECUTE → EVALUATE
                                            ↑          ↓
                                            └─ REFINE ←┘ (if needed)
    """
    # Initialize services
    gemini = GeminiService(gemini_api_key)
    async_apis = AsyncSearchAPIs(pubmed_key, scopus_key, semantic_key)
    
    # Create graph
    workflow = StateGraph(SearchState)
    
    # Add nodes với partial application
    workflow.add_node("analyze_query", lambda state: analyze_query(state, gemini))
    workflow.add_node("plan_strategy", lambda state: plan_strategy(state, gemini))
    workflow.add_node("optimize_queries", lambda state: optimize_queries(state, gemini))
    workflow.add_node("execute_search", lambda state: execute_search(state, async_apis))
    workflow.add_node("evaluate_results", lambda state: evaluate_results(state, gemini, async_apis))
    workflow.add_node("refine_query", lambda state: refine_query(state, gemini))
    
    # Set entry point
    workflow.set_entry_point("analyze_query")
    
    # Add edges (deterministic flow)
    workflow.add_edge("analyze_query", "plan_strategy")
    workflow.add_edge("plan_strategy", "optimize_queries")
    workflow.add_edge("optimize_queries", "execute_search")
    workflow.add_edge("execute_search", "evaluate_results")
    
    # Conditional edge: evaluate → refine OR end
    workflow.add_conditional_edges(
        "evaluate_results",
        should_refine,
        {
            "refine": "refine_query",
            "end": END
        }
    )
    
    # Refinement loop back
    workflow.add_edge("refine_query", "optimize_queries")
    
    # Compile
    graph = workflow.compile()
    
    print("✅ LangGraph workflow compiled successfully!")
    
    return graph


def invoke_search(graph, user_query: str, user_preferences: dict):
    """
    Execute search workflow
    
    Args:
        graph: Compiled LangGraph
        user_query: User's search query
        user_preferences: {
            'max_results': int,
            'year_range': [start, end],
            'sources': ['PubMed', 'Scopus', 'Semantic Scholar']
        }
    
    Returns:
        Final state với results
    """
    initial_state = {
        'user_query': user_query,
        'user_preferences': user_preferences,
        'query_analysis': None,
        'search_strategy': None,
        'search_results': None,
        'quality_score': 0.0,
        'needs_refinement': False,
        'refinement_reason': '',
        'refinement_count': 0,
        'final_results': [],
        'metadata': {},
        'messages': []
    }
    
    print(f"\n{'='*60}")
    print(f"🚀 Starting LangGraph Search Workflow")
    print(f"{'='*60}")
    print(f"Query: {user_query}")
    print(f"Preferences: {user_preferences}")
    print(f"{'='*60}\n")
    
    # Invoke graph
    final_state = graph.invoke(initial_state)
    
    print(f"\n{'='*60}")
    print(f"✅ Workflow Completed")
    print(f"{'='*60}")
    print(f"Final Results: {len(final_state['final_results'])} unique articles")
    print(f"Quality Score: {final_state['quality_score']:.2f}")
    print(f"Refinement Attempts: {final_state['refinement_count']}")
    print(f"{'='*60}\n")
    
    return final_state
