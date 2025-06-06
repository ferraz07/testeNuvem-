# db_init.py
from fastapi import APIRouter
import psycopg2

router = APIRouter()

@router.post("/init-db")
def init_db():
    conn = psycopg2.connect(
        dbname="railway",
        user="postgres",
        password="xOkwAHOpXeOwDabcREDkVVdwGSivRyDE",
        host="postgres.railway.internal",
        port="5432"
    )
    cur = conn.cursor()
    with open("SQLQuery_2.sql", "r") as file:
        sql_script = file.read()
    cur.execute(sql_script)
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "Database initialized"}
