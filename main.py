import os
import jwt
import datetime

from fastapi import FastAPI, HTTPException, Request, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os
from db_init import router as db_router  # importa seu novo router
from authlib.integrations.starlette_client import OAuth, OAuthError

from dotenv import load_dotenv
load_dotenv()

# Consts
GOOGLE_CLIENT_ID      = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET  = os.environ["GOOGLE_CLIENT_SECRET"]
GOOGLE_REDIRECT_URI   = os.environ["GOOGLE_REDIRECT_URI"]

JWT_SECRET_KEY        = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM         = os.environ.get("JWT_ALGORITHM", "HS256")
JWT_EXPIRES_IN_SECONDS = int(os.environ.get("JWT_EXPIRES_IN_SECONDS", "604800"))



app = FastAPI()

app.include_router(db_router)  # registra as rotas
#app = FastAPI()
#router = APIRouter()

# Permitir acesso do front-end (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4321"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    access_token_url="https://oauth2.googleapis.com/token",
    authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
    api_base_url="https://www.googleapis.com/oauth2/v2/",
    userinfo_endpoint="https://openidconnect.googleapis.com/v1/userinfo",
    client_kwargs={
        "scope": "openid email profile",
    },
)

def generate_jwt(user_id: int, email: str) -> str:
    """
    Gera um JWT com payload:
      {
        "sub": <user_id>,
        "email": <email>,
        "exp": <timestamp_em_segundos>
      }
    """
    exp = datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXPIRES_IN_SECONDS)
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": exp.timestamp()
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token

def decode_jwt(token: str) -> dict:
    """
    Decodifica/verifica o JWT.
    Retorna o payload se válido; levanta exceção se inválido.
    """
    payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    return payload

@app.get("/auth/google/url")
async def get_google_oauth_url():
    """
    Retorna JSON com a URL para redirecionar ao Google Consent Screen.
    Frontend faz FETCH → recebe { "url": "https://accounts.google.com/..." } 
    e então faz window.location.href = url
    """
    google = oauth.create_client("google")
    # Cria a URL de autorização; state/session é gerenciado internamente pelo Authlib
    redirect_uri = GOOGLE_REDIRECT_URI
    authorization_url, state = google.create_authorization_url(redirect_uri)
    return {"url": authorization_url}


@app.get("/auth/google/callback")
async def auth_google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Callback que o Google chama após o usuário concordar. 
    Query params: code=<código> e state=<state gerado>.
    1) Troca code → token
    2) parse_id_token → userinfo
    3) Upsert no banco
    4) Gera JWT próprio
    5) Redireciona para front-end: https://app.../oauth/callback?token=<seu_jwt>
    """
    try:
        token = await oauth.google.authorize_access_token(request)
        userinfo = await oauth.google.parse_id_token(request, token)
    except OAuthError as e:
        return JSONResponse({"error": "Falha no OAuth callback", "details": str(e)}, status_code=400)

    # userinfo exemplo:
    # {
    #   "sub": "117690082921964879865", 
    #   "name": "Alice Example", 
    #   "email": "alice@example.com",
    #   "picture": "https://lh3.googleusercontent.com/..",
    #   "email_verified": True, ...
    # }
    google_id = userinfo["sub"]
    email     = userinfo["email"]
    name      = userinfo["name"]
    picture   = userinfo.get("picture")

    # 3) Upsert no banco
    try:
        user = db.query(User).filter(User.google_id == google_id).one()
        # Se quiser, atualize e-mail, nome, picture caso tenha mudado
        updated = False
        if user.email != email:
            user.email = email
            updated = True
        if user.name != name:
            user.name = name
            updated = True
        if user.picture_url != picture:
            user.picture_url = picture
            updated = True
        if updated:
            db.commit()
    except NoResultFound:
        user = User(google_id=google_id, email=email, name=name, picture_url=picture)
        db.add(user)
        db.commit()
        db.refresh(user)

    # 4) Gera JWT
    jwt_token = generate_jwt(user_id=user.id, email=user.email)

    # 5) Redireciona para o frontend com ?token=<jwt>
    #  Ex.: https://app.seudominio.com/oauth/callback?token=eyJhbGciOi...
    dest = f"{FRONTEND_BASE_URL}/oauth/callback?token={jwt_token}"
    return RedirectResponse(dest)


@app.get("/profile")
async def profile(current_user: User = Depends(get_current_user)): # exemplo de adicionar o middleware
    """
    Exemplo de rota protegida. 
    Frontend faz: GET /profile com header Authorization: Bearer <jwt>
    e recebe JSON com dados do usuário.
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "picture_url": current_user.picture_url
    }

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
    data = dados.get("data")  # Novo campo
    senha = dados.get("senha")  # Novo campo

    db_url = os.environ["DATABASE_URL"]
    conn = psycopg2.connect(db_url)

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO clientes (nome, idade, plano, email, data, senha)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nome, idade, plano, email, data, senha))
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
