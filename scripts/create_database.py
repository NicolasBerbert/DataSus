import sqlite3
import pandas as pd
import os
from datetime import datetime

def create_database_structure():
    """
    Cria a estrutura do banco de dados SQLite para armazenar dados de internações hospitalares
    """
    
    # Caminho para o banco de dados
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'internacoes_datasus.db')
    
    # Conecta ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop table if exists (para desenvolvimento)
    cursor.execute('DROP TABLE IF EXISTS internacoes')
    
    # Cria a tabela principal de internações
    cursor.execute('''
        CREATE TABLE internacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            
            -- Identificação e localização
            uf_zi TEXT,
            ano_cmpt INTEGER,
            mes_cmpt INTEGER,
            espec TEXT,
            cgc_hosp TEXT,
            n_aih TEXT,
            ident INTEGER,
            cep TEXT,
            munic_res TEXT,
            munic_mov TEXT,
            
            -- Dados demográficos
            nasc TEXT,
            sexo INTEGER,
            cod_idade INTEGER,
            idade REAL,
            raca_cor TEXT,
            nacional TEXT,
            
            -- Dados clínicos
            diag_princ TEXT,
            proc_solic TEXT,
            proc_rea TEXT,
            complex TEXT,
            
            -- Internação e permanência
            dt_inter TEXT,
            dt_saida TEXT,
            dias_perm REAL,
            car_int TEXT,
            
            -- UTI
            uti_mes_to TEXT,
            marca_uti TEXT,
            val_uti REAL,
            
            -- Valores financeiros
            val_sh REAL,
            val_sp REAL,
            val_sadt REAL,
            val_rn REAL,
            val_acomp REAL,
            val_ortp REAL,
            val_sangue REAL,
            val_sadtsr REAL,
            val_transp REAL,
            val_obsang REAL,
            val_ped1ac REAL,
            val_tot REAL,
            val_sh_fed REAL,
            val_sp_fed REAL,
            val_sh_ges REAL,
            val_sp_ges REAL,
            val_uci REAL,
            us_tot REAL,
            
            -- Acompanhamento
            diar_acom TEXT,
            qt_diarias REAL,
            
            -- Gestão
            cobranca TEXT,
            nat_jur TEXT,
            gestao TEXT,
            gestrisco TEXT,
            gestor_cod TEXT,
            gestor_tp TEXT,
            gestor_cpf TEXT,
            financ TEXT,
            regct TEXT,
            
            -- Estabelecimento
            cnes TEXT,
            cnpj_mant TEXT,
            
            -- Controle
            sequencia TEXT,
            remessa TEXT,
            
            -- Adicionais
            diagsec1 TEXT,
            tpdisec1 TEXT,
            arquivo_origem TEXT,
            ind_vdrl TEXT,
            
            -- Timestamp de criação
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Cria índices para otimizar consultas
    cursor.execute('CREATE INDEX idx_diag_princ ON internacoes(diag_princ)')
    cursor.execute('CREATE INDEX idx_munic_res ON internacoes(munic_res)')
    cursor.execute('CREATE INDEX idx_idade ON internacoes(idade)')
    cursor.execute('CREATE INDEX idx_sexo ON internacoes(sexo)')
    cursor.execute('CREATE INDEX idx_ano_mes ON internacoes(ano_cmpt, mes_cmpt)')
    cursor.execute('CREATE INDEX idx_dt_inter ON internacoes(dt_inter)')
    cursor.execute('CREATE INDEX idx_val_tot ON internacoes(val_tot)')
    
    # Cria tabela de metadados
    cursor.execute('''
        CREATE TABLE metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            table_name TEXT,
            total_records INTEGER,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            data_source TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Banco de dados criado com sucesso em: {db_path}")
    
    return db_path

def populate_database():
    """
    Popula o banco de dados com os dados do CSV processado
    """
    
    # Caminhos
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed', 'dados_limpos_internacoes_pr_2025.csv')
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'internacoes_datasus.db')
    
    # Carrega o CSV
    print("Carregando dados do CSV...")
    df = pd.read_csv(csv_path)
    
    # Mapeia as colunas do CSV para as colunas do banco
    column_mapping = {
        'UF_ZI': 'uf_zi',
        'ANO_CMPT': 'ano_cmpt',
        'MES_CMPT': 'mes_cmpt',
        'ESPEC': 'espec',
        'CGC_HOSP': 'cgc_hosp',
        'N_AIH': 'n_aih',
        'IDENT': 'ident',
        'CEP': 'cep',
        'MUNIC_RES': 'munic_res',
        'MUNIC_MOV': 'munic_mov',
        'NASC': 'nasc',
        'SEXO': 'sexo',
        'COD_IDADE': 'cod_idade',
        'IDADE': 'idade',
        'RACA_COR': 'raca_cor',
        'NACIONAL': 'nacional',
        'DIAG_PRINC': 'diag_princ',
        'PROC_SOLIC': 'proc_solic',
        'PROC_REA': 'proc_rea',
        'COMPLEX': 'complex',
        'DT_INTER': 'dt_inter',
        'DT_SAIDA': 'dt_saida',
        'DIAS_PERM': 'dias_perm',
        'CAR_INT': 'car_int',
        'UTI_MES_TO': 'uti_mes_to',
        'MARCA_UTI': 'marca_uti',
        'VAL_UTI': 'val_uti',
        'VAL_SH': 'val_sh',
        'VAL_SP': 'val_sp',
        'VAL_SADT': 'val_sadt',
        'VAL_RN': 'val_rn',
        'VAL_ACOMP': 'val_acomp',
        'VAL_ORTP': 'val_ortp',
        'VAL_SANGUE': 'val_sangue',
        'VAL_SADTSR': 'val_sadtsr',
        'VAL_TRANSP': 'val_transp',
        'VAL_OBSANG': 'val_obsang',
        'VAL_PED1AC': 'val_ped1ac',
        'VAL_TOT': 'val_tot',
        'VAL_SH_FED': 'val_sh_fed',
        'VAL_SP_FED': 'val_sp_fed',
        'VAL_SH_GES': 'val_sh_ges',
        'VAL_SP_GES': 'val_sp_ges',
        'VAL_UCI': 'val_uci',
        'US_TOT': 'us_tot',
        'DIAR_ACOM': 'diar_acom',
        'QT_DIARIAS': 'qt_diarias',
        'COBRANCA': 'cobranca',
        'NAT_JUR': 'nat_jur',
        'GESTAO': 'gestao',
        'GESTRISCO': 'gestrisco',
        'GESTOR_COD': 'gestor_cod',
        'GESTOR_TP': 'gestor_tp',
        'GESTOR_CPF': 'gestor_cpf',
        'FINANC': 'financ',
        'REGCT': 'regct',
        'CNES': 'cnes',
        'CNPJ_MANT': 'cnpj_mant',
        'SEQUENCIA': 'sequencia',
        'REMESSA': 'remessa',
        'DIAGSEC1': 'diagsec1',
        'TPDISEC1': 'tpdisec1',
        'ARQUIVO_ORIGEM': 'arquivo_origem',
        'IND_VDRL': 'ind_vdrl'
    }
    
    # Renomeia as colunas
    df = df.rename(columns=column_mapping)
    
    # Seleciona apenas as colunas que existem no banco
    db_columns = list(column_mapping.values())
    df = df[db_columns]
    
    # Conecta ao banco e insere os dados
    conn = sqlite3.connect(db_path)
    
    print(f"Inserindo {len(df)} registros no banco de dados...")
    df.to_sql('internacoes', conn, if_exists='append', index=False)
    
    # Atualiza metadados
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO metadata (table_name, total_records, data_source)
        VALUES (?, ?, ?)
    ''', ('internacoes', len(df), csv_path))
    
    conn.commit()
    conn.close()
    
    print("Dados inseridos com sucesso!")
    
    return len(df)

if __name__ == "__main__":
    # Cria a estrutura do banco
    db_path = create_database_structure()
    
    # Popula o banco com os dados
    total_records = populate_database()
    
    print(f"\nResumo:")
    print(f"- Banco de dados: {db_path}")
    print(f"- Total de registros: {total_records}")
    print(f"- Estrutura criada com índices otimizados")
    print(f"- Pronto para uso no dashboard Streamlit")