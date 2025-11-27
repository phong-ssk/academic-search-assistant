"""
Node: Evaluate Results with AI Abstract Filtering
Đánh giá chất lượng kết quả & filter papers by relevance
"""
from typing import Dict, List
from ..state_schema import SearchState
from ..gemini_service import GeminiService
from ..async_apis import AsyncSearchAPIs
from ..prompts.filter_prompt import create_filter_prompt
import json
import time


def evaluate_results(state: SearchState, gemini: GeminiService, async_apis: AsyncSearchAPIs) -> SearchState:
    """
    NEW EVALUATION PROCESS:
    1. Deduplicate results
    2. AI reads EVERY abstract and scores relevance (1-10)
    3. Keep only papers with score >= 7
    4. Calculate math-based quality score
    5. Decide refinement based on kept_count vs target

    Stopping criteria:
    1. Kept papers >= 50% of target
    2. Already refined 2 times
    """
    results_dict = state['search_results']
    user_query = state['user_query']
    query_analysis = state.get('query_analysis', {})
    preferences = state['user_preferences']
    refinement_count = state.get('refinement_count', 0)

    # Count total results
    total_count = sum(len(articles) for articles in results_dict.values())

    # Basic check: No results
    if total_count == 0:
        state['needs_refinement'] = True
        state['refinement_reason'] = "No results found"
        state['quality_score'] = 0.0
        state['final_results'] = []
        state['filtered_results'] = []
        state['discarded_articles'] = []
        state['filter_statistics'] = {
            'total_found': 0,
            'kept': 0,
            'discarded': 0,
            'avg_score': 0.0,
            'pass_rate': 0.0
        }
        state['messages'].append({
            'role': 'system',
            'content': "⚠️  No results found, needs refinement"
        })
        return state

    # Step 1: Deduplicate & merge
    print(f"\n🔍 Step 1: Deduplicating {total_count} articles...")
    unique_articles = async_apis.deduplicate_results(results_dict)
    print(f"   → {len(unique_articles)} unique articles after deduplication")

    # Step 2: AI Filter & Rank every article
    print(f"\n🤖 Step 2: AI filtering {len(unique_articles)} articles by relevance...")
    filtered_results, discarded_articles, relevance_scores = filter_by_ai_relevance(
        unique_articles,
        user_query,
        query_analysis,
        gemini
    )

    # Step 3: Calculate statistics
    total_found = len(unique_articles)
    kept_count = len(filtered_results)
    discarded_count = len(discarded_articles)
    avg_score = sum(relevance_scores.values()) / total_found if total_found > 0 else 0.0
    pass_rate = kept_count / total_found if total_found > 0 else 0.0

    filter_statistics = {
        'total_found': total_found,
        'kept': kept_count,
        'discarded': discarded_count,
        'avg_score': round(avg_score, 2),
        'pass_rate': round(pass_rate * 100, 1)  # Percentage
    }

    print(f"\n📊 Filter Statistics:")
    print(f"   - Total found: {total_found}")
    print(f"   - Kept (score >= 7): {kept_count}")
    print(f"   - Discarded: {discarded_count}")
    print(f"   - Avg relevance score: {avg_score:.2f}/10")
    print(f"   - Pass rate: {pass_rate*100:.1f}%")

    # Step 4: Calculate quality score (math-based, not AI guessing)
    quality_score = pass_rate  # Simple: % of papers that passed filter

    # Step 5: Decide if refinement is needed
    requested = preferences.get('max_results', 10)
    has_enough = kept_count >= (requested * 0.5)  # Need at least 50% of target

    # Decision logic
    if refinement_count >= 2:
        needs_refinement = False
        reason = f"Max refinement attempts reached ({refinement_count}/2)"
    elif kept_count == 0:
        needs_refinement = True
        reason = "No relevant papers found (all scored < 7)"
    elif not has_enough:
        needs_refinement = True
        reason = f"Insufficient quality papers ({kept_count} < {requested*0.5:.0f} needed)"
    else:
        needs_refinement = False
        reason = f"Sufficient quality papers ({kept_count} >= {requested*0.5:.0f})"

    # Update state with new fields
    state['filtered_results'] = filtered_results
    state['discarded_articles'] = discarded_articles
    state['relevance_scores'] = relevance_scores
    state['filter_statistics'] = filter_statistics
    state['final_results'] = filtered_results  # Final results are the filtered ones
    state['quality_score'] = quality_score
    state['needs_refinement'] = needs_refinement
    state['refinement_reason'] = reason

    print(f"\n🎯 Decision:")
    print(f"   - Quality Score: {quality_score:.2f}")
    print(f"   - Needs Refinement: {needs_refinement}")
    print(f"   - Reason: {reason}")

    state['messages'].append({
        'role': 'system',
        'content': f"✅ Filtered: {kept_count}/{total_found} papers (avg score: {avg_score:.1f}/10)"
    })

    # Add metadata
    state['metadata'] = {
        'total_found': total_count,
        'unique_count': len(unique_articles),
        'filtered_count': kept_count,
        'quality_score': quality_score,
        'refinement_count': refinement_count,
        'sources_used': list(results_dict.keys())
    }

    return state


