from sqlalchemy import create_engine
from langchain.sql_database import SQLDatabase
import os, json, re
from langchain_experimental.sql import SQLDatabaseChain
from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from sqlalchemy.sql import text
import numpy as np
import pandas as pd

try:
    import globalVariable as GV
except ImportError:
    import app.dataService.globalVariable as GV

def remove_sql_clause(sql_str, clause_name):
    """
    Removes the specified clause from the SQL string.

    Parameters:
    sql_str (str): The original SQL string.
    clause_name (str): The name of the clause to remove.

    Returns:
    str: The SQL string with the clause removed.
    """
    # Define a regex pattern to match the clause and any following characters up to the next clause or the end of the string
    pattern = re.compile(r"(?i)\s*{}\s+.*?(?=(?:\s+\w+\s+|$))".format(re.escape(clause_name)))
    
    # Use the pattern to remove the clause from the SQL string
    return pattern.sub("", sql_str)


class sqlModel(object):
    def __init__(self):
        self.model = ChatOpenAI(model_name="gpt-3.5-turbo-1106", temperature=0, openai_api_key = GV.openai_key)
        # , model_kwargs={"seed": 42})
        self.spider_dataset_dir = GV.SPIDER_FOLDER

    def predict(self, q, db_id):
        database_path = os.path.join(self.spider_dataset_dir, f'database/{db_id}/{db_id}.sqlite')  # Update this with the actual path
        # Create the SQLite URI for the database
        database_uri = f'sqlite:///{database_path}'
        engine = create_engine(database_uri)
        db = SQLDatabase(engine)
        db_chain = SQLDatabaseChain.from_llm(self.model, 
                          db,
                          use_query_checker=True,
                          return_sql = True,
                          verbose = True
                         )
        res = db_chain.run(q)
        # remove limit clause
        res_ = remove_sql_clause(res, "LIMIT")
        return res_

    def sql2text(self, sql: str = "SELECT name ,  country ,  age FROM singer ORDER BY age DESC"):
        sql2text_prompt = """
        Please translate the following sql query into natural language. Please only output the natural language result.

        {sql}

        Natural language:
        """
        prompt = PromptTemplate.from_template(sql2text_prompt)
        sql2text_chain = prompt | self.model
        res =sql2text_chain.invoke({
            "sql": sql
        })
        return res.content


if __name__ == '__main__':
    # Define the path to your SQLite database file
    db_name = "activity_1"
    q = "what is this data about?"
    # nl 2 sql
    sqlmodel = sqlModel()
    res = sqlmodel.predict(q, db_name)
    print(f"result for the {q}: \n {res}")
    # sql 2 text
    nl = sqlmodel.sql2text()
    print(f"{nl}")