import psycopg2

conn = psycopg2.connect(
    dbname="railway",
    user="postgres",
    password="xOkwAHOpXeOwDabcREDkVVdwGSivRyDE",
    host="postgres.railway.internal",
    port="5432"
)

cur = conn.cursor()

# Coloque o conteúdo do seu SQL aqui (ou leia de um arquivo .sql)
with open("SQLQuery_2.sql", "r") as file:
    sql_script = file.read()

cur.execute(sql_script)
conn.commit()

cur.close()
conn.close()
