import sqlparse
import re
from sqlparse.sql import Where

class MyClass:
    def _get_where_conditions(self, sql):
        """
        Correctly extracts WHERE clause conditions using the 'sqlparse' library.
        """
        conditions = set()
        parsed = sqlparse.parse(sql)
        if not parsed:
            return conditions

        # This function recursively searches for a WHERE clause in the token stream
        def find_where(tokens):
            for token in tokens:
                if isinstance(token, Where):
                    # Found a WHERE clause. Now, extract its conditions.
                    # We get the string content of the clause, excluding the 'WHERE' keyword itself.
                    raw_conditions = ''.join(t.value for t in token.tokens[1:]).strip()
                    # Split by 'AND' or 'OR' to get individual conditions
                    split_conds = re.split(r'\s+(?:AND|OR)\s+', raw_conditions, flags=re.IGNORECASE)
                    for cond in split_conds:
                        if cond.strip():
                            conditions.add(cond.strip().lower())
                    # Stop after finding the first top-level WHERE clause
                    # Extracts and processes only the conditions of the outermost WHERE clause
                    return
                # Recursively check inside grouped statements (parentheses)
                if token.is_group:
                    find_where(token.tokens)

        find_where(parsed[0].tokens)
        return conditions


sql1 = "SELECT * FROM users WHERE age > 18 AND city = 'New York'"
sql2 = "SELECT * FROM products WHERE category = 'Electronics' OR price < 100"
sql4 = "SELECT * FROM table1"
sql5 = "SELECT * FROM table2 WHERE a=1 AND b=2 OR c=3"

my_instance = MyClass()

print(f"SQL 1: {my_instance._get_where_conditions(sql1)}")
print(f"SQL 2: {my_instance._get_where_conditions(sql2)}")
print(f"SQL 4: {my_instance._get_where_conditions(sql4)}")
print(f"SQL 5: {my_instance._get_where_conditions(sql5)}")