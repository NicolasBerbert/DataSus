import sqlite3
import os

def popular_tabelas_faltantes():
    """
    Popula as tabelas procedimentos, municípios e metadata que ficaram vazias
    """
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'internacoes_datasus.db')
    csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed', 'dados_completos_internacoes_pr_2025.csv')
    
    if not os.path.exists(db_path):
        print("Banco de dados não encontrado!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Populando tabelas que ficaram vazias...")
    
    # Limpar tabela metadata primeiro se existir
    cursor.execute('DELETE FROM metadata')
    
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
        AND codigo_procedimento_solicitado != '0'
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
    
    # Verificar resultados
    print("\n✅ Resultados:")
    tables = ['procedimentos', 'municipios', 'metadata']
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f"   - {table}: {count} registros")
    
    # Mostrar alguns exemplos
    print("\nExemplos de procedimentos:")
    cursor.execute('''
        SELECT p.codigo, p.descricao, COUNT(*) as frequencia
        FROM procedimentos p
        JOIN internacoes i ON p.codigo = i.codigo_procedimento_solicitado
        GROUP BY p.codigo, p.descricao
        ORDER BY COUNT(*) DESC
        LIMIT 5
    ''')
    for codigo, desc, freq in cursor.fetchall():
        print(f"   - {codigo}: {desc} ({freq:,} casos)")
    
    print("\nExemplos de municípios:")
    cursor.execute('''
        SELECT m.codigo, m.nome, COUNT(*) as frequencia
        FROM municipios m
        JOIN pacientes p ON m.codigo = p.codigo_municipio_residencia
        GROUP BY m.codigo, m.nome
        ORDER BY COUNT(*) DESC
        LIMIT 5
    ''')
    for codigo, nome, freq in cursor.fetchall():
        print(f"   - {codigo}: {nome} ({freq:,} pacientes)")
    
    conn.close()
    print("\n✅ Tabelas populadas com sucesso!")

if __name__ == "__main__":
    popular_tabelas_faltantes()