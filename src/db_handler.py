import os
import sys
import psycopg2
from datetime import datetime, timezone, timedelta
from psycopg2.extras import DictCursor


class DBHandler:
    def __init__(self):
        self.database_url = os.environ["DATABASE_URL"]

    def exec_query(self, query_str):
        try:
            with psycopg2.connect(self.database_url, sslmode='require') as conn:
                with conn.cursor(cursor_factory=DictCursor) as cur:
                    cur.execute(query_str)
        except Exception as e:
            print(e.__str__())

    def update_dticket_status_record(self, target_date: datetime, type: str, status: bool):
        if type != "sea" and type != "land":
            sys.exit("typeはseaまたはlandのいずれかで指定する必要があります。")
        table_name = "dticket_status"
        dt_now = str(datetime.now(timezone(timedelta(hours=9))))
        query_str = f"INSERT INTO {table_name} VALUES (\'{target_date.strftime('%Y-%m-%d')}\',\'{type}\',\'{status}\',\'{dt_now}\')"
        self.exec_query(query_str)