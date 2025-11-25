"""
LangGraph State Schema
Định nghĩa cấu trúc state cho workflow
"""
from typing import TypedDict, List, Dict, Optional, Annotated
from langgraph.graph import add_messages


class SearchState(TypedDict):
    """
    State cho search workflow
    """
    # Input
    user_query: str
    user_preferences: Dict  # {max_results, year_range, sources}
    
    # Analysis
    query_analysis: Optional[Dict]  # {intent, topic, language, complexity, keywords, mesh_terms}
    
    # Planning
    search_strategy: Optional[Dict]  # {sources, source_priority, filters, reason}
    
    # Execution
    search_results: Optional[Dict]  # {source: [articles]}
    
    # Evaluation
    quality_score: float
    needs_refinement: bool
    refinement_reason: str
    refinement_count: int
    
    # Output
    final_results: List[Dict]
    metadata: Dict
    
    # Messages (for debugging/logging)
    messages: Annotated[list, add_messages]
