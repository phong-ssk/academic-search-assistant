"""
AI Filter Prompt Templates
Used for filtering and ranking research papers by relevance
"""


def create_filter_prompt(user_query: str, article: dict, topic_analysis: dict = None) -> str:
    """
    Create prompt for AI to evaluate paper relevance

    Args:
        user_query: Original user search query
        article: Paper metadata (title, abstract, year, journal)
        topic_analysis: Optional topic/intent analysis from query_analysis

    Returns:
        Formatted prompt string
    """

    # Extract article info
    title = article.get('title', 'N/A')
    abstract = article.get('abstract', 'N/A')
    year = article.get('year', 'N/A')
    journal = article.get('journal', 'N/A')

    # Build context from topic analysis if available
    context = ""
    if topic_analysis:
        topic = topic_analysis.get('topic', '')
        intent = topic_analysis.get('intent', '')
        if topic:
            context += f"\nResearch Topic: {topic}"
        if intent:
            context += f"\nUser Intent: {intent}"

    # Handle missing abstract
    if abstract == 'N/A' or not abstract:
        abstract_section = "Abstract: NOT AVAILABLE (please evaluate based on title only)"
        note = "\nNOTE: Since abstract is missing, use title-based scoring and apply more lenient criteria."
    else:
        abstract_section = f"Abstract: {abstract[:500]}..."  # Limit to 500 chars to save tokens
        note = ""

    prompt = f"""You are an expert research paper reviewer specializing in academic literature evaluation.

TASK: Evaluate how relevant this research paper is to the user's query.

USER QUERY: "{user_query}"{context}

PAPER DETAILS:
- Title: {title}
- {abstract_section}
- Journal: {journal}
- Year: {year}
{note}

EVALUATION CRITERIA (Score 1-10):
1. **Direct Relevance** (0-4 points):
   - Does the paper directly address the user's query topic?
   - 4: Directly answers the query
   - 2-3: Related but not focused
   - 0-1: Tangentially related or off-topic

2. **Methodological Appropriateness** (0-3 points):
   - Are the methods/approach suitable for the query?
   - 3: Highly appropriate methodology
   - 1-2: Somewhat relevant methods
   - 0: Irrelevant or inappropriate methods

3. **Quality & Impact** (0-3 points):
   - Publication recency and journal quality
   - 3: Recent (<5 years) in reputable journal
   - 1-2: Older or moderate journal
   - 0: Very old or questionable source

SCORING GUIDELINES:
- **8-10**: HIGHLY RELEVANT - Directly addresses query, excellent match
- **6-7**: MODERATELY RELEVANT - Related and useful, keep if specific niche
- **4-5**: SOMEWHAT RELEVANT - Tangentially related, discard unless critical gap
- **1-3**: LOW RELEVANCE - Off-topic or not useful, discard

DECISION RULE:
- Keep papers with score >= 7 (highly relevant)
- Discard papers with score < 7 unless exceptional circumstances

OUTPUT FORMAT (Valid JSON only):
{{
  "relevance_score": <integer 1-10>,
  "keep": <true or false>,
  "reasoning": "<brief 1-2 sentence explanation of score>",
  "key_finding": "<1 sentence summary if relevant, or 'N/A' if not>"
}}

IMPORTANT:
- Be strict but fair in scoring
- Consider both exact keyword matches AND conceptual relevance
- If abstract is missing, be more cautious (lower scores)
- Return ONLY the JSON object, no additional text
"""

    return prompt


