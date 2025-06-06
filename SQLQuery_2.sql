-- Apagar tabelas se já existirem (na ordem correta de dependência)
DROP TABLE IF EXISTS Mensagem;
DROP TABLE IF EXISTS Conversa;
DROP TABLE IF EXISTS Agenda;
DROP TABLE IF EXISTS Medico;
DROP TABLE IF EXISTS Paciente;
DROP TABLE IF EXISTS Usuario;
GO

-- Tabela de Usuários (Base)
CREATE TABLE Usuario (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    Email NVARCHAR(255) UNIQUE NOT NULL,
    Senha NVARCHAR(255) NOT NULL
);
GO

-- Tabela de Médicos
CREATE TABLE Medico (
    UsuarioID INT PRIMARY KEY,
    Nome NVARCHAR(150) NOT NULL,
    Especialidade NVARCHAR(100),
    CRM VARCHAR(20) UNIQUE NOT NULL,
    Logradouro NVARCHAR(255),
    Numero VARCHAR(20),
    Complemento NVARCHAR(100),
    Bairro NVARCHAR(100),
    Cidade NVARCHAR(100),
    Estado CHAR(2),
    CEP VARCHAR(9),
    CONSTRAINT FK_Medico_Usuario FOREIGN KEY (UsuarioID) REFERENCES Usuario(ID) ON DELETE CASCADE
);
GO

-- Tabela de Pacientes
CREATE TABLE Paciente (
    UsuarioID INT PRIMARY KEY,
    Nome NVARCHAR(150) NOT NULL,
    DataNascimento DATE,
    CPF VARCHAR(11) UNIQUE NOT NULL,
    CONSTRAINT FK_Paciente_Usuario FOREIGN KEY (UsuarioID) REFERENCES Usuario(ID) ON DELETE CASCADE
);
GO

-- Tabela de Agendamentos
CREATE TABLE Agenda (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    MedicoID INT NOT NULL,
    PacienteID INT NOT NULL,
    DataInicio DATETIME2 NOT NULL,
    DataFim DATETIME2 NOT NULL,
    Status NVARCHAR(50) NOT NULL DEFAULT 'Agendada',
    CONSTRAINT FK_Agenda_Medico FOREIGN KEY (MedicoID) REFERENCES Medico(UsuarioID),
    CONSTRAINT FK_Agenda_Paciente FOREIGN KEY (PacienteID) REFERENCES Paciente(UsuarioID)
);
GO

-- =======================================================
-- NOVAS TABELAS PARA O CHAT
-- =======================================================

-- Tabela para identificar uma conversa entre um médico e um paciente
CREATE TABLE Conversa (
    ID INT IDENTITY(1,1) PRIMARY KEY,
    MedicoUsuarioID INT NOT NULL,
    PacienteUsuarioID INT NOT NULL,
    CONSTRAINT FK_Conversa_Medico FOREIGN KEY (MedicoUsuarioID) REFERENCES Medico(UsuarioID),
    CONSTRAINT FK_Conversa_Paciente FOREIGN KEY (PacienteUsuarioID) REFERENCES Paciente(UsuarioID),
    CONSTRAINT UQ_Conversa_Medico_Paciente UNIQUE (MedicoUsuarioID, PacienteUsuarioID) -- Garante que só exista uma conversa por par médico-paciente
);
GO

-- Tabela para armazenar cada mensagem de uma conversa
CREATE TABLE Mensagem (
    ID BIGINT IDENTITY(1,1) PRIMARY KEY,
    ConversaID INT NOT NULL,
    RemetenteUsuarioID INT NOT NULL, -- ID do usuário (médico ou paciente) que enviou
    Texto NVARCHAR(MAX) NOT NULL, -- O conteúdo da mensagem
    DataEnvio DATETIME2 NOT NULL DEFAULT GETDATE(), -- Data e hora do envio
    Lido BIT NOT NULL DEFAULT 0, -- 0 para não lida, 1 para lida
    CONSTRAINT FK_Mensagem_Conversa FOREIGN KEY (ConversaID) REFERENCES Conversa(ID),
    CONSTRAINT FK_Mensagem_Remetente FOREIGN KEY (RemetenteUsuarioID) REFERENCES Usuario(ID)
);
GO

PRINT 'Tabelas (incluindo Chat) criadas com sucesso!';
