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

    print("PORT:", os.environ.get("PORT"))

    # Pega a URL do Railway
    db_url = os.environ["DATABASE_URL"]
    # Conecta usando a URL diretamente
    conn = psycopg2.connect(db_url)

    cur = conn.cursor()
    cur.execute("INSERT INTO clientes (nome, idade) VALUES (%s, %s)", (nome, idade))
    conn.commit()
    cur.close()
    conn.close()

    return {"status": "ok", "dados": dados}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
