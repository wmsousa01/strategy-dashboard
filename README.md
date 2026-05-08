# Sensor Tower Technology Strategy Assignment

## Overview

This project was developed as part of a Technology Strategy take-home assignment focused on analyzing app store performance, user feedback, product updates, and monetization trends for **MONOPOLY GO!**.

The objective was to transform raw and partially malformed datasets into actionable business insights through:
- data ingestion
- cleaning and normalization
- exploratory data analysis (EDA)
- visualization
- executive storytelling
- interactive dashboard development

The final deliverable includes both:
- static analytical outputs
- an interactive executive dashboard

---

# Project Objectives

The analysis focused on identifying:

- Grossing rank trends
- Rating evolution
- User review patterns
- Product update frequency
- Monetization-related friction
- Correlation between live-ops events and store performance

---

# Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core development |
| Pandas | Data processing |
| NumPy | Numerical operations |
| Matplotlib | Static visualizations |
| Plotly | Interactive visualizations |
| Streamlit | Executive dashboard |
| Jupyter Notebook | Exploratory analysis |

---

# Project Structure

```text
sensor-tower/
│
├── dashboard/
│   └── app.py
│
├── data/
│   └── raw dataset files
│
├── exports/
│   ├── timeline_clean.csv
│   ├── ratings_clean.csv
│   ├── reviews_clean.csv
│   └── ranks_clean.csv
│
├── charts/
│   ├── grossing_rank_trend.png
│   ├── average_rating_evolution.png
│   ├── review_sentiment_distribution.png
│   ├── timeline_event_distribution.png
│   ├── top_review_topics.png
│   └── grossing_rank_vs_timeline_events.png
│
├── notebooks/
│   ├── data exploration notebooks
│   └── exploratory analysis
│
├── src/
│   ├── load_data.py
│   ├── clean_data.py
│   └── 03_eda.py
│
├── slides/
│   └── executive presentation assets
│
├── requirements.txt
├── README.md
└── .gitignores


