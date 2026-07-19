import pytest

from src.recommender import Song, UserProfile, Recommender

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def make_full_recommender() -> Recommender:
    """Builds a recommender with one distinct song per sample profile's genre/mood pair."""
    songs = [
        Song(id=1, title="Storm Runner", artist="Voltline", genre="rock", mood="intense", energy=0.91, tempo_bpm=152, valence=0.48, danceability=0.66, acousticness=0.10),
        Song(id=2, title="Midnight Coding", artist="LoRoom", genre="lofi", mood="chill", energy=0.42, tempo_bpm=78, valence=0.56, danceability=0.62, acousticness=0.71),
        Song(id=3, title="Sunrise City", artist="Neon Echo", genre="pop", mood="happy", energy=0.82, tempo_bpm=118, valence=0.84, danceability=0.79, acousticness=0.18),
        Song(id=4, title="Midnight Roses", artist="Sol del Barrio", genre="salsa", mood="romantic", energy=0.84, tempo_bpm=176, valence=0.88, danceability=0.93, acousticness=0.32),
        Song(id=5, title="Clair de Lune", artist="Claude Debussy", genre="classical", mood="melancholic", energy=0.30, tempo_bpm=66, valence=0.34, danceability=0.18, acousticness=0.94),
        Song(id=6, title="Iron Rebellion", artist="Black Forge", genre="metal", mood="angry", energy=0.95, tempo_bpm=168, valence=0.18, danceability=0.32, acousticness=0.05),
        Song(id=7, title="Backroad Letters", artist="Willow & Pine", genre="country", mood="nostalgic", energy=0.48, tempo_bpm=84, valence=0.58, danceability=0.52, acousticness=0.88),
        Song(id=8, title="Starlight Surge", artist="Aurora Pulse", genre="EDM", mood="euphoric", energy=0.94, tempo_bpm=132, valence=0.90, danceability=0.82, acousticness=0.04),
        Song(id=9, title="Island Sidewalks", artist="Coral Roots", genre="reggae", mood="playful", energy=0.68, tempo_bpm=88, valence=0.82, danceability=0.84, acousticness=0.55),
        Song(id=10, title="Autumn Window", artist="Maple & Hollow", genre="folk", mood="sad", energy=0.32, tempo_bpm=72, valence=0.28, danceability=0.38, acousticness=0.94),
    ]
    return Recommender(songs)


SAMPLE_USER_PROFILES = [
    pytest.param({"favorite_genre": "rock", "favorite_mood": "intense", "target_energy": 0.9, "likes_acoustic": False}, "rock", "intense", id="intense-rock"),
    pytest.param({"favorite_genre": "lofi", "favorite_mood": "chill", "target_energy": 0.35, "likes_acoustic": True}, "lofi", "chill", id="chill-lofi"),
    pytest.param({"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8, "likes_acoustic": False}, "pop", "happy", id="happy-pop"),
    pytest.param({"favorite_genre": "salsa", "favorite_mood": "romantic", "target_energy": 0.8, "likes_acoustic": False}, "salsa", "romantic", id="romantic-salsa"),
    pytest.param({"favorite_genre": "classical", "favorite_mood": "melancholic", "target_energy": 0.3, "likes_acoustic": True}, "classical", "melancholic", id="melancholic-classical"),
    pytest.param({"favorite_genre": "metal", "favorite_mood": "angry", "target_energy": 0.95, "likes_acoustic": False}, "metal", "angry", id="angry-metal"),
    pytest.param({"favorite_genre": "country", "favorite_mood": "nostalgic", "target_energy": 0.45, "likes_acoustic": True}, "country", "nostalgic", id="nostalgic-country"),
    pytest.param({"favorite_genre": "EDM", "favorite_mood": "euphoric", "target_energy": 0.9, "likes_acoustic": False}, "EDM", "euphoric", id="euphoric-edm"),
    pytest.param({"favorite_genre": "reggae", "favorite_mood": "playful", "target_energy": 0.65, "likes_acoustic": True}, "reggae", "playful", id="playful-reggae"),
    pytest.param({"favorite_genre": "folk", "favorite_mood": "sad", "target_energy": 0.3, "likes_acoustic": True}, "folk", "sad", id="sad-folk"),
]


@pytest.mark.parametrize("profile_kwargs, expected_genre, expected_mood", SAMPLE_USER_PROFILES)
def test_recommend_top_result_matches_profile(profile_kwargs, expected_genre, expected_mood):
    """Checks that the top recommendation's genre and mood match each sample profile's preferences."""
    user = UserProfile(**profile_kwargs)
    rec = make_full_recommender()
    results = rec.recommend(user, k=1)

    assert results[0].genre == expected_genre
    assert results[0].mood == expected_mood


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""
