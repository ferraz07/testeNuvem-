import os
import uvicorn
from fastapi import FastAPI, Request
import psycopg2

app = FastAPI()

@app.get("/")
def root():
    return {"message": "API clientes ativa!"}

@app.post("/clientes")
async def add_cliente(request: Request):
    dados = await request.json()
    nome = dados.get("nome")
    idade = dados.get("idade")
    plano = dados.get("plano")
    email = dados.get("email")
    data = dados.get("data")
    status = dados.get("status")

    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clientes (nome, idade, plano, email, data, status) VALUES (%s, %s, %s, %s, %s, %s)",
        (nome, idade, plano, email, data, status),
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok", "dados": dados}

@app.delete("/clientes/{id}")
def delete_cliente(id: int):
    conn = psycopg2.connect(os.environ["DATABASE_URL"])
    cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "ok", "message": f"Cliente {id} removido"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
