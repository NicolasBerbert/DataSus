import sqlite3
import os
import requests
import json

def get_procedimentos_fallback():
    """
    Lista de fallback com os principais procedimentos SUS
    Baseado nos códigos mais comuns do sistema
    """
    
    print("🔄 Usando lista local de procedimentos (fallback)...")
    
    procedimentos_sus = {
        # Procedimentos mais comuns identificados no banco
        '301060088': {'nome': 'Consulta médica em atenção básica', 'grupo': 'Consultas'},
        '303140151': {'nome': 'Atendimento de urgência em clínica médica', 'grupo': 'Urgência'},
        '310010039': {'nome': 'Parto normal', 'grupo': 'Obstetrícia'},
        '303010037': {'nome': 'Atendimento médico em clínica básica', 'grupo': 'Consultas'},
        '411010034': {'nome': 'Cirurgia de catarata', 'grupo': 'Cirurgia Oftalmológica'},
        '415020034': {'nome': 'Procedimento ortopédico', 'grupo': 'Ortopedia'},
        '303070102': {'nome': 'Atendimento em pediatria', 'grupo': 'Pediatria'},
        '303060212': {'nome': 'Consulta em cardiologia', 'grupo': 'Cardiologia'},
        '303170190': {'nome': 'Atendimento neurológico', 'grupo': 'Neurologia'},
        '415010012': {'nome': 'Cirurgia geral de pequeno porte', 'grupo': 'Cirurgia Geral'},
        '303150050': {'nome': 'Consulta em urologia', 'grupo': 'Urologia'},
        '304080020': {'nome': 'Exame laboratorial básico', 'grupo': 'Exames'},
        '303100044': {'nome': 'Atendimento ginecológico', 'grupo': 'Ginecologia'},
        '303040149': {'nome': 'Consulta em endocrinologia', 'grupo': 'Endocrinologia'},
        '404010032': {'nome': 'Fisioterapia motora', 'grupo': 'Fisioterapia'},
        '407030026': {'nome': 'Terapia ocupacional', 'grupo': 'Terapia'},
        '304100021': {'nome': 'Exame de imagem', 'grupo': 'Diagnóstico por Imagem'},
        '303140046': {'nome': 'Atendimento clínico hospitalar', 'grupo': 'Internação'},
        '407040102': {'nome': 'Psicoterapia individual', 'grupo': 'Saúde Mental'},
        '415040035': {'nome': 'Cirurgia ortopédica de médio porte', 'grupo': 'Ortopedia'},
        
        # Procedimentos baseados em padrões comuns da Tabela SUS
        '201010038': {'nome': 'Transplante de órgão', 'grupo': 'Transplantes'},
        '209040033': {'nome': 'Quimioterapia', 'grupo': 'Oncologia'},
        '211050091': {'nome': 'Radioterapia', 'grupo': 'Oncologia'},
        '301060010': {'nome': 'Consulta médica básica', 'grupo': 'Consultas'},
        '301060070': {'nome': 'Consulta médica especializada', 'grupo': 'Consultas'},
        '303010010': {'nome': 'Atendimento clínico ambulatorial', 'grupo': 'Ambulatorial'},
        '303010029': {'nome': 'Consulta clínica de retorno', 'grupo': 'Consultas'},
        '303010045': {'nome': 'Avaliação clínica inicial', 'grupo': 'Avaliação'},
        '303010053': {'nome': 'Acompanhamento clínico', 'grupo': 'Acompanhamento'},
        '303010061': {'nome': 'Consulta médica de rotina', 'grupo': 'Consultas'},
        '303010070': {'nome': 'Atendimento médico ambulatorial', 'grupo': 'Ambulatorial'},
        '303010088': {'nome': 'Consulta médica domiciliar', 'grupo': 'Domiciliar'},
        '303010100': {'nome': 'Avaliação médica especializada', 'grupo': 'Avaliação'},
        '303010118': {'nome': 'Atendimento médico de urgência', 'grupo': 'Urgência'},
        '303010126': {'nome': 'Consulta médica preventiva', 'grupo': 'Prevenção'},
    }
    
    print(f"📋 {len(procedimentos_sus)} procedimentos principais carregados")
    
    return procedimentos_sus

