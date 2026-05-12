from spark_engine.spark_engine import load_csv_to_delta, get_schema, execute_query
from llm_engine.llm_engine import generate_sql, generate_explanation
from validator.validator import validate_and_fix
from result_analyzer.result_analyzer import analyze_result

def process_query(csv_path, table_name, question):
    response = {}

    try:
        # Step 1 - Load CSV to Delta Lake
        print("Step 1: Loading CSV to Delta Lake...")
        schema, delta_path = load_csv_to_delta(csv_path, table_name)
        response["schema"] = schema

        # Step 2 - Generate SQL from question
        print("Step 2: Generating SQL from question...")
        sql = generate_sql(question, schema, table_name)
        response["generated_sql"] = sql
        print(f"Generated SQL: {sql}")

        # Step 3 - Validate and fix SQL
        print("Step 3: Validating SQL...")
        sql, is_valid = validate_and_fix(sql, schema, table_name)
        response["validated_sql"] = sql
        response["is_valid"] = is_valid

        if not is_valid:
            response["error"] = "SQL validation failed after retries"
            return response

        # Step 4 - Execute SQL
        print("Step 4: Executing SQL...")
        result_df = execute_query(sql, table_name)
        response["result_data"] = result_df

        # Step 5 - Analyze result
        print("Step 5: Analyzing result...")
        analysis = analyze_result(result_df)
        response["analysis"] = analysis

        # Step 6 - Generate explanation
        print("Step 6: Generating explanation...")
        explanation = generate_explanation(
            question, sql, analysis.get("result_summary", "")
        )
        response["explanation"] = explanation

        print("Done!")
        return response

    except Exception as e:
        response["error"] = str(e)
        print(f"Error: {e}")
        return response