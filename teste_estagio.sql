-- Criação do banco de dados e tabelas para o teste de estágio
CREATE DATABASE IF NOT EXISTS teste_estagio
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_0900_ai_ci;

USE teste_estagio;

-- Criação da tabela operadoras conforme especificações
DROP TABLE IF EXISTS operadoras;

CREATE TABLE operadoras (
  cnpj              CHAR(14)      NOT NULL,
  registro_ans      INT           NULL,
  razao_social      VARCHAR(255)  NULL,
  modalidade        VARCHAR(120)  NULL,
  uf                CHAR(2)       NULL,
  cadastro_duplicado BOOLEAN      NULL,
  PRIMARY KEY (cnpj),
  KEY idx_operadoras_registro_ans (registro_ans),
  KEY idx_operadoras_uf (uf),
  KEY idx_operadoras_razao_social (razao_social)
) ENGINE=InnoDB;

-- Criação da tabela despesas_consolidadas conforme especificações
DROP TABLE IF EXISTS despesas_consolidadas;

CREATE TABLE despesas_consolidadas (
  id                BIGINT        NOT NULL AUTO_INCREMENT,
  cnpj              CHAR(14)      NOT NULL,
  razao_social      VARCHAR(255)  NULL,
  ano               YEAR          NOT NULL,
  trimestre         TINYINT       NOT NULL,
  valor_despesas    DECIMAL(18,2) NULL,

  -- flags opcionais (caso existam no seu CSV 1.3)
  razao_social_suspeita BOOLEAN NULL,

  PRIMARY KEY (id),
  KEY idx_dc_cnpj (cnpj),
  KEY idx_dc_periodo (ano, trimestre),
  KEY idx_dc_razao (razao_social),

  CONSTRAINT fk_dc_operadoras
    FOREIGN KEY (cnpj) REFERENCES operadoras(cnpj)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
) ENGINE=InnoDB;

-- Criação da tabela despesas_agregadas conforme especificações
DROP TABLE IF EXISTS despesas_agregadas;

CREATE TABLE despesas_agregadas (
  id                       BIGINT        NOT NULL AUTO_INCREMENT,
  razao_social             VARCHAR(255)  NOT NULL,
  uf                       CHAR(2)       NOT NULL,
  total_despesas           DECIMAL(18,2) NULL,
  media_despesas_trimestre DECIMAL(18,2) NULL,
  desvio_padrao_despesas   DECIMAL(18,2) NULL,
  PRIMARY KEY (id),
  KEY idx_da_total (total_despesas),
  KEY idx_da_razao_uf (razao_social, uf),
  KEY idx_da_uf (uf)
) ENGINE=InnoDB;