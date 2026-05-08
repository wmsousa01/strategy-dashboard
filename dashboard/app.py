import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path


st.set_page_config(
    page_title="Sensor Tower Strategy Dashboard",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent
EXPORTS_DIR = BASE_DIR / "exports"


@st.cache_data
def load_data():
    timeline_path = EXPORTS_DIR / "timeline_clean.csv"
    ratings_path = EXPORTS_DIR / "ratings_clean.csv"
    reviews_path = EXPORTS_DIR / "reviews_clean.csv"
    ranks_path = EXPORTS_DIR / "ranks_clean.csv"

    for path in [timeline_path, ratings_path, reviews_path, ranks_path]:
        if not path.exists():
            raise FileNotFoundError(f"Missing file: {path}")

    timeline_df = pd.read_csv(timeline_path)
    ratings_df = pd.read_csv(ratings_path)
    reviews_df = pd.read_csv(reviews_path)
    ranks_df = pd.read_csv(ranks_path)

    for df in [timeline_df, ratings_df, reviews_df, ranks_df]:
        df["date"] = pd.to_datetime(df["date"])

    return timeline_df, ratings_df, reviews_df, ranks_df


def generate_ai_style_insights(kpis: dict) -> list[str]:
    insights = []

    avg_rank = kpis["avg_rank"]
    best_rank = kpis["best_rank"]
    worst_rank = kpis["worst_rank"]
    avg_rating = kpis["avg_rating"]
    negative_review_pct = kpis["negative_review_pct"]
    top_topic = kpis["top_topic"]
    update_count = kpis["update_count"]

    if avg_rank <= 2:
        insights.append(
            f"MONOPOLY GO! demonstrates elite monetization performance, maintaining an average grossing rank of {avg_rank:.2f} and ranking between #{best_rank:.0f} and #{worst_rank:.0f}."
        )

    if avg_rating >= 4.5:
        insights.append(
            f"The application maintains strong cumulative user satisfaction with an average rating of {avg_rating:.2f}, despite concentrated negative feedback."
        )

    if negative_review_pct >= 80:
        insights.append(
            f"Negative reviews represent {negative_review_pct:.1f}% of the review dataset, suggesting either elevated user friction or a dataset skew toward critical feedback."
        )

    if top_topic:
        insights.append(
            f"The dominant complaint topic is '{top_topic}', indicating a strategic area to monitor after monetization changes and product releases."
        )

    if update_count >= 50:
        insights.append(
            f"The product released {update_count} version updates during the analyzed period, reinforcing evidence of an aggressive live-ops and optimization strategy."
        )

    insights.append(
        "Recommendation: implement automated post-release monitoring for ranking movement, sentiment variation, and monetization-related complaints within 7 days after major releases."
    )

    return insights


st.title("MONOPOLY GO! Strategy Dashboard")

st.markdown(
    "Executive analysis of app store performance, reviews, ratings, and live-ops activity."
)

try:
    timeline_df, ratings_df, reviews_df, ranks_df = load_data()
    st.success("Datasets loaded successfully")

except Exception as e:
    st.error("Error loading datasets")
    st.exception(e)
    st.stop()


with st.expander("Dataset validation"):
    st.write("BASE_DIR:", BASE_DIR)
    st.write("EXPORTS_DIR:", EXPORTS_DIR)
    st.write("Timeline:", timeline_df.shape)
    st.write("Ratings:", ratings_df.shape)
    st.write("Reviews:", reviews_df.shape)
    st.write("Ranks:", ranks_df.shape)


# KPIs
avg_rank = ranks_df["store_product_rank_grossing"].mean()
best_rank = ranks_df["store_product_rank_grossing"].min()
worst_rank = ranks_df["store_product_rank_grossing"].max()

avg_rating = ratings_df["average_star_cumulative"].mean()

review_count = len(reviews_df)

negative_review_pct = (
    reviews_df["review_sentiment"]
    .value_counts(normalize=True)
    .get("negative", 0) * 100
)

update_count = len(
    timeline_df[
        timeline_df["event_type_name"] == "new_version"
    ]
)

top_topic = (
    reviews_df["topics"]
    .value_counts()
    .idxmax()
)

kpis = {
    "avg_rank": avg_rank,
    "best_rank": best_rank,
    "worst_rank": worst_rank,
    "avg_rating": avg_rating,
    "review_count": review_count,
    "negative_review_pct": negative_review_pct,
    "update_count": update_count,
    "top_topic": top_topic,
}


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Average Grossing Rank",
    f"{avg_rank:.2f}"
)

col2.metric(
    "Best / Worst Rank",
    f"#{best_rank:.0f} / #{worst_rank:.0f}"
)

col3.metric(
    "Average Rating",
    f"{avg_rating:.2f}"
)

col4.metric(
    "Total Reviews",
    f"{review_count:,}"
)

col5, col6, col7, col8 = st.columns(4)

col5.metric(
    "Negative Reviews",
    f"{negative_review_pct:.1f}%"
)

col6.metric(
    "App Updates",
    f"{update_count}"
)

col7.metric(
    "Top Complaint Topic",
    top_topic
)

col8.metric(
    "Platforms",
    ranks_df["market_code"].nunique()
)


# Grossing Rank Trend
st.header("Grossing Rank Trend")

