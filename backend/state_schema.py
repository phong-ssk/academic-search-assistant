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

    # NEW: AI Filtering & Ranking
    filtered_results: Optional[List[Dict]]  # Papers that passed AI filter (score >= 7)
    discarded_articles: Optional[List[Dict]]  # Papers rejected by AI + reasons
    relevance_scores: Optional[Dict]  # {article_id: score} mapping
    filter_statistics: Optional[Dict]  # {total_found, kept, discarded, avg_score, pass_rate}

    # NEW: Literature Synthesis
    synthesis_summary: Optional[str]  # AI-generated literature review
    synthesis_metadata: Optional[Dict]  # {papers_count, avg_year, synthesis_date}

    # Output
    final_results: List[Dict]
    metadata: Dict

    # Messages (for debugging/logging)
    messages: Annotated[list, add_messages]
