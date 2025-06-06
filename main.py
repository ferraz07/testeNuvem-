from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

app = FastAPI()

# Permitir acesso do front-end (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def conectar():
    return psycopg2.connect(os.environ["DATABASE_URL"])

@app.get("/")
def root():
    return {"message": "API ativa"}

@app.post("/clientes")
async def add_cliente(request: Request):
    dados = await request.json()
    nome = dados.get("nome")
    idade = dados.get("idade")
    plano = dados.get("plano")
    email = dados.get("email")
    nascimento = dados.get("nascimento")  # Novo campo
    senha = dados.get("senha")  # Novo campo

    db_url = os.environ["DATABASE_URL"]
    conn = psycopg2.connect(db_url)

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO clientes (nome, idade, plano, email, nascimento, senha)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nome, idade, plano, email, nascimento, senha))
    conn.commit()
    cur.close()
    conn.close()

    return {"status": "ok", "dados": dados}


@app.get("/clientes")
def listar_clientes():
    conn = conectar()
    cur = conn.cursor()
    cur.execute("SELECT * FROM clientes")
    resultado = cur.fetchall()
    cur.close()
    conn.close()
    return {"clientes": resultado}

@app.delete("/clientes/{id}")
def remover_cliente(id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute("DELETE FROM clientes WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"status": "removido"}
