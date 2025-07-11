import sqlite3
import pandas as pd
import os
from datetime import datetime

def create_lookup_tables(cursor):
    """Cria tabelas de apoio com códigos e descrições"""
    
    # Tabela de CID-10 (principais diagnósticos)
    cursor.execute('''
        CREATE TABLE cid_diagnosticos (
            codigo TEXT PRIMARY KEY,
            descricao TEXT,
            capitulo TEXT,
            grupo TEXT,
            sensivel_atencao_basica BOOLEAN DEFAULT FALSE
        )
    ''')
    
    # Tabela de sexo
    cursor.execute('''
        CREATE TABLE sexo (
            codigo INTEGER PRIMARY KEY,
            descricao TEXT
        )
    ''')
    
    # Tabela de caráter de internação
    cursor.execute('''
        CREATE TABLE carater_internacao (
            codigo TEXT PRIMARY KEY,
            descricao TEXT
        )
    ''')
    
    # Tabela de complexidade
    cursor.execute('''
        CREATE TABLE complexidade (
            codigo TEXT PRIMARY KEY,
            descricao TEXT
        )
    ''')
    
    # Tabela de municípios do Paraná
    cursor.execute('''
        CREATE TABLE municipios (
            codigo TEXT PRIMARY KEY,
            nome TEXT,
            regiao_saude TEXT,
            populacao INTEGER
        )
    ''')
    
    # Tabela de procedimentos
    cursor.execute('''
        CREATE TABLE procedimentos (
            codigo TEXT PRIMARY KEY,
            descricao TEXT,
            grupo_procedimento TEXT
        )
    ''')
    
    # Tabela de especialidades
    cursor.execute('''
        CREATE TABLE especialidades (
            codigo TEXT PRIMARY KEY,
            descricao TEXT
        )
    ''')
    
    # Tabela de natureza jurídica
    cursor.execute('''
        CREATE TABLE natureza_juridica (
            codigo TEXT PRIMARY KEY,
            descricao TEXT
        )
    ''')
    
    # Tabela de tipos de gestão
    cursor.execute('''
        CREATE TABLE tipos_gestao (
            codigo TEXT PRIMARY KEY,
            descricao TEXT
        )
    ''')
    
    # Tabela de financiamento
    cursor.execute('''
        CREATE TABLE tipos_financiamento (
            codigo TEXT PRIMARY KEY,
            descricao TEXT
        )
    ''')

