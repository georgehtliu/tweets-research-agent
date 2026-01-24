"""
Add targeted tweets to improve demo query results
"""
import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from data_generator import MockXDataGenerator

def add_demo_tweets():
    """Add targeted tweets for demo queries"""
    
    # Load existing data
    project_root = Path(__file__).parent.parent
    data_file = project_root / "data" / "mock_x_data.json"
    with open(data_file, 'r', encoding='utf-8') as f:
        existing_posts = json.load(f)
    
    generator = MockXDataGenerator(seed=999)  # Different seed for demo tweets
    new_posts = []
    post_id_start = len(existing_posts)
    
    now = datetime.now()
    
    # 1. Verified accounts talking about JavaScript (recent, for 7-day comparison)
    print("Adding verified JavaScript tweets...")
    for i in range(8):
        days_ago = random.randint(0, 6)  # Within last week
        hours_ago = random.randint(0, 23)
        timestamp = now - timedelta(days=days_ago, hours=hours_ago)
        
        author = generator._generate_author(category="tech", celebrity_name="Sam Altman" if i % 3 == 0 else None)
        author["verified"] = True
        author["author_type"] = "celebrity" if i % 3 == 0 else "influencer"
        
        sentiment = random.choice(["positive", "negative", "neutral"])
        text = generator._generate_post_content("JavaScript", sentiment, "tech", name=None, lang="en")
        
        engagement = generator._generate_engagement(author["author_type"])
        # Boost engagement for verified accounts
        engagement["likes"] = random.randint(5000, 50000)
        engagement["retweets"] = random.randint(1000, 20000)
        
        new_posts.append({
            "id": f"post_{post_id_start + len(new_posts)}",
            "text": text,
            "author": author,
            "created_at": timestamp.isoformat(),
            "engagement": engagement,
            "sentiment": sentiment,
            "category": "tech",
            "topics": ["JavaScript"],
            "language": "en",
            "has_media": random.random() > 0.7,
            "is_reply": False,
            "reply_to": None
        })
    
    # 2. Verified accounts talking about Python (recent, for 7-day comparison)
    print("Adding verified Python tweets...")
    for i in range(8):
        days_ago = random.randint(0, 6)  # Within last week
        hours_ago = random.randint(0, 23)
        timestamp = now - timedelta(days=days_ago, hours=hours_ago)
        
        author = generator._generate_author(category="tech", celebrity_name="Andrej Karpathy" if i % 3 == 0 else None)
        author["verified"] = True
        author["author_type"] = "celebrity" if i % 3 == 0 else "influencer"
        
        sentiment = random.choice(["positive", "negative", "neutral"])
        text = generator._generate_post_content("Python", sentiment, "tech", name=None, lang="en")
        
        engagement = generator._generate_engagement(author["author_type"])
        engagement["likes"] = random.randint(5000, 50000)
        engagement["retweets"] = random.randint(1000, 20000)
        
        new_posts.append({
            "id": f"post_{post_id_start + len(new_posts)}",
            "text": text,
            "author": author,
            "created_at": timestamp.isoformat(),
            "engagement": engagement,
            "sentiment": sentiment,
            "category": "tech",
            "topics": ["Python"],
            "language": "en",
            "has_media": random.random() > 0.7,
            "is_reply": False,
            "reply_to": None
        })
    
    # 3. Verified sports accounts with high engagement
    print("Adding verified sports high engagement tweets...")
    for i in range(10):
        author = generator._generate_author(category="sports", celebrity_name=random.choice(["Messi", "LeBron", "Serena"]))
        author["verified"] = True
        author["author_type"] = "celebrity"
        
        topic = random.choice(["Premier League", "NBA", "tennis", "soccer"])
        sentiment = random.choice(["positive", "negative", "neutral"])
        text = generator._generate_post_content(topic, sentiment, "sports", name=None, lang="en")
        
        # Very high engagement
        engagement = {
            "likes": random.randint(20000, 200000),
            "retweets": random.randint(5000, 50000),
            "replies": random.randint(500, 5000),
            "bookmarks": random.randint(100, 2000)
        }
        
        days_ago = random.randint(0, 14)
        timestamp = now - timedelta(days=days_ago)
        
        new_posts.append({
            "id": f"post_{post_id_start + len(new_posts)}",
            "text": text,
            "author": author,
            "created_at": timestamp.isoformat(),
            "engagement": engagement,
            "sentiment": sentiment,
            "category": "sports",
            "topics": [topic],
            "language": "en",
            "has_media": True,  # Sports posts often have media
            "is_reply": False,
            "reply_to": None
        })
    
    # 4. Recent negative sentiment posts (for "most discussed this week → negative only")
    print("Adding recent negative sentiment tweets...")
    for i in range(15):
        days_ago = random.randint(0, 6)  # Within last week
        hours_ago = random.randint(0, 23)
        timestamp = now - timedelta(days=days_ago, hours=hours_ago)
        
        category, topic = generator._pick_category_and_topic()
        author = generator._generate_author(category=category)
        text = generator._generate_post_content(topic, "negative", category, name=None, lang="en")
        
        engagement = generator._generate_engagement(author["author_type"])
        # Boost engagement for discussion
        engagement["likes"] = random.randint(1000, 15000)
        engagement["retweets"] = random.randint(500, 8000)
        
        new_posts.append({
            "id": f"post_{post_id_start + len(new_posts)}",
            "text": text,
            "author": author,
            "created_at": timestamp.isoformat(),
            "engagement": engagement,
            "sentiment": "negative",
            "category": category,
            "topics": [topic],
            "language": "en",
            "has_media": random.random() > 0.7,
            "is_reply": False,
            "reply_to": None
        })
    
    # 5. Scorsese entertainment posts
    print("Adding Scorsese entertainment tweets...")
    for i in range(8):
        author = generator._generate_author(category="entertainment", celebrity_name="Scorsese")
        author["verified"] = True
        
        topic = random.choice(["Oscar season", "movies", "streaming", "TV shows"])
        sentiment = random.choice(["positive", "negative", "neutral"])
        text = generator._generate_post_content(topic, sentiment, "entertainment", name="Scorsese", lang="en")
        
        engagement = generator._generate_engagement("celebrity")
        engagement["likes"] = random.randint(10000, 100000)
        
        days_ago = random.randint(0, 20)
        timestamp = now - timedelta(days=days_ago)
        
        new_posts.append({
            "id": f"post_{post_id_start + len(new_posts)}",
            "text": text,
            "author": author,
            "created_at": timestamp.isoformat(),
            "engagement": engagement,
            "sentiment": sentiment,
            "category": "entertainment",
            "topics": [topic],
            "language": "en",
            "has_media": random.random() > 0.6,
            "is_reply": False,
            "reply_to": None
        })
    
    # 6. More fashion sustainable/runway posts
    print("Adding fashion sustainable/runway tweets...")
    for i in range(12):
        topic = random.choice(["sustainable fashion", "runway"])
        author = generator._generate_author(category="fashion")
        sentiment = random.choice(["positive", "negative", "neutral"])
        text = generator._generate_post_content(topic, sentiment, "fashion", name=None, lang="en")
        
        engagement = generator._generate_engagement(author["author_type"])
        days_ago = random.randint(0, 25)
        timestamp = now - timedelta(days=days_ago)
        
        new_posts.append({
            "id": f"post_{post_id_start + len(new_posts)}",
            "text": text,
            "author": author,
            "created_at": timestamp.isoformat(),
            "engagement": engagement,
            "sentiment": sentiment,
            "category": "fashion",
            "topics": [topic],
            "language": "en",
            "has_media": True,  # Fashion posts often have media
            "is_reply": False,
            "reply_to": None
        })
    
    # 7. Spanish fashion posts
    print("Adding Spanish fashion tweets...")
    for i in range(10):
        topic = random.choice(["sustainable fashion", "runway", "streetwear", "haute couture"])
        author = generator._generate_author(category="fashion", celebrity_name=random.choice(["Rihanna", "Pharrell"]) if i % 3 == 0 else None)
        if i % 3 == 0:
            author["verified"] = True
        
        sentiment = random.choice(["positive", "negative", "neutral"])
        name = random.choice(["Rihanna", "Pharrell", "Anna Wintour"]) if random.random() < 0.5 else None
        text = generator._generate_foreign_content(topic, sentiment, "fashion", name or "Rihanna", "es")
        
        engagement = generator._generate_engagement(author["author_type"])
        days_ago = random.randint(0, 20)
        timestamp = now - timedelta(days=days_ago)
        
        new_posts.append({
            "id": f"post_{post_id_start + len(new_posts)}",
            "text": text,
            "author": author,
            "created_at": timestamp.isoformat(),
            "engagement": engagement,
            "sentiment": sentiment,
            "category": "fashion",
            "topics": [topic],
            "language": "es",
            "has_media": random.random() > 0.6,
            "is_reply": False,
            "reply_to": None
        })
    
    # 8. French art/museums posts
    print("Adding French art/museums tweets...")
    for i in range(10):
        topic = random.choice(["museums", "contemporary art", "galleries", "art market"])
        author = generator._generate_author(category="art", celebrity_name=random.choice(["Banksy", "Damien Hirst"]) if i % 3 == 0 else None)
        if i % 3 == 0:
            author["verified"] = True
        
        sentiment = random.choice(["positive", "negative", "neutral"])
        name = random.choice(["Banksy", "Damien Hirst", "Jeff Koons"]) if random.random() < 0.5 else None
        text = generator._generate_foreign_content(topic, sentiment, "art", name or "Banksy", "fr")
        
        engagement = generator._generate_engagement(author["author_type"])
        days_ago = random.randint(0, 20)
        timestamp = now - timedelta(days=days_ago)
        
        new_posts.append({
            "id": f"post_{post_id_start + len(new_posts)}",
            "text": text,
            "author": author,
            "created_at": timestamp.isoformat(),
            "engagement": engagement,
            "sentiment": sentiment,
            "category": "art",
            "topics": [topic],
            "language": "fr",
            "has_media": random.random() > 0.6,
            "is_reply": False,
            "reply_to": None
        })
    
    # 9. Portuguese sports posts
    print("Adding Portuguese sports tweets...")
    for i in range(10):
        topic = random.choice(["soccer", "Premier League", "World Cup", "tennis", "F1"])
        author = generator._generate_author(category="sports", celebrity_name=random.choice(["Messi", "Ronaldo"]) if i % 3 == 0 else None)
        if i % 3 == 0:
            author["verified"] = True
        
        sentiment = random.choice(["positive", "negative", "neutral"])
        name = random.choice(["Messi", "Ronaldo", "Mbappé"]) if random.random() < 0.5 else None
        text = generator._generate_foreign_content(topic, sentiment, "sports", name or "Messi", "pt")
        
        engagement = generator._generate_engagement(author["author_type"])
        days_ago = random.randint(0, 20)
        timestamp = now - timedelta(days=days_ago)
        
        new_posts.append({
            "id": f"post_{post_id_start + len(new_posts)}",
            "text": text,
            "author": author,
            "created_at": timestamp.isoformat(),
            "engagement": engagement,
            "sentiment": sentiment,
            "category": "sports",
            "topics": [topic],
            "language": "pt",
            "has_media": True,  # Sports posts often have media
            "is_reply": False,
            "reply_to": None
        })
    
    # 10. More AI posts (for simple query)
    print("Adding more AI tweets...")
    for i in range(10):
        author = generator._generate_author(category="tech")
        sentiment = random.choice(["positive", "negative", "neutral"])
        text = generator._generate_post_content("AI", sentiment, "tech", name=None, lang="en")
        
        engagement = generator._generate_engagement(author["author_type"])
        days_ago = random.randint(0, 15)
        timestamp = now - timedelta(days=days_ago)
        
        new_posts.append({
            "id": f"post_{post_id_start + len(new_posts)}",
            "text": text,
            "author": author,
            "created_at": timestamp.isoformat(),
            "engagement": engagement,
            "sentiment": sentiment,
            "category": "tech",
            "topics": ["AI"],
            "language": "en",
            "has_media": random.random() > 0.7,
            "is_reply": False,
            "reply_to": None
        })
    
    # Combine and save
    all_posts = existing_posts + new_posts
    
    # Save updated data
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(all_posts, f, indent=2, ensure_ascii=False, default=str)
    
    print(f"\n✅ Added {len(new_posts)} demo tweets")
    print(f"Total posts: {len(all_posts)}")
    
    # Verify coverage
    print("\n📊 Updated Coverage:")
    verified_js = sum(1 for p in all_posts if p.get('author', {}).get('verified') and ('javascript' in p.get('text', '').lower() or 'javascript' in [t.lower() for t in p.get('topics', [])]))
    verified_python = sum(1 for p in all_posts if p.get('author', {}).get('verified') and ('python' in p.get('text', '').lower() or 'python' in [t.lower() for t in p.get('topics', [])]))
    print(f"  Verified JS: {verified_js}, Verified Python: {verified_python}")
    
    verified_sports_high = sum(1 for p in all_posts if p.get('author', {}).get('verified') and p.get('category') == 'sports' and sum(p.get('engagement', {}).values()) > 10000)
    print(f"  Verified sports high engagement: {verified_sports_high}")
    
    week_ago = now - timedelta(days=7)
    recent_negative = sum(1 for p in all_posts if datetime.fromisoformat(p.get('created_at', '').replace('Z', '+00:00').replace('+00:00', '')) >= week_ago and p.get('sentiment') == 'negative')
    print(f"  Recent negative: {recent_negative}")
    
    scorsese_ent = sum(1 for p in all_posts if 'scorsese' in p.get('author', {}).get('display_name', '').lower() and p.get('category') == 'entertainment')
    print(f"  Scorsese entertainment: {scorsese_ent}")
    
    fashion_sustainable = sum(1 for p in all_posts if p.get('category') == 'fashion' and ('sustainable fashion' in p.get('text', '').lower() or 'sustainable fashion' in [t.lower() for t in p.get('topics', [])]))
    fashion_runway = sum(1 for p in all_posts if p.get('category') == 'fashion' and ('runway' in p.get('text', '').lower() or 'runway' in [t.lower() for t in p.get('topics', [])]))
    print(f"  Fashion sustainable: {fashion_sustainable}, runway: {fashion_runway}")
    
    spanish_fashion = sum(1 for p in all_posts if p.get('language') == 'es' and p.get('category') == 'fashion')
    print(f"  Spanish fashion: {spanish_fashion}")
    
    french_art_museums = sum(1 for p in all_posts if p.get('language') == 'fr' and p.get('category') == 'art' and ('museum' in p.get('text', '').lower() or 'museums' in [t.lower() for t in p.get('topics', [])]))
    print(f"  French art/museums: {french_art_museums}")
    
    portuguese_sports = sum(1 for p in all_posts if p.get('language') == 'pt' and p.get('category') == 'sports')
    print(f"  Portuguese sports: {portuguese_sports}")

if __name__ == "__main__":
    add_demo_tweets()
