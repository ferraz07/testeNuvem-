from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database import get_connection
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI()

# Configuração do CORS necesária
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==== MODELS ====

class Usuario(BaseModel):
    email: str
    senha: str

class Paciente(BaseModel):
    usuario_id: int
    nome: str
    data_nascimento: str
    cpf: str

class Medico(BaseModel):
    usuario_id: int
    nome: str
    especialidade: str
    crm: str

class Agenda(BaseModel):
    medico_id: int
    paciente_id: int
    data_inicio: str
    data_fim: str
    status: str = "Agendada"

class Conversa(BaseModel):
    medico_usuario_id: int
    paciente_usuario_id: int

class Mensagem(BaseModel):
    conversa_id: int
    remetente_usuario_id: int
    texto: str
    
class PacienteComUsuario(BaseModel):
    email: str
    senha: str
    nome: str
    cpf: str
    data_nascimento: str  # formato 'YYYY-MM-DD'

# ==== USUARIO ====

@app.post("/pacientes-com-usuario")
def cadastrar_paciente_com_usuario(dados: PacienteComUsuario):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # 1. Inserir na tabela Usuario
        cur.execute(
            "INSERT INTO Usuario (Email, Senha) VALUES (%s, %s) RETURNING ID",
            (dados.email, dados.senha)
        )
        usuario_id = cur.fetchone()[0]

        # 2. Inserir na tabela Paciente com o ID retornado
        cur.execute(
            "INSERT INTO Paciente (UsuarioID, Nome, CPF, DataNascimento) VALUES (%s, %s, %s, %s)",
            (usuario_id, dados.nome, dados.cpf, dados.data_nascimento)
        )

        conn.commit()
        return {"mensagem": "Paciente cadastrado com sucesso!", "usuario_id": usuario_id}

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        cur.close()
        conn.close()

@app.post("/usuarios")
def criar_usuario(usuario: Usuario):
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO Usuario (Email, Senha) VALUES (%s, %s) RETURNING ID", (usuario.email, usuario.senha))
        usuario_id = cur.fetchone()[0]
        conn.commit()
        return {"usuario_id": usuario_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/usuarios")
def listar_usuarios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Usuario")
    data = cur.fetchall()
    conn.close()
    return data

@app.delete("/usuarios/{usuario_id}")
def deletar_usuario(usuario_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM Usuario WHERE ID = %s", (usuario_id,))
    conn.commit()
    conn.close()
    return {"msg": "Usuário deletado"}

# ==== PACIENTE ====

@app.post("/pacientes")
def criar_paciente(paciente: Paciente):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Paciente (UsuarioID, Nome, DataNascimento, CPF) VALUES (%s, %s, %s, %s)",
        (paciente.usuario_id, paciente.nome, paciente.data_nascimento, paciente.cpf)
    )
    conn.commit()
    conn.close()
    return {"msg": "Paciente criado"}

@app.get("/pacientes")
def listar_pacientes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Paciente")
    data = cur.fetchall()
    conn.close()
    return data

# ==== MEDICO ====

@app.post("/medicos")
def criar_medico(medico: Medico):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Medico (UsuarioID, Nome, Especialidade, CRM) VALUES (%s, %s, %s, %s)",
        (medico.usuario_id, medico.nome, medico.especialidade, medico.crm)
    )
    conn.commit()
    conn.close()
    return {"msg": "Médico criado"}

@app.get("/medicos")
def listar_medicos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Medico")
    data = cur.fetchall()
    conn.close()
    return data

# ==== AGENDA ====

@app.post("/agendas")
def criar_agendamento(agenda: Agenda):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Agenda (MedicoID, PacienteID, DataInicio, DataFim, Status) VALUES (%s, %s, %s, %s, %s)",
        (agenda.medico_id, agenda.paciente_id, agenda.data_inicio, agenda.data_fim, agenda.status)
    )
    conn.commit()
    conn.close()
    return {"msg": "Agendamento criado"}

@app.get("/agendas")
def listar_agendamentos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Agenda")
    data = cur.fetchall()
    conn.close()
    return data

# ==== CONVERSA ====

@app.post("/conversas")
def criar_conversa(conversa: Conversa):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Conversa (MedicoUsuarioID, PacienteUsuarioID) VALUES (%s, %s)",
        (conversa.medico_usuario_id, conversa.paciente_usuario_id)
    )
    conn.commit()
    conn.close()
    return {"msg": "Conversa criada"}

@app.get("/conversas")
def listar_conversas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Conversa")
    data = cur.fetchall()
    conn.close()
    return data

# ==== MENSAGEM ====

@app.post("/mensagens")
def enviar_mensagem(msg: Mensagem):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Mensagem (ConversaID, RemetenteUsuarioID, Texto) VALUES (%s, %s, %s)",
        (msg.conversa_id, msg.remetente_usuario_id, msg.texto)
    )
    conn.commit()
    conn.close()
    return {"msg": "Mensagem enviada"}

@app.get("/mensagens")
def listar_mensagens():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM Mensagem")
    data = cur.fetchall()
    conn.close()
    return data
