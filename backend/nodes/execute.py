"""
Node: Execute Search
Thực thi tìm kiếm SONG SONG với async
"""
from typing import Dict
from ..state_schema import SearchState
from ..async_apis import AsyncSearchAPIs
import asyncio


async def execute_search_async(state: SearchState, async_apis: AsyncSearchAPIs) -> SearchState:
    """
    Thực thi tìm kiếm song song trên các nguồn đã chọn
    với caching & early stopping
    """
    strategy = state['search_strategy']
    queries = strategy.get('optimized_queries', {})
    filters = strategy.get('filters', {})
    
    year_range = filters.get('year_range', [2020, 2025])
    max_per_source = filters.get('max_results_per_source', 10)
    
    print(f"\n🚀 Executing parallel search:")
    print(f"   - Year range: {year_range[0]}-{year_range[1]}")
    print(f"   - Max per source: {max_per_source}")
    
    # Execute parallel search
    results_dict = await async_apis.search_all_parallel(
        queries=queries,
        max_results_per_source=max_per_source,
        year_start=year_range[0],
        year_end=year_range[1]
    )
    
    state['search_results'] = results_dict
    
    # Log results count
    total_count = sum(len(articles) for articles in results_dict.values())
    
    state['messages'].append({
        'role': 'system',
        'content': f"✅ Found {total_count} articles from {len(results_dict)} sources"
    })
    
    print(f"\n📊 Search Results:")
    for source, articles in results_dict.items():
        print(f"   - {source}: {len(articles)} articles")
    
    return state


def execute_search(state: SearchState, async_apis: AsyncSearchAPIs) -> SearchState:
    """
    Wrapper để chạy async function trong sync context
    """
    # Chạy async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        updated_state = loop.run_until_complete(execute_search_async(state, async_apis))
        return updated_state
    finally:
        loop.close()
