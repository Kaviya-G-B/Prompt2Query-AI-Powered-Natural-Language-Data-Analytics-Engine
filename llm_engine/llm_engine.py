import requests
import json

OLLAMA_HOST = "172.20.112.1"
OLLAMA_PORT = 11434
MODEL_NAME = "phi3"

def generate_sql(question, schema, table_name):
    schema_str = ", ".join([f"{col} ({dtype})" for col, dtype in schema])

    prompt = f"""You are a SQL expert. Generate a single SQL query only.
Table name: {table_name}
Columns: {schema_str}
Question: {question}
Rules:
- Return ONLY the SQL query, nothing else
- No explanations, no markdown, no backticks
SQL:"""

    response = requests.post(
        f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    data = response.json()
    print("LLM Raw Response:", data)

    # Handle different response formats
    if "response" in data:
        sql = data["response"].strip()
    elif "message" in data:
        sql = data["message"]["content"].strip()
    else:
        sql = str(data)

    # Clean up
    sql = sql.replace("```sql", "").replace("```", "").strip()
    lines = [l.strip() for l in sql.split("\n") if l.strip()]
    for line in lines:
        if line.upper().startswith("SELECT"):
            return line

    return lines[0] if lines else sql

def generate_explanation(question, sql, result_summary):
    prompt = f"""You are a data analyst. Explain this result in 2-3 simple sentences.
Question: {question}
SQL: {sql}
Result: {result_summary}
Explanation:"""

    response = requests.post(
        f"http://{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate",
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )

    data = response.json()
    if "response" in data:
        return data["response"].strip()
    elif "message" in data:
        return data["message"]["content"].strip()
    return "Analysis complete."