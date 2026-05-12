import pandas as pd

def analyze_result(df):
    result = {}

    if df is None or df.empty:
        return {"error": "No results found"}

    columns = list(df.columns)
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object']).columns.tolist()

    result["row_count"] = len(df)
    result["columns"] = columns
    result["data"] = df.to_dict(orient="records")

    # Decide chart type
    if len(df) == 1 and len(numeric_cols) == 1 and len(columns) == 1:
        result["chart_type"] = "metric"
        result["metric_value"] = df[numeric_cols[0]].iloc[0]
        result["metric_label"] = numeric_cols[0]

    elif len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        result["chart_type"] = "bar"
        result["x_column"] = categorical_cols[0]
        result["y_column"] = numeric_cols[0]

    elif len(numeric_cols) >= 2:
        result["chart_type"] = "line"
        result["x_column"] = columns[0]
        result["y_column"] = numeric_cols[1]

    else:
        result["chart_type"] = "table"

    # Summary stats
    if numeric_cols:
        col = numeric_cols[0]
        result["summary"] = {
            "max": float(df[col].max()),
            "min": float(df[col].min()),
            "average": float(df[col].mean()),
            "total": float(df[col].sum())
        }
        result["result_summary"] = (
            f"The result has {len(df)} rows. "
            f"Maximum {col} is {df[col].max():.2f}, "
            f"minimum is {df[col].min():.2f}, "
            f"average is {df[col].mean():.2f}."
        )
    else:
        result["result_summary"] = f"Query returned {len(df)} rows."

    return result