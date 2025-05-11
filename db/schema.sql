-- Enable UUID generation
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table for Contacts
CREATE TABLE IF NOT EXISTS contatos (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255),
    codigo VARCHAR(50),
    fantasia VARCHAR(255),
    tipo_pessoa CHAR(1),
    cpf_cnpj VARCHAR(20),
    inscricao_estadual VARCHAR(30),
    rg VARCHAR(20),
    telefone VARCHAR(20),
    celular VARCHAR(20),
    email VARCHAR(255),
    id_endereco INTEGER NULL -- Foreign key will be added after endereco table is created
);

-- Table for Addresses
CREATE TABLE IF NOT EXISTS enderecos (
    id SERIAL PRIMARY KEY, -- Local primary key
    endereco VARCHAR(255),
    numero VARCHAR(50),
    complemento VARCHAR(255),
    bairro VARCHAR(255),
    municipio VARCHAR(255),
    cep VARCHAR(10),
    uf VARCHAR(2),
    pais VARCHAR(100)
);

-- Add foreign key to contatos table
ALTER TABLE contatos
ADD CONSTRAINT fk_endereco
FOREIGN KEY (id_endereco)
REFERENCES enderecos (id);

-- Table for OS Categories
CREATE TABLE IF NOT EXISTS categorias_os (
    id INTEGER PRIMARY KEY,
    descricao VARCHAR(255)
);

-- Table for Payment Methods
CREATE TABLE IF NOT EXISTS formas_pagamento (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(255)
);

-- Table for Service Orders
CREATE TABLE IF NOT EXISTS ordens_servico (
    id INTEGER PRIMARY KEY,
    numero_ordem_servico VARCHAR(50),
    situacao VARCHAR(10), -- Storing the numeric code
    data_emissao DATE,
    data_prevista TIMESTAMP NULL,
    data_conclusao DATE NULL, -- Will be NULL for non-finalized orders
    total_servicos NUMERIC(10, 2),
    total_ordem_servico NUMERIC(10, 2),
    total_pecas NUMERIC(10, 2),
    equipamento VARCHAR(255),
    equipamento_serie VARCHAR(255),
    descricao_problema TEXT,
    observacoes TEXT,
    observacoes_internas TEXT,
    orcar CHAR(1),
    orcado CHAR(1),
    alq_comissao NUMERIC(5, 2),
    vlr_comissao NUMERIC(10, 2),
    desconto NUMERIC(10, 2),
    id_lista_preco INTEGER,
    tecnico VARCHAR(255),
    id_contato INTEGER NULL, -- Foreign key
    id_vendedor INTEGER NULL, -- Foreign key
    id_categoria_os INTEGER NULL, -- Foreign key
    id_forma_pagamento INTEGER NULL, -- Foreign key
    id_conta_contabil INTEGER NULL,
    data_extracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    linha_dispositivo VARCHAR(50), -- New custom field
    tipo_servico VARCHAR(100), -- New custom field
    origem_cliente VARCHAR(50), -- New custom field (from markers)

    CONSTRAINT fk_contato
        FOREIGN KEY (id_contato)
        REFERENCES contatos (id),
    CONSTRAINT fk_vendedor
        FOREIGN KEY (id_vendedor)
        REFERENCES contatos (id), -- Assuming vendedor is also a contact
    CONSTRAINT fk_categoria_os
        FOREIGN KEY (id_categoria_os)
        REFERENCES categorias_os (id),
    CONSTRAINT fk_forma_pagamento
        FOREIGN KEY (id_forma_pagamento)
        REFERENCES formas_pagamento (id)
);

-- Future Table for Markers
CREATE TABLE IF NOT EXISTS marcadores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(255) UNIQUE
);

-- Future Junction Table for OS Markers
CREATE TABLE IF NOT EXISTS ordem_servico_marcadores (
    id_ordem_servico INTEGER,
    id_marcador INTEGER,
    PRIMARY KEY (id_ordem_servico, id_marcador),
    CONSTRAINT fk_os_marcadores_os
        FOREIGN KEY (id_ordem_servico)
        REFERENCES ordens_servico (id),
    CONSTRAINT fk_os_marcadores_marcadores
        FOREIGN KEY (id_marcador)
        REFERENCES marcadores (id)
);
