"""
Token optimization utilities for truncating content before sending to LLM
"""
from typing import List, Dict, Any


def truncate_text(text: str, max_chars: int = None, max_tokens: int = None) -> str:
    """
    Truncate text to fit within token/character limits
    
    Args:
        text: Text to truncate
        max_chars: Maximum characters (approximate)
        max_tokens: Maximum tokens (1 token ≈ 4 chars)
        
    Returns:
        Truncated text
    """
    if max_tokens:
        max_chars = max_tokens * 4
    
    if max_chars and len(text) > max_chars:
        # Truncate at word boundary if possible
        truncated = text[:max_chars]
        last_space = truncated.rfind(' ')
        if last_space > max_chars * 0.8:  # If we're close to a word boundary
            return truncated[:last_space] + "..."
        return truncated + "..."
    
    return text


def truncate_result(result: Dict, max_text_length: int = 150, include_fields: List[str] = None) -> Dict:
    """
    Truncate a single result item to reduce token usage
    
    Args:
        result: Result dictionary
        max_text_length: Maximum length for text field
        include_fields: Fields to include (None = all)
        
    Returns:
        Truncated result dictionary
    """
    truncated = {}
    
    if include_fields is None:
        include_fields = ["id", "text", "author", "sentiment", "engagement", "created_at"]
    
    for field in include_fields:
        if field not in result:
            continue
        
        value = result[field]
        
        if field == "text":
            truncated[field] = truncate_text(str(value), max_chars=max_text_length)
        elif field == "author" and isinstance(value, dict):
            # Only include essential author info
            truncated[field] = {
                "display_name": value.get("display_name", "")[:50],
                "verified": value.get("verified", False)
            }
        elif field == "engagement" and isinstance(value, dict):
            # Summarize engagement
            total = sum(v for v in value.values() if isinstance(v, (int, float)))
            truncated[field] = {"total": total}
        else:
            truncated[field] = value
    
    return truncated


def truncate_results_for_llm(results: List[Dict], max_items: int = 6, max_text_length: int = 120) -> List[Dict]:
    """
    Truncate a list of results for LLM consumption
    
    Args:
        results: List of result dictionaries
        max_items: Maximum number of items to include
        max_text_length: Maximum text length per item
        
    Returns:
        Truncated list of results
    """
    truncated = []
    for result in results[:max_items]:
        truncated.append(truncate_result(result, max_text_length=max_text_length))
    
    return truncated


def create_concise_data_summary(results: List[Dict], query: str, max_items: int = 6, max_text_length: int = 100) -> str:
    """
    Create a concise summary of results for LLM prompts
    
    Args:
        results: List of result dictionaries
        query: Original query
        max_items: Maximum items to include
        max_text_length: Maximum text length per item
        
    Returns:
        Concise summary string
    """
    if not results:
        return f"Query: {query}\n\nNo results found."
    
    summary = f"Query: {query}\n\n"
    summary += f"Found {len(results)} items. Sample ({min(max_items, len(results))}):\n\n"
    
    truncated_results = truncate_results_for_llm(results, max_items=max_items, max_text_length=max_text_length)
    
    for i, item in enumerate(truncated_results, 1):
        text = item.get('text', '')[:max_text_length]
        author = item.get('author', {}).get('display_name', 'Unknown') if isinstance(item.get('author'), dict) else 'Unknown'
        sentiment = item.get('sentiment', 'unknown')
        engagement = item.get('engagement', {}).get('total', 0) if isinstance(item.get('engagement'), dict) else 0
        
        summary += f"{i}. {text}\n"
        summary += f"   [{author}, {sentiment}, {engagement} eng]\n\n"
    
    if len(results) > max_items:
        summary += f"... and {len(results) - max_items} more items\n"
    
    return summary
