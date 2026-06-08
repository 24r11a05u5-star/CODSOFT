import math
from collections import defaultdict
from typing import List, Dict, Tuple, Set


class ContentAnalyzer:
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        return text.lower().split()
    
    @staticmethod
    def compute_term_frequency(tokens: List[str]) -> Dict[str, float]:
        tf = defaultdict(float)
        total_terms = len(tokens)
        for token in tokens:
            tf[token] += 1
        for token in tf:
            tf[token] /= total_terms
        return dict(tf)
    
    @staticmethod
    def compute_idf(item_tokens_list: List[List[str]]) -> Dict[str, float]:
        idf = defaultdict(float)
        total_items = len(item_tokens_list)
        
        for token_list in item_tokens_list:
            unique_tokens = set(token_list)
            for token in unique_tokens:
                idf[token] += 1
        
        for token in idf:
            idf[token] = math.log(total_items / idf[token]) if idf[token] > 0 else 0
        
        return dict(idf)
    
    @staticmethod
    def cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        dot_product = 0.0
        norm1 = 0.0
        norm2 = 0.0
        
        all_keys = set(vec1.keys()) | set(vec2.keys())
        
        for key in all_keys:
            val1 = vec1.get(key, 0.0)
            val2 = vec2.get(key, 0.0)
            dot_product += val1 * val2
            norm1 += val1 ** 2
            norm2 += val2 ** 2
        
        denominator = math.sqrt(norm1) * math.sqrt(norm2)
        return dot_product / denominator if denominator > 0 else 0.0


class Item:
    
    def __init__(self, item_id: str, title: str, category: str, 
                 description: str, rating: float = 0.0):
        self.item_id = item_id
        self.title = title
        self.category = category
        self.description = description
        self.rating = rating
        self.tokens = ContentAnalyzer.tokenize(f"{title} {category} {description}")
        self.tfidf_vector = {}
    
    def compute_tfidf(self, idf: Dict[str, float]):
        tf = ContentAnalyzer.compute_term_frequency(self.tokens)
        self.tfidf_vector = {}
        for term, tf_val in tf.items():
            self.tfidf_vector[term] = tf_val * idf.get(term, 0.0)
    
    def __repr__(self):
        return f"Item({self.item_id}: {self.title}, {self.category})"


class User:
    
    def __init__(self, user_id: str, name: str):
        self.user_id = user_id
        self.name = name
        self.ratings = {}
        self.preferences = {}
        self.interaction_count = defaultdict(int)
    
    def rate_item(self, item_id: str, rating: float):
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")
        self.ratings[item_id] = rating
    
    def update_preferences(self, item: Item, rating: float):
        if item.category not in self.preferences:
            self.preferences[item.category] = 0.0
        self.preferences[item.category] += (rating - 3) * 0.1
        self.interaction_count[item.category] += 1
    
    def get_preference_vector(self, all_categories: Set[str]) -> Dict[str, float]:
        vector = {}
        for category in all_categories:
            vector[category] = self.preferences.get(category, 0.0)
        return vector


