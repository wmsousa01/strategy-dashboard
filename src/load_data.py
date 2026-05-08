import json
import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "tech_strat_assignment17.dataset.txt"
EXPORTS_DIR = BASE_DIR / "exports"

def fix_common_json_issues(content: str) -> str:
    content = re.sub(r'(\d)O(\d)', r'\g<1>0\g<2>', content)
    content = re.sub(r':\s*(\d+)O\b', lambda m: f": {m.group(1)}0", content)
    content = re.sub(r':\s*\$(\d+)', r': \1', content)

    content = re.sub(
        r'("app_id":\s*"[^"]+")\s+("product_id")',
        r'\1,\n                    \2',
        content
    )

    # Fix: last review is missing closing object brace
    content = re.sub(
        r'("topics":\s*"advertisements"\s*)\]\s*,\s*"review_terms"',
        r'\1}\n            ],\n            "review_terms"',
        content
    )

    # Fix: last product is missing closing brace before products list closes
    content = re.sub(
        r'("review_terms":\s*\[\]\s*)\]\s*,\s*"current_data_points_of_query"',
        r'\1}\n    ],\n    "current_data_points_of_query"',
        content
    )

    return content


def load_json(path: Path) -> dict:
    """
    Load and repair malformed JSON dataset.
    """

    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    with open(path, "r", encoding="utf-8") as file:
        raw_content = file.read()

    fixed_content = fix_common_json_issues(raw_content)

    try:
        return json.loads(fixed_content)

    except json.JSONDecodeError as e:
        error_position = e.pos

        start = max(0, error_position - 300)
        end = min(len(fixed_content), error_position + 300)

        print("\nJSON ERROR CONTEXT:")
        print("-" * 80)
        print(fixed_content[start:end])
        print("-" * 80)

        raise e


def validate_main_structure(raw_data: dict) -> None:
    required_keys = [
        "code",
        "report_status",
        "report_name",
        "start_date",
        "end_date",
        "products",
    ]

    missing_keys = [
        key for key in required_keys
        if key not in raw_data
    ]

    if missing_keys:
        raise ValueError(
            f"Missing required keys: {missing_keys}"
        )

    if not isinstance(raw_data["products"], list):
        raise TypeError("'products' must be a list")


def build_dataframes(
    raw_data: dict
) -> dict[str, pd.DataFrame]:

    all_timeline = []
    all_ratings = []
    all_reviews = []
    all_ranks = []

    for product in raw_data.get("products", []):

        product_metadata = {
            "app_name": product.get("app_name"),
            "app_id": product.get("app_id"),
            "product_name": product.get("product_name"),
            "product_id": product.get("product_id"),
            "company_name": product.get("company_name"),
            "publisher_name": product.get("publisher_name"),
            "market_code": product.get("market_code"),
            "device_code": product.get("device_code"),
            "category_name": product.get("category_name"),
        }

        for item in product.get("timeline", []):
            all_timeline.append({
                **item,
                **product_metadata
            })

        for item in product.get("ratings", []):
            all_ratings.append({
                **item,
                **product_metadata
            })

        for item in product.get("reviews", []):
            all_reviews.append({
                **item,
                **product_metadata
            })

        for item in product.get("ranks", []):
            all_ranks.append({
                **item,
                **product_metadata
            })

    return {
        "timeline": pd.DataFrame(all_timeline),
        "ratings": pd.DataFrame(all_ratings),
        "reviews": pd.DataFrame(all_reviews),
        "ranks": pd.DataFrame(all_ranks),
    }


def print_dataset_summary(
    raw_data: dict,
    dataframes: dict[str, pd.DataFrame]
) -> None:

    print("\nDataset loaded successfully")
    print("-" * 60)

    print(f"Report name: {raw_data.get('report_name')}")
    print(f"Report status: {raw_data.get('report_status')}")
    print(
        f"Date range: "
        f"{raw_data.get('start_date')} "
        f"to "
        f"{raw_data.get('end_date')}"
    )

    print(f"Products: {len(raw_data.get('products', []))}")

    print("\nProducts found:")

    for product in raw_data.get("products", []):

        print(
            f"- {product.get('app_name')} | "
            f"{product.get('market_code')} | "
            f"{product.get('device_code')}"
        )

    print("\nDataFrames:")

    for name, df in dataframes.items():

        print(
            f"- {name}: "
            f"{df.shape[0]} rows x "
            f"{df.shape[1]} columns"
        )


def validate_dataframes(
    dataframes: dict[str, pd.DataFrame]
) -> None:

    print("\nValidation summary")
    print("-" * 60)

    for name, df in dataframes.items():

        print(f"\n{name.upper()}")

        print(f"Rows: {len(df)}")
        print(f"Columns: {list(df.columns)}")

        if df.empty:

            print("WARNING: DataFrame is empty")

        else:

            print("\nNull values:")
            print(df.isnull().sum())


def export_dataframes(
    dataframes: dict[str, pd.DataFrame]
) -> None:

    EXPORTS_DIR.mkdir(exist_ok=True)

    for name, df in dataframes.items():

        output_path = EXPORTS_DIR / f"{name}_raw.csv"

        df.to_csv(output_path, index=False)

        print(f"\nExported: {output_path}")


def main() -> None:

    raw_data = load_json(DATA_PATH)

    validate_main_structure(raw_data)

    dataframes = build_dataframes(raw_data)

    print_dataset_summary(raw_data, dataframes)

    validate_dataframes(dataframes)

    export_dataframes(dataframes)

    print("\nPipeline completed successfully")


if __name__ == "__main__":
    main()