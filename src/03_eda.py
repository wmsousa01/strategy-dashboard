import time
import matplotlib

matplotlib.use("Agg")

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
EXPORTS_DIR = BASE_DIR / "exports"
CHARTS_DIR = BASE_DIR / "charts"

CHARTS_DIR.mkdir(exist_ok=True)

plt.style.use("ggplot")


def save_chart(filename: str):
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / filename, dpi=120, bbox_inches="tight")
    plt.close()
    print(f"Exported chart: {filename}")


def main():
    start_time = time.time()

    print("Starting EDA pipeline...")
    print("-" * 50)

    print("Loading datasets...")
    timeline_df = pd.read_csv(EXPORTS_DIR / "timeline_clean.csv")
    ratings_df = pd.read_csv(EXPORTS_DIR / "ratings_clean.csv")
    reviews_df = pd.read_csv(EXPORTS_DIR / "reviews_clean.csv")
    ranks_df = pd.read_csv(EXPORTS_DIR / "ranks_clean.csv")
    print("Datasets loaded")

    print("Converting date columns...")
    for df in [timeline_df, ratings_df, reviews_df, ranks_df]:
        df["date"] = pd.to_datetime(df["date"])
    print("Date conversion completed")

    print("\nAnalyzing timeline events...")
    event_counts = timeline_df["event_type_name"].value_counts()
    print(event_counts)

    plt.figure(figsize=(10, 5))
    event_counts.plot(kind="bar")
    plt.title("Timeline Event Distribution")
    plt.xlabel("Event Type")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    save_chart("timeline_event_distribution.png")

    print("\nAnalyzing grossing rank trend...")
    grossing_trend = (
        ranks_df
        .groupby("date")["store_product_rank_grossing"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(14, 6))
    plt.plot(grossing_trend["date"], grossing_trend["store_product_rank_grossing"])
    plt.gca().invert_yaxis()
    plt.title("Grossing Rank Trend Over Time")
    plt.xlabel("Date")
    plt.ylabel("Grossing Rank")
    plt.grid(True)
    save_chart("grossing_rank_trend.png")

    print("\nAnalyzing ratings evolution...")
    rating_trend = (
        ratings_df
        .groupby("date")["average_star_cumulative"]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(14, 6))
    plt.plot(rating_trend["date"], rating_trend["average_star_cumulative"])
    plt.title("Average Rating Evolution")
    plt.xlabel("Date")
    plt.ylabel("Average Rating")
    plt.grid(True)
    save_chart("average_rating_evolution.png")

    print("\nAnalyzing review sentiment...")
    sentiment_counts = reviews_df["review_sentiment"].value_counts()
    print(sentiment_counts)

    plt.figure(figsize=(8, 5))
    sentiment_counts.plot(kind="bar")
    plt.title("Review Sentiment Distribution")
    plt.xlabel("Sentiment")
    plt.ylabel("Count")
    plt.xticks(rotation=0)
    save_chart("review_sentiment_distribution.png")

    print("\nAnalyzing top review topics...")
    top_topics = reviews_df["topics"].value_counts().head(10)
    print(top_topics)

    plt.figure(figsize=(10, 6))
    top_topics.plot(kind="barh")
    plt.title("Top Review Topics")
    plt.xlabel("Count")
    plt.ylabel("Topic")
    plt.gca().invert_yaxis()
    save_chart("top_review_topics.png")

    print("\nAnalyzing grossing rank vs timeline events...")
    event_dates = timeline_df[["date", "event_type_name"]].drop_duplicates()

    plt.figure(figsize=(16, 7))
    plt.plot(
        grossing_trend["date"],
        grossing_trend["store_product_rank_grossing"],
        label="Grossing Rank"
    )

    plt.gca().invert_yaxis()

    for _, row in event_dates.iterrows():
        plt.axvline(row["date"], linestyle="--", alpha=0.3)

    plt.title("Grossing Rank vs Timeline Events")
    plt.xlabel("Date")
    plt.ylabel("Grossing Rank")
    plt.legend()
    plt.grid(True)
    save_chart("grossing_rank_vs_timeline_events.png")

    print("\nExecutive Summary Data")
    print("-" * 50)

    print("\nGrossing Rank Summary:")
    print(ranks_df["store_product_rank_grossing"].describe())

    print("\nAverage Rating Summary:")
    print(ratings_df["average_star_cumulative"].describe())

    print("\nReview Sentiment Distribution (%):")
    print(reviews_df["review_sentiment"].value_counts(normalize=True) * 100)

    print("\nTop Review Topics:")
    print(reviews_df["topics"].value_counts().head(10))

    print("\nEDA pipeline completed successfully")
    print(f"Execution time: {time.time() - start_time:.2f} seconds")


if __name__ == "__main__":
    main()