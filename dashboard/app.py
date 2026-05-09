import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path


st.set_page_config(
    page_title="MONOPOLY GO! — Sensor Tower Intelligence",
    layout="wide",
    page_icon="🎲"
)

st.markdown("""
<style>
.main .block-container { padding-top: 1rem; }

.kpi-card {
    background: #ffffff;
    border: 1px solid #e4e4e7;
    border-radius: 8px;
    padding: 16px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    min-height: 90px;
}
.kpi-label {
    font-size: 11px;
    color: #6b7280;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 6px;
}
.kpi-value {
    font-size: 26px;
    font-weight: 700;
    color: #00897B;
    line-height: 1.1;
}
.kpi-context {
    font-size: 11px;
    color: #9ca3af;
    margin-top: 4px;
}
.app-header {
    background: #ffffff;
    border: 1px solid #e4e4e7;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.app-name { font-size: 22px; font-weight: 700; color: #111827; }
.app-meta { font-size: 13px; color: #6b7280; margin-top: 4px; }
.badge {
    display: inline-block;
    background: #f3f4f6;
    color: #374151;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    border-radius: 4px;
    margin-right: 6px;
}
.badge-teal { background: #e0f2f1; color: #00695C; }
</style>
""", unsafe_allow_html=True)


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

    reviews_df["year_month"] = reviews_df["date"].dt.to_period("M").dt.to_timestamp()

    return timeline_df, ratings_df, reviews_df, ranks_df


def kpi_card(label: str, value: str, context: str = "") -> str:
    return f"""
    <div class="kpi-card">
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-context">{context}</div>
    </div>
    """


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
            f"MONOPOLY GO! ranked **#1 in the Google Play Games category every single day** across the entire analysis period — "
            f"and held the **#{best_rank:.0f}–#{worst_rank:.0f} position in the overall store** grossing chart."
        )
    if avg_rating >= 4.5:
        insights.append(
            f"The application maintains strong cumulative user satisfaction with an average rating of {avg_rating:.2f} "
            "across platforms, despite concentrated negative feedback."
        )
    if negative_review_pct >= 80:
        insights.append(
            f"Negative reviews represent {negative_review_pct:.1f}% of the review dataset, suggesting either elevated "
            "user friction or a dataset skew toward critical feedback."
        )
    if top_topic:
        insights.append(
            f"The dominant complaint topic is '{top_topic}', indicating a strategic area to monitor "
            "after monetization changes and product releases."
        )
    if update_count >= 40:
        insights.append(
            f"The product released {update_count} distinct version updates during the analyzed period, "
            "reinforcing evidence of an aggressive live-ops and optimization strategy."
        )
    insights.append(
        "Recommendation: implement automated post-release monitoring for ranking movement, sentiment variation, "
        "and monetization-related complaints within 7 days after major releases."
    )
    return insights


# --- Load data ---
try:
    timeline_df, ratings_df, reviews_df, ranks_df = load_data()
except Exception as e:
    st.error("Error loading datasets")
    st.exception(e)
    st.stop()


# --- KPI calculations ---
ranks_games   = ranks_df[ranks_df["category_id"] == "game"]
ranks_overall = ranks_df[ranks_df["category_id"] == "all"]

# Games category: #1 every day — express as % of days at #1
games_days_at_1 = (ranks_games["store_product_rank_grossing"] == 1).mean() * 100

# Overall store: varies between #2 and #3
avg_rank_overall  = ranks_overall["store_product_rank_grossing"].mean()
best_rank_overall = ranks_overall["store_product_rank_grossing"].min()
worst_rank_overall = ranks_overall["store_product_rank_grossing"].max()

# Used by AI insights (overall store avg is the meaningful moving number)
avg_rank  = avg_rank_overall
best_rank = best_rank_overall
worst_rank = worst_rank_overall

avg_rating = ratings_df["average_star_cumulative"].mean()
review_count = len(reviews_df)
negative_review_pct = (
    reviews_df["review_sentiment"]
    .value_counts(normalize=True)
    .get("negative", 0) * 100
)
update_count = (
    timeline_df[timeline_df["event_type_name"] == "new_version"]["new_value"].nunique()
)
top_topic = reviews_df["topics"].value_counts().idxmax()
platform_count = ratings_df["market_code"].nunique()

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

date_min = ratings_df["date"].min().strftime("%b %d, %Y")
date_max = ratings_df["date"].max().strftime("%b %d, %Y")


