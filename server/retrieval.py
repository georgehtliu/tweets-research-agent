"""
Hybrid Retrieval System
Combines semantic search (embeddings) and keyword search for robust data retrieval
"""
import json
import re
from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import config

class HybridRetriever:
    """Hybrid retrieval combining semantic and keyword search"""
    
    def __init__(self, data: List[Dict]):
        """
        Initialize retriever with dataset
        
        Args:
            data: List of posts/documents to search
        """
        self.data = data
        self.embeddings = None
        self.embedding_model = None
        
        # Initialize embedding model for semantic search
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            self._build_embeddings()
        except Exception as e:
            print(f"Warning: Could not load embedding model: {e}")
            print("Falling back to keyword-only search")
    
    def _build_embeddings(self):
        """Build embeddings for all documents"""
        if self.embedding_model is None:
            return
        
        texts = [self._extract_text(post) for post in self.data]
        self.embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        print(f"✅ Built embeddings for {len(texts)} documents")
    
    def _extract_text(self, post: Dict) -> str:
        """Extract searchable text from post"""
        text_parts = [post.get("text", "")]
        
        # Add topics
        if "topics" in post:
            text_parts.extend(post["topics"])
        
        # Add author info
        if "author" in post and isinstance(post["author"], dict):
            text_parts.append(post["author"].get("display_name", ""))
        
        return " ".join(text_parts)
    
    def _get_total_engagement(self, post: Dict) -> int:
        """Safely calculate total engagement, handling various data types"""
        engagement = post.get("engagement", {})
        if not isinstance(engagement, dict):
            return 0
        
        total = 0
        for value in engagement.values():
            # Handle both int and string values
            if isinstance(value, (int, float)):
                total += int(value)
            elif isinstance(value, str):
                try:
                    total += int(value)
                except (ValueError, TypeError):
                    pass  # Skip non-numeric strings
        
        return total
    
    def keyword_search(self, query: str, top_k: int = None) -> List[Tuple[Dict, float]]:
        """
        Keyword-based search using TF-IDF-like scoring
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of (post, score) tuples sorted by relevance
        """
        if top_k is None:
            top_k = config.KEYWORD_SEARCH_TOP_K
        
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        
        results = []
        
        for post in self.data:
            text = self._extract_text(post).lower()
            text_words = set(re.findall(r'\b\w+\b', text))
            
            # Calculate simple word overlap score
            if query_words:
                overlap = len(query_words & text_words) / len(query_words)
                
                # Boost score for exact phrase matches
                if query_lower in text:
                    overlap *= 2
                
                # Boost score for verified authors
                if post.get("author", {}).get("verified", False):
                    overlap *= 1.2
                
                # Boost score for high engagement
                engagement = post.get("engagement", {})
                total_engagement = (
                    engagement.get("likes", 0) +
                    engagement.get("retweets", 0) +
                    engagement.get("replies", 0)
                )
                if total_engagement > 100:
                    overlap *= 1.1
                
                results.append((post, overlap))
        
        # Sort by score and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def semantic_search(self, query: str, top_k: int = None) -> List[Tuple[Dict, float]]:
        """
        Semantic search using embeddings
        
        Args:
            query: Search query
            top_k: Number of results to return
            
        Returns:
            List of (post, score) tuples sorted by relevance
        """
        if top_k is None:
            top_k = config.SEMANTIC_SEARCH_TOP_K
        
        if self.embedding_model is None or self.embeddings is None:
            # Fallback to keyword search
            return self.keyword_search(query, top_k)
        
        # Encode query
        query_embedding = self.embedding_model.encode([query], show_progress_bar=False)
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # Get top_k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = [(self.data[i], float(similarities[i])) for i in top_indices]
        return results
    
    def hybrid_search(self, query: str, top_k: int = None, alpha: float = None) -> List[Dict]:
        """
        Hybrid search combining semantic and keyword search
        
        Args:
            query: Search query
            top_k: Number of results to return
            alpha: Weight for semantic vs keyword (0-1, higher = more semantic)
            
        Returns:
            List of posts sorted by combined relevance score
        """
        if top_k is None:
            top_k = config.SEMANTIC_SEARCH_TOP_K
        if alpha is None:
            alpha = config.HYBRID_ALPHA
        
        # Get results from both methods
        semantic_results = self.semantic_search(query, top_k * 2)
        keyword_results = self.keyword_search(query, top_k * 2)
        
        # Create score dictionaries
        semantic_scores = {post["id"]: score for post, score in semantic_results}
        keyword_scores = {post["id"]: score for post, score in keyword_results}
        
        # Normalize scores to 0-1 range (avoid division by zero)
        all_semantic_scores = [s for _, s in semantic_results]
        all_keyword_scores = [s for _, s in keyword_results]
        
        max_semantic = max(all_semantic_scores) if all_semantic_scores else 1
        if max_semantic <= 0:
            max_semantic = 1
        semantic_scores = {k: v / max_semantic for k, v in semantic_scores.items()}
        
        max_keyword = max(all_keyword_scores) if all_keyword_scores else 1
        if max_keyword <= 0:
            max_keyword = 1
        keyword_scores = {k: v / max_keyword for k, v in keyword_scores.items()}
        
        # Combine scores
        combined_scores = {}
        all_post_ids = set(semantic_scores.keys()) | set(keyword_scores.keys())
        
        for post_id in all_post_ids:
            sem_score = semantic_scores.get(post_id, 0)
            key_score = keyword_scores.get(post_id, 0)
            combined_score = alpha * sem_score + (1 - alpha) * key_score
            combined_scores[post_id] = combined_score
        
        # Get posts and sort by combined score
        post_dict = {post["id"]: post for post in self.data}
        results = [
            post_dict[post_id] for post_id in sorted(
                combined_scores.keys(),
                key=lambda x: combined_scores[x],
                reverse=True
            ) if post_id in post_dict
        ]
        
        return results[:top_k]
    
    def filter_by_metadata(self, posts: List[Dict], filters: Dict) -> List[Dict]:
        """
        Filter posts by metadata (author, date, sentiment, etc.)
        
        Args:
            posts: List of posts to filter
            filters: Dictionary of filter criteria
                - verified: bool
                - sentiment: str or list
                - min_engagement: int
                - date_range: tuple of (start_date, end_date)
                - author_type: str or list
                
        Returns:
            Filtered list of posts
        """
        filtered = posts
        
        if "verified" in filters:
            filtered = [p for p in filtered if p.get("author", {}).get("verified") == filters["verified"]]
        
        if "sentiment" in filters:
            sentiment_filter = filters["sentiment"]
            if isinstance(sentiment_filter, str):
                sentiment_filter = [sentiment_filter]
            filtered = [p for p in filtered if p.get("sentiment") in sentiment_filter]
        
        if "min_engagement" in filters:
            min_eng = filters["min_engagement"]
            # Convert to int/float if it's a string
            try:
                min_eng = int(min_eng) if isinstance(min_eng, str) else min_eng
            except (ValueError, TypeError):
                # If conversion fails, skip this filter
                pass
            else:
                filtered = [
                    p for p in filtered
                    if self._get_total_engagement(p) >= min_eng
                ]
        
        if "author_type" in filters:
            author_type_filter = filters["author_type"]
            if isinstance(author_type_filter, str):
                author_type_filter = [author_type_filter]
            filtered = [
                p for p in filtered
                if p.get("author", {}).get("author_type") in author_type_filter
            ]
        
        return filtered
