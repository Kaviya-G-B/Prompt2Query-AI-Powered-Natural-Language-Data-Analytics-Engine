import re

def validate_sql(sql, schema, table_name):
    errors = []
    column_names = [col.lower() for col, dtype in schema]

    if table_name.lower() not in sql.lower():
        errors.append(f"Table '{table_name}' not found in SQL")

    sql_lower = sql.lower()

    if 'select' not in sql_lower:
        errors.append("SQL missing SELECT statement")

    if 'from' not in sql_lower:
        errors.append("SQL missing FROM statement")

    return errors

def auto_correct_sql(sql, schema, table_name):
    column_names = [col for col, dtype in schema]
    words = sql.split()
    corrected = []
    for i, word in enumerate(words):
        if i > 0 and words[i-1].upper() == 'FROM':
            corrected.append(table_name)
        else:
            corrected.append(word)
    sql = ' '.join(corrected)
    for col in column_names:
        pattern = re.compile(re.escape(col), re.IGNORECASE)
        sql = pattern.sub(col, sql)
    return sql

def validate_and_fix(sql, schema, table_name, max_retries=3):
    for attempt in range(max_retries):
        errors = validate_sql(sql, schema, table_name)
        if not errors:
            return sql, True
        sql = auto_correct_sql(sql, schema, table_name)
    errors = validate_sql(sql, schema, table_name)
    if not errors:
        return sql, True
    return sql, False