class RecommendationEngine:
    
    def __init__(self):
        self.items = {}
        self.users = {}
        self.idf = {}
        self.all_categories = set()
    
    def add_item(self, item_id: str, title: str, category: str, 
                description: str, rating: float = 0.0):
        item = Item(item_id, title, category, description, rating)
        self.items[item_id] = item
        self.all_categories.add(category)
        self._recompute_tfidf()
    
    def add_user(self, user_id: str, name: str):
        if user_id not in self.users:
            self.users[user_id] = User(user_id, name)
    
    def _recompute_tfidf(self):
        all_tokens = [item.tokens for item in self.items.values()]
        self.idf = ContentAnalyzer.compute_idf(all_tokens)
        for item in self.items.values():
            item.compute_tfidf(self.idf)
    
    def user_rate_item(self, user_id: str, item_id: str, rating: float):
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        if item_id not in self.items:
            raise ValueError(f"Item {item_id} not found")
        
        self.users[user_id].rate_item(item_id, rating)
        self.users[user_id].update_preferences(self.items[item_id], rating)
    
    def content_based_recommendations(self, user_id: str, 
                                     top_n: int = 5) -> List[Tuple[Item, float]]:
        if user_id not in self.users:
            return []
        
        user = self.users[user_id]
        high_rated_items = [item_id for item_id, rating in user.ratings.items() 
                           if rating >= 4]
        
        if not high_rated_items:
            return []
        
        high_rated_vectors = [self.items[iid].tfidf_vector for iid in high_rated_items]
        
        recommendations = {}
        for item_id, item in self.items.items():
            if item_id in user.ratings:
                continue
            
            similarities = [ContentAnalyzer.cosine_similarity(item.tfidf_vector, hrv)
                          for hrv in high_rated_vectors]
            avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
            
            recommendations[item_id] = avg_similarity
        
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [(self.items[iid], score) for iid, score in sorted_recs[:top_n]]
    
    def _euclidean_distance(self, user1: User, user2: User) -> float:
        all_categories = self.all_categories
        vec1 = user1.get_preference_vector(all_categories)
        vec2 = user2.get_preference_vector(all_categories)
        
        sum_squared_diff = 0.0
        for cat in all_categories:
            diff = vec1.get(cat, 0.0) - vec2.get(cat, 0.0)
            sum_squared_diff += diff ** 2
        
        return math.sqrt(sum_squared_diff)
    
    def find_similar_users(self, user_id: str, top_n: int = 5) -> List[Tuple[User, float]]:
        if user_id not in self.users:
            return []
        
        target_user = self.users[user_id]
        distances = {}
        
        for other_user_id, other_user in self.users.items():
            if other_user_id == user_id:
                continue
            distance = self._euclidean_distance(target_user, other_user)
            distances[other_user_id] = distance
        
        sorted_users = sorted(distances.items(), key=lambda x: x[1])
        return [(self.users[uid], dist) for uid, dist in sorted_users[:top_n]]
    
    def collaborative_filtering_recommendations(self, user_id: str, 
                                               top_n: int = 5) -> List[Tuple[Item, float]]:
        if user_id not in self.users:
            return []
        
        user = self.users[user_id]
        similar_users = self.find_similar_users(user_id, top_n=5)
        
        if not similar_users:
            return []
        
        recommendations = defaultdict(float)
        for similar_user, distance in similar_users:
            weight = 1.0 / (1.0 + distance)
            
            for item_id, rating in similar_user.ratings.items():
                if item_id not in user.ratings and rating >= 4:
                    recommendations[item_id] += weight * rating
        
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [(self.items[iid], score) for iid, score in sorted_recs[:top_n]]
    
    def hybrid_recommendations(self, user_id: str, top_n: int = 5,
                              content_weight: float = 0.4,
                              collaborative_weight: float = 0.6) -> List[Tuple[Item, float]]:
        content_recs = self.content_based_recommendations(user_id, top_n * 2)
        collaborative_recs = self.collaborative_filtering_recommendations(user_id, top_n * 2)
        
        combined_scores = {}
        
        for item, score in content_recs:
            combined_scores[item.item_id] = content_weight * score
        
        for item, score in collaborative_recs:
            if item.item_id in combined_scores:
                combined_scores[item.item_id] += collaborative_weight * score
            else:
                combined_scores[item.item_id] = collaborative_weight * score
        
        for item_id, item in self.items.items():
            if item.rating > 0 and item_id in combined_scores:
                combined_scores[item_id] += item.rating * 0.1
        
        sorted_recs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        return [(self.items[iid], score) for iid, score in sorted_recs[:top_n]]
    
    def category_based_recommendations(self, user_id: str, category: str,
                                      top_n: int = 5) -> List[Tuple[Item, float]]:
        if user_id not in self.users:
            return []
        
        user = self.users[user_id]
        category_items = [(iid, item) for iid, item in self.items.items()
                         if item.category == category and iid not in user.ratings]
        
        sorted_items = sorted(category_items, key=lambda x: x[1].rating, reverse=True)
        return [(item, item.rating) for _, item in sorted_items[:top_n]]
    
    def get_statistics(self) -> Dict:
        return {
            'total_users': len(self.users),
            'total_items': len(self.items),
            'total_categories': len(self.all_categories),
            'categories': list(self.all_categories),
            'total_ratings': sum(len(u.ratings) for u in self.users.values())
        }
    
    def get_user_recommendations_summary(self, user_id: str) -> Dict:
        if user_id not in self.users:
            return {'error': 'User not found'}
        
        return {
            'hybrid': self.hybrid_recommendations(user_id, top_n=5),
            'content_based': self.content_based_recommendations(user_id, top_n=5),
            'collaborative': self.collaborative_filtering_recommendations(user_id, top_n=5)
        }