def create_batch_filter_prompt(user_query: str, articles: list, topic_analysis: dict = None) -> str:
    """
    Create prompt for batch evaluation (evaluate multiple papers at once)
    More efficient for API calls

    Args:
        user_query: Original user search query
        articles: List of paper metadata
        topic_analysis: Optional topic/intent analysis

    Returns:
        Formatted batch prompt
    """

    context = ""
    if topic_analysis:
        topic = topic_analysis.get('topic', '')
        intent = topic_analysis.get('intent', '')
        if topic:
            context += f"\nResearch Topic: {topic}"
        if intent:
            context += f"\nUser Intent: {intent}"

    # Build papers list
    papers_text = ""
    for i, article in enumerate(articles, 1):
        title = article.get('title', 'N/A')
        abstract = article.get('abstract', 'N/A')
        year = article.get('year', 'N/A')

        if abstract == 'N/A' or not abstract:
            abstract_text = "[NO ABSTRACT]"
        else:
            abstract_text = abstract[:300]  # Limit length

        papers_text += f"\n\n--- PAPER {i} ---\nTitle: {title}\nAbstract: {abstract_text}\nYear: {year}\n"

    prompt = f"""You are an expert research paper reviewer.

TASK: Evaluate the relevance of {len(articles)} papers to the user's query.

USER QUERY: "{user_query}"{context}

PAPERS TO EVALUATE:{papers_text}

For EACH paper, provide a score (1-10) using these criteria:
- Direct relevance to query (0-4 points)
- Methodological appropriateness (0-3 points)
- Quality & recency (0-3 points)

SCORING:
- 8-10: HIGHLY RELEVANT, keep
- 6-7: MODERATELY RELEVANT, keep if niche match
- 1-5: LOW RELEVANCE, discard

Keep papers with score >= 7.

OUTPUT FORMAT (Valid JSON array):
[
  {{
    "paper_id": 1,
    "relevance_score": <1-10>,
    "keep": <true/false>,
    "reasoning": "<brief explanation>"
  }},
  ...
]

Return ONLY the JSON array, no additional text.
"""

    return prompt


def create_synthesis_prompt(user_query: str, papers: list, query_analysis: dict = None) -> str:
    """
    Create prompt for literature synthesis

    Args:
        user_query: Original user search query
        papers: List of filtered high-quality papers
        query_analysis: Optional query analysis context

    Returns:
        Synthesis prompt
    """

    # Build papers text with citations
    papers_text = ""
    for i, paper in enumerate(papers, 1):
        title = paper.get('title', 'N/A')
        abstract = paper.get('abstract', 'N/A')
        year = paper.get('year', 'N/A')
        authors = paper.get('authors', [])

        # Format authors
        if authors:
            if len(authors) > 2:
                author_text = f"{authors[0]} et al."
            else:
                author_text = ", ".join(authors)
        else:
            author_text = "Unknown"

        papers_text += f"\n[{i}] {author_text} ({year}): {title}\n"
        if abstract and abstract != 'N/A':
            papers_text += f"    Summary: {abstract[:400]}...\n"

    # Add context
    context = ""
    if query_analysis:
        topic = query_analysis.get('topic', '')
        if topic:
            context = f"\nResearch Domain: {topic}"

    prompt = f"""You are an expert research synthesizer specializing in academic literature review.

TASK: Write a comprehensive literature review summary based on the following {len(papers)} research papers.

USER QUERY: "{user_query}"{context}

RESEARCH PAPERS:{papers_text}

INSTRUCTIONS:
1. **ANSWER THE QUERY**: Directly address what the user asked - this is the primary goal
2. **KEY FINDINGS**: Summarize the main discoveries and conclusions across these papers
3. **METHODOLOGICAL TRENDS**: Note common research approaches, if applicable
4. **CONSENSUS & CONFLICTS**: Highlight agreements or disagreements between studies
5. **RESEARCH GAPS**: Identify what's missing or needs further investigation
6. **CITATIONS**: Reference papers using [1], [2], etc. format

FORMAT REQUIREMENTS:
- Use markdown formatting
- Length: 300-500 words
- Professional academic tone but accessible
- Be concise yet comprehensive
- Start with a direct answer to the query

STRUCTURE:
### Key Findings
[Main discoveries that answer the query]

### Research Trends
[Common approaches and patterns]

### Notable Results
[Specific findings worth highlighting with citations]

### Knowledge Gaps
[What remains unclear or understudied]

Begin your synthesis now:
"""

    return prompt
