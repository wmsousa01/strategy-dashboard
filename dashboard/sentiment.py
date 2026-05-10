"""
Keyword-based sentiment intensity scorer for 1-star review content.
Calibrated to MONOPOLY GO! review vocabulary (2024-10 to 2025-05).

Score range: 0–100
  0–37  → Mildly Critical     (soft complaints, nostalgic tone)
  38–54 → Moderately Critical (monetization frustration, unfairness)
  55–71 → Strongly Critical   (rigging, bans, scam accusations)
  72–100→ Severely Critical   (fraud allegations, rage, threats)
"""

import pandas as pd

# Weights calibrated against observed keyword frequencies in this dataset.
# Higher weight = stronger signal of severe criticism.
KEYWORDS: dict[str, float] = {
    # Fraud / legal accusations
    "scam":         18, "fraud":        18, "steal":        15,
    "stolen":       15, "theft":        15, "illegal":      15,
    "lawsuit":      15,

    # Rigging / fairness — very prevalent in this dataset
    "rigged":       12, "cheat":        10, "unfair":       10,
    "impossible":    8,

    # Account banning — high-frequency theme
    "banned":       10, " ban ":        10, "ban your":     10,

    # Monetization anger
    "greedy":       10, "greed":        10, "money grab":   12,
    "pay to win":   12, "pay to play":  10, "paywall":      10,
    "pay wall":     10,

    # Strong negative descriptors
    "horrible":      8, "terrible":      8, "garbage":       8,
    "disgusting":    8, "pathetic":      8, "awful":         8,
    "worst":         6,

    # Waste
    "waste":         6, "wasted":        6, "useless":       6,
    "worthless":     6,

    # Technical issues
    "crash":         4, "broken":        5, "glitch":        4,
    "bug":           3, "error":         3, "lag":           3,

    # Monetization pressure (softer)
    "expensive":     4, "overpriced":    5,

    # Mild issues
    "bad":           2, "poor":          2, "slow":          2,
}

# Negative weights (reduce intensity — complaint is softer/nostalgic)
SOFTENERS: dict[str, float] = {
    "used to love":   -12, "loved this":    -10, "used to enjoy": -12,
    "used to be":      -8, "was fun":        -8, "was great":      -8,
    "miss the old":   -10, "before the":     -5, "used to":        -5,
    "love":            -4, "enjoy":          -4, "still fun":      -6,
    "fun":             -3, "great":          -3, "good":           -2,
}


def score_review(text: str) -> float:
    """
    Returns an intensity score 0–100.
    Baseline is 35 (all reviews are already 1-star, so we start above zero).
    """
    if not isinstance(text, str) or not text.strip():
        return 35.0

    tl = text.lower()
    score = 35.0

    for kw, w in KEYWORDS.items():
        if kw in tl:
            score += w

    for kw, w in SOFTENERS.items():
        if kw in tl:
            score += w  # w is already negative

    # Amplifiers: excessive punctuation and all-caps words signal rage
    exclamations = text.count("!")
    if exclamations >= 3:
        score += 8
    elif exclamations >= 2:
        score += 4

    caps_words = sum(1 for word in text.split() if word.isupper() and len(word) > 2)
    if caps_words >= 3:
        score += 10
    elif caps_words >= 2:
        score += 5

    return round(min(100.0, max(0.0, score)), 1)


def sentiment_label(score: float) -> tuple[str, str]:
    """Returns (display_label, hex_color) for a given intensity score."""
    if score < 38:
        return "Mildly Critical", "#22c55e"
    elif score < 55:
        return "Moderately Critical", "#eab308"
    elif score < 72:
        return "Strongly Critical", "#f97316"
    else:
        return "Severely Critical", "#ef4444"


def score_dataframe(reviews_df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of reviews_df with a sentiment_score column added."""
    df = reviews_df.copy()
    df["sentiment_score"] = df["content"].apply(score_review)
    return df


def monthly_summary(scored_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate scored reviews by month.
    Returns a DataFrame with columns:
        year_month, review_count, avg_score, median_score,
        pct_severe, pct_strong, pct_moderate, pct_mild,
        label, color, top_keywords
    """
    rows = []
    for month, grp in scored_df.groupby("year_month"):
        scores = grp["sentiment_score"]
        avg = scores.mean()
        label, color = sentiment_label(avg)

        n = len(grp)
        pct_severe   = (scores >= 72).mean() * 100
        pct_strong   = ((scores >= 55) & (scores < 72)).mean() * 100
        pct_moderate = ((scores >= 38) & (scores < 55)).mean() * 100
        pct_mild     = (scores < 38).mean() * 100

        # Top 3 keywords found in this month's reviews (for tooltip)
        month_text = " ".join(grp["content"].dropna().str.lower().tolist())
        top_kws = sorted(
            [(kw, month_text.count(kw)) for kw in KEYWORDS if month_text.count(kw) > 0],
            key=lambda x: x[1] * KEYWORDS[x[0]],
            reverse=True
        )[:3]
        top_kw_str = ", ".join(k for k, _ in top_kws) if top_kws else "—"

        rows.append({
            "year_month":   str(month),
            "review_count": n,
            "avg_score":    round(avg, 1),
            "median_score": round(scores.median(), 1),
            "pct_severe":   round(pct_severe, 1),
            "pct_strong":   round(pct_strong, 1),
            "pct_moderate": round(pct_moderate, 1),
            "pct_mild":     round(pct_mild, 1),
            "label":        label,
            "color":        color,
            "top_keywords": top_kw_str,
        })

    return pd.DataFrame(rows).sort_values("year_month").reset_index(drop=True)