# --- App identity header ---
st.markdown(f"""
<div class="app-header">
    <div style="display:flex; align-items:flex-start; gap:16px;">
        <div style="font-size:48px; line-height:1;">🎲</div>
        <div>
            <div class="app-name">MONOPOLY GO!</div>
            <div class="app-meta">Scopely, Inc. &nbsp;·&nbsp; Games &nbsp;·&nbsp; US Market</div>
            <div style="margin-top:8px;">
                <span class="badge badge-teal">iOS</span>
                <span class="badge badge-teal">Android</span>
                <span class="badge">Rankings: Google Play only</span>
                <span class="badge">{date_min} — {date_max}</span>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# --- Tab navigation ---
tab_overview, tab_rankings, tab_reviews, tab_timeline = st.tabs([
    "Overview",
    "Rankings",
    "Ratings & Reviews",
    "Timeline",
])


# ============================================================
# TAB 1 — OVERVIEW
# ============================================================
with tab_overview:

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi_card("Games Category Rank", "#1", f"{games_days_at_1:.0f}% of days · Google Play"), unsafe_allow_html=True)
    c2.markdown(kpi_card("Overall Store Rank", f"#{best_rank_overall:.0f} – #{worst_rank_overall:.0f}", f"Avg {avg_rank_overall:.2f} · Google Play grossing"), unsafe_allow_html=True)
    c3.markdown(kpi_card("Avg Rating", f"{avg_rating:.2f} ★", "iOS + Android cumulative"), unsafe_allow_html=True)
    c4.markdown(kpi_card("Total Reviews", f"{review_count:,}", "1-star only (API filter)"), unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    c5.markdown(kpi_card("Negative Reviews", f"{negative_review_pct:.0f}%", "Dataset skewed to critical feedback"), unsafe_allow_html=True)
    c6.markdown(kpi_card("App Releases", str(update_count), "Distinct version updates"), unsafe_allow_html=True)
    c7.markdown(kpi_card("Top Complaint Topic", top_topic.replace("_", " ").title(), "By review count"), unsafe_allow_html=True)
    c8.markdown(kpi_card("Platforms", str(platform_count), "iOS & Android"), unsafe_allow_html=True)

    st.markdown("---")

    st.subheader("AI-Generated Executive Insights")
    st.caption("Generated from validated KPIs and cleaned datasets using rule-based executive reasoning.")
    for insight in generate_ai_style_insights(kpis):
        st.markdown(f"- {insight}")

    st.markdown("---")

    st.subheader("Key Findings & Strategic Recommendations")
    st.markdown("""
**Key Findings**

- **MONOPOLY GO! ranked #1 in the Google Play Games category every single day** of the analysis period (366/366 days). In the overall store grossing chart it held **#2–#3**, averaging **2.39**. Apple Store rank data was not available in this export.
- **43 distinct version releases** across the analysis period reflect an aggressive live-ops and optimization strategy.
- **Ratings remained stable** — iOS averaged **4.80 ★** and Android **4.66 ★** — despite concentrated critical review volume.
- **November 2024 saw a review spike of 922 complaints** (vs. ~100–180/month baseline), coinciding with multiple version releases and likely monetization changes.
- Top complaint themes: **monetization**, **accessibility**, **advertisements**, **performance/bugs**.
- The review dataset is filtered to 1-star reviews only — treat as a critical-feedback signal, not a representative sample.

**Strategic Recommendations**

1. **Post-release monitoring** — track ranking, sentiment, and topic movement within 7 days after each release.
2. **Investigate the Nov 2024 spike** — identify which version or event drove the 9× review volume surge.
3. **Monetization friction** — monitor complaint spikes related to monetization and advertisements.
4. **Accessibility review** — investigate recurring accessibility-related feedback.
5. **Platform-specific monitoring** — iOS rates ~0.14 ★ higher than Android; investigate Android-specific friction points.
""")

    with st.expander("API Response Structure — what this data provides"):
        st.markdown(
            f"**4 Sensor Tower API bundles** queried for MONOPOLY GO! from **{date_min}** to **{date_max}**, US market, iOS + Android."
        )
        ca, cb = st.columns(2)
        with ca:
            st.markdown("**Ranks** — Daily grossing & free chart positions")
            st.markdown(
                f"- {len(ranks_df):,} daily observations · Google Play only\n"
                "- Key fields: `store_product_rank_grossing`, `store_product_rank_free`, `market_code`, `date`\n"
                "- Use case: track competitive position, measure impact of releases on monetization rank"
            )
            st.markdown("---")
            st.markdown("**Ratings** — Cumulative star ratings over time")
            st.markdown(
                f"- {len(ratings_df):,} daily observations · iOS & Android\n"
                "- Key fields: `average_star_cumulative`, star-level breakdowns (1–5), `market_code`, `date`\n"
                "- Use case: monitor rating health, detect post-release sentiment shifts by platform"
            )
        with cb:
            st.markdown("**Reviews** — Individual user review texts")
            st.markdown(
                f"- {len(reviews_df):,} reviews · iOS & Android\n"
                "- Key fields: `rating_value`, `content`, `topics`, `review_sentiment`, `product_version`\n"
                "- ⚠️ **1-star reviews only** — API filter applied at query time\n"
                "- Use case: surface complaint themes, tie user friction to specific releases"
            )
            st.markdown("---")
            st.markdown("**Timeline** — App store events")
            st.markdown(
                f"- {len(timeline_df):,} events · iOS & Android\n"
                "- Key fields: `event_type_name`, `old_value`, `new_value`, `release_notes`, `date`\n"
                "- Event types: `new_version`, `size_change`, `screenshot_change`, `app_description`\n"
                "- Use case: correlate product changes with rank movement and review spikes"
            )

    with st.expander("Dataset validation"):
        st.write("Timeline:", timeline_df.shape)
        st.write("Ratings:", ratings_df.shape)
        st.write("Reviews:", reviews_df.shape)
        st.write("Ranks:", ranks_df.shape)


# ============================================================
# TAB 2 — RANKINGS
# ============================================================
with tab_rankings:

    # Build per-category rank series (one row per date per category — no averaging)
    cat_labels = {
        "game":       "Games Category",
        "game_board": "Board Games Sub-category",
        "all":        "Overall Store",
    }
    rank_by_cat = ranks_df.copy()
    rank_by_cat["chart"] = rank_by_cat["category_id"].map(cat_labels)

    # Shared y-axis config: integer ticks, inverted (#1 at top)
    yaxis_rank = dict(
        autorange="reversed",
        tickmode="array",
        tickvals=[1, 2, 3],
        ticktext=["#1", "#2", "#3"],
        title="Grossing Rank",
    )

    # --- Chart 1: all categories side by side ---
    st.subheader("Daily Grossing Rank by Category — Google Play")
    st.caption(
        "Three chart types tracked simultaneously: Games Category, Board Games sub-category, "
        "and Overall Store. MONOPOLY GO! held **#1 in both Games charts every day**; "
        "Overall Store rank varied between **#2 and #3**."
    )

    fig_rank_cat = px.line(
        rank_by_cat.sort_values("date"),
        x="date",
        y="store_product_rank_grossing",
        color="chart",
        line_shape="hv",
        color_discrete_map={
            "Games Category":            "#00897B",
            "Board Games Sub-category":  "#26A69A",
            "Overall Store":             "#FF7043",
        },
        title="Grossing Rank by Category — Google Play",
        labels={"store_product_rank_grossing": "Rank", "date": "Date", "chart": "Category"}
    )
    fig_rank_cat.update_yaxes(**yaxis_rank)
    fig_rank_cat.update_layout(legend=dict(orientation="h", y=-0.15))
    st.plotly_chart(fig_rank_cat, width="stretch")

    # --- Chart 2: Overall store rank vs timeline events ---
    st.subheader("Overall Store Rank vs Timeline Events")
    st.caption(
        "Overall Google Play grossing rank (across all apps). "
        "Dashed lines mark version releases — use this to spot rank movement after updates."
    )

    overall_trend = (
        ranks_overall
        .sort_values("date")[["date", "store_product_rank_grossing"]]
        .reset_index(drop=True)
    )

    fig_event_rank = px.line(
        overall_trend,
        x="date",
        y="store_product_rank_grossing",
        line_shape="hv",
        title="Overall Store Grossing Rank with Version Release Context",
        labels={"store_product_rank_grossing": "Rank", "date": "Date"}
    )
    fig_event_rank.update_traces(line_color="#FF7043")
    fig_event_rank.update_yaxes(**yaxis_rank)

    version_dates = (
        timeline_df[timeline_df["event_type_name"] == "new_version"]["date"]
        .drop_duplicates()
    )
    for d in version_dates:
        fig_event_rank.add_vline(x=d, line_width=1, line_dash="dash", line_color="#00897B", opacity=0.35)

    st.plotly_chart(fig_event_rank, width="stretch")

    with st.expander("Preview raw ranks data"):
        st.dataframe(ranks_df.head(100))


# ============================================================
# TAB 3 — RATINGS & REVIEWS
# ============================================================
with tab_reviews:

    st.subheader("iOS vs Android Rating Trends")

    platform_rating = (
        ratings_df
        .groupby(["date", "market_code"])["average_star_cumulative"]
        .mean()
        .reset_index()
    )

    fig_platform_rating = px.line(
        platform_rating,
        x="date",
        y="average_star_cumulative",
        color="market_code",
        color_discrete_map={"apple-store": "#007AFF", "google-play": "#34A853"},
        title="Cumulative Average Rating — iOS vs Android",
        labels={"market_code": "Platform", "average_star_cumulative": "Avg Rating", "date": "Date"}
    )
    fig_platform_rating.update_yaxes(range=[4.5, 5.0])
    st.plotly_chart(fig_platform_rating, width="stretch")
    st.caption("iOS consistently rates higher (~4.80 ★) than Android (~4.66 ★).")

    st.subheader("Combined Rating Evolution")

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
        title="Average Rating Evolution (iOS + Android combined)",
        labels={"average_star_cumulative": "Avg Rating", "date": "Date"}
    )
    fig_rating.update_traces(line_color="#00897B")
    st.plotly_chart(fig_rating, width="stretch")

    st.markdown("---")

    st.subheader("Critical Review Volume Over Time")
    st.caption(
        "All reviews are 1-star (API export filtered to critical feedback). "
        "Volume spikes indicate periods of heightened user friction. "
        "Dashed lines mark new version releases."
    )

    monthly_reviews = (
        reviews_df
        .groupby("year_month")
        .size()
        .reset_index(name="review_count")
    )

    fig_monthly_reviews = px.bar(
        monthly_reviews,
        x="year_month",
        y="review_count",
        title="Monthly Critical Review Volume",
        labels={"year_month": "Month", "review_count": "Reviews"},
        color_discrete_sequence=["#00897B"]
    )

    version_release_dates = (
        timeline_df[timeline_df["event_type_name"] == "new_version"]["date"]
        .drop_duplicates()
    )
    for d in version_release_dates:
        fig_monthly_reviews.add_vline(x=d, line_width=1, line_dash="dash", line_color="gray", opacity=0.25)

    st.plotly_chart(fig_monthly_reviews, width="stretch")

    st.markdown("---")

    col_t1, col_t2 = st.columns([1, 2])

    with col_t1:
        st.subheader("Top Complaint Topics")

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
            title="Top 10 Complaint Topics",
            color_discrete_sequence=["#00897B"],
            labels={"count": "Reviews", "topic": "Topic"}
        )
        fig_topics.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_topics, width="stretch")

    with col_t2:
        st.subheader("Complaint Topics Over Time")
        st.caption("How complaint themes shifted month by month — useful for tying user friction to specific releases.")

        top_topic_list = reviews_df["topics"].value_counts().head(8).index.tolist()
        topic_monthly = (
            reviews_df[reviews_df["topics"].isin(top_topic_list)]
            .groupby(["year_month", "topics"])
            .size()
            .reset_index(name="count")
        )

        fig_topic_time = px.bar(
            topic_monthly,
            x="year_month",
            y="count",
            color="topics",
            barmode="stack",
            title="Top Complaint Topics by Month",
            labels={"year_month": "Month", "count": "Reviews", "topics": "Topic"}
        )
        st.plotly_chart(fig_topic_time, width="stretch")

    with st.expander("Preview raw reviews data"):
        st.dataframe(reviews_df.drop(columns=["year_month"]).head(100))


# ============================================================
# TAB 4 — TIMELINE
# ============================================================
with tab_timeline:

    st.subheader("App Store Event Distribution")

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
        title="Timeline Event Distribution",
        color_discrete_sequence=["#00897B"],
        labels={"event_type": "Event Type", "count": "Count"}
    )
    st.plotly_chart(fig_events, width="stretch")

    st.subheader("Version Release Log")
    st.caption(f"{update_count} distinct version releases across the analysis period.")

    version_log = (
        timeline_df[timeline_df["event_type_name"] == "new_version"]
        [["date", "market_code", "old_value", "new_value", "release_notes"]]
        .drop_duplicates(subset=["date", "new_value"])
        .sort_values("date", ascending=False)
        .reset_index(drop=True)
    )
    version_log.columns = ["Date", "Platform", "Previous Version", "New Version", "Release Notes"]
    st.dataframe(version_log, use_container_width=True)

    with st.expander("Preview raw timeline data"):
        st.dataframe(timeline_df.head(100))
