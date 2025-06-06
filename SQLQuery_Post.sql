-- Apagar tabelas se já existirem (na ordem correta de dependência)
DROP TABLE IF EXISTS Mensagem;
DROP TABLE IF EXISTS Conversa;
DROP TABLE IF EXISTS Agenda;
DROP TABLE IF EXISTS Medico;
DROP TABLE IF EXISTS Paciente;
DROP TABLE IF EXISTS Usuario;

-- Tabela de Usuários (Base)
CREATE TABLE Usuario (
    ID SERIAL PRIMARY KEY,
    Email VARCHAR(255) UNIQUE NOT NULL,
    Senha VARCHAR(255) NOT NULL
);

-- Tabela de Médicos
CREATE TABLE Medico (
    UsuarioID INT PRIMARY KEY,
    Nome VARCHAR(150) NOT NULL,
    Especialidade VARCHAR(100),
    CRM VARCHAR(20) UNIQUE NOT NULL,
    Logradouro VARCHAR(255),
    Numero VARCHAR(20),
    Complemento VARCHAR(100),
    Bairro VARCHAR(100),
    Cidade VARCHAR(100),
    Estado CHAR(2),
    CEP VARCHAR(9),
    CONSTRAINT FK_Medico_Usuario FOREIGN KEY (UsuarioID) REFERENCES Usuario(ID) ON DELETE CASCADE
);

-- Tabela de Pacientes
CREATE TABLE Paciente (
    UsuarioID INT PRIMARY KEY,
    Nome VARCHAR(150) NOT NULL,
    DataNascimento DATE,
    CPF VARCHAR(11) UNIQUE NOT NULL,
    CONSTRAINT FK_Paciente_Usuario FOREIGN KEY (UsuarioID) REFERENCES Usuario(ID) ON DELETE CASCADE
);

-- Tabela de Agendamentos
CREATE TABLE Agenda (
    ID SERIAL PRIMARY KEY,
    MedicoID INT NOT NULL,
    PacienteID INT NOT NULL,
    DataInicio TIMESTAMP NOT NULL,
    DataFim TIMESTAMP NOT NULL,
    Status VARCHAR(50) NOT NULL DEFAULT 'Agendada',
    CONSTRAINT FK_Agenda_Medico FOREIGN KEY (MedicoID) REFERENCES Medico(UsuarioID),
    CONSTRAINT FK_Agenda_Paciente FOREIGN KEY (PacienteID) REFERENCES Paciente(UsuarioID)
);

-- Tabela para identificar uma conversa entre um médico e um paciente
CREATE TABLE Conversa (
    ID SERIAL PRIMARY KEY,
    MedicoUsuarioID INT NOT NULL,
    PacienteUsuarioID INT NOT NULL,
    CONSTRAINT FK_Conversa_Medico FOREIGN KEY (MedicoUsuarioID) REFERENCES Medico(UsuarioID),
    CONSTRAINT FK_Conversa_Paciente FOREIGN KEY (PacienteUsuarioID) REFERENCES Paciente(UsuarioID),
    CONSTRAINT UQ_Conversa_Medico_Paciente UNIQUE (MedicoUsuarioID, PacienteUsuarioID)
);

-- Tabela para armazenar cada mensagem de uma conversa
CREATE TABLE Mensagem (
    ID BIGSERIAL PRIMARY KEY,
    ConversaID INT NOT NULL,
    RemetenteUsuarioID INT NOT NULL,
    Texto TEXT NOT NULL,
    DataEnvio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Lido BOOLEAN NOT NULL DEFAULT FALSE,
    CONSTRAINT FK_Mensagem_Conversa FOREIGN KEY (ConversaID) REFERENCES Conversa(ID),
    CONSTRAINT FK_Mensagem_Remetente FOREIGN KEY (RemetenteUsuarioID) REFERENCES Usuario(ID)
);
