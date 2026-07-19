import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# --- Scoring recipe -------------------------------------------------------
# Genre match:        +2.0 (strongest signal - genres are mostly unique per song)
# Mood match:         +1.0 (secondary signal, more situational than genre)
# Energy similarity:  +0.0 to +1.5, scaled by how close the song's energy is
#                     to the user's target energy
# Acousticness fit:   +0.5 flat bonus when the song's acousticness lines up
#                     with the user's likes_acoustic preference
GENRE_MATCH_POINTS = 2.0
MOOD_MATCH_POINTS = 1.0
ENERGY_MAX_POINTS = 1.5
ACOUSTIC_FIT_POINTS = 0.5
ACOUSTIC_HIGH_THRESHOLD = 0.6
ACOUSTIC_LOW_THRESHOLD = 0.4


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _format_explanation(reasons: List[str]) -> str:
    """Turns the reason phrases from score_song() into one human-readable sentence."""
    if not reasons:
        return "No strong match with your stated preferences."
    text = "; ".join(reasons)
    return text[0].upper() + text[1:] + "."


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def _score_song(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Adapts a UserProfile/Song pair into the dict shape score_song() expects."""
        user_prefs = {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "likes_acoustic": user.likes_acoustic,
        }
        return score_song(user_prefs, asdict(song))

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Scores every song against the user's profile and returns the top k, highest-scoring first."""
        scored = [(self._score_song(user, song)[0], song) for song in self.songs]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [song for _, song in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Returns a human-readable sentence explaining why a song scored the way it did."""
        _, reasons = self._score_song(user, song)
        return _format_explanation(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id": int(row["id"]),
                "title": row["title"],
                "artist": row["artist"],
                "genre": row["genre"],
                "mood": row["mood"],
                "energy": float(row["energy"]),
                "tempo_bpm": float(row["tempo_bpm"]),
                "valence": float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    This is the single source of truth for the scoring recipe; Recommender
    (the OOP/dataclass API) adapts its inputs into dicts and delegates here
    too, so the two APIs can't drift apart.
    """
    genre = song["genre"]
    mood = song["mood"]
    energy = song["energy"]
    acousticness = song["acousticness"]
    favorite_genre = user_prefs.get("genre", "")
    favorite_mood = user_prefs.get("mood", "")
    target_energy = user_prefs.get("energy", 0.5)
    likes_acoustic = user_prefs.get("likes_acoustic", False)

    score = 0.0
    reasons: List[str] = []

    if genre.strip().lower() == favorite_genre.strip().lower():
        score += GENRE_MATCH_POINTS
        reasons.append(f"the genre ({genre}) matches your favorite (+{GENRE_MATCH_POINTS:.2f})")

    if mood.strip().lower() == favorite_mood.strip().lower():
        score += MOOD_MATCH_POINTS
        reasons.append(f"the mood ({mood}) matches your favorite (+{MOOD_MATCH_POINTS:.2f})")

    energy_diff = abs(energy - target_energy)
    energy_points = max(0.0, ENERGY_MAX_POINTS * (1 - energy_diff))
    score += energy_points
    if energy_diff <= 0.15:
        reasons.append(
            f"its energy ({energy:.2f}) closely matches your target ({target_energy:.2f}) (+{energy_points:.2f})"
        )
    elif energy_diff <= 0.35:
        reasons.append(
            f"its energy ({energy:.2f}) is reasonably close to your target ({target_energy:.2f}) (+{energy_points:.2f})"
        )

    if likes_acoustic and acousticness >= ACOUSTIC_HIGH_THRESHOLD:
        score += ACOUSTIC_FIT_POINTS
        reasons.append(
            f"its acoustic sound ({acousticness:.2f}) fits your preference for acoustic tracks (+{ACOUSTIC_FIT_POINTS:.2f})"
        )
    elif not likes_acoustic and acousticness <= ACOUSTIC_LOW_THRESHOLD:
        score += ACOUSTIC_FIT_POINTS
        reasons.append(
            f"its produced/non-acoustic sound ({acousticness:.2f}) fits your preference (+{ACOUSTIC_FIT_POINTS:.2f})"
        )

    return round(score, 2), reasons

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = _format_explanation(reasons)
        scored.append((song, score, explanation))

    scored.sort(key=lambda item: item[1], reverse=True)
    return scored[:k]
