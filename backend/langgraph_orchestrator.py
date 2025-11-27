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
from .nodes.synthesize import synthesize_findings  # NEW
from .gemini_service import GeminiService
from .async_apis import AsyncSearchAPIs


def should_refine(state: SearchState) -> Literal["refine", "synthesize"]:
    """
    NEW DECISION LOGIC - Math-based, not AI guessing

    Quyết định có refine hay tiếp tục synthesis

    Điều kiện TIẾP TỤC (synthesize):
    1. Kept papers >= 50% of target (sufficient quality results)
    2. OR refinement_count >= 2 (max attempts reached)

    Điều kiện REFINE:
    1. Kept papers < 50% of target
    2. AND refinement_count < 2
    """
    needs_refinement = state.get('needs_refinement', False)
    refinement_count = state.get('refinement_count', 0)
    filtered_count = len(state.get('filtered_results', []))
    target = state['user_preferences'].get('max_results', 10)

    # Get statistics for logging
    filter_stats = state.get('filter_statistics', {})
    avg_score = filter_stats.get('avg_score', 0.0)

    # Decision: Continue to synthesis if we have enough quality papers OR max attempts reached
    if not needs_refinement:
        print(f"\n✅ Search completed successfully!")
        print(f"   → {filtered_count} quality papers (avg score: {avg_score}/10)")
        return "synthesize"

    # Max attempts reached - proceed to synthesis with what we have
    if refinement_count >= 2:
        print(f"\n⚠️  Max refinement attempts reached ({refinement_count}/2)")
        print(f"   → Proceeding with {filtered_count} quality papers")
        return "synthesize"

    # Need more results - refine query
    print(f"\n🔄 Refinement needed (attempt {refinement_count + 1}/2)")
    print(f"   → Only {filtered_count}/{target} quality papers found")
    return "refine"


def build_search_graph(gemini_api_key: str, pubmed_key: str = None,
                       scopus_key: str = None, semantic_key: str = None):
    """
    Build LangGraph workflow with AI Filtering & Synthesis

    NEW Flow:
    START → ANALYZE → PLAN → OPTIMIZE → EXECUTE → EVALUATE (AI Filter)
                                            ↑          ↓
                                            └─ REFINE ←┘ (if needed)
                                                       ↓
                                                   SYNTHESIZE → END
    """
    # Initialize services
    gemini = GeminiService(gemini_api_key)
    async_apis = AsyncSearchAPIs(pubmed_key, scopus_key, semantic_key)

    # Create graph
    workflow = StateGraph(SearchState)

    # Add nodes with partial application
    workflow.add_node("analyze_query", lambda state: analyze_query(state, gemini))
    workflow.add_node("plan_strategy", lambda state: plan_strategy(state, gemini))
    workflow.add_node("optimize_queries", lambda state: optimize_queries(state, gemini))
    workflow.add_node("execute_search", lambda state: execute_search(state, async_apis))
    workflow.add_node("evaluate_results", lambda state: evaluate_results(state, gemini, async_apis))
    workflow.add_node("refine_query", lambda state: refine_query(state, gemini))
    workflow.add_node("synthesize_findings", lambda state: synthesize_findings(state, gemini))  # NEW

    # Set entry point
    workflow.set_entry_point("analyze_query")

    # Add edges (deterministic flow)
    workflow.add_edge("analyze_query", "plan_strategy")
    workflow.add_edge("plan_strategy", "optimize_queries")
    workflow.add_edge("optimize_queries", "execute_search")
    workflow.add_edge("execute_search", "evaluate_results")

    # Conditional edge: evaluate → refine OR synthesize
    workflow.add_conditional_edges(
        "evaluate_results",
        should_refine,
        {
            "refine": "refine_query",
            "synthesize": "synthesize_findings"  # NEW path
        }
    )

    # Refinement loop back
    workflow.add_edge("refine_query", "optimize_queries")

    # Synthesis leads to END
    workflow.add_edge("synthesize_findings", END)  # NEW

    # Compile
    graph = workflow.compile()

    print("✅ LangGraph Research Agent workflow compiled successfully!")
    print("   → NEW: AI abstract filtering + literature synthesis enabled")

    return graph


def invoke_search(graph, user_query: str, user_preferences: dict, progress_callback=None):
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
        progress_callback: Optional callback function(node_name: str, state: dict) for progress updates

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
        # NEW: AI Filtering fields
        'filtered_results': None,
        'discarded_articles': None,
        'relevance_scores': None,
        'filter_statistics': None,
        # NEW: Synthesis fields
        'synthesis_summary': None,
        'synthesis_metadata': None,
        # Output
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

    # Invoke graph with streaming if callback provided
    if progress_callback:
        # Stream through workflow nodes
        for event in graph.stream(initial_state):
            # Event is a dict with node name as key
            for node_name, node_state in event.items():
                print(f"📍 Node: {node_name}")
                progress_callback(node_name, node_state)

        # Get final state
        final_state = node_state
    else:
        # Regular invoke without streaming
        final_state = graph.invoke(initial_state)

    print(f"\n{'='*60}")
    print(f"✅ Research Agent Workflow Completed")
    print(f"{'='*60}")

    # Get filter statistics
    filter_stats = final_state.get('filter_statistics', {})
    total_found = filter_stats.get('total_found', 0)
    kept = len(final_state.get('final_results', []))
    discarded = filter_stats.get('discarded', 0)
    avg_score = filter_stats.get('avg_score', 0.0)

    print(f"Search Results:")
    print(f"  - Total found: {total_found}")
    print(f"  - High-quality papers (kept): {kept}")
    print(f"  - Filtered out: {discarded}")
    print(f"  - Avg relevance score: {avg_score}/10")
    print(f"  - Refinement attempts: {final_state['refinement_count']}")

    # Check if synthesis was generated
    if final_state.get('synthesis_summary'):
        synth_meta = final_state.get('synthesis_metadata', {})
        print(f"\nLiterature Review:")
        print(f"  - Status: {synth_meta.get('status', 'unknown')}")
        print(f"  - Papers synthesized: {synth_meta.get('papers_count', 0)}")

    print(f"{'='*60}\n")

    return final_state
