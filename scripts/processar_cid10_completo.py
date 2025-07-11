import sqlite3
import os
import re

def processar_arquivo_cid10():
    """
    Processa o arquivo CID-10 completo e extrai todos os códigos e descrições
    """
    
    cid_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', 'cid10_ultimaversaodisponivel_2012.txt')
    
    if not os.path.exists(cid_file):
        print(f"Arquivo CID-10 não encontrado: {cid_file}")
        return {}
    
    print("Processando arquivo CID-10 completo...")
    
    cid_mapping = {}
    current_chapter = "Não classificado"
    current_group = "Não classificado"
    
    # Padrões para identificar diferentes elementos
    codigo_pattern = re.compile(r'^([A-Z]\d{2})\.?(\d)?\s+(.+)$')
    chapter_pattern = re.compile(r'^CAP[ÍI]TULO\s+([IVX]+)\s*-?\s*(.+)$', re.IGNORECASE)
    group_pattern = re.compile(r'^([A-Z]\d{2}-[A-Z]\d{2})\s+(.+)$')
    
    # Mapear capítulos para melhor classificação
    chapter_mapping = {
        'I': 'Doenças infecciosas e parasitárias',
        'II': 'Neoplasias',
        'III': 'Doenças do sangue e dos órgãos hematopoéticos',
        'IV': 'Doenças endócrinas, nutricionais e metabólicas',
        'V': 'Transtornos mentais e comportamentais',
        'VI': 'Doenças do sistema nervoso',
        'VII': 'Doenças do olho e anexos',
        'VIII': 'Doenças do ouvido e da apófise mastóide',
        'IX': 'Doenças do aparelho circulatório',
        'X': 'Doenças do aparelho respiratório',
        'XI': 'Doenças do aparelho digestivo',
        'XII': 'Doenças da pele e do tecido subcutâneo',
        'XIII': 'Doenças do sistema osteomuscular',
        'XIV': 'Doenças do aparelho geniturinário',
        'XV': 'Gravidez, parto e puerpério',
        'XVI': 'Algumas afecções originadas no período perinatal',
        'XVII': 'Malformações congênitas',
        'XVIII': 'Sintomas, sinais e achados anormais',
        'XIX': 'Lesões, envenenamentos e outras causas externas',
        'XX': 'Causas externas de morbidade e mortalidade',
        'XXI': 'Fatores que influenciam o estado de saúde'
    }
    
    # Códigos que são tipicamente sensíveis à atenção básica
    sensivel_patterns = [
        r'^A0[0-9]',  # Infecções intestinais
        r'^A3[0-9]',  # Hanseníase e outras infecções
        r'^A4[6-9]',  # Erisipela e outras infecções bacterianas
        r'^E1[0-4]',  # Diabetes mellitus
        r'^I1[0-9]',  # Doenças hipertensivas
        r'^I2[0-5]',  # Doenças isquêmicas do coração (algumas)
        r'^J0[0-6]',  # Infecções respiratórias agudas superiores
        r'^J1[0-8]',  # Pneumonia
        r'^J2[0-2]',  # Outras infecções respiratórias agudas
        r'^J4[0-7]',  # Doenças crônicas das vias aéreas inferiores
        r'^K2[0-9]',  # Doenças do esôfago, estômago e duodeno
        r'^K5[0-9]',  # Doenças não inflamatórias do trato genital feminino
        r'^L0[0-9]',  # Infecções da pele
        r'^N3[0-9]',  # Doenças do trato urinário
        r'^N7[0-7]',  # Doenças inflamatórias dos órgãos pélvicos femininos
        r'^Z0[0-9]',  # Exames e contatos com serviços de saúde
        r'^Z3[0-9]',  # Procedimentos de atenção básica
    ]
    
    def is_sensivel_atencao_basica(codigo):
        """Verifica se o código é sensível à atenção básica"""
        for pattern in sensivel_patterns:
            if re.match(pattern, codigo):
                return True
        return False
    
    try:
        with open(cid_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                if not line:
                    continue
                
                # Verificar se é um capítulo
                chapter_match = chapter_pattern.match(line)
                if chapter_match:
                    roman_num = chapter_match.group(1)
                    chapter_desc = chapter_match.group(2).strip()
                    current_chapter = chapter_mapping.get(roman_num, chapter_desc)
                    current_group = "Não classificado"
                    continue
                
                # Verificar se é um grupo
                group_match = group_pattern.match(line)
                if group_match:
                    current_group = group_match.group(2).strip()
                    continue
                
                # Verificar se é um código
                codigo_match = codigo_pattern.match(line)
                if codigo_match:
                    codigo_base = codigo_match.group(1)
                    codigo_sub = codigo_match.group(2) if codigo_match.group(2) else ""
                    descricao = codigo_match.group(3).strip()
                    
                    # Montar código completo
                    if codigo_sub:
                        codigo_completo = f"{codigo_base}{codigo_sub}"
                    else:
                        codigo_completo = codigo_base
                    
                    # Limpar descrição de caracteres especiais
                    descricao = re.sub(r'[+*]', '', descricao).strip()
                    
                    # Determinar se é sensível à atenção básica
                    sensivel = is_sensivel_atencao_basica(codigo_completo)
                    
                    # Adicionar ao mapeamento
                    cid_mapping[codigo_completo] = {
                        'descricao': descricao,
                        'capitulo': current_chapter,
                        'grupo': current_group,
                        'sensivel_atencao_basica': sensivel
                    }
                    
                    if line_num % 1000 == 0:
                        print(f"Processadas {line_num} linhas, {len(cid_mapping)} códigos extraídos...")
    
    except Exception as e:
        print(f"Erro ao processar arquivo: {e}")
        return {}
    
    print(f"✅ Processamento concluído: {len(cid_mapping)} códigos CID-10 extraídos")
    
    return cid_mapping

def atualizar_todos_cids_banco():
    """Atualiza o banco com todos os códigos CID-10 do arquivo"""
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'internacoes_datasus.db')
    
    if not os.path.exists(db_path):
        print("Banco de dados não encontrado!")
        return
    
    # Processar arquivo CID-10
    cid_mapping = processar_arquivo_cid10()
    
    if not cid_mapping:
        print("Nenhum código CID-10 foi extraído!")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Atualizando banco de dados...")
    
    # Primeiro, obter todos os CIDs que existem nas internações
    cursor.execute("""
        SELECT DISTINCT codigo_diagnostico_principal
        FROM internacoes 
        WHERE codigo_diagnostico_principal IS NOT NULL
    """)
    cids_nas_internacoes = set(row[0] for row in cursor.fetchall())
    
    print(f"CIDs únicos nas internações: {len(cids_nas_internacoes)}")
    
    # Atualizar apenas os CIDs que estão sendo usados
    updates = 0
    inserts = 0
    not_found = 0
    
    for cid_codigo in cids_nas_internacoes:
        if cid_codigo in cid_mapping:
            cid_info = cid_mapping[cid_codigo]
            
            try:
                # Tentar atualizar primeiro
                cursor.execute("""
                    UPDATE cid_diagnosticos 
                    SET descricao = ?, capitulo = ?, grupo = ?, sensivel_atencao_basica = ?
                    WHERE codigo = ?
                """, (
                    cid_info['descricao'],
                    cid_info['capitulo'],
                    cid_info['grupo'],
                    cid_info['sensivel_atencao_basica'],
                    cid_codigo
                ))
                
                if cursor.rowcount > 0:
                    updates += 1
                else:
                    # Se não existe, inserir
                    cursor.execute("""
                        INSERT INTO cid_diagnosticos (codigo, descricao, capitulo, grupo, sensivel_atencao_basica)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        cid_codigo,
                        cid_info['descricao'],
                        cid_info['capitulo'],
                        cid_info['grupo'],
                        cid_info['sensivel_atencao_basica']
                    ))
                    inserts += 1
            
            except Exception as e:
                print(f"Erro ao processar CID {cid_codigo}: {e}")
        else:
            not_found += 1
            # Tentar variações do código (com ponto, sem subcategoria, etc.)
            variations = [
                cid_codigo.replace('.', ''),  # Remover pontos
                cid_codigo[:3],               # Só a categoria principal
                cid_codigo[:4] if len(cid_codigo) > 3 else cid_codigo,  # Primeiros 4 caracteres
            ]
            
            found_variation = False
            for variation in variations:
                if variation in cid_mapping and variation != cid_codigo:
                    cid_info = cid_mapping[variation]
                    try:
                        cursor.execute("""
                            UPDATE cid_diagnosticos 
                            SET descricao = ?, capitulo = ?, grupo = ?, sensivel_atencao_basica = ?
                            WHERE codigo = ?
                        """, (
                            cid_info['descricao'],
                            cid_info['capitulo'],
                            cid_info['grupo'],
                            cid_info['sensivel_atencao_basica'],
                            cid_codigo
                        ))
                        
                        if cursor.rowcount > 0:
                            updates += 1
                            found_variation = True
                            break
                        else:
                            cursor.execute("""
                                INSERT INTO cid_diagnosticos (codigo, descricao, capitulo, grupo, sensivel_atencao_basica)
                                VALUES (?, ?, ?, ?, ?)
                            """, (
                                cid_codigo,
                                cid_info['descricao'],
                                cid_info['capitulo'],
                                cid_info['grupo'],
                                cid_info['sensivel_atencao_basica']
                            ))
                            inserts += 1
                            found_variation = True
                            break
                    except Exception as e:
                        print(f"Erro ao processar variação do CID {cid_codigo} -> {variation}: {e}")
            
            if found_variation:
                not_found -= 1
    
    # Commit das alterações
    conn.commit()
    
    # Verificar resultados finais
    cursor.execute("SELECT COUNT(*) FROM cid_diagnosticos WHERE descricao NOT LIKE 'Diagnóstico %'")
    total_com_descricao = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM cid_diagnosticos")
    total_cids = cursor.fetchone()[0]
    
    print(f"\n✅ Atualização concluída:")
    print(f"   - {updates} CIDs atualizados")
    print(f"   - {inserts} CIDs inseridos")
    print(f"   - {not_found} CIDs não encontrados no arquivo")
    print(f"   - Total de CIDs com descrição: {total_com_descricao}")
    print(f"   - Total de CIDs no banco: {total_cids}")
    
    # Mostrar alguns exemplos dos CIDs atualizados
    print(f"\nExemplos de CIDs atualizados:")
    cursor.execute("""
        SELECT 
            i.codigo_diagnostico_principal,
            cid.descricao,
            COUNT(*) as frequencia
        FROM internacoes i
        LEFT JOIN cid_diagnosticos cid ON i.codigo_diagnostico_principal = cid.codigo
        WHERE i.codigo_diagnostico_principal IS NOT NULL
        AND cid.descricao IS NOT NULL
        AND cid.descricao NOT LIKE 'Diagnóstico %'
        GROUP BY i.codigo_diagnostico_principal, cid.descricao
        ORDER BY COUNT(*) DESC
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    for i, (codigo, descricao, freq) in enumerate(results, 1):
        print(f"   {i:2d}. {codigo} - {descricao} ({freq:,} casos)")
    
    conn.close()

if __name__ == "__main__":
    atualizar_todos_cids_banco()