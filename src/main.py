"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

try:
    from .recommender import load_songs, recommend_songs
except ImportError:
    from recommender import load_songs, recommend_songs

USER_PROFILES = [
    {"name": "High Energy Pop", "prefs": {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": False}},
    {"name": "Deep Intense Rock", "prefs": {"genre": "rock", "mood": "intense", "energy": 0.9, "likes_acoustic": False}},
    {"name": "Chill Lofi", "prefs": {"genre": "lofi", "mood": "chill", "energy": 0.35, "likes_acoustic": True}},
    {"name": "Romantic Salsa", "prefs": {"genre": "salsa", "mood": "romantic", "energy": 0.8, "likes_acoustic": False}},
    {"name": "Melancholic Classical", "prefs": {"genre": "classical", "mood": "melancholic", "energy": 0.3, "likes_acoustic": True}},
    {"name": "Angry Metal", "prefs": {"genre": "metal", "mood": "angry", "energy": 0.95, "likes_acoustic": False}},
    {"name": "Nostalgic Country", "prefs": {"genre": "country", "mood": "nostalgic", "energy": 0.45, "likes_acoustic": True}},
    {"name": "Euphoric EDM", "prefs": {"genre": "EDM", "mood": "euphoric", "energy": 0.9, "likes_acoustic": False}},
    {"name": "Playful Reggae", "prefs": {"genre": "reggae", "mood": "playful", "energy": 0.65, "likes_acoustic": True}},
    {"name": "Sad Acoustic Folk", "prefs": {"genre": "folk", "mood": "sad", "energy": 0.3, "likes_acoustic": True}},
]


def main() -> None:
    songs = load_songs("data/songs.csv")

    for profile in USER_PROFILES:
        print(f"\n=== {profile['name']} ===")
        recommendations = recommend_songs(profile["prefs"], songs, k=5)

        print("\nTop recommendations:\n")
        for rec in recommendations:
            # You decide the structure of each returned item.
            # A common pattern is: (song, score, explanation)
            song, score, explanation = rec
            print(f"{song['title']} by {song['artist']} - Score: {score:.2f}")
            print(f"Reason: {explanation}")
            print()


if __name__ == "__main__":
    main()