def format_recommendations(recs: List[Tuple[Item, float]], title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    if not recs:
        print("  No recommendations available yet.")
    else:
        for idx, (item, score) in enumerate(recs, 1):
            print(f"  {idx}. {item.title} ({item.category})")
            print(f"     ➜ Score: {score:.3f} | Base Rating: {item.rating:.1f}/5")


def run_demo():
    engine = RecommendationEngine()
    
    movies = [
        ("m1", "Inception", "Sci-Fi", "Mind-bending thriller about dreams within dreams", 4.8),
        ("m2", "The Matrix", "Sci-Fi", "Hacker discovers reality is simulation", 4.7),
        ("m3", "Interstellar", "Sci-Fi", "Space exploration and time relativity", 4.9),
        ("m4", "Shawshank Redemption", "Drama", "Prison escape and friendship story", 4.9),
        ("m5", "The Godfather", "Drama", "Mafia family power and legacy", 4.8),
        ("m6", "Forrest Gump", "Drama", "Life journey through American history", 4.7),
        ("m7", "Pulp Fiction", "Crime", "Non-linear crime stories intertwined", 4.6),
        ("m8", "The Dark Knight", "Action", "Batman battles the Joker", 4.9),
        ("m9", "Mad Max Fury Road", "Action", "Post-apocalyptic car chase thriller", 4.7),
        ("m10", "Avengers Endgame", "Action", "Superheroes save the universe", 4.6),
    ]
    
    books = [
        ("b1", "Dune", "Sci-Fi", "Epic space opera about desert planet politics", 4.5),
        ("b2", "Foundation", "Sci-Fi", "Psychohistory and galactic empire", 4.6),
        ("b3", "1984", "Dystopian", "Totalitarian government surveillance state", 4.4),
        ("b4", "Pride and Prejudice", "Romance", "Social class and love in England", 4.5),
        ("b5", "The Great Gatsby", "Drama", "Jazz age wealth and obsession", 4.4),
    ]
    
    for item_id, title, category, desc, rating in movies + books:
        engine.add_item(item_id, title, category, desc, rating)
    
    users_data = [
        ("u1", "Alice - Sci-Fi Enthusiast"),
        ("u2", "Bob - Drama Lover"),
        ("u3", "Charlie - Action Fan"),
        ("u4", "Diana - Mixed Tastes"),
    ]
    
    for user_id, name in users_data:
        engine.add_user(user_id, name)
    
    ratings_data = [
        ("u1", "m1", 5), ("u1", "m2", 5), ("u1", "m3", 5), ("u1", "b1", 5), ("u1", "b2", 4),
        ("u2", "m4", 5), ("u2", "m5", 5), ("u2", "m6", 4), ("u2", "b4", 5), ("u2", "b5", 4),
        ("u3", "m8", 5), ("u3", "m9", 5), ("u3", "m10", 4), ("u3", "m7", 4), ("u3", "m3", 3),
        ("u4", "m1", 5), ("u4", "m4", 4), ("u4", "m8", 4), ("u4", "b1", 4), ("u4", "b4", 3),
    ]
    
    for user_id, item_id, rating in ratings_data:
        engine.user_rate_item(user_id, item_id, rating)
    
    while True:
        print("\n" + "="*60)
        print("  RECOMMENDATION SYSTEM DEMO")
        print("="*60)
        print("  1. View System Statistics")
        print("  2. Get Recommendations for User")
        print("  3. Rate an Item for User")
        print("  4. View All Items")
        print("  5. Exit")
        print("="*60)
        
        choice = input("\nSelect option (1-5): ").strip()
        
        if choice == "1":
            stats = engine.get_statistics()
            print(f"\n  Total Users: {stats['total_users']}")
            print(f"  Total Items: {stats['total_items']}")
            print(f"  Categories: {', '.join(stats['categories'])}")
            print(f"  Total Ratings: {stats['total_ratings']}")
        
        elif choice == "2":
            user_id = input("  Enter user ID (u1, u2, u3, u4): ").strip()
            if user_id not in engine.users:
                print("  Invalid user ID")
                continue
            
            recs = engine.hybrid_recommendations(user_id, top_n=5)
            user_name = engine.users[user_id].name
            format_recommendations(recs, f"Recommendations for {user_name}")
        
        elif choice == "3":
            user_id = input("  Enter user ID (u1-u4): ").strip()
            if user_id not in engine.users:
                print("  Invalid user ID")
                continue
            
            item_id = input("  Enter item ID (m1-m10, b1-b5): ").strip()
            if item_id not in engine.items:
                print("  Invalid item ID")
                continue
            
            try:
                rating = float(input("  Enter rating (1-5): ").strip())
                engine.user_rate_item(user_id, item_id, rating)
                print(f"  Rating recorded!")
            except ValueError:
                print("  Invalid rating")
        
        elif choice == "4":
            print("\n  MOVIES:")
            for item_id, item in engine.items.items():
                if item.category in ["Sci-Fi", "Drama", "Crime", "Action"]:
                    print(f"    {item_id}: {item.title} ({item.category}) - {item.rating}/5")
            print("\n  BOOKS:")
            for item_id, item in engine.items.items():
                if item.category in ["Sci-Fi", "Dystopian", "Romance", "Drama"]:
                    print(f"    {item_id}: {item.title} ({item.category}) - {item.rating}/5")
        
        elif choice == "5":
            print("  Exiting system. Goodbye!")
            break
        
        else:
            print("  Invalid option. Please try again.")


if __name__ == "__main__":
    run_demo()
