"""
Create a python class that enables operate on a postgres database using psycopg2. I need the following FUNCTION support

FUNCTION

__init__()
__enter__()
__exit__()
connect_with_url(url)
upsert(table_name, _dict) - insert or update a row in a table if id is present in _dict
delete(table_name, _id) - delete a row in a table by id
get(table_name, _id) - get a row in table by id
get_all(table_name) - get all rows in a table
run_sql(sql) - run a sql statement

get_table_definition(table_name) - get a table definition in a 'create table' format directly from postgres

get_all_table_names() - get all table names in the database as a list

get_table_definitions_for_prompt() - combine get_table_definitions() and get_all_table_names() to generate a string that 
contains new line separated table definitions in a 'create_table' format for all tables in the database that can be used for 
our llm prompt
"""
import psycopg2
from psycopg2.extras import RealDictCursor

class PostgresDatabase:
    def __init__(self, connection_string, schema):
        self.connection_string = connection_string
        self.conn = None
        self.schema=schema

    def __enter__(self):
        self.conn = psycopg2.connect(self.connection_string)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.conn:
            self.conn.close()

    def connect_with_url(self, url):
        self.connection_string = url
        if self.conn:
            self.conn.close()
        self.conn = psycopg2.connect(self.connection_string)

        with self.conn.cursor() as cursor:
            cursor.execute(f"SET search_path TO {self.schema}")

    def upsert(self, table_name, _dict):
        if '_id' in _dict and self.conn:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT * FROM {self.schema}.{table_name} WHERE id = %s", (_dict['_id'],))
            if cursor.fetchone():
                cursor.execute(f"UPDATE {self.schema}.{table_name} SET %s = %s WHERE id = %s",
                               (psycopg2.extras.Json(_dict), _dict['_id'])) # type: ignore
            else:
                cursor.execute(f"INSERT INTO {self.schema}.{table_name} VALUES (%s)", (psycopg2.extras.Json(_dict),)) # type: ignore
            cursor.close()
            self.conn.commit()

    def delete(self, table_name, _id):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(f"DELETE FROM {self.schema}.{table_name} WHERE id = %s", (_id,))
            cursor.close()
            self.conn.commit()

    def get(self, table_name, _id):
        if self.conn:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(f"SELECT * FROM {self.schema}.{table_name} WHERE id = %s", (_id,))
            result = cursor.fetchone()
            cursor.close()
            return result

    def get_all(self, table_name):
        if self.conn:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(f"SELECT * FROM {self.schema}.{table_name}")
            results = cursor.fetchall()
            cursor.close()
            return results

    def run_sql(self, sql):
        if self.conn:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(sql)
            results = cursor.fetchall()
            cursor.close()
            return results

    def get_table_definition(self, table_name):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s", (table_name,))
            columns = cursor.fetchall()
            if not columns:
                return None
            create_table_sql = f"CREATE TABLE {self.schema}.{table_name} ("
            create_table_sql += ", ".join([f"{col[0]} {col[1]}" for col in columns])
            create_table_sql += ");"
            return create_table_sql

    def get_all_table_names(self):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{self.schema}'")
            result = cursor.fetchall()
            cursor.close()
            return [row[0] for row in result]

    def get_sample_table_data(self, table_name):
        import pandas as pd

        if self.conn:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(f"SELECT * FROM {self.schema}.{table_name} LIMIT 10")
            results = cursor.fetchall()
            cursor.close()
            return pd.DataFrame(results).to_markdown()

    def get_table_definitions_for_prompt(self):
        table_names = self.get_all_table_names()
        if table_names:
            # table_definitions = [self.get_table_definition(table_name) for table_name in table_names]
            table_definitions = [self.get_table_definition(table_name)  + f'\n Sample Data for {table_name}:\n' + self.get_sample_table_data(table_name) for table_name in table_names]
            return "\n\n".join(table for table in table_definitions if table is not None)