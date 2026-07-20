# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

**VibeFinder 1.0** — a rule-based recommender that scores songs against a listener's stated genre, mood, energy, and acoustic preferences.

---

## 2. Intended Use  

VibeFinder generates a ranked top-5 list of songs pulled from a fixed catalog, along with a plain-English explanation of why each song was picked. A listener fills out a short taste profile — a favorite genre, a favorite mood, an ideal energy level, and whether they lean toward acoustic or produced sound — and the system scores every song in the catalog against that profile. It assumes the listener can name a single favorite genre and mood that will exactly match one of the tags already used in the catalog (it does no fuzzy or "close enough" genre matching), that their taste is internally consistent (it doesn't check for contradictions like "chill" + "metal"), and that one snapshot of preferences is enough — there's no history, feedback, or way for the profile to evolve over time. This is a classroom exploration project meant to make the mechanics and biases of a recommender visible and easy to reason about, not a production system for real listeners — the catalog is tiny (18 songs), hardcoded, and there's no real user data, accounts, or persistence involved.

---

## 3. How the Model Works  

Think of it like a point system. Every song has a genre tag (like "pop" or "folk"), a mood tag (like "happy" or "melancholic"), and a few numbers describing how energetic, fast, upbeat, danceable, and acoustic it sounds. A listener's profile says what genre and mood they're in the mood for, roughly how much energy they want, and whether they prefer acoustic or produced-sounding music. To score a song, the system hands out points one piece at a time: a big chunk of points if the genre matches exactly, a smaller chunk if the mood matches exactly, a sliding amount of points based on how close the song's energy is to what the listener asked for (a perfect match gets the most, and it tapers off the farther apart they are), and a small flat bonus if the song's acoustic-ness lines up with what the listener said they like. All of those points just get added together into one total score, the catalog gets sorted from highest score to lowest, and the top five come back to the listener along with a sentence explaining which pieces earned points and how much. The starter version of this project only had empty stubs for reading the song list and doing the scoring — I filled in all of the actual point-counting and ranking behavior described above, plus the sentence-generation that explains each result. I also gave the system a second, more organized way of representing songs and listener profiles as reusable objects, so the same point rules work no matter which style the rest of the program uses. Finally, I made sure the printed results show the artist's name next to the song title, so the explanations read the way a person would actually describe a song.

---

## 4. Data  

The catalog (`data/songs.csv`) has 18 songs, unmodified from the starter project. It spans 15 different genres (pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, country, classical, metal, reggae, folk, salsa, EDM) and 14 different moods (happy, chill, intense, moody, relaxed, focused, confident, nostalgic, melancholic, angry, playful, sad, romantic, euphoric) — which means most genres and nearly all moods appear on only one or two songs each. That's great for giving every test profile a clean "signature song," but it also means the catalog has almost no genuine overlap to test finer-grained taste — there's no way to compare, say, two different pop songs with different moods, because pop only has two entries and they don't share a mood. Musically, the dataset is missing a lot: no lyrics or language, no sub-genre or fusion tags (a song is just "one" genre), no vocal vs. instrumental distinction, no cultural or regional context, no indication of era/decade, and no listening-history or collaborative signal (who else liked this) — everything the model knows about a song is these nine columns and nothing more.

---

## 5. Strengths  

VibeFinder works best for profiles whose genre is close to unique in the catalog — Melancholic Classical, Sad Acoustic Folk, Nostalgic Country, Playful Reggae, and Romantic Salsa all land a confident, obviously-correct #1 pick (score at or near the 5.00 max) because there's essentially only one "signature song" for that genre, so genre + mood + energy + acoustic-ness all point at the same track. The energy-fit rule behaves exactly the way you'd expect throughout: closer energy always scores higher than farther energy, with no weird reversals, so within any single profile the ordering of "how close is this song's energy to what I wanted" always feels sensible. The acoustic bonus also captures a real, intuitive split in the data — electronic/pop/EDM tracks sit under 0.20 acousticness while folk/classical/ambient tracks sit above 0.85, so "likes acoustic" vs. "likes produced" cleanly separates two real clusters rather than an arbitrary line. Profiles like High Energy Pop and Chill Lofi are the clearest wins: the top pick, the score, and the generated explanation sentence all read as obviously correct to a human, with no need to second-guess the reasoning.

---

## 6. Limitations and Bias 

One clear weakness surfaced in the "Contradictory Chill Rager" test (genre=metal, mood=chill, target_energy=0.95): the model's #1 pick was "Iron Rebellion," an angry metal track, even though its mood is the exact opposite of what the user asked for. This happens because genre match (+2.00) and energy closeness (+1.50) are summed independently of mood, so a song can rack up enough points from just those two features to outrank every song that actually matches the user's stated mood. The scoring has no way to detect internally contradictory preferences or to check whether a song's overall vibe coheres with the user's full profile — it just adds up independent point values. In practice this means the system overfits to whichever single feature carries the most weight (genre, then energy), so users whose taste doesn't line up cleanly across all four dimensions at once get top picks that "technically" match on paper but feel wrong in practice. A fairer design would need to weigh mood mismatches more heavily when genre and energy already dominate, or flag when a song's defining descriptor (like an "angry" mood) directly conflicts with what the user asked for.

---

## 7. Evaluation  

I ran all 13 profiles defined in `src/main.py` against the full catalog: 10 "realistic" taste profiles (High Energy Pop, Deep Intense Rock, Chill Lofi, Romantic Salsa, Melancholic Classical, Angry Metal, Nostalgic Country, Euphoric EDM, Playful Reggae, Sad Acoustic Folk) plus 3 adversarial edge cases designed to break the scoring (Contradictory Chill Rager, Extreme Zero Energy Euphoria, Nonexistent Genre Ghost). For each one I checked two things: did the #1 pick actually match the genre and mood the profile asked for, and did the runner-ups (ranks 2-5) make sense or were they just "loud coincidences" — songs that scored well for reasons that had nothing to do with what the user said they wanted.

What surprised me is how often the runner-up slots are filled by the same handful of high-energy songs (`Gym Hero`, `Storm Runner`, `Iron Rebellion`, `Starlight Surge`) regardless of genre or mood, purely because they all sit in the 0.84-0.95 energy band — the model isn't really recommending five different things, it's recommending one good match plus four "close enough on energy" filler songs. It was also surprising, and a little concerning, that when a genre or mood string doesn't exist in the catalog at all (like `vaporwave` or `ecstatic`), the system doesn't fail or warn — it just silently drops those signals to zero and quietly falls back to sorting by energy alone, with no indication to the user that half their stated taste was ignored.

**Pairwise comparisons:**

- **High Energy Pop vs. Deep Intense Rock** — these ask for similar energy (0.80 vs 0.90) but a different genre and mood, and the #1 picks are correctly different (`Sunrise City`, pop/happy vs `Storm Runner`, rock/intense). But `Gym Hero` (genre pop, mood *intense*, energy 0.93) lands as the #2 pick in **both** lists — for the pop fan it only really matches on genre + energy (its mood is "intense," not "happy"), and for the rock fan it only matches on mood + energy (its genre is "pop," not "rock"). This is exactly the "why does Gym Hero keep showing up for Happy Pop" question: the model doesn't require all three categorical/numeric signals to line up, it just adds partial credit from whichever two happen to agree, so a song that's a clean miss on one whole dimension can still out-rank songs that only nail a single dimension.
- **High Energy Pop vs. Chill Lofi** — opposite ends of the energy dial (0.80 vs 0.35). Here the system behaves exactly as expected: zero overlap between the two top-5 lists, which makes sense — energy is doing real, sensible discriminating work when it isn't competing with a genre/mood mismatch.
- **Melancholic Classical vs. Sad Acoustic Folk** — different genre and mood, but nearly identical energy target (0.30) and both prefer acoustic songs. Three of the five recommended songs are literally the same (`Spacewalk Thoughts`, `Library Rain`, `Coffee Shop Stories`) in both lists. This makes sense once you notice that after the #1 exact-match song is chosen, every remaining song is basically being sorted by "how low-energy and acoustic is it" — genre and mood stop mattering because none of the leftover songs match either profile's genre/mood anyway.
- **Euphoric EDM vs. Angry Metal** — both ask for very high energy (0.90 and 0.95) with completely different genre/mood. Four of the same songs (`Storm Runner`, `Gym Hero`, `Iron Rebellion`, `Midnight Roses`) show up as filler in both lists, in nearly the same order. In plain terms: ask for "loud," in any genre, and you'll get roughly the same stack of loud songs — the model has a much better sense of "high energy" than it does of "this specific vibe."
- **Contradictory Chill Rager vs. Angry Metal** — same genre (metal) and almost the same energy target (0.95), but one profile pairs that with mood "chill" and the other with mood "angry." Angry Metal correctly scores `Iron Rebellion` a perfect 5.00 because all four signals line up. Contradictory Chill Rager *also* puts `Iron Rebellion` in the #1 slot (score 3.50) on genre + energy alone — even though the user explicitly asked for "chill" — while the songs that actually match "chill" (`Midnight Coding`, `Library Rain`, `Spacewalk Thoughts`) get outscored and pushed to ranks 2-4. This is the clearest proof that mood is treated as a bonus on top of the score, not a real constraint the system checks against.
- **Extreme Zero Energy Euphoria vs. Nonexistent Genre Ghost** — both are edge cases, but instructively different: "ambient" is a real genre in the catalog, so `Spacewalk Thoughts` still gets its +2.00 genre bonus and wins #1. "Vaporwave" (and mood "ecstatic") don't exist anywhere in the catalog, so genre and mood contribute nothing for every song, and the entire top 5 collapses into "the five highest-energy songs in the whole catalog," full stop. Comparing the two shows exactly where the fallback behavior kicks in: one unmatched category (genre) still leaves mood or energy to do useful work, but two unmatched categories at once leaves energy as the *only* signal, and the recommender can't tell the difference between "no strong opinion" and "profile made up of nonsense values."

### Terminal Output: Adversarial Edge-Case Profiles

```
=== Contradictory Chill Rager ===

Top recommendations:

Iron Rebellion by Black Forge - Score: 3.50
Reason: The genre (metal) matches your favorite (+2.00); its energy (0.95) closely matches your target (0.95) (+1.50).

Midnight Coding by LoRoom - Score: 2.21
Reason: The mood (chill) matches your favorite (+1.00); its acoustic sound (0.71) fits your preference for acoustic tracks (+0.50).

Library Rain by Paper Lanterns - Score: 2.10
Reason: The mood (chill) matches your favorite (+1.00); its acoustic sound (0.86) fits your preference for acoustic tracks (+0.50).

Spacewalk Thoughts by Orbit Bloom - Score: 2.00
Reason: The mood (chill) matches your favorite (+1.00); its acoustic sound (0.92) fits your preference for acoustic tracks (+0.50).

Starlight Surge by Aurora Pulse - Score: 1.48
Reason: Its energy (0.94) closely matches your target (0.95) (+1.48).
```

```
=== Extreme Zero Energy Euphoria ===

Top recommendations:

Spacewalk Thoughts by Orbit Bloom - Score: 3.08
Reason: The genre (ambient) matches your favorite (+2.00); its energy (0.28) is reasonably close to your target (0.00) (+1.08).

Starlight Surge by Aurora Pulse - Score: 1.59
Reason: The mood (euphoric) matches your favorite (+1.00); its produced/non-acoustic sound (0.04) fits your preference (+0.50).

Clair de Lune by Claude Debussy - Score: 1.05
Reason: Its energy (0.30) is reasonably close to your target (0.00) (+1.05).

Autumn Window by Maple & Hollow - Score: 1.02
Reason: Its energy (0.32) is reasonably close to your target (0.00) (+1.02).

Library Rain by Paper Lanterns - Score: 0.98
Reason: Its energy (0.35) is reasonably close to your target (0.00) (+0.98).
```

```
=== Nonexistent Genre Ghost ===

Top recommendations:

Iron Rebellion by Black Forge - Score: 1.42
Reason: Its energy (0.95) closely matches your target (1.00) (+1.42).

Starlight Surge by Aurora Pulse - Score: 1.41
Reason: Its energy (0.94) closely matches your target (1.00) (+1.41).

Gym Hero by Max Pulse - Score: 1.40
Reason: Its energy (0.93) closely matches your target (1.00) (+1.40).

Storm Runner by Voltline - Score: 1.36
Reason: Its energy (0.91) closely matches your target (1.00) (+1.36).

Midnight Roses by Sol del Barrio - Score: 1.26
Reason: Its energy (0.84) is reasonably close to your target (1.00) (+1.26).
```

---

## 8. Future Work  

The catalog already loads `valence`, `danceability`, and `tempo_bpm` for every song, but none of them currently affect the score — adding those as optional preferences (e.g. "I want something danceable" or "I want a specific tempo range") would use data that's already sitting there unused. I'd also replace exact-string genre matching with some notion of genre adjacency (so "pop" and "indie pop" count as close, not a total miss) and let a user name a secondary/backup genre or mood instead of just one. For explanations, I'd show the *misses* as well as the hits — right now a song's explanation only lists what it earned points for, so a user has no way to see that their mood preference was actually ignored (as in the "Contradictory Chill Rager" case) unless they read the score breakdown carefully. To improve diversity, I'd cap how many songs from the same artist can appear in one top-5 list and consider swapping one "safe" pick for a wildcard/exploration song outside the user's stated genre. Finally, to handle more complex tastes, I'd let users weight the four signals themselves (some people care much more about energy than genre) and add a simple contradiction check that flags profiles like "chill" + "metal" instead of silently scoring them like any other input.

---

## 9. Personal Reflection  

Building this made it obvious that a recommender doesn't need anything fancy to feel personal and "smart" — a handful of additive point rules is enough to produce results that mostly feel right. But it also showed me how easily that simplicity hides real problems: because the scoring just sums independent signals, whichever signal has the biggest number attached to it quietly runs the show, and testing only with "reasonable" profiles never would have surfaced that — it took deliberately adversarial profiles (contradictory prefs, extreme values, made-up genres) to reveal that mood is basically a tie-breaker and that an unrecognized genre silently degrades the whole system to "sort by energy" with no warning. The most unexpected discovery was that the system's bias isn't really about which genres it "likes" — it's structural, baked into the relative point weights, and it would show up no matter which specific genres or moods were in the catalog. That's changed how I think about real recommendation apps: when a playlist or feed feels oddly repetitive or fixated on one thing, it's probably not because the app is malicious or the catalog is bad — it's very possibly because one or two easy-to-measure signals (like recency or engagement) are quietly outweighing everything else in a scoring formula nobody outside the team ever sees.