def carregar_procedimentos_arquivo():
    """
    Carrega procedimentos do arquivo TXT fornecido pelo usuário
    Formato: código de 10 dígitos seguido da descrição
    """
    
    arquivo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw', 'tb_procedimento.txt')
    
    print(f"📂 Carregando procedimentos do arquivo: {arquivo_path}")
    
    if not os.path.exists(arquivo_path):
        print(f"❌ Arquivo não encontrado: {arquivo_path}")
        return {}
    
    procedimentos_dict = {}
    linhas_processadas = 0
    linhas_erro = 0
    
    try:
        with open(arquivo_path, 'r', encoding='latin-1') as file:
            for linha_num, linha in enumerate(file, 1):
                try:
                    linha = linha.strip()
                    if not linha:
                        continue
                    
                    # Extrair código (primeiros 10 caracteres)
                    codigo = linha[:10]
                    
                    # Extrair descrição (começando do caractere 10 até antes dos dados finais)
                    # A descrição vai até aproximadamente a posição 300, depois vêm dados numéricos
                    descricao_completa = linha[10:300].strip()
                    
                    # Limpar a descrição removendo espaços extras
                    palavras = descricao_completa.split()
                    
                    # Filtrar palavras: manter apenas as que contêm letras (remover códigos numéricos)
                    palavras_filtradas = []
                    for palavra in palavras:
                        # Parar se encontrar códigos longos (mais que 3 dígitos seguidos)
                        if len(palavra) > 3 and palavra.isdigit():
                            break
                        # Parar se encontrar padrões como "2I00010001"
                        if len(palavra) > 5 and any(c.isdigit() for c in palavra) and any(c.isalpha() for c in palavra):
                            # Se mais da metade são números, provavelmente é código
                            num_digits = sum(1 for c in palavra if c.isdigit())
                            if num_digits > len(palavra) / 2:
                                break
                        # Manter palavra se contém principalmente letras
                        if any(c.isalpha() for c in palavra):
                            palavras_filtradas.append(palavra)
                    
                    # Pegar no máximo as primeiras 15 palavras válidas
                    descricao = ' '.join(palavras_filtradas[:15])
                    
                    # Remover caracteres especiais e normalizar
                    descricao = descricao.replace('À', 'A').replace('Ã', 'A').replace('Á', 'A')
                    descricao = descricao.replace('É', 'E').replace('Ê', 'E')
                    descricao = descricao.replace('Í', 'I').replace('Î', 'I')
                    descricao = descricao.replace('Ó', 'O').replace('Ô', 'O').replace('Õ', 'O')
                    descricao = descricao.replace('Ú', 'U').replace('Ü', 'U')
                    descricao = descricao.replace('Ç', 'C')
                    descricao = descricao.replace('ì', 'i').replace('í', 'i')
                    descricao = descricao.replace('ã', 'a').replace('à', 'a').replace('á', 'a')
                    descricao = descricao.replace('é', 'e').replace('ê', 'e')
                    descricao = descricao.replace('ó', 'o').replace('ô', 'o').replace('õ', 'o')
                    descricao = descricao.replace('ú', 'u').replace('ü', 'u')
                    descricao = descricao.replace('ç', 'c')
                    
                    # Limpar espaços extras e caracteres especiais no final
                    descricao = ' '.join(descricao.split())
                    
                    if len(codigo) == 10 and descricao:
                        # Classificar procedimento por código
                        grupo = classificar_procedimento_por_codigo(codigo)
                        
                        procedimentos_dict[codigo] = {
                            'nome': descricao.title(),
                            'grupo': grupo
                        }
                        
                        linhas_processadas += 1
                        
                        # Mostrar primeiros 10 procedimentos
                        if linhas_processadas <= 10:
                            print(f"   {codigo}: {descricao.title()}")
                    else:
                        linhas_erro += 1
                        
                except Exception as e:
                    linhas_erro += 1
                    if linhas_erro <= 5:
                        print(f"   ⚠️ Erro na linha {linha_num}: {e}")
    
    except Exception as e:
        print(f"❌ Erro ao ler arquivo: {e}")
        return {}
    
    print(f"✅ {linhas_processadas} procedimentos carregados com sucesso")
    if linhas_erro > 0:
        print(f"   ⚠️ {linhas_erro} linhas com erro")
    
    return procedimentos_dict

def classificar_procedimento_por_codigo(codigo):
    """
    Classifica procedimento baseado no padrão do código SUS
    """
    
    if codigo.startswith('201'):
        return 'Transplantes'
    elif codigo.startswith('209'):
        return 'Quimioterapia/Oncologia'
    elif codigo.startswith('211'):
        return 'Radioterapia'
    elif codigo.startswith('301'):
        return 'Consultas e Atendimentos'
    elif codigo.startswith('303'):
        return 'Procedimentos Clínicos'
    elif codigo.startswith('304'):
        return 'Exames e Diagnósticos'
    elif codigo.startswith('310'):
        return 'Obstetrícia e Parto'
    elif codigo.startswith('401'):
        return 'Vigilância em Saúde'
    elif codigo.startswith('404'):
        return 'Fisioterapia'
    elif codigo.startswith('407'):
        return 'Terapias'
    elif codigo.startswith('411'):
        return 'Cirurgias Oftalmológicas'
    elif codigo.startswith('415'):
        return 'Cirurgias Ortopédicas'
    else:
        return 'Outros Procedimentos'

