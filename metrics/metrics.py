import json
import re
import numpy as np
from sql_metadata import Parser
import os
import pathlib


class CoverageAndNoveltyEvaluator:
    """
    计算覆盖率与新颖性相关指标:
    1. 模式探索广度 (Schema Exploration Breadth) (表/列覆盖率)
    2. 操作多样性 (Operator Diversity) (聚合/子句覆盖率)
    这里考虑的是所有推荐的查询，即第一轮推荐了5个查询，我们都考虑进去，而不是只考虑用户点击的那个查询。
    """

    def __init__(self, json_filepath, schema_filepath):
        self.recommendation_lists_sql = self._parse_log_file_for_recommendations(json_filepath)
        self.schema_info = self._parse_schema(schema_filepath)
        self.parsed_recommendations = [[self._parse_sql(sql) for sql in step_sqls] for step_sqls in
                                       self.recommendation_lists_sql]
    # 读取-初始化的推荐查询以及后续的所有查询
    def _parse_log_file_for_recommendations(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        recommendation_lists = [log_data['userdata']['origQuerySugg']['sql']]
        for step in log_data['userdata']['suerQueryData']:
            if 'QuerySugg' in step and 'sql' in step['QuerySugg']:
                recommendation_lists.append(step['QuerySugg']['sql'])
        return recommendation_lists

    # 从schema.sql读取相应的数据库信息
    def _parse_schema(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            tables = re.findall(r'CREATE TABLE\s+([\w`"]+)', content, re.IGNORECASE)
            table_defs = re.findall(r'CREATE TABLE\s+[\w`"]+\s*\((.*?)\);', content, re.DOTALL | re.IGNORECASE)
            all_columns = set()
            for table_def in table_defs:
                for line in table_def.strip().split('\n'):
                    line = line.strip()
                    if not line or line.upper().startswith(('PRIMARY', 'FOREIGN', 'CONSTRAINT', ')', 'UNIQUE')):
                        continue
                    match = re.match(r'[`"]?(\w+)[`"]?', line)
                    if match:
                        all_columns.add(match.group(1))
            return {"tables": {t.strip('`"') for t in tables}, "columns": all_columns}
        except FileNotFoundError:
            print(f"警告: schema文件 '{filepath}' 未找到。")
            return {"tables": set(), "columns": set()}

    def _parse_sql(self, sql):
        if not sql: return {'tables': set(), 'columns': set(), 'aggregations': set(), 'clauses': set()}
        try:
            AGG_OPS, CLAUSE_KEYWORDS = ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN'], {'GROUP BY', 'ORDER BY', 'JOIN'}
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

    def calculate_coverage_metrics(self):
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

        AGG_FUNCTIONS, CLAUSES = {'COUNT', 'SUM', 'AVG', 'MAX', 'MIN'}, {'GROUP BY', 'ORDER BY', 'JOIN'}
        agg_coverage = len(recommended_aggs.intersection(AGG_FUNCTIONS)) / len(AGG_FUNCTIONS) if AGG_FUNCTIONS else 0
        clause_coverage = len(recommended_clauses.intersection(CLAUSES)) / len(CLAUSES) if CLAUSES else 0

        return {
            "表覆盖率 (Table Coverage)": table_coverage,
            "列覆盖率 (Column Coverage)": column_coverage,
            "聚合函数覆盖率 (Aggregation Coverage)": agg_coverage,
            "关键子句覆盖率 (Clause Coverage)": clause_coverage
        }

    def evaluate(self):
        return self.calculate_coverage_metrics()


class CohesionEvaluator:
    """计算基于用户实际选择查询序列的五个会话连贯性指标。"""

    def __init__(self, json_filepath):
        self.chosen_queries_sql = self._parse_log_file_for_chosen_queries(json_filepath)
        self.parsed_chosen_queries = [self._parse_sql_for_fragments(sql) for sql in self.chosen_queries_sql]

    # 读取用户实际选择的查询序列
    def _parse_log_file_for_chosen_queries(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            log_data = json.load(f)
        return [step.get('SQL', {}).get('sql') for step in log_data['userdata']['suerQueryData']]

    # 将SQL语句切分为：投影、选择、聚合、表
    def _parse_sql_for_fragments(self, sql):
        if not sql: return {'projections': set(), 'selections': set(), 'aggregations': set(), 'tables': set()}
        try:
            AGG_OPS = ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN']
            aggs = {op for op in AGG_OPS if re.search(r'\b' + op + r'\s*\(', sql, re.IGNORECASE)}
            selections = set()
            where_match = re.search(r'WHERE\s+(.*?)(?:GROUP BY|ORDER BY|LIMIT|;|\Z)', sql, re.IGNORECASE | re.DOTALL)
            if where_match:
                conditions = where_match.group(1)
                selections = {cond.strip() for cond in re.split(r'\bAND\b|\bOR\b', conditions, flags=re.IGNORECASE)}
            parser = Parser(sql)
            return {'projections': set(parser.columns), 'selections': selections, 'aggregations': aggs,
                    'tables': set(parser.tables)}
        except Exception:
            return {'projections': set(), 'selections': set(), 'aggregations': set(), 'tables': set()}

    def evaluate(self):
        if len(self.parsed_chosen_queries) < 2:
            return {"编辑指数 (Edit Index)": 0, "Jaccard指数 (Jaccard Index)": 0, "余弦指数 (Cosine Index)": 0,
                    "公共片段指数 (Common Fragments Index)": 0, "公共表指数 (Common Tables Index)": 0}

        indices = {k: [] for k in ["edit", "jaccard", "cosine", "cf", "ct"]}
        max_tables_in_session = max((len(p['tables']) for p in self.parsed_chosen_queries if p['tables']), default=1)

        for i in range(1, len(self.parsed_chosen_queries)):
            q_prev, q_curr = self.parsed_chosen_queries[i - 1], self.parsed_chosen_queries[i]

            # Edit Index
            added = sum(len(q_curr[key] - q_prev[key]) for key in q_curr)
            removed = sum(len(q_prev[key] - q_curr[key]) for key in q_curr)
            indices["edit"].append(max(0, 1 - ((added + removed) / 10)))

            # Jaccard Index
            fragments_prev = q_prev['projections'] | q_prev['selections'] | q_prev['aggregations'] | q_prev['tables']
            fragments_curr = q_curr['projections'] | q_curr['selections'] | q_curr['aggregations'] | q_curr['tables']
            intersection_size = len(fragments_prev.intersection(fragments_curr))
            union_size = len(fragments_prev.union(fragments_curr))
            indices["jaccard"].append(intersection_size / union_size if union_size > 0 else 0)

            # Cosine Index
            vec_prev = np.array([len(q_prev[f]) for f in ['projections', 'selections', 'aggregations', 'tables']])
            vec_curr = np.array([len(q_curr[f]) for f in ['projections', 'selections', 'aggregations', 'tables']])
            dot_product, norm_prev, norm_curr = np.dot(vec_prev, vec_curr), np.linalg.norm(vec_prev), np.linalg.norm(
                vec_curr)
            indices["cosine"].append(dot_product / (norm_prev * norm_curr) if norm_prev > 0 and norm_curr > 0 else (
                1.0 if norm_prev == norm_curr else 0.0))

            # Common Fragments Index
            ncf = sum(len(q_curr[key].intersection(q_prev[key])) for key in q_curr)
            indices["cf"].append(min(1, ncf / 10))

            # Common Tables Index
            nct = len(q_curr['tables'].intersection(q_prev['tables']))
            indices["ct"].append(nct / max_tables_in_session if max_tables_in_session > 0 else 0)

        return {
            "编辑指数 (Edit Index)": np.mean(indices["edit"]),
            "Jaccard指数 (Jaccard Index)": np.mean(indices["jaccard"]),
            "余弦指数 (Cosine Index)": np.mean(indices["cosine"]),
            "公共片段指数 (Common Fragments Index)": np.mean(indices["cf"]),
            "公共表指数 (Common Tables Index)": np.mean(indices["ct"])
        }


def evaluate_user_session(json_filepath: str, schema_folder_name: str) -> dict:
    """
    依据给定的JSON用户会话日志和数据库schema，计算并保存客观评估指标。
    """
    all_metrics = {}
    SCHEMA_BASE_DIR = "../backend/app/data/dataset/spider/database/"
    schema_filepath = os.path.join(SCHEMA_BASE_DIR, schema_folder_name, "schema.sql")

    RESULTS_DIR = "results"
    os.makedirs(RESULTS_DIR, exist_ok=True)
    json_filename_stem = pathlib.Path(json_filepath).stem
    output_txt_filepath = os.path.join(RESULTS_DIR, f"{json_filename_stem}.txt")

    print(f"\n--- 开始评估: '{json_filepath}' | Schema: '{schema_filepath}' ---")

    coverage_evaluator = CoverageAndNoveltyEvaluator(json_filepath, schema_filepath)
    all_metrics.update(coverage_evaluator.evaluate())

    cohesion_evaluator = CohesionEvaluator(json_filepath)
    all_metrics.update(cohesion_evaluator.evaluate())

    try:
        with open(output_txt_filepath, 'w', encoding='utf-8') as f:
            if not all_metrics:
                f.write("未生成任何评估结果。\n")
                print(f"\n警告: 未生成评估结果。文件 '{output_txt_filepath}' 已创建但为空。")
                return all_metrics

            f.write("=" * 55 + "\n")
            f.write(" " * 15 + "综合客观指标评估结果\n")
            f.write("=" * 55 + "\n\n")

            f.write("--- 覆盖率指标 ---\n")
            coverage_keys = ["表覆盖率 (Table Coverage)", "列覆盖率 (Column Coverage)",
                             "聚合函数覆盖率 (Aggregation Coverage)", "关键子句覆盖率 (Clause Coverage)"]
            for key in coverage_keys:
                if key in all_metrics: f.write(f"{key:<40}: {all_metrics.get(key, 0):.4f}\n")

            f.write("\n--- 会话连贯性指标 ---\n")
            cohesion_keys = ["编辑指数 (Edit Index)", "Jaccard指数 (Jaccard Index)", "余弦指数 (Cosine Index)",
                             "公共片段指数 (Common Fragments Index)", "公共表指数 (Common Tables Index)"]
            for key in cohesion_keys:
                if key in all_metrics: f.write(f"{key:<40}: {all_metrics.get(key, 0):.4f}\n")

            f.write("=" * 55 + "\n")
            print(f"\n评估结果已成功保存到: {output_txt_filepath}")

    except Exception as e:
        print(f"\n保存结果到文件 '{output_txt_filepath}' 时发生错误: {e}")

    return all_metrics


if __name__ == "__main__":
    USER_JSON_DIR = "../backend/app/data/dataset/user/"
    # 这里需要根据用户实际情况，去指定分析的基座数据库，这里我的用户查询记录都是基于"customers_and_addresses"生成的
    DEFAULT_SCHEMA_FOLDER = "customers_and_addresses"
    if not os.path.isdir(USER_JSON_DIR):
        print(f"错误: 用户JSON文件目录 '{USER_JSON_DIR}' 不存在。请检查路径。")
    else:
        # 从User记录中提取出所有的历史json文件，后续依次处理评估
        json_files = [f for f in os.listdir(USER_JSON_DIR) if f.endswith('.json')]
        if not json_files:
            print(f"在目录 '{USER_JSON_DIR}' 中未找到任何JSON文件。")
        else:
            print(f"\n--- 找到 {len(json_files)} 个JSON文件，开始批量处理 ---")
            for i, filename in enumerate(json_files):
                filepath = os.path.join(USER_JSON_DIR, filename)
                print(f"\n[{i + 1}/{len(json_files)}] 正在处理文件: {filename}")
                evaluate_user_session(filepath, DEFAULT_SCHEMA_FOLDER)
            print("\n--- 所有JSON文件的评估处理完成 ---")

    print("\n评估流程结束。")