def populate_lookup_tables(cursor):
    """Popula as tabelas de apoio com dados comuns"""
    
    # Dados de sexo
    sexo_data = [
        (1, 'Masculino'),
        (3, 'Feminino')
    ]
    cursor.executemany('INSERT INTO sexo VALUES (?, ?)', sexo_data)
    
    # Dados de caráter de internação
    carater_data = [
        ('01', 'Eletiva'),
        ('02', 'Urgência'),
        ('03', 'Acidente de Trabalho'),
        ('04', 'Acidente de Trânsito'),
        ('05', 'Outros Tipos de Acidentes'),
        ('06', 'Doença Relacionada ao Trabalho')
    ]
    cursor.executemany('INSERT INTO carater_internacao VALUES (?, ?)', carater_data)
    
    # Dados de complexidade
    complexidade_data = [
        ('01', 'Baixa Complexidade'),
        ('02', 'Média Complexidade'),
        ('03', 'Alta Complexidade')
    ]
    cursor.executemany('INSERT INTO complexidade VALUES (?, ?)', complexidade_data)
    
    # Principais CIDs com descrições (amostra dos mais comuns)
    cid_data = [
        ('N390', 'Infecção do trato urinário, local não especificado', 'Doenças do aparelho geniturinário', 'Doenças do trato urinário', True),
        ('L031', 'Celulite de dedo da mão e do pé', 'Doenças da pele e do tecido subcutâneo', 'Infecções da pele', True),
        ('N179', 'Doença renal crônica não especificada', 'Doenças do aparelho geniturinário', 'Insuficiência renal', True),
        ('K579', 'Doença diverticular do intestino, parte não especificada, sem perfuração ou abscesso', 'Doenças do aparelho digestivo', 'Doenças intestinais', False),
        ('N300', 'Cistite aguda', 'Doenças do aparelho geniturinário', 'Cistite', True),
        ('K818', 'Outros transtornos funcionais especificados do intestino', 'Doenças do aparelho digestivo', 'Transtornos funcionais', True),
        ('N832', 'Outras obstruções e refluxo vesicoureteral', 'Doenças do aparelho geniturinário', 'Obstrução ureteral', False),
        ('I10', 'Hipertensão essencial', 'Doenças do aparelho circulatório', 'Hipertensão', True),
        ('E149', 'Diabetes mellitus não especificado sem complicações', 'Doenças endócrinas', 'Diabetes', True),
        ('J440', 'Doença pulmonar obstrutiva crônica com infecção respiratória aguda do trato respiratório inferior', 'Doenças do aparelho respiratório', 'DPOC', True)
    ]
    cursor.executemany('INSERT INTO cid_diagnosticos VALUES (?, ?, ?, ?, ?)', cid_data)
    
    # Especialidades comuns
    especialidades_data = [
        ('01', 'Clínica Médica'),
        ('02', 'Clínica Cirúrgica'),
        ('03', 'Obstetrícia'),
        ('04', 'Pediatria'),
        ('05', 'Pneumologia'),
        ('06', 'Cardiologia'),
        ('07', 'Neurologia'),
        ('08', 'Ortopedia'),
        ('09', 'Urologia'),
        ('10', 'Nefrologia')
    ]
    cursor.executemany('INSERT INTO especialidades VALUES (?, ?)', especialidades_data)
    
    # Natureza jurídica
    natureza_data = [
        ('1023', 'Administração Pública Municipal'),
        ('2062', 'Fundação Pública Municipal'),
        ('3999', 'Outras Organizações'),
        ('1104', 'Autarquia Municipal'),
        ('2135', 'Associação Privada')
    ]
    cursor.executemany('INSERT INTO natureza_juridica VALUES (?, ?)', natureza_data)
    
    # Tipos de gestão
    gestao_data = [
        ('1', 'Gestão Federal'),
        ('2', 'Gestão Estadual'),
        ('3', 'Gestão Municipal'),
        ('4', 'Dupla')
    ]
    cursor.executemany('INSERT INTO tipos_gestao VALUES (?, ?)', gestao_data)
    
    # Tipos de financiamento
    financiamento_data = [
        ('01', 'Recursos Federais'),
        ('02', 'Recursos Estaduais'),
        ('03', 'Recursos Municipais'),
        ('04', 'Recursos Privados'),
        ('05', 'Convênios'),
        ('06', 'FAEC - Fundo de Ações Estratégicas e Compensação')
    ]
    cursor.executemany('INSERT INTO tipos_financiamento VALUES (?, ?)', financiamento_data)

