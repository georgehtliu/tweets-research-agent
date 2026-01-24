"""
Tool Definitions for Agentic Research Agent
Explicit tools that can be called dynamically by the LLM
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from retrieval import HybridRetriever


class ToolRegistry:
    """Registry of available tools for the agent"""
    
    def __init__(self, retriever: HybridRetriever, data: List[Dict]):
        """
        Initialize tool registry
        
        Args:
            retriever: HybridRetriever instance
            data: Full dataset
        """
        self.retriever = retriever
        self.data = data
        self._build_author_index()
        self._build_temporal_index()
    
    def _build_author_index(self):
        """Build index of posts by author"""
        self.author_index = {}
        for post in self.data:
            author_id = post.get("author", {}).get("id", "unknown")
            if author_id not in self.author_index:
                self.author_index[author_id] = []
            self.author_index[author_id].append(post)
    
    def _build_temporal_index(self):
        """Build temporal index for time-based queries"""
        self.temporal_posts = []
        for post in self.data:
            created_at = post.get("created_at")
            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    self.temporal_posts.append((dt, post))
                except:
                    pass
        self.temporal_posts.sort(key=lambda x: x[0])
    
    def get_tool_definitions(self) -> List[Dict]:
        """
        Get tool definitions in OpenAI function-calling format
        
        Returns:
            List of tool definition dictionaries
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": "keyword_search",
                    "description": "Search posts using keyword matching. Good for exact terms, hashtags, or specific phrases.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query with keywords or phrases"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "semantic_search",
                    "description": "Search posts using semantic similarity. Good for finding conceptually related content even without exact keyword matches.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language query describing what to find"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "hybrid_search",
                    "description": "Combine keyword and semantic search for best results. Recommended default search method.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to return (default: 10)",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "user_profile_lookup",
                    "description": "Find all posts by a specific author/user. Useful for analyzing individual perspectives or tracking author activity.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "author_name": {
                                "type": "string",
                                "description": "Display name or username of the author"
                            },
                            "author_id": {
                                "type": "string",
                                "description": "Author ID if known (optional)"
                            },
                            "verified_only": {
                                "type": "boolean",
                                "description": "Only return posts from verified accounts",
                                "default": False
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "temporal_trend_analyzer",
                    "description": "Analyze posts over time periods. Useful for identifying trends, spikes, or temporal patterns.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "days_back": {
                                "type": "integer",
                                "description": "Number of days to look back (default: 7)",
                                "default": 7
                            },
                            "start_date": {
                                "type": "string",
                                "description": "Start date in ISO format (YYYY-MM-DD)"
                            },
                            "end_date": {
                                "type": "string",
                                "description": "End date in ISO format (YYYY-MM-DD)"
                            },
                            "query": {
                                "type": "string",
                                "description": "Optional: filter posts by this query before temporal analysis"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "filter_by_metadata",
                    "description": "Filter posts by metadata criteria (sentiment, engagement, author type, etc.). Use after retrieving initial results.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "posts": {
                                "type": "array",
                                "description": "List of post IDs to filter (from previous search results)"
                            },
                            "sentiment": {
                                "type": "string",
                                "description": "Filter by sentiment: 'positive', 'negative', or 'neutral'",
                                "enum": ["positive", "negative", "neutral"]
                            },
                            "min_engagement": {
                                "type": "integer",
                                "description": "Minimum total engagement (likes + retweets + replies)"
                            },
                            "verified_only": {
                                "type": "boolean",
                                "description": "Only include verified authors",
                                "default": False
                            },
                            "author_type": {
                                "type": "string",
                                "description": "Filter by author type: 'researcher', 'influencer', 'developer', 'journalist', 'regular_user'",
                                "enum": ["researcher", "influencer", "developer", "journalist", "regular_user"]
                            }
                        },
                        "required": []
                    }
                }
            }
        ]
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool call
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Dictionary with 'success', 'results', and 'message'
        """
        try:
            if tool_name == "keyword_search":
                query = arguments.get("query", "")
                top_k = arguments.get("top_k", 10)
                results = self.retriever.keyword_search(query, top_k)
                return {
                    "success": True,
                    "results": [post for post, score in results],
                    "message": f"Found {len(results)} results",
                    "scores": {post["id"]: score for post, score in results}
                }
            
            elif tool_name == "semantic_search":
                query = arguments.get("query", "")
                top_k = arguments.get("top_k", 10)
                results = self.retriever.semantic_search(query, top_k)
                return {
                    "success": True,
                    "results": [post for post, score in results],
                    "message": f"Found {len(results)} results",
                    "scores": {post["id"]: score for post, score in results}
                }
            
            elif tool_name == "hybrid_search":
                query = arguments.get("query", "")
                top_k = arguments.get("top_k", 10)
                results = self.retriever.hybrid_search(query, top_k)
                return {
                    "success": True,
                    "results": results,
                    "message": f"Found {len(results)} results"
                }
            
            elif tool_name == "user_profile_lookup":
                author_name = arguments.get("author_name")
                author_id = arguments.get("author_id")
                verified_only = arguments.get("verified_only", False)
                
                results = []
                for post in self.data:
                    author = post.get("author", {})
                    match = False
                    
                    if author_id and author.get("id") == author_id:
                        match = True
                    elif author_name and author_name.lower() in author.get("display_name", "").lower():
                        match = True
                    
                    if match:
                        if verified_only and not author.get("verified", False):
                            continue
                        results.append(post)
                
                return {
                    "success": True,
                    "results": results,
                    "message": f"Found {len(results)} posts by this author"
                }
            
            elif tool_name == "temporal_trend_analyzer":
                days_back = arguments.get("days_back", 7)
                start_date = arguments.get("start_date")
                end_date = arguments.get("end_date")
                query = arguments.get("query")
                
                # Filter by date range
                now = datetime.now()
                if end_date:
                    try:
                        end_dt = datetime.fromisoformat(end_date)
                    except:
                        end_dt = now
                else:
                    end_dt = now
                
                if start_date:
                    try:
                        start_dt = datetime.fromisoformat(start_date)
                    except:
                        start_dt = end_dt - timedelta(days=days_back)
                else:
                    start_dt = end_dt - timedelta(days=days_back)
                
                # Filter posts by date
                filtered_posts = []
                for dt, post in self.temporal_posts:
                    if start_dt <= dt <= end_dt:
                        filtered_posts.append(post)
                
                # Optionally filter by query
                if query:
                    query_results = self.retriever.hybrid_search(query, top_k=len(filtered_posts))
                    query_ids = {p["id"] for p in query_results}
                    filtered_posts = [p for p in filtered_posts if p["id"] in query_ids]
                
                # Analyze trends
                daily_counts = {}
                sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
                total_engagement = 0
                
                for post in filtered_posts:
                    date_key = post.get("created_at", "")[:10]  # YYYY-MM-DD
                    if date_key:
                        daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
                    
                    sentiment = post.get("sentiment", "neutral")
                    if sentiment in sentiment_counts:
                        sentiment_counts[sentiment] += 1
                    
                    engagement = post.get("engagement", {})
                    if isinstance(engagement, dict):
                        total_engagement += sum(v for v in engagement.values() if isinstance(v, (int, float)))
                
                return {
                    "success": True,
                    "results": filtered_posts,
                    "message": f"Analyzed {len(filtered_posts)} posts from {start_dt.date()} to {end_dt.date()}",
                    "trends": {
                        "daily_counts": daily_counts,
                        "sentiment_distribution": sentiment_counts,
                        "total_engagement": total_engagement,
                        "average_engagement": total_engagement / len(filtered_posts) if filtered_posts else 0
                    }
                }
            
            elif tool_name == "filter_by_metadata":
                post_ids = arguments.get("posts", [])
                sentiment = arguments.get("sentiment")
                min_engagement = arguments.get("min_engagement")
                verified_only = arguments.get("verified_only", False)
                author_type = arguments.get("author_type")
                
                # Get posts by IDs
                post_dict = {p["id"]: p for p in self.data}
                posts = [post_dict[pid] for pid in post_ids if pid in post_dict]
                
                # Apply filters
                filters = {}
                if sentiment:
                    filters["sentiment"] = sentiment
                if min_engagement is not None:
                    filters["min_engagement"] = min_engagement
                if verified_only:
                    filters["verified"] = True
                if author_type:
                    filters["author_type"] = author_type
                
                filtered = self.retriever.filter_by_metadata(posts, filters)
                
                return {
                    "success": True,
                    "results": filtered,
                    "message": f"Filtered to {len(filtered)} posts matching criteria"
                }
            
            else:
                return {
                    "success": False,
                    "results": [],
                    "message": f"Unknown tool: {tool_name}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "results": [],
                "message": f"Error calling {tool_name}: {str(e)}"
            }
