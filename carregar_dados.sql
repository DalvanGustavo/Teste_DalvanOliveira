USE teste_estagio;

DROP TABLE IF EXISTS stg_operadoras;
CREATE TABLE stg_operadoras (
  registro_ans       VARCHAR(50),
  cnpj               VARCHAR(50),
  razao_social       VARCHAR(255),
  modalidade         VARCHAR(120),
  uf                 VARCHAR(10),
  cadastro_duplicado VARCHAR(10)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS stg_despesas_consolidadas;
CREATE TABLE stg_despesas_consolidadas (
  cnpj                  VARCHAR(50),
  razao_social           VARCHAR(255),
  ano                   VARCHAR(10),
  trimestre              VARCHAR(10),
  valor_despesas         VARCHAR(50),
  razao_social_suspeita  VARCHAR(10)
) ENGINE=InnoDB;

DROP TABLE IF EXISTS stg_despesas_agregadas;
CREATE TABLE stg_despesas_agregadas (
  razao_social              VARCHAR(255),
  uf                        VARCHAR(10),
  total_despesas            VARCHAR(50),
  media_despesas_trimestre  VARCHAR(50),
  desvio_padrao_despesas    VARCHAR(50)
) ENGINE=InnoDB;

-- ==========================

TRUNCATE TABLE stg_operadoras;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/Relatorio_cadop.csv'
INTO TABLE stg_operadoras
CHARACTER SET latin1
FIELDS TERMINATED BY ';'
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(@registro_operadora, @cnpj, @razao_social, @nome_fantasia, @modalidade,
 @logradouro, @numero, @complemento, @bairro, @cidade, @uf, @cep,
 @ddd, @telefone, @fax, @email, @representante, @cargo_rep,
 @data_registro, @situacao, @data_situacao, @data_cancelamento)
SET
  registro_ans = @registro_operadora,
  cnpj = @cnpj,
  razao_social = @razao_social,
  modalidade = @modalidade,
  uf = @uf,
  cadastro_duplicado = NULL;

-- ======================

TRUNCATE TABLE stg_despesas_consolidadas;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/consolidado_despesas.csv'
INTO TABLE stg_despesas_consolidadas
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(cnpj, razao_social, ano, trimestre, valor_despesas, razao_social_suspeita);

-- =======================

TRUNCATE TABLE stg_despesas_agregadas;

LOAD DATA INFILE 'C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/despesas_agregadas.csv'
INTO TABLE stg_despesas_agregadas
CHARACTER SET utf8mb4
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(razao_social, uf, total_despesas, media_despesas_trimestre, desvio_padrao_despesas);


-- ===========================


INSERT INTO operadoras (cnpj, registro_ans, razao_social, modalidade, uf, cadastro_duplicado)
SELECT
  cnpj_limpo,
  registro_int,
  NULLIF(TRIM(razao_social), ''),
  NULLIF(TRIM(modalidade), ''),
  uf_limpa,
  NULL
FROM (
  SELECT
    REGEXP_REPLACE(TRIM(cnpj), '[^0-9]', '') AS cnpj_limpo,
    CASE
      WHEN TRIM(registro_ans) REGEXP '^[0-9]+$' THEN CAST(TRIM(registro_ans) AS UNSIGNED)
      ELSE NULL
    END AS registro_int,
    razao_social,
    modalidade,
    CASE
      WHEN UPPER(TRIM(uf)) REGEXP '^[A-Z]{2}$' THEN UPPER(TRIM(uf))
      ELSE NULL
    END AS uf_limpa
  FROM stg_operadoras
) t
WHERE LENGTH(cnpj_limpo) = 14
ON DUPLICATE KEY UPDATE
  registro_ans = VALUES(registro_ans),
  razao_social = VALUES(razao_social),
  modalidade = VALUES(modalidade),
  uf = VALUES(uf);
  
-- ==========

INSERT INTO despesas_consolidadas (cnpj, razao_social, ano, trimestre, valor_despesas, razao_social_suspeita)
SELECT
  cnpj_limpo,
  NULLIF(TRIM(razao_social), ''),
  CAST(ano_int AS YEAR),
  trimestre_int,
  valor_dec,
  suspeita_bool
FROM (
  SELECT
    REGEXP_REPLACE(TRIM(cnpj), '[^0-9]', '') AS cnpj_limpo,
    razao_social,
    CASE WHEN TRIM(ano) REGEXP '^[0-9]{4}$' THEN CAST(TRIM(ano) AS UNSIGNED) END AS ano_int,
    CASE WHEN TRIM(trimestre) REGEXP '^[1-4]$' THEN CAST(TRIM(trimestre) AS UNSIGNED) END AS trimestre_int,
    CASE
      WHEN TRIM(valor_despesas) REGEXP '^[0-9.,]+$'
        THEN CAST(REPLACE(REPLACE(TRIM(valor_despesas), '.', ''), ',', '.') AS DECIMAL(18,2))
      ELSE NULL
    END AS valor_dec,
    (LOWER(TRIM(razao_social_suspeita)) IN ('true','1','t','sim','s')) AS suspeita_bool
  FROM stg_despesas_consolidadas
) t
WHERE LENGTH(cnpj_limpo) = 14
  AND ano_int IS NOT NULL
  AND trimestre_int IS NOT NULL
  AND valor_dec IS NOT NULL;


-- =====================

INSERT INTO despesas_agregadas (razao_social, uf, total_despesas, media_despesas_trimestre, desvio_padrao_despesas)
SELECT
  TRIM(razao_social),
  UPPER(TRIM(uf)),
  total_dec,
  media_dec,
  std_dec
FROM (
  SELECT
    razao_social,
    uf,

    CASE
      WHEN TRIM(total_despesas) REGEXP '^[0-9.,]+$' THEN
        CAST(
          CASE
            WHEN INSTR(total_despesas, ',') > 0
              THEN REPLACE(REPLACE(TRIM(total_despesas), '.', ''), ',', '.')
            ELSE TRIM(total_despesas)
          END
        AS DECIMAL(30,2))
      ELSE NULL
    END AS total_dec,

    CASE
      WHEN TRIM(media_despesas_trimestre) REGEXP '^[0-9.,]+$' THEN
        CAST(
          CASE
            WHEN INSTR(media_despesas_trimestre, ',') > 0
              THEN REPLACE(REPLACE(TRIM(media_despesas_trimestre), '.', ''), ',', '.')
            ELSE TRIM(media_despesas_trimestre)
          END
        AS DECIMAL(30,2))
      ELSE NULL
    END AS media_dec,

    CASE
      WHEN TRIM(desvio_padrao_despesas) REGEXP '^[0-9.,]+$' THEN
        CAST(
          CASE
            WHEN INSTR(desvio_padrao_despesas, ',') > 0
              THEN REPLACE(REPLACE(TRIM(desvio_padrao_despesas), '.', ''), ',', '.')
            ELSE TRIM(desvio_padrao_despesas)
          END
        AS DECIMAL(30,2))
      ELSE NULL
    END AS std_dec

  FROM stg_despesas_agregadas
) t
WHERE TRIM(razao_social) <> ''
  AND UPPER(TRIM(uf)) REGEXP '^[A-Z]{2}$';
  
  -- Query 1
  
  WITH periodos AS (
  SELECT
    MIN(ano * 10 + trimestre) AS p_ini,
    MAX(ano * 10 + trimestre) AS p_fim
  FROM teste_estagio.despesas_consolidadas
),
base AS (
  SELECT
    d.cnpj,
    SUM(CASE WHEN (d.ano * 10 + d.trimestre) = (SELECT p_ini FROM periodos) THEN d.valor_despesas END) AS v_ini,
    SUM(CASE WHEN (d.ano * 10 + d.trimestre) = (SELECT p_fim FROM periodos) THEN d.valor_despesas END) AS v_fim
  FROM teste_estagio.despesas_consolidadas d
  GROUP BY d.cnpj
),
crescimento AS (
  SELECT
    b.cnpj,
    o.razao_social,
    b.v_ini,
    b.v_fim,
    ((b.v_fim - b.v_ini) / b.v_ini) * 100 AS crescimento_percentual
  FROM base b
  JOIN teste_estagio.operadoras o ON o.cnpj = b.cnpj
  WHERE b.v_ini IS NOT NULL
    AND b.v_fim IS NOT NULL
    AND b.v_ini > 0
)
SELECT *
FROM crescimento
ORDER BY crescimento_percentual DESC
LIMIT 5;

-- Query 2

SELECT
  o.uf,
  SUM(d.valor_despesas) AS total_despesas_uf,
  COUNT(DISTINCT d.cnpj) AS qtd_operadoras_com_despesa,
  (SUM(d.valor_despesas) / NULLIF(COUNT(DISTINCT d.cnpj), 0)) AS media_por_operadora_uf
FROM teste_estagio.despesas_consolidadas d
JOIN teste_estagio.operadoras o ON o.cnpj = d.cnpj
WHERE o.uf IS NOT NULL AND o.uf <> ''
GROUP BY o.uf
ORDER BY total_despesas_uf DESC
LIMIT 5;

-- Query 3

WITH ultimos AS (
  SELECT ano, trimestre
  FROM (
    SELECT DISTINCT ano, trimestre
    FROM teste_estagio.despesas_consolidadas
    ORDER BY ano DESC, trimestre DESC
    LIMIT 3
  ) x
),
valores AS (
  SELECT d.cnpj, d.ano, d.trimestre, SUM(d.valor_despesas) AS valor_trim
  FROM teste_estagio.despesas_consolidadas d
  JOIN ultimos u ON u.ano=d.ano AND u.trimestre=d.trimestre
  GROUP BY d.cnpj, d.ano, d.trimestre
),
media_trim AS (
  SELECT ano, trimestre, AVG(valor_trim) AS media_geral_trim
  FROM valores
  GROUP BY ano, trimestre
),
acima AS (
  SELECT v.cnpj, v.ano, v.trimestre, (v.valor_trim > m.media_geral_trim) AS acima_media
  FROM valores v
  JOIN media_trim m ON m.ano=v.ano AND m.trimestre=v.trimestre
),
contagem AS (
  SELECT cnpj, SUM(acima_media) AS trimestres_acima
  FROM acima
  GROUP BY cnpj
)
SELECT
  COUNT(*) AS qtd_operadoras_acima_media_em_2_ou_mais_trimestres
FROM contagem
WHERE trimestres_acima >= 2;