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
    """Generate high-quality mock X/Twitter posts across multiple domains"""
    
    # Categories with sub-topics
    TOPICS_BY_CATEGORY = {
        "tech": [
            "AI", "Machine Learning", "Python", "JavaScript", "Web3", "Blockchain",
            "Climate Tech", "Biotech", "Space Tech", "Quantum Computing", "LLMs",
            "Neural Networks", "Data Science", "Cybersecurity", "Cloud Computing"
        ],
        "sports": [
            "NFL", "NBA", "soccer", "Premier League", "tennis", "US Open",
            "Olympics", "F1", "Formula 1", "MMA", "boxing", "March Madness",
            "World Cup", "Champions League", "baseball", "MLB", "golf", "Masters"
        ],
        "politics": [
            "elections", "voting rights", "climate policy", "healthcare reform",
            "immigration", "foreign policy", "Supreme Court", "Congress",
            "local government", "education policy", "tax reform", "infrastructure"
        ],
        "fashion": [
            "streetwear", "haute couture", "sustainable fashion", "runway",
            "designer collabs", "vintage", "trends", "Paris Fashion Week",
            "NYFW", "minimalism", "statement pieces", "slow fashion"
        ],
        "art": [
            "contemporary art", "galleries", "street art", "photography",
            "digital art", "museums", "biennials", "installations",
            "emerging artists", "art market", "public art", "NFT art"
        ],
        "entertainment": [
            "movies", "Oscar season", "streaming", "TV shows", "music",
            "concert tours", "gaming", "K-pop", "podcasts", "celebrity culture"
        ],
    }
    
    # Flattened for backward compat / random pick
    TOPICS = [
        "AI", "Machine Learning", "Python", "Web3", "Blockchain", "LLMs",
        "NFL", "NBA", "soccer", "tennis", "Olympics", "F1", "MMA",
        "elections", "climate policy", "healthcare", "immigration",
        "streetwear", "sustainable fashion", "runway", "Paris Fashion Week",
        "contemporary art", "street art", "photography", "museums",
        "movies", "streaming", "music", "gaming", "K-pop"
    ]
    
    # Sentiment indicators (generic)
    POSITIVE_PHRASES = [
        "amazing", "brilliant", "excited", "love this", "game changer",
        "revolutionary", "breakthrough", "incredible", "fantastic", "fire"
    ]
    NEGATIVE_PHRASES = [
        "concerned", "worried", "skeptical", "not convinced", "overhyped",
        "risky", "problematic", "disappointed", "questionable", "overrated"
    ]
    NEUTRAL_PHRASES = [
        "interesting", "worth considering", "food for thought", "curious",
        "not sure", "need to research", "fascinating", "intriguing"
    ]
    
    # Category-specific phrases
    CATEGORY_PHRASES = {
        "tech": {
            "positive": ["game changer", "breakthrough", "ship it", "build in public", "excited to try"],
            "negative": ["overhyped", "vaporware", "not production-ready", "privacy concerns", "ethical concerns"],
            "neutral": ["interesting approach", "worth watching", "early days", "need to dig in"],
        },
        "sports": {
            "positive": ["GOAT", "clutch", "legacy game", "best in the league", "absolute scenes"],
            "negative": ["choke", "robbed", "rigged", "washed", "overrated"],
            "neutral": ["hot take", "depends on the matchup", "we'll see", "stats don't lie"],
        },
        "politics": {
            "positive": ["historic", "long overdue", "step in the right direction", "accountability"],
            "negative": ["concerning", "backwards", "dangerous precedent", "out of touch", "corrupt"],
            "neutral": ["complicated", "nuance needed", "follow the money", "both sides"],
        },
        "fashion": {
            "positive": ["slay", "never misses", "obsessed", "that fit", "iconic"],
            "negative": ["flop", "overpriced", "basic", "trying too hard", "dated"],
            "neutral": ["interesting choice", "see how it ages", "statement", "divisive"],
        },
        "art": {
            "positive": ["masterpiece", "moving", "powerful", "underrated", "genius"],
            "negative": ["pretentious", "empty", "overpriced", "derivative", "meh"],
            "neutral": ["thought-provoking", "depends on the viewer", "conversation starter", "polarizing"],
        },
        "entertainment": {
            "positive": ["banger", "no skip", "peak cinema", "obsessed", "underrated"],
            "negative": ["mid", "overhyped", "fell off", "cash grab", "cringe"],
            "neutral": ["divisive", "not for everyone", "grew on me", "solid"],
        },
    }
    
    HASHTAGS_BY_CATEGORY = {
        "tech": ["#Tech", "#AI", "#BuildInPublic", "#Innovation"],
        "sports": ["#Sports", "#SZN", "#Ball", "#RespectTheGame"],
        "politics": ["#Politics", "#Civics", "#Democracy", "#Policy"],
        "fashion": ["#Fashion", "#OOTD", "#StreetStyle", "#FashionWeek"],
        "art": ["#Art", "#ContemporaryArt", "#Museums", "#ArtWorld"],
        "entertainment": ["#Movies", "#Music", "#Streaming", "#Culture"],
    }

    # Notable names (subject of tweets) by category
    NOTABLE_NAMES = {
        "tech": ["Elon Musk", "Sam Altman", "Zuckerberg", "Satya Nadella", "Andrej Karpathy"],
        "sports": ["Messi", "Ronaldo", "LeBron", "Curry", "Serena", "Mbappé", "Djokovic", "Mahomes"],
        "politics": ["AOC", "Bernie", "Mitch McConnell", "Pelosi", "Trudeau"],
        "fashion": ["Rihanna", "Virgil Abloh", "Anna Wintour", "Kanye", "Pharrell"],
        "art": ["Banksy", "Jeff Koons", "Damien Hirst", "Yayoi Kusama", "KAWS"],
        "entertainment": ["Taylor Swift", "Beyoncé", "Drake", "BTS", "Tom Cruise", "Scorsese"],
    }

    # Foreign languages: code -> {positive, negative, neutral, templates with {name} {topic}}
    FOREIGN_LANGUAGES = {
        "es": {
            "positive": ["increíble", "genial", "brutal", "ídolo", "legendario", "bestia"],
            "negative": ["decepcionante", "malo", "overrated", "flojo", "regular"],
            "neutral": ["interesante", "a ver", "habrá que ver", "curioso", "ni fu ni fa"],
            "templates": [
                "Increíble lo de {name} hoy. {phrase}",
                "{name} otra vez demostrando por qué es el mejor. {phrase}",
                "Qué opinan de {name} y {topic}? {phrase}",
                "{topic}: {name} siempre {phrase}",
                "No hay nadie como {name}. {phrase}",
                "{name} en {topic} — {phrase}",
            ],
        },
        "fr": {
            "positive": ["incroyable", "énorme", "légendaire", "magique", "maestro"],
            "negative": ["décevant", "nul", "bof", "overrated", "faible"],
            "neutral": ["intéressant", "à voir", "curieux", "correct", "pas mal"],
            "templates": [
                "Incroyable ce que fait {name}. {phrase}",
                "{name} et {topic} — {phrase}",
                "Vous en pensez quoi de {name}? {phrase}",
                "{topic}: {name} encore {phrase}",
                "Personne comme {name}. {phrase}",
            ],
        },
        "pt": {
            "positive": ["incrível", "monstro", "lendário", "genial", "fenômeno"],
            "negative": ["decepcionante", "ruim", "fraco", "overrated", "medíocre"],
            "neutral": ["interessante", "vamos ver", "curioso", "ok", "mais ou menos"],
            "templates": [
                "Incrível o que {name} faz. {phrase}",
                "{name} em {topic} — {phrase}",
                "O que acharam de {name}? {phrase}",
                "{topic} e {name}. {phrase}",
                "Não tem como {name}. {phrase}",
            ],
        },
        "de": {
            "positive": ["unglaublich", "krass", "legende", "stark", "brillant"],
            "negative": ["enttäuschend", "schwach", "overrated", "mäßig", "naja"],
            "neutral": ["interessant", "mal sehen", "kurios", "okay", "geht so"],
            "templates": [
                "Unglaublich, was {name} wieder macht. {phrase}",
                "{name} und {topic} — {phrase}",
                "Was haltet ihr von {name}? {phrase}",
                "{topic}: {name} mal wieder {phrase}",
            ],
        },
        "ja": {
            "positive": ["すごい", "神", "最高", "やばい", "伝説"],
            "negative": ["微妙", "ダメ", "overrated", "残念", "普通"],
            "neutral": ["おもしろい", "どうだろう", "気になる", "まあまあ", "様子見"],
            "templates": [
                "{name}すごすぎる。{phrase}",
                "{topic}の{name} — {phrase}",
                "{name}どう思う？{phrase}",
                "{name}はやっぱり{phrase}",
            ],
        },
    }

    # Author types (celebrity uses notable names as display_name)
    AUTHOR_TYPES = {
        "researcher": {"verified": True, "followers_range": (1000, 50000)},
        "influencer": {"verified": True, "followers_range": (10000, 1000000)},
        "developer": {"verified": False, "followers_range": (100, 5000)},
        "journalist": {"verified": True, "followers_range": (5000, 200000)},
        "regular_user": {"verified": False, "followers_range": (10, 1000)},
        "celebrity": {"verified": True, "followers_range": (500000, 50000000)},
    }
    
    def __init__(self, seed: int = 42):
        """Initialize generator with seed for reproducibility"""
        random.seed(seed)
        self.posts = []
    
    def _templates_for_category(self, category: str, topic: str, sentiment: str, name: str = None) -> list:
        """Category-specific content templates. Optional name for mention-based tweets."""
        pos = self.CATEGORY_PHRASES[category]["positive"]
        neg = self.CATEGORY_PHRASES[category]["negative"]
        neu = self.CATEGORY_PHRASES[category]["neutral"]
        pick = lambda s: random.choice(pos if s == "positive" else neg if s == "negative" else neu)
        generic_pos = self.POSITIVE_PHRASES
        generic_neg = self.NEGATIVE_PHRASES
        generic_neu = self.NEUTRAL_PHRASES
        gpick = lambda s: random.choice(generic_pos if s == "positive" else generic_neg if s == "negative" else generic_neu)

        base = [
            f"Thoughts on {topic}: {pick(sentiment)}",
            f"{topic} is {gpick(sentiment)}",
            f"Anyone else {random.choice(['excited', 'concerned', 'curious'])} about {topic}?",
            f"Hot take: {topic} — {pick(sentiment)}",
        ]
        if name:
            base += [
                f"{name}'s take on {topic} is {pick(sentiment)}",
                f"That {name} moment — {pick(sentiment)}",
                f"Nobody does it like {name}. {pick(sentiment)}",
                f"{name} and {topic}: {pick(sentiment)}",
            ]
        if category == "tech":
            base += [
                f"Just read a {gpick(sentiment)} paper on {topic}",
                f"Deep dive into {topic}: {random.choice(['promising', 'concerning', 'interesting'])} findings",
            ]
            if name:
                base += [f"{name} on {topic}: {pick(sentiment)}"]
        elif category == "sports":
            base += [
                f"That {topic} game was {pick(sentiment)}",
                f"MVP-level {topic} discourse today. {pick(sentiment)}",
                f"Nothing like {topic} season. {pick(sentiment)}",
            ]
            if name:
                base += [
                    f"{name} in that {topic} game was {pick(sentiment)}",
                    f"{name} legacy game. {pick(sentiment)}",
                ]
        elif category == "politics":
            base += [
                f"The {topic} conversation is {random.choice(['heating up', 'missing nuance', 'important'])}. {pick(sentiment)}",
                f"Important thread on {topic}. {pick(sentiment)}",
                f"Everyone talking about {topic} but nobody saying {pick(sentiment)}",
            ]
            if name:
                base += [f"{name} on {topic}: {pick(sentiment)}"]
        elif category == "fashion":
            base += [
                f"This {topic} moment is {pick(sentiment)}",
                f"{topic} never misses. {pick(sentiment)}",
                f"Street style x {topic}: {pick(sentiment)}",
            ]
            if name:
                base += [f"{name} x {topic} — {pick(sentiment)}"]
        elif category == "art":
            base += [
                f"Saw a {topic} show recently. {pick(sentiment)}",
                f"This {topic} piece is {pick(sentiment)}",
                f"{topic} take: {pick(sentiment)}",
            ]
            if name:
                base += [f"{name} and {topic}: {pick(sentiment)}"]
        elif category == "entertainment":
            base += [
                f"That {topic} drop was {pick(sentiment)}",
                f"Nobody's talking about {topic} enough. {pick(sentiment)}",
                f"{topic} — {pick(sentiment)}",
            ]
            if name:
                base += [f"{name} on {topic} — {pick(sentiment)}"]
        return base

    def _generate_foreign_content(self, topic: str, sentiment: str, category: str, name: str, lang: str) -> str:
        """Generate post content in a foreign language. Name required."""
        data = self.FOREIGN_LANGUAGES[lang]
        phrases = data["positive"] if sentiment == "positive" else data["negative"] if sentiment == "negative" else data["neutral"]
        phrase = random.choice(phrases)
        templates = data["templates"]
        t = random.choice(templates)
        content = t.format(name=name, topic=topic, phrase=phrase)
        if random.random() > 0.6:
            tags = self.HASHTAGS_BY_CATEGORY.get(category, self.HASHTAGS_BY_CATEGORY["tech"])
            content += " " + " ".join(random.sample(tags, random.randint(1, 2)))
        return content

    def _generate_post_content(self, topic: str, sentiment: str, category: str, name: str = None, lang: str = "en") -> str:
        """Generate realistic post content. Optional name mention, optional foreign language."""
        if lang != "en":
            use_name = name or random.choice(self.NOTABLE_NAMES.get(category, self.NOTABLE_NAMES["tech"]))
            content = self._generate_foreign_content(topic, sentiment, category, use_name, lang)
        else:
            templates = self._templates_for_category(category, topic, sentiment, name=name)
            content = random.choice(templates)
            if random.random() > 0.65:
                tags = self.HASHTAGS_BY_CATEGORY.get(category, self.HASHTAGS_BY_CATEGORY["tech"])
                content += " " + " ".join(random.sample(tags, random.randint(1, 2)))
        return content
    
    def _generate_author(self, category: str = None, celebrity_name: str = None) -> Dict:
        """Generate author metadata. Optionally use celebrity_name (from NOTABLE_NAMES) as display_name."""
        if celebrity_name:
            author_config = self.AUTHOR_TYPES["celebrity"]
            handle = celebrity_name.lower().replace(" ", "")[:15]
            return {
                "username": f"{handle}_{random.randint(1, 99)}",
                "display_name": celebrity_name,
                "verified": author_config["verified"],
                "followers": random.randint(*author_config["followers_range"]),
                "author_type": "celebrity",
            }
        types = [t for t in self.AUTHOR_TYPES.keys() if t != "celebrity"]
        author_type = random.choice(types)
        author_config = self.AUTHOR_TYPES[author_type]
        return {
            "username": f"{author_type}_{random.randint(1, 1000)}",
            "display_name": f"{author_type.title()} {random.randint(1, 100)}",
            "verified": author_config["verified"],
            "followers": random.randint(*author_config["followers_range"]),
            "author_type": author_type,
        }
    
    def _generate_engagement(self, author_type: str) -> Dict:
        """Generate realistic engagement metrics"""
        base_multiplier = {
            "celebrity": 50,
            "influencer": 10,
            "researcher": 5,
            "journalist": 3,
            "developer": 2,
            "regular_user": 1,
        }.get(author_type, 1)
        
        return {
            "likes": random.randint(0, 10000 * base_multiplier),
            "retweets": random.randint(0, 5000 * base_multiplier),
            "replies": random.randint(0, 500 * base_multiplier),
            "bookmarks": random.randint(0, 200 * base_multiplier)
        }
    
    def _pick_category_and_topic(self) -> tuple:
        """Pick category then topic from that category. Returns (category, topic)."""
        category = random.choice(list(self.TOPICS_BY_CATEGORY.keys()))
        topic = random.choice(self.TOPICS_BY_CATEGORY[category])
        return category, topic

    def generate_post(self, post_id: int, fixed_category: str = None, fixed_topic: str = None) -> Dict:
        """Generate a single mock post. Optional fixed_category/fixed_topic for threads."""
        if fixed_category and fixed_topic:
            category, topic = fixed_category, fixed_topic
            topics_list = [topic]
        else:
            category, topic = self._pick_category_and_topic()
            pool = [t for t in self.TOPICS_BY_CATEGORY[category] if t != topic]
            n_extra = random.randint(0, min(2, len(pool)))
            extra = random.sample(pool, n_extra) if n_extra else []
            topics_list = [topic] + extra

        sentiment = random.choice(["positive", "negative", "neutral"])

        # Language: mostly English, ~18% foreign (es, fr, pt, de, ja)
        lang = "en" if random.random() < 0.82 else random.choice(["es", "fr", "pt", "de", "ja"])
        use_name = (random.random() < 0.35) or (lang != "en")
        name = None
        celebrity_name = None
        if use_name:
            name = random.choice(self.NOTABLE_NAMES.get(category, self.NOTABLE_NAMES["tech"]))
            if random.random() < 0.12:
                celebrity_name = name

        author = self._generate_author(category=None, celebrity_name=celebrity_name)
        engagement = self._generate_engagement(author["author_type"])

        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)

        text = self._generate_post_content(topic, sentiment, category, name=name if use_name else None, lang=lang)

        post = {
            "id": f"post_{post_id}",
            "text": text,
            "author": author,
            "created_at": timestamp.isoformat(),
            "engagement": engagement,
            "sentiment": sentiment,
            "category": category,
            "topics": topics_list,
            "language": lang,
            "has_media": random.random() > 0.7,
            "is_reply": False,
            "reply_to": None
        }

        return post
    
    def generate_thread(self, thread_id: int, num_posts: int = 3) -> List[Dict]:
        """Generate a threaded conversation with consistent category/topic"""
        category, topic = self._pick_category_and_topic()
        posts = []

        original_post = self.generate_post(thread_id * 1000, fixed_category=category, fixed_topic=topic)
        original_post["is_reply"] = False
        posts.append(original_post)

        for i in range(num_posts - 1):
            reply = self.generate_post(thread_id * 1000 + i + 1, fixed_category=category, fixed_topic=topic)
            reply["is_reply"] = True
            reply["reply_to"] = original_post["id"]
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
    for sent, count in sorted(sentiments.items()):
        print(f"  {sent}: {count}")
    print("Category distribution:")
    categories = {}
    for post in posts:
        c = post.get("category", "?")
        categories[c] = categories.get(c, 0) + 1
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    print("Language distribution:")
    langs = {}
    for post in posts:
        L = post.get("language", "en")
        langs[L] = langs.get(L, 0) + 1
    for lang, count in sorted(langs.items()):
        print(f"  {lang}: {count}")

if __name__ == "__main__":
    main()
