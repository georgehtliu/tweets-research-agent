"""
Mock X (Twitter) Data Generator
Creates realistic simulated social media posts for testing the agentic workflow
"""
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path

class MockXDataGenerator:
    """Generate high-quality mock X/Twitter posts"""
    
    # Topics and themes
    TOPICS = [
        "AI", "Machine Learning", "Python", "JavaScript", "Web3", "Blockchain",
        "Climate Tech", "Biotech", "Space Tech", "Quantum Computing", "LLMs",
        "Neural Networks", "Data Science", "Cybersecurity", "Cloud Computing"
    ]
    
    # Sentiment indicators
    POSITIVE_PHRASES = [
        "amazing", "brilliant", "excited", "love this", "game changer",
        "revolutionary", "breakthrough", "incredible", "fantastic", "brilliant"
    ]
    
    NEGATIVE_PHRASES = [
        "concerned", "worried", "skeptical", "not convinced", "overhyped",
        "risky", "problematic", "disappointed", "questionable", "overrated"
    ]
    
    NEUTRAL_PHRASES = [
        "interesting", "worth considering", "food for thought", "curious",
        "not sure", "need to research", "fascinating", "intriguing"
    ]
    
    # Author types
    AUTHOR_TYPES = {
        "researcher": {"verified": True, "followers_range": (1000, 50000)},
        "influencer": {"verified": True, "followers_range": (10000, 1000000)},
        "developer": {"verified": False, "followers_range": (100, 5000)},
        "journalist": {"verified": True, "followers_range": (5000, 200000)},
        "regular_user": {"verified": False, "followers_range": (10, 1000)}
    }
    
    def __init__(self, seed: int = 42):
        """Initialize generator with seed for reproducibility"""
        random.seed(seed)
        self.posts = []
    
    def _generate_post_content(self, topic: str, sentiment: str) -> str:
        """Generate realistic post content"""
        base_templates = [
            f"Just read an {random.choice(self.POSITIVE_PHRASES if sentiment == 'positive' else self.NEGATIVE_PHRASES if sentiment == 'negative' else self.NEUTRAL_PHRASES)} paper on {topic}",
            f"Thoughts on {topic}: {random.choice(self.POSITIVE_PHRASES if sentiment == 'positive' else self.NEGATIVE_PHRASES if sentiment == 'negative' else self.NEUTRAL_PHRASES)}",
            f"{topic} is {random.choice(self.POSITIVE_PHRASES if sentiment == 'positive' else self.NEGATIVE_PHRASES if sentiment == 'negative' else self.NEUTRAL_PHRASES)}",
            f"Hot take: {topic} will {random.choice(['change everything', 'be overhyped', 'need more research'])}",
            f"Anyone else {random.choice(['excited', 'concerned', 'curious'])} about {topic}?",
            f"Deep dive into {topic}: {random.choice(['promising', 'concerning', 'interesting'])} findings",
        ]
        
        content = random.choice(base_templates)
        
        # Add some variation
        if random.random() > 0.7:
            content += f" #Tech #AI #Innovation"
        
        return content
    
    def _generate_author(self) -> Dict:
        """Generate author metadata"""
        author_type = random.choice(list(self.AUTHOR_TYPES.keys()))
        author_config = self.AUTHOR_TYPES[author_type]
        
        return {
            "username": f"{author_type}_{random.randint(1, 1000)}",
            "display_name": f"{author_type.title()} {random.randint(1, 100)}",
            "verified": author_config["verified"],
            "followers": random.randint(*author_config["followers_range"]),
            "author_type": author_type
        }
    
    def _generate_engagement(self, author_type: str) -> Dict:
        """Generate realistic engagement metrics"""
        # Influencers and researchers get more engagement
        base_multiplier = {
            "influencer": 10,
            "researcher": 5,
            "journalist": 3,
            "developer": 2,
            "regular_user": 1
        }.get(author_type, 1)
        
        return {
            "likes": random.randint(0, 10000 * base_multiplier),
            "retweets": random.randint(0, 5000 * base_multiplier),
            "replies": random.randint(0, 500 * base_multiplier),
            "bookmarks": random.randint(0, 200 * base_multiplier)
        }
    
    def generate_post(self, post_id: int) -> Dict:
        """Generate a single mock post"""
        topic = random.choice(self.TOPICS)
        sentiment = random.choice(["positive", "negative", "neutral"])
        author = self._generate_author()
        engagement = self._generate_engagement(author["author_type"])
        
        # Generate timestamp within last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
        
        post = {
            "id": f"post_{post_id}",
            "text": self._generate_post_content(topic, sentiment),
            "author": author,
            "created_at": timestamp.isoformat(),
            "engagement": engagement,
            "sentiment": sentiment,
            "topics": [topic] + random.sample(self.TOPICS, random.randint(0, 2)),
            "language": "en",
            "has_media": random.random() > 0.7,
            "is_reply": False,
            "reply_to": None
        }
        
        return post
    
    def generate_thread(self, thread_id: int, num_posts: int = 3) -> List[Dict]:
        """Generate a threaded conversation"""
        topic = random.choice(self.TOPICS)
        author = self._generate_author()
        posts = []
        
        original_post = self.generate_post(thread_id * 1000)
        original_post["is_reply"] = False
        original_post["topics"] = [topic]
        posts.append(original_post)
        
        for i in range(num_posts - 1):
            reply = self.generate_post(thread_id * 1000 + i + 1)
            reply["is_reply"] = True
            reply["reply_to"] = original_post["id"]
            reply["topics"] = [topic]
            posts.append(reply)
        
        return posts
    
    def generate_dataset(self, num_posts: int = 100, include_threads: bool = True) -> List[Dict]:
        """Generate full dataset"""
        posts = []
        
        # Generate individual posts
        for i in range(num_posts):
            posts.append(self.generate_post(i))
        
        # Add some threaded conversations
        if include_threads:
            num_threads = num_posts // 10
            for thread_id in range(num_threads):
                thread_posts = self.generate_thread(thread_id, random.randint(2, 5))
                posts.extend(thread_posts)
        
        self.posts = posts
        return posts
    
    def save_to_file(self, filepath: str = "data/mock_x_data.json"):
        """Save generated dataset to file"""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.posts, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"✅ Generated {len(self.posts)} posts and saved to {filepath}")
        return filepath

def main():
    """Generate mock dataset"""
    generator = MockXDataGenerator(seed=42)
    posts = generator.generate_dataset(num_posts=100, include_threads=True)
    generator.save_to_file()
    
    # Print statistics
    print(f"\n📊 Dataset Statistics:")
    print(f"Total posts: {len(posts)}")
    print(f"Verified authors: {sum(1 for p in posts if p['author']['verified'])}")
    print(f"Sentiment distribution:")
    sentiments = {}
    for post in posts:
        sentiments[post['sentiment']] = sentiments.get(post['sentiment'], 0) + 1
    for sent, count in sentiments.items():
        print(f"  {sent}: {count}")

if __name__ == "__main__":
    main()