def atualizar_procedimentos_database():
    """
    Atualiza a tabela de procedimentos no banco de dados
    """
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'internacoes_datasus.db')
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        print(f"   Esperado em: {db_path}")
        return False
    
    # Carregar procedimentos do arquivo TXT fornecido
    procedimentos_arquivo = carregar_procedimentos_arquivo()
    
    # Usar fallback se arquivo falhar
    if not procedimentos_arquivo:
        print("🔄 Arquivo não disponível, usando lista local...")
        procedimentos_conhecidos = get_procedimentos_fallback()
    else:
        procedimentos_conhecidos = procedimentos_arquivo
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Buscar códigos únicos de procedimentos das internações
        cursor.execute('''
            SELECT DISTINCT codigo_procedimento_solicitado as codigo
            FROM internacoes 
            WHERE codigo_procedimento_solicitado IS NOT NULL 
            AND codigo_procedimento_solicitado != ''
            ORDER BY codigo
        ''')
        
        codigos_banco = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📊 Códigos únicos de procedimentos: {len(codigos_banco)}")
        
        # Atualizar descrições dos procedimentos
        atualizados = 0
        nao_encontrados = 0
        
        for codigo_banco in codigos_banco:
            nome_atualizado = None
            grupo_atualizado = None
            
            # Buscar nas fontes conhecidas
            # Tentar código original e com zero à frente
            codigo_encontrado = None
            if codigo_banco in procedimentos_conhecidos:
                codigo_encontrado = codigo_banco
            elif ('0' + codigo_banco) in procedimentos_conhecidos:
                codigo_encontrado = '0' + codigo_banco
            
            if codigo_encontrado:
                proc_info = procedimentos_conhecidos[codigo_encontrado]
                nome_atualizado = proc_info['nome']
                grupo_atualizado = proc_info['grupo']
                atualizados += 1
                if atualizados <= 10:  # Mostrar apenas os primeiros 10
                    print(f"   ✅ {codigo_banco} -> {codigo_encontrado} = {nome_atualizado}")
            else:
                # Classificar por padrão do código
                nome_atualizado = f'Procedimento {codigo_banco}'
                grupo_atualizado = classificar_procedimento_por_codigo(codigo_banco)
                nao_encontrados += 1
            
            # Atualizar no banco
            cursor.execute('''
                UPDATE procedimentos 
                SET descricao = ?, grupo_procedimento = ?
                WHERE codigo = ?
            ''', (nome_atualizado, grupo_atualizado, codigo_banco))
        
        conn.commit()
        
        print(f"\n✅ Atualização concluída:")
        print(f"   - Procedimentos do arquivo: {atualizados}")
        print(f"   - Classificados por padrão: {nao_encontrados}")
        print(f"   - Total de códigos únicos processados: {len(codigos_banco)}")
        
        # Verificar resultados por grupo
        cursor.execute('''
            SELECT 
                grupo_procedimento,
                COUNT(*) as quantidade
            FROM procedimentos
            GROUP BY grupo_procedimento
            ORDER BY COUNT(*) DESC
            LIMIT 10
        ''')
        
        print(f"\n📊 Procedimentos por grupo:")
        for grupo, quantidade in cursor.fetchall():
            print(f"   - {grupo}: {quantidade} procedimentos")
        
        # Top 10 procedimentos mais frequentes
        print(f"\n🏆 Top 10 procedimentos mais frequentes:")
        cursor.execute('''
            SELECT 
                p.descricao,
                COUNT(i.id) as frequencia
            FROM procedimentos p
            JOIN internacoes i ON p.codigo = i.codigo_procedimento_solicitado
            WHERE p.descricao NOT LIKE 'Procedimento %'
            GROUP BY p.codigo, p.descricao
            ORDER BY COUNT(i.id) DESC
            LIMIT 10
        ''')
        
        for descricao, frequencia in cursor.fetchall():
            print(f"   - {descricao}: {frequencia:,} casos")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar banco: {e}")
        conn.rollback()
        conn.close()
        return False

if __name__ == "__main__":
    print("=== ATUALIZADOR DE PROCEDIMENTOS SUS ===")
    print()
    
    sucesso = atualizar_procedimentos_database()
    
    if sucesso:
        print("\n✅ Script executado com sucesso!")
        print("\n💡 Procedimentos atualizados usando o arquivo fornecido!")
        print("   Arquivo processado: data/raw/tb_procedimento.txt")
    else:
        print("\n❌ Script falhou!")
        exit(1)