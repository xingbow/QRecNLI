import json
import re
from sql_metadata import Parser
import sqlite3

class CoverageEvaluator:
    """
    Calculates coverage and novelty related metrics:
    1. Schema Exploration Breadth (Table/Column Coverage)
    2. Operator Diversity (Aggregation/Clause Coverage)
    This considers all recommended queries. For instance, if 5 queries are
    recommended in one round, all are included, not just the one the user clicked on.

    --Args:
        json_filepath (str): The path to the input JSON log file containing session data.
        schema_filepath (str): The path to the .sql schema file for the database.

    --Attributes:
        recommendation_lists_sql (list[list[str]]): A list of lists, where each
                                                    inner list contains the SQL query
                                                    strings recommended in a single turn.

        schema_info (dict[str, set]): A dictionary containing all table and column
                                      names from the schema. Keys are 'tables' and 'columns'.

        parsed_recommendations (list[list[dict]]): A parsed representation of
                                                   `recommendation_lists_sql`, where each
                                                   query is a dictionary of its components.
    """

    def __init__(self, json_filepath, schema_filepath):
        """
        Reads the initial recommended queries and all subsequent ones.
        """
        self.recommendation_lists_sql = self._parse_log_file_for_recommendations(json_filepath)
        self.schema_info = self._parse_schema(schema_filepath)
        self.parsed_recommendations = [[self._parse_sql(sql) for sql in step_sqls] for step_sqls in
                                       self.recommendation_lists_sql]

    def _parse_log_file_for_recommendations(self, filepath):
        """
        Reads the initial recommended queries and all subsequent ones from the log file.
        --Args:
            filepath (str): The path to the JSON log file.

        --Outputs:
            list[list[str]]: A list of lists, where each inner list contains
                             the SQL recommendations for a single turn.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        recommendation_lists = [log_data['userdata']['origQuerySugg']['sql']]
        for step in log_data['userdata']['suerQueryData']:
            if 'QuerySugg' in step and 'sql' in step['QuerySugg']:
                recommendation_lists.append(step['QuerySugg']['sql'])
        return recommendation_lists

    def _parse_schema(self, db_filepath):
        """
        Reads database schema information directly from a .sqlite file.
        --Args:
            db_filepath (str): The path to the .sqlite database file.

        --Outputs:
            dict[str, set]: A dictionary containing sets for table and column names.
        """
        all_tables = set()
        all_columns = set()

        try:
            # Connect to a SQLite database
            conn = sqlite3.connect(db_filepath)
            cursor = conn.cursor()

            # 1. Get the names of all the tables
            # sqlite_master is a special table that stores metadata about the database
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            all_tables = {table[0] for table in tables}

            # 2. Iterate through each table and get the names of all its columns
            for table_name in all_tables:
                # PRAGMA table_info() is a special command for getting table structure information
                cursor.execute(f'PRAGMA table_info("{table_name}");')
                columns_info = cursor.fetchall()
                # The column name is in the second position (index 1) of the PRAGMA result.
                for col in columns_info:
                    all_columns.add(col[1])

            conn.close()
            return {"tables": all_tables, "columns": all_columns}

        except sqlite3.Error as e:
            print(f"Warning: Failed to read schema from '{db_filepath}'. Error: {e}")
            return {"tables": set(), "columns": set()}
        except FileNotFoundError:
            print(f"Warning: Database file '{db_filepath}' not found.")
            return {"tables": set(), "columns": set()}

    def _parse_sql(self, sql):
        """
        Parses a single SQL query to extract its components.
        --Args:
            sql (str): The SQL query string to parse.

        --Outputs:
            dict[str, set]: A dictionary containing the parsed components. Keys are
                            'tables', 'columns', 'aggregations', and 'clauses'.
        """
        if not sql: return {'tables': set(), 'columns': set(), 'aggregations': set(), 'clauses': set()}
        try:
            AGG_OPS, CLAUSE_KEYWORDS = ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN'], {'GROUP BY', 'ORDER BY', 'LIMIT', 'INTERSECT', 'UNION', 'EXCEPT', 'JOIN', 'WHERE'}
            aggs, clauses = set(), set()
            for op in AGG_OPS:
                if re.search(r'\b' + op + r'\s*\(', sql, re.IGNORECASE): aggs.add(op)
            for clause in CLAUSE_KEYWORDS:
                if re.search(r'\b' + clause + r'\b', sql, re.IGNORECASE): clauses.add(clause)
            parser = Parser(sql)
            return {'tables': set(parser.tables), 'columns': set(parser.columns), 'aggregations': aggs,
                    'clauses': clauses}
        except Exception:
            return {'tables': set(), 'columns': set(), 'aggregations': set(), 'clauses': set()}

    def evaluate(self):
        """
        Calculates and returns the coverage metrics.
        --Output: coverage_metrics (dict): A dictionary of computed coverage metrics.
            Example:
                {
                    "Table Coverage": 0.75,
                    "Column Coverage": 0.42,
                    "Aggregation Coverage": 0.6,
                    "Clause Coverage": 1.0
                }
        """
        recommended_tables, recommended_columns, recommended_aggs, recommended_clauses = set(), set(), set(), set()
        for step_parsed in self.parsed_recommendations:
            for parsed_info in step_parsed:
                recommended_tables.update(parsed_info['tables'])
                recommended_columns.update(parsed_info['columns'])
                recommended_aggs.update(parsed_info['aggregations'])
                recommended_clauses.update(parsed_info['clauses'])

        total_tables, total_columns = self.schema_info['tables'], self.schema_info['columns']
        table_coverage = len(recommended_tables) / len(total_tables) if total_tables else 0
        column_coverage = len(recommended_columns) / len(total_columns) if total_columns else 0

        AGG_FUNCTIONS, CLAUSES = {'COUNT', 'SUM', 'AVG', 'MAX', 'MIN'}, {'GROUP BY', 'ORDER BY', 'LIMIT', 'INTERSECT', 'UNION', 'EXCEPT', 'JOIN', 'WHERE'}
        agg_coverage = len(recommended_aggs.intersection(AGG_FUNCTIONS)) / len(AGG_FUNCTIONS) if AGG_FUNCTIONS else 0
        clause_coverage = len(recommended_clauses.intersection(CLAUSES)) / len(CLAUSES) if CLAUSES else 0

        return {
            "Table Coverage": table_coverage,
            "Column Coverage": column_coverage,
            "Aggregation Coverage": agg_coverage,
            "Clause Coverage": clause_coverage
        }
