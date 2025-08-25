import json
import re
import numpy as np
from sql_metadata import Parser
import sqlparse
from sqlparse.sql import Where


class CohesionEvaluator:
    """
    Calculates five session cohesion metrics based on the sequence of queries
    actually chosen by the user.

    The primary method, `evaluate()`, returns a dictionary containing the
    average value for each of the five metrics calculated over the entire
    session. The five metrics are: Edit Index, Jaccard Index, Cosine Index,
    Common Fragments Index, and Common Tables Index.

    --Args:
        json_filepath (str): The path to the input JSON log file. This file
                             should contain the user's session data.

    --Attributes:
        chosen_queries_sql (list[str]): A list of SQL query strings extracted
                                        from the log file in the order they were chosen.

        parsed_chosen_queries (list[dict]): A list of dictionaries, where each
                                            dictionary represents a parsed SQL query.
                                            The keys are 'projections','clauses', 'aggregations', and 'tables',
                                            and the values are sets of the corresponding SQL fragments.
    """

    def __init__(self, json_filepath):
        """
        Initializes the CohesionEvaluator instance.
        """
        self.chosen_queries_sql = self._parse_log_file_for_chosen_queries(json_filepath)
        self.parsed_chosen_queries = [self._parse_sql_for_fragments(sql) for sql in self.chosen_queries_sql]

    def _parse_log_file_for_chosen_queries(self, filepath):
        """
        Reads and extracts the sequence of chosen SQL queries from the log file.
        --Args:
            filepath (str): The path to the JSON log file.

        --Outputs:
            list[str]: A list of SQL query strings in the order they were executed.
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            log_data = json.load(f)

        chosen_queries = []
        interaction_log = log_data.get("interaction_log", [])

        # Iterate through each turn in the interaction log
        for turn in interaction_log:
            # We are interested in turns of type 'interaction' which contain the executed SQL
            if turn.get("type") == "interaction":
                system_response = turn.get("system_response", {})
                sql = system_response.get("sql")

                # Add the SQL to our list if it exists and is not empty
                if sql:
                    chosen_queries.append(sql)

        return chosen_queries

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
                    return
                # Recursively check inside grouped statements (parentheses)
                if token.is_group:
                    find_where(token.tokens)

        find_where(parsed[0].tokens)
        return conditions

    def _parse_sql_for_fragments(self, sql):
        """
        Parses the SQL statement into fragments: projections, selections, aggregations, tables.
        --Args:
            sql (str): The SQL query string to parse.

        --Outputs:
            dict[str, set]: A dictionary containing the parsed fragments. The
                            keys are 'projections', 'clauses', 'aggregations', and 'tables',
                            and the values are sets of strings representing the fragments.
        """
        if not sql:
            return {'projections': set(), 'selections': set(), 'clauses': set(), 'aggregations': set(), 'tables': set()}
        try:
            AGG_OPS = ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN']
            CLAUSE_KEYWORDS = {'GROUP BY', 'ORDER BY', 'LIMIT', 'INTERSECT', 'UNION', 'EXCEPT', 'JOIN'}
            aggs = {op for op in AGG_OPS if re.search(r'\b' + op + r'\s*\(', sql, re.IGNORECASE)}
            clauses = {
                clause for clause in CLAUSE_KEYWORDS
                if re.search(r'\b' + clause.replace(' ', r'\s+') + r'\b', sql, re.IGNORECASE)
            }
            parser = Parser(sql)
            selections = self._get_where_conditions(sql)
            return {
                'projections': set(parser.columns),
                'selections': selections,
                'clauses': clauses,
                'aggregations': aggs,
                'tables': set(parser.tables)
            }
        except Exception:
            return {'projections': set(), 'selections': set(), 'clauses': set(), 'aggregations': set(), 'tables': set()}

    def evaluate(self):
        """
        Calculates and returns the cohesion metrics.

        --Output:
            all_cohesion_metrics(dict): A dictionary of computed metrics.
            Example:
                {
                "Edit Index": 0.835,
                "Jaccard Index": 0.612,
                "Cosine Index": 0.791,
                "Common Fragments Index": 0.75,
                "Common Tables Index": 0.917
                }
        """
        if len(self.parsed_chosen_queries) < 2:
            return {
                "Edit Index": 0.0,
                "Jaccard Index": 0.0,
                "Cosine Index": 0.0,
                "Common Fragments Index": 0.0,
                "Common Tables Index": 0.0
            }

        indices = {k: [] for k in ["edit", "jaccard", "cosine", "cf", "ct"]}
        max_tables_in_session = max((len(p['tables']) for p in self.parsed_chosen_queries if p['tables']), default=1)

        fragment_keys = ['projections', 'selections', 'clauses', 'aggregations', 'tables']

        for i in range(1, len(self.parsed_chosen_queries)):
            q_prev, q_curr = self.parsed_chosen_queries[i - 1], self.parsed_chosen_queries[i]

            # Edit Index
            added = sum(len(q_curr[key] - q_prev[key]) for key in q_curr)
            removed = sum(len(q_prev[key] - q_curr[key]) for key in q_curr)
            indices["edit"].append(max(0, 1 - ((added + removed) / 10)))

            # Jaccard Index
            fragments_prev = set().union(*(q_prev[key] for key in fragment_keys))
            fragments_curr = set().union(*(q_curr[key] for key in fragment_keys))

            intersection_size = len(fragments_prev.intersection(fragments_curr))
            union_size = len(fragments_prev.union(fragments_curr))
            indices["jaccard"].append(
                intersection_size / union_size if union_size > 0 else 1.0 if not fragments_prev and not fragments_curr else 0.0)

            # Cosine Index
            vec_prev = np.array([len(q_prev[f]) for f in fragment_keys])
            vec_curr = np.array([len(q_curr[f]) for f in fragment_keys])
            dot_product = np.dot(vec_prev, vec_curr)
            norm_prev = np.linalg.norm(vec_prev)
            norm_curr = np.linalg.norm(vec_curr)
            if norm_prev > 0 and norm_curr > 0:
                indices["cosine"].append(dot_product / (norm_prev * norm_curr))
            else:
                indices["cosine"].append(1.0 if norm_prev == norm_curr else 0.0)

            # Common Fragments Index
            ncf = sum(len(q_curr[key].intersection(q_prev[key])) for key in fragment_keys)
            indices["cf"].append(min(1, ncf / 10))

            # Common Tables Index
            nct = len(q_curr['tables'].intersection(q_prev['tables']))
            indices["ct"].append(nct / max_tables_in_session if max_tables_in_session > 0 else 0)

        return {
            "Edit Index": np.mean(indices["edit"]),
            "Jaccard Index": np.mean(indices["jaccard"]),
            "Cosine Index": np.mean(indices["cosine"]),
            "Common Fragments Index": np.mean(indices["cf"]),
            "Common Tables Index": np.mean(indices["ct"])
        }
