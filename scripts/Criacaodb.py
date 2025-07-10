import sqlite3
import pandas as pd

# Carregar CSV com low_memory=False para evitar warning
df = pd.read_csv('RDPR2501.csv', sep=',', encoding='utf-8', low_memory=False)
df.columns = df.columns.str.strip().str.upper()  # garantir colunas em maiúsculo e limpas

conn = sqlite3.connect('internacoes_datasus.db')
cursor = conn.cursor()

# Criar tabelas com os nomes das colunas iguais ao CSV (ou próximos), para facilitar inserção
cursor.executescript("""
CREATE TABLE IF NOT EXISTS PACIENTE (
    PACIENTE_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    CPF_AUT TEXT UNIQUE,
    NASC TEXT,
    SEXO TEXT,
    IDADE INTEGER,
    COD_IDADE TEXT,
    RACA_COR TEXT,
    ETNIA TEXT,
    NACIONAL TEXT,
    MUNIC_RES TEXT,
    CEP TEXT
);

CREATE TABLE IF NOT EXISTS HOSPITAL (
    HOSPITAL_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    CGC_HOSP TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS INTERNACAO (
    INTERNACAO_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    N_AIH TEXT UNIQUE,
    PACIENTE_ID INTEGER,
    HOSPITAL_ID INTEGER,
    DT_INTER TEXT,
    DT_SAIDA TEXT,
    DIAS_PERM INTEGER,
    MORTE INTEGER,
    CAR_INT TEXT,
    ANO_CMPT INTEGER,
    MES_CMPT INTEGER,
    FOREIGN KEY(PACIENTE_ID) REFERENCES PACIENTE(PACIENTE_ID),
    FOREIGN KEY(HOSPITAL_ID) REFERENCES HOSPITAL(HOSPITAL_ID)
);

CREATE TABLE IF NOT EXISTS DIAGNOSTICO (
    CODIGO TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS UTIS (
    UTIS_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    MARCA_UTI TEXT,
    UTI_MES_IN INTEGER,
    UTI_MES_AN INTEGER,
    UTI_MES_AL INTEGER,
    UTI_MES_TO INTEGER,
    UTI_INT_IN INTEGER,
    UTI_INT_AN INTEGER,
    UTI_INT_AL INTEGER,
    UTI_INT_TO INTEGER,
    VAL_UTI REAL,
    VAL_UCI REAL,
    MARCA_UCI TEXT
);

CREATE TABLE IF NOT EXISTS VALORES (
    VALORES_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    VAL_SH REAL,
    VAL_SP REAL,
    VAL_SADT REAL,
    VAL_RN REAL,
    VAL_ACOMP REAL,
    VAL_ORTP REAL,
    VAL_SANGUE REAL,
    VAL_SADTSR REAL,
    VAL_TRANSP REAL,
    VAL_OBSANG REAL,
    VAL_PED1AC REAL,
    VAL_TOT REAL,
    VAL_SH_FED REAL,
    VAL_SP_FED REAL,
    VAL_SH_GES REAL,
    VAL_SP_GES REAL,
    US_TOT REAL
);
""")

conn.commit()

# Inserir PACIENTES únicos
pacientes_unicos = df[['CPF_AUT', 'NASC', 'SEXO', 'IDADE', 'COD_IDADE', 'RACA_COR', 'ETNIA', 'NACIONAL', 'MUNIC_RES', 'CEP']].drop_duplicates()

for _, row in pacientes_unicos.iterrows():
    cursor.execute("""
        INSERT OR IGNORE INTO PACIENTE (
            CPF_AUT, NASC, SEXO, IDADE, COD_IDADE,
            RACA_COR, ETNIA, NACIONAL, MUNIC_RES, CEP
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(row['CPF_AUT']) if pd.notna(row['CPF_AUT']) else None,
        str(row['NASC']) if pd.notna(row['NASC']) else None,
        str(row['SEXO']) if pd.notna(row['SEXO']) else None,
        int(row['IDADE']) if pd.notna(row['IDADE']) else None,
        str(row['COD_IDADE']) if pd.notna(row['COD_IDADE']) else None,
        str(row['RACA_COR']) if pd.notna(row['RACA_COR']) else None,
        str(row['ETNIA']) if pd.notna(row['ETNIA']) else None,
        str(row['NACIONAL']) if pd.notna(row['NACIONAL']) else None,
        str(row['MUNIC_RES']) if pd.notna(row['MUNIC_RES']) else None,
        str(row['CEP']) if pd.notna(row['CEP']) else None
    ))

conn.commit()

# Inserir HOSPITAIS únicos
hospitais_unicos = df[['CGC_HOSP']].drop_duplicates()
for _, row in hospitais_unicos.iterrows():
    cursor.execute("""
        INSERT OR IGNORE INTO HOSPITAL (CGC_HOSP) VALUES (?)
    """, (str(row['CGC_HOSP']) if pd.notna(row['CGC_HOSP']) else None,))

conn.commit()

# Carregar pacientes e hospitais para pegar IDs
pacientes_df = pd.read_sql_query("SELECT PACIENTE_ID, CPF_AUT FROM PACIENTE", conn)
hospitais_df = pd.read_sql_query("SELECT HOSPITAL_ID, CGC_HOSP FROM HOSPITAL", conn)

# Juntar IDs no dataframe original
df = df.merge(pacientes_df, on='CPF_AUT', how='left')
df = df.merge(hospitais_df, on='CGC_HOSP', how='left')

# Inserir INTERNACOES
for _, row in df.iterrows():
    cursor.execute("""
        INSERT OR IGNORE INTO INTERNACAO (
            N_AIH, PACIENTE_ID, HOSPITAL_ID, DT_INTER, DT_SAIDA,
            DIAS_PERM, MORTE, CAR_INT, ANO_CMPT, MES_CMPT
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(row['N_AIH']) if pd.notna(row['N_AIH']) else None,
        row['PACIENTE_ID'] if pd.notna(row['PACIENTE_ID']) else None,
        row['HOSPITAL_ID'] if pd.notna(row['HOSPITAL_ID']) else None,
        str(row['DT_INTER']) if 'DT_INTER' in df.columns and pd.notna(row['DT_INTER']) else None,
        str(row['DT_SAIDA']) if 'DT_SAIDA' in df.columns and pd.notna(row['DT_SAIDA']) else None,
        int(row['DIAS_PERM']) if pd.notna(row['DIAS_PERM']) else None,
        int(row['MORTE']) if pd.notna(row['MORTE']) else None,
        str(row['CAR_INT']) if pd.notna(row['CAR_INT']) else None,
        int(row['ANO_CMPT']) if pd.notna(row['ANO_CMPT']) else None,
        int(row['MES_CMPT']) if pd.notna(row['MES_CMPT']) else None
    ))

