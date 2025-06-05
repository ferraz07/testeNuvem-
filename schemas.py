from pydantic import BaseModel
from typing import Optional
from datetime import date

class UsuarioBase(BaseModel):
    nome: str
    email: str

class UsuarioCreate(UsuarioBase):
    senha: str

class UsuarioOut(UsuarioBase):
    id: int
    class Config:
        orm_mode = True

class MedicoCreate(BaseModel):
    usuario_id: int
    especialidade: str

class MedicoOut(BaseModel):
    id: int
    especialidade: str
    usuario_id: int
    class Config:
        orm_mode = True
