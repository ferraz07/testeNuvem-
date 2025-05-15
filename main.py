from fastapi import FastAPI, Request
import os
import psycopg2

app = FastAPI()

@app.post("/clientes")
async def add_cliente(request: Request):
    dados = await request.json()
    nome = dados.get("nome")
    idade = dados.get("idade")

    conn = psycopg2.connect(
        host=os.environ["PGHOST"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        database=os.environ["PGDATABASE"],
        port=os.environ.get("PGPORT", 5432)
    )
    cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome, idade) VALUES (%s, %s)", (nome, idade))
    conn.commit()
    cur.close()
    conn.close()

    return {"status": "ok"}
