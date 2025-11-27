"""
Node: Synthesize Findings
AI-generated literature review from filtered papers
"""
from typing import Dict
from ..state_schema import SearchState
from ..gemini_service import GeminiService
from ..prompts.filter_prompt import create_synthesis_prompt
from datetime import datetime


def synthesize_findings(state: SearchState, gemini: GeminiService) -> SearchState:
    """
    Generate AI literature review summary

    Process:
    1. Take all filtered high-quality papers (score >= 7)
    2. Send abstracts to Gemini with synthesis prompt
    3. AI writes comprehensive 300-500 word review
    4. Add metadata (paper count, avg year, date)

    Args:
        state: SearchState with filtered_results
        gemini: Gemini service

    Returns:
        Updated state with synthesis_summary
    """
    filtered_papers = state.get('filtered_results', [])
    user_query = state['user_query']
    query_analysis = state.get('query_analysis', {})

    print(f"\n📝 Synthesizing findings from {len(filtered_papers)} papers...")

    # Handle edge case: no papers to synthesize
    if len(filtered_papers) == 0:
        state['synthesis_summary'] = """
### No High-Quality Papers Found

Unfortunately, no papers met the relevance threshold (score >= 7/10) for this query.

**Recommendations:**
- Try broadening your search terms
- Expand the year range
- Consider related or alternative keywords
- Check if the topic is too specific or niche

The search process was completed, but refinement or query adjustment is recommended for better results.
"""
        state['synthesis_metadata'] = {
            'papers_count': 0,
            'avg_year': 'N/A',
            'synthesis_date': datetime.now().isoformat(),
            'status': 'no_papers'
        }

        print("   ⚠️  No papers to synthesize - returning empty synthesis")
        return state

    # Handle small dataset (< 3 papers)
    if len(filtered_papers) < 3:
        # Simple summary instead of full synthesis
        titles = [p.get('title', 'N/A') for p in filtered_papers]
        years = [p.get('year', 0) for p in filtered_papers if isinstance(p.get('year'), int)]

        summary = f"""
### Limited Results Found

Only {len(filtered_papers)} high-quality paper(s) met the relevance criteria for this query.

**Papers:**
"""
        for i, paper in enumerate(filtered_papers, 1):
            title = paper.get('title', 'N/A')
            year = paper.get('year', 'N/A')
            authors = paper.get('authors', [])
            author_text = authors[0] if authors else 'Unknown'

            summary += f"\n{i}. {author_text} ({year}): {title}\n"

            # Add key finding if available
            key_finding = paper.get('key_finding', 'N/A')
            if key_finding != 'N/A':
                summary += f"   - {key_finding}\n"

        summary += """
**Note:** For more comprehensive results, consider:
- Broadening search terms
- Expanding date range
- Adjusting query specificity
"""

        state['synthesis_summary'] = summary
        state['synthesis_metadata'] = {
            'papers_count': len(filtered_papers),
            'avg_year': sum(years) / len(years) if years else 'N/A',
            'synthesis_date': datetime.now().isoformat(),
            'status': 'limited_data'
        }

        print(f"   ⚠️  Only {len(filtered_papers)} papers - using simple summary")
        return state

    # Full synthesis for >= 3 papers
    try:
        print("   🤖 Generating AI literature review...")

        # Build synthesis prompt
        prompt = create_synthesis_prompt(user_query, filtered_papers, query_analysis)

        # Call Gemini
        response = gemini.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={
                'temperature': 0.4,  # Balanced creativity and accuracy
                'max_output_tokens': 2000  # Allow longer synthesis
            }
        )

        synthesis_text = response.text.strip()

        # Calculate metadata
        years = [p.get('year', 0) for p in filtered_papers if isinstance(p.get('year'), int)]
        avg_year = sum(years) / len(years) if years else 'N/A'

        state['synthesis_summary'] = synthesis_text
        state['synthesis_metadata'] = {
            'papers_count': len(filtered_papers),
            'avg_year': round(avg_year, 1) if isinstance(avg_year, (int, float)) else avg_year,
            'synthesis_date': datetime.now().isoformat(),
            'status': 'success',
            'model': 'gemini-2.0-flash'
        }

        print(f"   ✅ Synthesis completed")
        print(f"      - Length: {len(synthesis_text)} characters")
        print(f"      - Papers synthesized: {len(filtered_papers)}")
        print(f"      - Avg publication year: {avg_year if isinstance(avg_year, str) else f'{avg_year:.1f}'}")

        state['messages'].append({
            'role': 'system',
            'content': f"✅ Generated literature review from {len(filtered_papers)} papers"
        })

    except Exception as e:
        print(f"   ❌ Synthesis error: {e}")

        # Fallback: Create basic summary
        fallback_summary = f"""
### Literature Review Summary

**Query:** "{user_query}"

**Papers Analyzed:** {len(filtered_papers)}

This synthesis could not be generated due to an error. However, {len(filtered_papers)} high-quality papers were found that are relevant to your query.

**Key Papers:**
"""
        for i, paper in enumerate(filtered_papers[:5], 1):  # Show top 5
            title = paper.get('title', 'N/A')
            year = paper.get('year', 'N/A')
            score = paper.get('relevance_score', 'N/A')
            fallback_summary += f"\n{i}. {title} ({year}) - Relevance: {score}/10\n"

        if len(filtered_papers) > 5:
            fallback_summary += f"\n... and {len(filtered_papers) - 5} more papers.\n"

        fallback_summary += "\n**Note:** Please review individual papers for detailed information."

        state['synthesis_summary'] = fallback_summary
        state['synthesis_metadata'] = {
            'papers_count': len(filtered_papers),
            'avg_year': 'N/A',
            'synthesis_date': datetime.now().isoformat(),
            'status': 'error',
            'error': str(e)
        }

        state['messages'].append({
            'role': 'system',
            'content': f"⚠️  Synthesis failed, using fallback summary"
        })

    return state