rank_trend = (
    ranks_df
    .groupby("date")["store_product_rank_grossing"]
    .mean()
    .reset_index()
)

fig_rank = px.line(
    rank_trend,
    x="date",
    y="store_product_rank_grossing",
    title="Grossing Rank Over Time"
)

fig_rank.update_yaxes(autorange="reversed")

st.plotly_chart(
    fig_rank,
    width="stretch"
)


# Rating Evolution
st.header("Average Rating Evolution")

rating_trend = (
    ratings_df
    .groupby("date")["average_star_cumulative"]
    .mean()
    .reset_index()
)

fig_rating = px.line(
    rating_trend,
    x="date",
    y="average_star_cumulative",
    title="Average Rating Evolution"
)

st.plotly_chart(
    fig_rating,
    width="stretch"
)


# Timeline Events
st.header("Timeline Event Distribution")

event_counts = (
    timeline_df["event_type_name"]
    .value_counts()
    .reset_index()
)

event_counts.columns = ["event_type", "count"]

fig_events = px.bar(
    event_counts,
    x="event_type",
    y="count",
    title="Timeline Event Distribution"
)

st.plotly_chart(
    fig_events,
    width="stretch"
)


# Review Sentiment
st.header("Review Sentiment Distribution")

sentiment_counts = (
    reviews_df["review_sentiment"]
    .value_counts()
    .reset_index()
)

sentiment_counts.columns = ["sentiment", "count"]

fig_sentiment = px.bar(
    sentiment_counts,
    x="sentiment",
    y="count",
    title="Review Sentiment"
)

st.plotly_chart(
    fig_sentiment,
    width="stretch"
)


# Top Review Topics
st.header("Top Review Topics")

topics = (
    reviews_df["topics"]
    .value_counts()
    .head(10)
    .reset_index()
)

topics.columns = ["topic", "count"]

fig_topics = px.bar(
    topics,
    x="count",
    y="topic",
    orientation="h",
    title="Top User Complaint Topics"
)

fig_topics.update_layout(
    yaxis={
        "categoryorder": "total ascending"
    }
)

st.plotly_chart(
    fig_topics,
    width="stretch"
)


# Platform Comparison
st.header("Platform Comparison")

platform_rank = (
    ranks_df
    .groupby("market_code")["store_product_rank_grossing"]
    .mean()
    .reset_index()
)

fig_platform_rank = px.bar(
    platform_rank,
    x="market_code",
    y="store_product_rank_grossing",
    title="Average Grossing Rank by Platform"
)

fig_platform_rank.update_yaxes(autorange="reversed")

st.plotly_chart(
    fig_platform_rank,
    width="stretch"
)


# Events vs Ranking
st.header("Grossing Rank vs Timeline Events")

event_dates = timeline_df[
    ["date", "event_type_name"]
].drop_duplicates()

fig_event_rank = px.line(
    rank_trend,
    x="date",
    y="store_product_rank_grossing",
    title="Grossing Rank with Timeline Event Context"
)

fig_event_rank.update_yaxes(autorange="reversed")

for _, row in event_dates.iterrows():
    fig_event_rank.add_vline(
        x=row["date"],
        line_width=1,
        line_dash="dash",
        opacity=0.25
    )

st.plotly_chart(
    fig_event_rank,
    width="stretch"
)


# AI-Generated Executive Insights
st.header("AI-Generated Executive Insights")

st.caption(
    "Generated from validated KPIs and cleaned datasets using rule-based executive reasoning."
)

ai_insights = generate_ai_style_insights(kpis)

for insight in ai_insights:
    st.markdown(f"- {insight}")


# Executive Insights
st.header("Executive Insights")

st.markdown("""
### Key Findings

- **MONOPOLY GO! maintained elite grossing performance**, with an average grossing rank of approximately **1.46**.
- The app stayed consistently between **#1 and #3** in grossing rank during the analyzed period.
- **Frequent version releases** indicate an aggressive live-ops and product optimization strategy.
- **Ratings remained stable**, averaging around **4.73**, despite concentrated negative review feedback.
- The review dataset appears heavily skewed toward negative feedback, which should be treated as a methodological limitation.
- The most frequent complaint themes are related to **monetization**, **accessibility**, **advertisements**, and **performance/bugs**.

### Strategic Recommendations

1. **Post-release monitoring**
   - Track ranking, sentiment, and topic movement within 7 days after each release.

2. **Monetization friction tracking**
   - Monitor complaint spikes related to monetization and advertisements.

3. **Accessibility review**
   - Investigate recurring accessibility-related feedback.

4. **Automated alerting**
   - Build alerts for spikes in bugs, ads, monetization, and update-related complaints.

5. **Platform-specific monitoring**
   - Continue comparing iOS and Android performance separately to identify platform-specific issues.
""")


with st.expander("Preview Raw Cleaned Data"):
    selected_dataset = st.selectbox(
        "Select dataset",
        [
            "timeline",
            "ratings",
            "reviews",
            "ranks"
        ]
    )

    if selected_dataset == "timeline":
        st.dataframe(timeline_df.head(100))

    elif selected_dataset == "ratings":
        st.dataframe(ratings_df.head(100))

    elif selected_dataset == "reviews":
        st.dataframe(reviews_df.head(100))

    elif selected_dataset == "ranks":
        st.dataframe(ranks_df.head(100))