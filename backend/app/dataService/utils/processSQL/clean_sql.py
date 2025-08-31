import re

# A list of SQL keywords.
# It is sorted by length in descending order. This is a crucial step to ensure
# that longer, multi-word keywords (e.g., 'GROUP BY') are matched before their
# shorter counterparts (e.g., 'BY'), preventing incorrect tokenization.
SQL_KEYWORDS = sorted([
    # Composite Keywords (highest priority)
    'GROUP BY', 'ORDER BY', 'PARTITION BY',
    'LEFT JOIN', 'RIGHT JOIN', 'INNER JOIN', 'FULL OUTER JOIN',
    'UNION ALL', 'INSERT INTO', 'DELETE FROM', 'CREATE TABLE',
    'PRIMARY KEY',

    # Single Long Keywords
    'INTERSECT', 'DISTINCT', 'BETWEEN', 'EXISTS',
    'SELECT', 'WHERE', 'HAVING', 'UPDATE', 'VALUES',
    'EXCEPT', 'LIMIT', 'OFFSET',

    # Aggregate/Window Functions & Sorting
    'COUNT', 'SUM', 'AVG', 'MIN', 'MAX',
    'DESC', 'ASC', 'OVER',

    # Logical, Join, Alias, and Comparison Operators
    'FROM', 'JOIN', 'LIKE', 'AND', 'NOT',
    'AS', 'ON', 'OR', 'IN', 'IS'

], key=len, reverse=True)


def clean_sql(sql: str) -> str:
    """
    Cleans and standardizes a raw SQL query string.

    This function performs several normalization steps:
    1. Removes common markdown code fences (e.g., ```sql, sqlquery).
    2. Removes double quotes and trailing semicolons.
    3. Converts all defined SQL keywords to uppercase.
    4. Keep column and table names in lowercase
    5. Standardizes all whitespace to single spaces.

    Args:
        sql (str): The raw SQL string to be cleaned.

    Returns:
        str: The cleaned and formatted SQL string, or the original input
             if it's not a string.
    """
    # Guard clause to handle non-string inputs gracefully.
    if not isinstance(sql, str):
        return sql

    # 1. Remove optional markdown code fences and trim leading/trailing whitespace.
    cleaned_sql = re.sub(r"^(```sql\s*|sqlquery:\s*)", "", sql, flags=re.IGNORECASE).strip()
    cleaned_sql = re.sub(r"^(```sql\s*|sqlquery:\s*)", "", cleaned_sql, flags=re.IGNORECASE).strip() 

    # 2. Remove all double quotes, often used for identifiers but can be inconsistent.
    cleaned_sql = cleaned_sql.replace('"', '')

    # 3. Remove a trailing semicolon, if present.
    if cleaned_sql.endswith(';'):
        cleaned_sql = cleaned_sql[:-1]

    # 4. Build a regex pattern to match all keywords as whole words.
    # The `\b` word boundaries prevent matching substrings within other words
    # (e.g., it won't match 'OR' in 'BORDER').
    keyword_pattern = '|'.join(r'\b' + re.escape(k) + r'\b' for k in SQL_KEYWORDS)

    # 5. Convert the entire query to lowercase to ensure case-insensitive matching.
    sql_lower = cleaned_sql.lower()

    # 6. Use a helper function with re.sub to find all keyword matches and
    # convert only those matched parts to uppercase.
    def uppercase_match(match):
        return match.group(0).upper()

    cleaned_sql = re.sub(keyword_pattern, uppercase_match, sql_lower, flags=re.IGNORECASE)

    # 7. Normalize all whitespace (multiple spaces, newlines, etc.) to a single space.
    final_sql = re.sub(r'\s+', ' ', cleaned_sql).strip()

    return final_sql


# Main execution block for demonstration and testing purposes.
if __name__ == '__main__':
    # Define a simple sample SQL query for testing.
    input_sql = '   SELECT customer_name, other_customer_details FROM "Customers" ORDER BY customer_id;   '

    # Call the cleanup function.
    cleaned_sql = clean_sql(input_sql)

    # Print the original and cleaned versions to compare.
    print(f"Original SQL: {input_sql}")
    print(f"Cleaned SQL:  {cleaned_sql}")

    # Define a more complex query to showcase multiple features of the cleaner.
    complex_sql_example = """
    ```sqlquery
    select
        user_id,
        COUNT(order_id) as order_count,
        max(order_date)
    from "orders_table"
    where order_date >= '2023-01-01' and not is_cancelled
    group by user_id
    having count(order_id) > 5
    order by order_count desc;
    ```
    """
    print("--- Complex Example ---")
    print(f"Original SQL:\n{complex_sql_example.strip()}")
    print(f"Cleaned SQL:\n{clean_sql(complex_sql_example)}")

    test_sqls = [
        "sqlquery: SELECT * FROM table",
        "SQLQUERY: SELECT * FROM table",
        "  sqlquery:  SELECT * FROM table  ",
        "```sql sqlquery:SELECT * FROM table```",
        "```sql\nsqlquery:  SELECT * FROM table\n```",
        "SELECT * FROM table",
        "   SELECT * FROM table   ",
        "```sql SELECT * FROM table ```",
    ]

    for sql in test_sqls:
        cleaned = clean_sql(sql)
        print(f"Original: '{sql}'")
        print(f"Cleaned: '{cleaned}'")
        print("-" * 20)
