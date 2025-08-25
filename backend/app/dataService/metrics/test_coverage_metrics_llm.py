# Assume the CoverageEvaluator or a similar class with the _parse_schema method is defined above.
# For a self-contained test, I will create a simple class here.
import re
import tempfile
import os


class SchemaParser:
    def _parse_schema(self, filepath):
        """
        Reads database schema information from a .sql file.
        --Args:
            filepath (str): The path to the .sql schema file.

        --Outputs:
            dict[str, set]: A dictionary containing two sets: one for all table
                            names and one for all column names found in the schema.
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # --- Modification : Allow "IF NOT EXISTS" ---
            tables = re.findall(r'CREATE TABLE(?:\s+IF NOT EXISTS)?\s+[`"]?(\w+)[`"]?', content, re.IGNORECASE)
            table_defs = re.findall(r'CREATE TABLE.*?\((.*?)\);', content, re.DOTALL | re.IGNORECASE)

            all_columns = set()
            for table_def in table_defs:
                # Iterate over each line in the table definition directly.
                for line in table_def.strip().split('\n'):
                    line = line.strip()
                    # Exclude empty lines, comments, and lines that are exclusively constraint definitions.
                    if not line or \
                       line.strip().startswith('--') or \
                       line.upper().startswith(('PRIMARY KEY', 'FOREIGN KEY', 'CONSTRAINT', ')', 'UNIQUE KEY')):
                        continue

                    # Match the column name at the beginning of the line.
                    match = re.match(r'[`"]?(\w+)[`"]?', line)
                    if match:
                        all_columns.add(match.group(1))

            return {"tables": {t.strip('`"') for t in tables}, "columns": all_columns}
        except FileNotFoundError:
            print(f"Warning: Schema file '{filepath}' not found.")
            return {"tables": set(), "columns": set()}


# ==============================================================================
# Test Suite for the _parse_schema function
# ==============================================================================
if __name__ == '__main__':

    # 1. Define the sample SQL schema content for testing
    sample_schema_sql = """
    -- This is a test schema for parsing
    CREATE TABLE users (
      `id` INTEGER PRIMARY KEY,
      username TEXT NOT NULL,
      email TEXT UNIQUE
    );

    CREATE TABLE IF NOT EXISTS products (
        product_id INTEGER,
        `name` TEXT,
        price REAL,
        PRIMARY KEY (product_id)
    );

    /*
     * A multi-line comment block
     * for the orders table.
    */
    CREATE TABLE orders (
        order_id INTEGER,
        user_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    """

    # 2. Define the expected output
    expected_tables = {'users', 'products', 'orders'}
    expected_columns = {'id', 'username', 'email', 'product_id', 'name', 'price', 'order_id', 'user_id', 'quantity'}

    # 3. Create an instance of the class containing the method to test
    parser = SchemaParser()

    # 4. Run the main test using a temporary file
    temp_file_path = ''
    try:
        # Create a temporary file to write the schema to
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".sql", encoding='utf-8') as temp:
            temp.write(sample_schema_sql)
            temp_file_path = temp.name

        print("--- Running Test: Standard Schema Parsing ---")

        # Call the function with the temporary file path
        result = parser._parse_schema(temp_file_path)

        # Assert that the results match the expectations
        print(f"Parsed tables: {result['tables']}")
        assert result[
                   'tables'] == expected_tables, f"Table mismatch! Expected {expected_tables}, got {result['tables']}"

        print(f"Parsed columns: {result['columns']}")
        assert result[
                   'columns'] == expected_columns, f"Column mismatch! Expected {expected_columns}, got {result['columns']}"

        print("✅ Standard Schema Parsing Test PASSED")

    except Exception as e:
        print(f"❌ Standard Schema Parsing Test FAILED: {e}")
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)