conn.commit()

# Inserir DIAGNOSTICOS (exemplos)
cid_cols = ['DIAG_PRINC', 'DIAG_SECUN', 'CID_ASSO', 'CID_MORTE', 'CID_NOTIF']
cid_set = set()
for col in cid_cols:
    if col in df.columns:
        cid_set.update(df[col].dropna().unique())

for cid in cid_set:
    if isinstance(cid, str) and cid.strip():
        cursor.execute("INSERT OR IGNORE INTO DIAGNOSTICO (CODIGO) VALUES (?)", (cid.strip(),))

conn.commit()

# Inserir UTIS
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO UTIS (
            MARCA_UTI, UTI_MES_IN, UTI_MES_AN, UTI_MES_AL, UTI_MES_TO,
            UTI_INT_IN, UTI_INT_AN, UTI_INT_AL, UTI_INT_TO,
            VAL_UTI, VAL_UCI, MARCA_UCI
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        str(row['MARCA_UTI']) if pd.notna(row['MARCA_UTI']) else None,
        int(row['UTI_MES_IN']) if pd.notna(row['UTI_MES_IN']) else None,
        int(row['UTI_MES_AN']) if pd.notna(row['UTI_MES_AN']) else None,
        int(row['UTI_MES_AL']) if pd.notna(row['UTI_MES_AL']) else None,
        int(row['UTI_MES_TO']) if pd.notna(row['UTI_MES_TO']) else None,
        int(row['UTI_INT_IN']) if pd.notna(row['UTI_INT_IN']) else None,
        int(row['UTI_INT_AN']) if pd.notna(row['UTI_INT_AN']) else None,
        int(row['UTI_INT_AL']) if pd.notna(row['UTI_INT_AL']) else None,
        int(row['UTI_INT_TO']) if pd.notna(row['UTI_INT_TO']) else None,
        float(row['VAL_UTI']) if pd.notna(row['VAL_UTI']) else None,
        float(row['VAL_UCI']) if 'VAL_UCI' in df.columns and pd.notna(row['VAL_UCI']) else None,
        str(row['MARCA_UCI']) if 'MARCA_UCI' in df.columns and pd.notna(row['MARCA_UCI']) else None
    ))
conn.commit()

# Inserir VALORES financeiros
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO VALORES (
            VAL_SH, VAL_SP, VAL_SADT, VAL_RN, VAL_ACOMP, VAL_ORTP, VAL_SANGUE,
            VAL_SADTSR, VAL_TRANSP, VAL_OBSANG, VAL_PED1AC, VAL_TOT,
            VAL_SH_FED, VAL_SP_FED, VAL_SH_GES, VAL_SP_GES, US_TOT
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        float(row['VAL_SH']) if pd.notna(row['VAL_SH']) else None,
        float(row['VAL_SP']) if pd.notna(row['VAL_SP']) else None,
        float(row['VAL_SADT']) if pd.notna(row['VAL_SADT']) else None,
        float(row['VAL_RN']) if pd.notna(row['VAL_RN']) else None,
        float(row['VAL_ACOMP']) if pd.notna(row['VAL_ACOMP']) else None,
        float(row['VAL_ORTP']) if pd.notna(row['VAL_ORTP']) else None,
        float(row['VAL_SANGUE']) if pd.notna(row['VAL_SANGUE']) else None,
        float(row['VAL_SADTSR']) if pd.notna(row['VAL_SADTSR']) else None,
        float(row['VAL_TRANSP']) if pd.notna(row['VAL_TRANSP']) else None,
        float(row['VAL_OBSANG']) if pd.notna(row['VAL_OBSANG']) else None,
        float(row['VAL_PED1AC']) if pd.notna(row['VAL_PED1AC']) else None,
        float(row['VAL_TOT']) if pd.notna(row['VAL_TOT']) else None,
        float(row['VAL_SH_FED']) if 'VAL_SH_FED' in df.columns and pd.notna(row['VAL_SH_FED']) else None,
        float(row['VAL_SP_FED']) if 'VAL_SP_FED' in df.columns and pd.notna(row['VAL_SP_FED']) else None,
        float(row['VAL_SH_GES']) if 'VAL_SH_GES' in df.columns and pd.notna(row['VAL_SH_GES']) else None,
        float(row['VAL_SP_GES']) if 'VAL_SP_GES' in df.columns and pd.notna(row['VAL_SP_GES']) else None,
        float(row['US_TOT']) if pd.notna(row['US_TOT']) else None
    ))
conn.commit()

conn.close()

print("Importação completa!")