def filter_by_ai_relevance(
    articles: List[Dict],
    user_query: str,
    query_analysis: Dict,
    gemini: GeminiService,
    score_threshold: float = 7.0,
    batch_size: int = 1  # Process one at a time for better accuracy
) -> tuple:
    """
    Filter articles using AI to read abstracts and score relevance

    Args:
        articles: List of deduplicated articles
        user_query: User's search query
        query_analysis: Query analysis from analyze node
        gemini: Gemini service
        score_threshold: Minimum score to keep (default: 7.0)
        batch_size: Number of articles to process at once (default: 1 for accuracy)

    Returns:
        (filtered_results, discarded_articles, relevance_scores)
    """
    filtered_results = []
    discarded_articles = []
    relevance_scores = {}

    total = len(articles)

    for i, article in enumerate(articles, 1):
        print(f"   Processing {i}/{total}: {article.get('title', 'N/A')[:60]}...")

        try:
            # Create unique ID for tracking
            article_id = article.get('doi') or article.get('pmid') or f"article_{i}"

            # Build filter prompt
            prompt = create_filter_prompt(user_query, article, query_analysis)

            # Call Gemini API
            response = gemini.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config={
                    'response_mime_type': 'application/json',
                    'temperature': 0.2  # Low temp for consistent scoring
                }
            )

            # Parse response
            result = json.loads(response.text.strip())

            score = float(result.get('relevance_score', 5.0))
            keep = result.get('keep', False)
            reasoning = result.get('reasoning', 'No reasoning provided')
            key_finding = result.get('key_finding', 'N/A')

            # Store score
            relevance_scores[article_id] = score

            # Add metadata to article
            article['relevance_score'] = score
            article['ai_reasoning'] = reasoning
            article['key_finding'] = key_finding

            # Categorize
            if keep and score >= score_threshold:
                filtered_results.append(article)
                print(f"      ✅ KEEP (Score: {score}/10)")
            else:
                article['discard_reason'] = reasoning
                discarded_articles.append(article)
                print(f"      ❌ DISCARD (Score: {score}/10) - {reasoning[:50]}...")

            # Small delay to avoid rate limits
            time.sleep(0.1)

        except json.JSONDecodeError as e:
            print(f"      ⚠️  JSON parse error, using fallback - {e}")
            # Fallback: assign neutral score
            score = 5.0
            article['relevance_score'] = score
            article['discard_reason'] = "AI parse error - assigned neutral score"
            relevance_scores[article_id] = score
            discarded_articles.append(article)

        except Exception as e:
            print(f"      ⚠️  Error evaluating article: {e}")
            # On error, keep the article (benefit of doubt)
            article['relevance_score'] = 6.0
            article['ai_reasoning'] = f"Error during evaluation: {str(e)}"
            relevance_scores[article_id] = 6.0
            filtered_results.append(article)

    return filtered_results, discarded_articles, relevance_scores