def create_database_structure():
    """
    Cria a estrutura do banco de dados SQLite normalizada para internações hospitalares
    """
    
    # Caminho para o banco de dados
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'internacoes_datasus.db')
    
    # Conecta ao banco de dados
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop tables if exist (para desenvolvimento)
    tables_to_drop = [
        'internacoes', 'pacientes', 'estabelecimentos', 'valores_financeiros',
        'cid_diagnosticos', 'sexo', 'carater_internacao', 'complexidade',
        'municipios', 'procedimentos', 'especialidades', 'natureza_juridica',
        'tipos_gestao', 'tipos_financiamento', 'metadata'
    ]
    
    for table in tables_to_drop:
        cursor.execute(f'DROP TABLE IF EXISTS {table}')
    
    # Cria tabelas de apoio primeiro
    create_lookup_tables(cursor)
    
    # Tabela de pacientes (informações demográficas)
    cursor.execute('''
        CREATE TABLE pacientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            idade_anos INTEGER,
            codigo_sexo INTEGER,
            data_nascimento DATE,
            codigo_municipio_residencia TEXT,
            cep TEXT,
            codigo_raca_cor TEXT,
            nacionalidade TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (codigo_sexo) REFERENCES sexo(codigo),
            FOREIGN KEY (codigo_municipio_residencia) REFERENCES municipios(codigo)
        )
    ''')
    
    # Tabela de estabelecimentos de saúde
    cursor.execute('''
        CREATE TABLE estabelecimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo_cnes TEXT UNIQUE,
            cnpj_hospital TEXT,
            cnpj_mantenedora TEXT,
            codigo_municipio_movimento TEXT,
            codigo_especialidade TEXT,
            codigo_natureza_juridica TEXT,
            codigo_tipo_gestao TEXT,
            codigo_complexidade TEXT,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (codigo_municipio_movimento) REFERENCES municipios(codigo),
            FOREIGN KEY (codigo_especialidade) REFERENCES especialidades(codigo),
            FOREIGN KEY (codigo_natureza_juridica) REFERENCES natureza_juridica(codigo),
            FOREIGN KEY (codigo_tipo_gestao) REFERENCES tipos_gestao(codigo),
            FOREIGN KEY (codigo_complexidade) REFERENCES complexidade(codigo)
        )
    ''')
    
    # Tabela principal de internações
    cursor.execute('''
        CREATE TABLE internacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_aih TEXT UNIQUE,
            
            -- Chaves estrangeiras
            paciente_id INTEGER,
            estabelecimento_id INTEGER,
            
            -- Período de competência
            ano_competencia INTEGER,
            mes_competencia INTEGER,
            
            -- Dados clínicos
            codigo_diagnostico_principal TEXT,
            codigo_diagnostico_secundario TEXT,
            codigo_procedimento_solicitado TEXT,
            codigo_procedimento_realizado TEXT,
            codigo_carater_internacao TEXT,
            
            -- Temporais da internação
            data_internacao DATE,
            data_saida DATE,
            dias_permanencia INTEGER,
            
            -- UTI
            dias_uti_total INTEGER,
            marca_uti TEXT,
            
            -- Gestação de risco
            gestacao_risco BOOLEAN DEFAULT FALSE,
            
            -- Acompanhante
            diarias_acompanhante INTEGER,
            quantidade_diarias INTEGER,
            
            -- Controle
            sequencia_registro TEXT,
            codigo_remessa TEXT,
            arquivo_origem TEXT,
            
            -- Timestamp
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (paciente_id) REFERENCES pacientes(id),
            FOREIGN KEY (estabelecimento_id) REFERENCES estabelecimentos(id),
            FOREIGN KEY (codigo_diagnostico_principal) REFERENCES cid_diagnosticos(codigo),
            FOREIGN KEY (codigo_carater_internacao) REFERENCES carater_internacao(codigo)
        )
    ''')
    
    # Tabela de valores financeiros (separada para normalização)
    cursor.execute('''
        CREATE TABLE valores_financeiros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            internacao_id INTEGER,
            
            -- Valores principais
            valor_servicos_hospitalares DECIMAL(10,2),
            valor_servicos_profissionais DECIMAL(10,2),
            valor_sadt DECIMAL(10,2),
            valor_total DECIMAL(10,2),
            valor_em_dolares DECIMAL(10,2),
            
            -- Valores específicos
            valor_recem_nascido DECIMAL(10,2),
            valor_acompanhante DECIMAL(10,2),
            valor_ortese_protese DECIMAL(10,2),
            valor_sangue DECIMAL(10,2),
            valor_transporte DECIMAL(10,2),
            valor_obstetricia DECIMAL(10,2),
            valor_pediatria DECIMAL(10,2),
            valor_uti DECIMAL(10,2),
            valor_uci DECIMAL(10,2),
            
            -- Valores por origem de recursos
            valor_sh_federal DECIMAL(10,2),
            valor_sp_federal DECIMAL(10,2),
            valor_sh_gestao DECIMAL(10,2),
            valor_sp_gestao DECIMAL(10,2),
            
            -- Tipo de financiamento
            codigo_tipo_financiamento TEXT,
            
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (internacao_id) REFERENCES internacoes(id),
            FOREIGN KEY (codigo_tipo_financiamento) REFERENCES tipos_financiamento(codigo)
        )
    ''')
    
    # Popula as tabelas de apoio
    populate_lookup_tables(cursor)
    
    # Cria índices para otimização
    indices = [
        'CREATE INDEX idx_internacoes_data_internacao ON internacoes(data_internacao)',
        'CREATE INDEX idx_internacoes_diagnostico ON internacoes(codigo_diagnostico_principal)',
        'CREATE INDEX idx_internacoes_ano_mes ON internacoes(ano_competencia, mes_competencia)',
        'CREATE INDEX idx_internacoes_carater ON internacoes(codigo_carater_internacao)',
        'CREATE INDEX idx_pacientes_idade ON pacientes(idade_anos)',
        'CREATE INDEX idx_pacientes_sexo ON pacientes(codigo_sexo)',
        'CREATE INDEX idx_pacientes_municipio ON pacientes(codigo_municipio_residencia)',
        'CREATE INDEX idx_valores_total ON valores_financeiros(valor_total)',
        'CREATE INDEX idx_estabelecimentos_cnes ON estabelecimentos(codigo_cnes)'
    ]
    
    for index in indices:
        cursor.execute(index)
    
    # Tabela de metadados
    cursor.execute('''
        CREATE TABLE metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tabela TEXT,
            total_registros INTEGER,
            ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fonte_dados TEXT,
            versao_estrutura TEXT DEFAULT '2.0'
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"Banco de dados normalizado criado com sucesso em: {db_path}")
    
    return db_path

def populate_database():
    """
    Popula o banco de dados normalizado com os dados do CSV processado
    """
    
    # Caminhos
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed', 'dados_completos_internacoes_pr_2025.csv')
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'internacoes_datasus.db')
    
    # Carrega o CSV
    print("Carregando dados do CSV...")
    df = pd.read_csv(csv_path)
    
    # Conecta ao banco
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Processando e inserindo dados nas tabelas normalizadas...")
    
    # Funções auxiliares para conversão segura
    def safe_int(value, default=None):
        try:
            if pd.isna(value) or value == '' or value is None:
                return default
            return int(float(value))
        except (ValueError, TypeError):
            return default
    
    def safe_float(value, default=None):
        try:
            if pd.isna(value) or value == '' or value is None:
                return default
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def safe_str(value, default=None):
        try:
            if pd.isna(value) or value == '' or value is None:
                return default
            return str(value).strip()
        except (ValueError, TypeError):
            return default
    
    # Dicionário para mapear pacientes já inseridos
    pacientes_map = {}
    estabelecimentos_map = {}
    
    for idx, row in df.iterrows():
        if idx % 1000 == 0:
            print(f"Processando registro {idx + 1}/{len(df)}")
            # Commit periódico para evitar perda de dados
            conn.commit()
        
        # Criar chave única para paciente
        paciente_key = f"{row.get('IDADE', 0)}_{row.get('SEXO', 0)}_{row.get('MUNIC_RES', '')}_{row.get('NASC', '')}"
        
        if paciente_key not in pacientes_map:
            # Inserir novo paciente
            try:
                cursor.execute('''
                    INSERT INTO pacientes (idade_anos, codigo_sexo, data_nascimento, codigo_municipio_residencia, cep, nacionalidade)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    safe_int(row.get('IDADE')),
                    safe_int(row.get('SEXO')),
                    safe_str(row.get('NASC')),
                    safe_str(row.get('MUNIC_RES')),
                    safe_str(row.get('CEP')),
                    safe_str(row.get('NACIONAL'))
                ))
                pacientes_map[paciente_key] = cursor.lastrowid
            except Exception as e:
                print(f"Erro ao inserir paciente no registro {idx}: {e}")
                continue
        
        # Criar chave única para estabelecimento
        estabelecimento_key = f"{row.get('CNES', '')}_{row.get('CGC_HOSP', '')}"
        
        if estabelecimento_key not in estabelecimentos_map:
            # Inserir novo estabelecimento
            try:
                cursor.execute('''
                    INSERT INTO estabelecimentos (codigo_cnes, cnpj_hospital, cnpj_mantenedora, 
                                                codigo_municipio_movimento, codigo_especialidade, 
                                                codigo_natureza_juridica, codigo_tipo_gestao, codigo_complexidade)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    safe_str(row.get('CNES')),
                    safe_str(row.get('CGC_HOSP')),
                    safe_str(row.get('CNPJ_MANT')),
                    safe_str(row.get('MUNIC_MOV')),
                    safe_str(row.get('ESPEC')),
                    safe_str(row.get('NAT_JUR')),
                    safe_str(row.get('GESTAO')),
                    safe_str(row.get('COMPLEX'))
                ))
                estabelecimentos_map[estabelecimento_key] = cursor.lastrowid
            except Exception as e:
                print(f"Erro ao inserir estabelecimento no registro {idx}: {e}")
                continue
        
        # Inserir internação
        try:
            cursor.execute('''
                INSERT INTO internacoes (numero_aih, paciente_id, estabelecimento_id, ano_competencia, mes_competencia,
                                       codigo_diagnostico_principal, codigo_diagnostico_secundario, 
                                       codigo_procedimento_solicitado, codigo_procedimento_realizado,
                                       codigo_carater_internacao, data_internacao, data_saida, dias_permanencia,
                                       dias_uti_total, gestacao_risco, diarias_acompanhante, quantidade_diarias,
                                       sequencia_registro, codigo_remessa, arquivo_origem)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                safe_str(row.get('N_AIH')),
                pacientes_map[paciente_key],
                estabelecimentos_map[estabelecimento_key],
                safe_int(row.get('ANO_CMPT')),
                safe_int(row.get('MES_CMPT')),
                safe_str(row.get('DIAG_PRINC')),
                safe_str(row.get('DIAGSEC1')),
                safe_str(row.get('PROC_SOLIC')),
                safe_str(row.get('PROC_REA')),
                safe_str(row.get('CAR_INT')),
                safe_str(row.get('DT_INTER')),
                safe_str(row.get('DT_SAIDA')),
                safe_int(row.get('DIAS_PERM')),
                safe_int(row.get('UTI_MES_TO')),
                bool(safe_int(row.get('GESTRISCO'), 0)),
                safe_int(row.get('DIAR_ACOM')),
                safe_float(row.get('QT_DIARIAS')),
                safe_str(row.get('SEQUENCIA')),
                safe_str(row.get('REMESSA')),
                safe_str(row.get('ARQUIVO_ORIGEM'))
            ))
        except Exception as e:
            print(f"Erro ao inserir internação no registro {idx}: {e}")
            print(f"Dados do registro: {dict(row)}")
            continue
        
        internacao_id = cursor.lastrowid
        
        # Inserir valores financeiros
        try:
            cursor.execute('''
                INSERT INTO valores_financeiros (internacao_id, valor_servicos_hospitalares, valor_servicos_profissionais,
                                               valor_sadt, valor_total, valor_em_dolares, valor_recem_nascido,
                                               valor_acompanhante, valor_ortese_protese, valor_sangue, valor_transporte,
                                               valor_obstetricia, valor_pediatria, valor_uti, valor_uci,
                                               valor_sh_federal, valor_sp_federal, valor_sh_gestao, valor_sp_gestao,
                                               codigo_tipo_financiamento)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                internacao_id,
                safe_float(row.get('VAL_SH'), 0),
                safe_float(row.get('VAL_SP'), 0),
                safe_float(row.get('VAL_SADT'), 0),
                safe_float(row.get('VAL_TOT'), 0),
                safe_float(row.get('US_TOT'), 0),
                safe_float(row.get('VAL_RN'), 0),
                safe_float(row.get('VAL_ACOMP'), 0),
                safe_float(row.get('VAL_ORTP'), 0),
                safe_float(row.get('VAL_SANGUE'), 0),
                safe_float(row.get('VAL_TRANSP'), 0),
                safe_float(row.get('VAL_OBSANG'), 0),
                safe_float(row.get('VAL_PED1AC'), 0),
                safe_float(row.get('VAL_UTI'), 0),
                safe_float(row.get('VAL_UCI'), 0),
                safe_float(row.get('VAL_SH_FED'), 0),
                safe_float(row.get('VAL_SP_FED'), 0),
                safe_float(row.get('VAL_SH_GES'), 0),
                safe_float(row.get('VAL_SP_GES'), 0),
                safe_str(row.get('FINANC'))
            ))
        except Exception as e:
            print(f"Erro ao inserir valores financeiros no registro {idx}: {e}")
            continue
    
    # Atualizar CIDs que não estão na tabela de apoio
    print("Atualizando tabela de CIDs com dados reais...")
    cursor.execute('''
        INSERT OR IGNORE INTO cid_diagnosticos (codigo, descricao, capitulo, grupo, sensivel_atencao_basica)
        SELECT DISTINCT codigo_diagnostico_principal, 
               'Diagnóstico ' || codigo_diagnostico_principal,
               'Não classificado',
               'Não classificado', 
               FALSE
        FROM internacoes 
        WHERE codigo_diagnostico_principal IS NOT NULL 
        AND codigo_diagnostico_principal NOT IN (SELECT codigo FROM cid_diagnosticos)
    ''')
    
    # Popular tabela de procedimentos com dados reais
    print("Populando tabela de procedimentos...")
    cursor.execute('''
        INSERT OR IGNORE INTO procedimentos (codigo, descricao, grupo_procedimento)
        SELECT DISTINCT codigo_procedimento_solicitado, 
               'Procedimento ' || codigo_procedimento_solicitado,
               'Não classificado'
        FROM internacoes 
        WHERE codigo_procedimento_solicitado IS NOT NULL 
        AND codigo_procedimento_solicitado != ''
    ''')
    
    # Popular tabela de municípios com dados reais (códigos únicos dos pacientes)
    print("Populando tabela de municípios...")
    cursor.execute('''
        INSERT OR IGNORE INTO municipios (codigo, nome, regiao_saude)
        SELECT DISTINCT codigo_municipio_residencia, 
               'Município ' || codigo_municipio_residencia,
               'Paraná'
        FROM pacientes 
        WHERE codigo_municipio_residencia IS NOT NULL 
        AND codigo_municipio_residencia != ''
    ''')
    
    # Adicionar também municípios de movimento dos estabelecimentos
    cursor.execute('''
        INSERT OR IGNORE INTO municipios (codigo, nome, regiao_saude)
        SELECT DISTINCT codigo_municipio_movimento, 
               'Município ' || codigo_municipio_movimento,
               'Paraná'
        FROM estabelecimentos 
        WHERE codigo_municipio_movimento IS NOT NULL 
        AND codigo_municipio_movimento != ''
    ''')
    
    # Atualizar metadados
    print("Atualizando metadados...")
    cursor.execute('''
        INSERT INTO metadata (tabela, total_registros, fonte_dados)
        VALUES 
        ('internacoes', (SELECT COUNT(*) FROM internacoes), ?),
        ('pacientes', (SELECT COUNT(*) FROM pacientes), ?),
        ('estabelecimentos', (SELECT COUNT(*) FROM estabelecimentos), ?),
        ('valores_financeiros', (SELECT COUNT(*) FROM valores_financeiros), ?),
        ('cid_diagnosticos', (SELECT COUNT(*) FROM cid_diagnosticos), ?),
        ('procedimentos', (SELECT COUNT(*) FROM procedimentos), ?),
        ('municipios', (SELECT COUNT(*) FROM municipios), ?)
    ''', (csv_path, csv_path, csv_path, csv_path, csv_path, csv_path, csv_path))
    
    conn.commit()
    conn.close()
    
    print("Dados inseridos com sucesso no banco normalizado!")
    
    return len(df)

if __name__ == "__main__":
    # Cria a estrutura do banco
    db_path = create_database_structure()
    
    # Popula o banco com os dados
    total_records = populate_database()
    
    print(f"\nResumo:")
    print(f"- Banco de dados normalizado: {db_path}")
    print(f"- Total de registros processados: {total_records}")
    print(f"- Estrutura com múltiplas tabelas relacionadas")
    print(f"- Códigos traduzidos para descrições legíveis")
    print(f"- Pronto para uso no dashboard Streamlit")