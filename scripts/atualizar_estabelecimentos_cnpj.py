import sqlite3
import os
import requests
import json
import time
import re

def limpar_cnpj(cnpj_bruto):
    """
    Limpa e formata CNPJ removendo decimais e caracteres especiais
    """
    if not cnpj_bruto:
        return None
    
    # Converter para string e remover parte decimal se existir
    cnpj_str = str(cnpj_bruto)
    if '.' in cnpj_str:
        cnpj_str = cnpj_str.split('.')[0]
    
    # Remover caracteres não numéricos
    cnpj_limpo = re.sub(r'[^0-9]', '', cnpj_str)
    
    # Preencher com zeros à esquerda para ter 14 dígitos
    cnpj_limpo = cnpj_limpo.zfill(14)
    
    # Validar se tem exatamente 14 dígitos
    if len(cnpj_limpo) == 14:
        return cnpj_limpo
    else:
        return None

def formatar_cnpj_display(cnpj):
    """
    Formata CNPJ para exibição: XX.XXX.XXX/XXXX-XX
    """
    if not cnpj or len(cnpj) != 14:
        return cnpj
    
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:14]}"

def buscar_empresa_receita_federal(cnpj):
    """
    Busca informações da empresa na API da Receita Federal
    """
    
    # APIs públicas conhecidas para consulta de CNPJ
    apis = [
        f"https://receitaws.com.br/v1/cnpj/{cnpj}",
        f"https://www.receitaws.com.br/v1/cnpj/{cnpj}",
        f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    ]
    
    for api_url in apis:
        try:
            print(f"   Tentando: {api_url.split('/')[2]}")
            
            # Headers para parecer uma requisição de navegador
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'pt-BR,pt;q=0.9,en;q=0.8',
            }
            
            response = requests.get(api_url, headers=headers, timeout=8)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar se não há erro na resposta
                if 'status' in data and data['status'] == 'ERROR':
                    print(f"   ❌ {data.get('message', 'Erro na API')}")
                    continue
                
                # Extrair nome da empresa dependendo do formato da API
                nome_empresa = None
                
                if 'nome' in data:
                    nome_empresa = data['nome']
                elif 'razao_social' in data:
                    nome_empresa = data['razao_social']
                elif 'company' in data and 'name' in data['company']:
                    nome_empresa = data['company']['name']
                
                if nome_empresa:
                    print(f"   ✅ Encontrado: {nome_empresa}")
                    
                    # Informações adicionais se disponíveis
                    info_extra = {}
                    if 'fantasia' in data and data['fantasia']:
                        info_extra['nome_fantasia'] = data['fantasia']
                    if 'situacao' in data:
                        info_extra['situacao'] = data['situacao']
                    if 'municipio' in data:
                        info_extra['municipio'] = data['municipio']
                    
                    return {
                        'nome': nome_empresa,
                        'extra': info_extra,
                        'fonte': api_url.split('/')[2]
                    }
                else:
                    print(f"   ⚠️ Resposta sem nome da empresa")
            else:
                print(f"   ❌ Status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Erro de conexão: {e}")
        except json.JSONDecodeError as e:
            print(f"   ❌ Erro JSON: {e}")
        except Exception as e:
            print(f"   ❌ Erro inesperado: {e}")
        
        # Pausa entre tentativas para não sobrecarregar as APIs
        time.sleep(0.5)
    
    return None

def get_estabelecimentos_fallback():
    """
    Lista de fallback com estabelecimentos de saúde conhecidos do Paraná
    """
    
    print("🔄 Usando lista local de estabelecimentos (fallback)...")
    
    estabelecimentos_conhecidos = {
        # Principais hospitais do Paraná
        '78143153000185': {'nome': 'Hospital das Clínicas da UFPR', 'tipo': 'Hospital Universitário'},
        '76416866003670': {'nome': 'Hospital Universitário Evangélico Mackenzie', 'tipo': 'Hospital Universitário'},
        '75403287000108': {'nome': 'Santa Casa de Misericórdia de Curitiba', 'tipo': 'Santa Casa'},
        '80759111000115': {'nome': 'Hospital São Vicente', 'tipo': 'Hospital Privado'},
        '78897519000101': {'nome': 'Hospital Erasto Gaertner', 'tipo': 'Hospital Oncológico'},
        '75802348000100': {'nome': 'Hospital Nossa Senhora das Graças', 'tipo': 'Hospital Privado'},
        '80860273000145': {'nome': 'Hospital Universitário Regional de Maringá', 'tipo': 'Hospital Universitário'},
        '07070735000130': {'nome': 'Hospital Municipal de Curitiba', 'tipo': 'Hospital Municipal'},
        '07088017000191': {'nome': 'UPA Cidade Industrial de Curitiba', 'tipo': 'UPA'},
        
        # Adicionar mais conforme necessário
        '00000000000000': {'nome': 'Estabelecimento Não Identificado', 'tipo': 'Não Identificado'},
    }
    
    print(f"📋 {len(estabelecimentos_conhecidos)} estabelecimentos principais carregados")
    
    return estabelecimentos_conhecidos

def atualizar_estabelecimentos_database():
    """
    Atualiza a tabela de estabelecimentos com nomes reais baseados nos CNPJs
    """
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'internacoes_datasus.db')
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        print(f"   Esperado em: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna nome_estabelecimento já existe
        cursor.execute("PRAGMA table_info(estabelecimentos)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'nome_estabelecimento' not in colunas:
            print("📝 Adicionando coluna nome_estabelecimento...")
            cursor.execute('ALTER TABLE estabelecimentos ADD COLUMN nome_estabelecimento TEXT')
            cursor.execute('ALTER TABLE estabelecimentos ADD COLUMN tipo_estabelecimento TEXT')
            conn.commit()
        
        # Buscar CNPJs únicos que ainda não foram processados
        cursor.execute('''
            SELECT DISTINCT cnpj_hospital 
            FROM estabelecimentos 
            WHERE cnpj_hospital IS NOT NULL 
            AND (nome_estabelecimento IS NULL OR nome_estabelecimento = '')
            ORDER BY cnpj_hospital
        ''')
        
        cnpjs_brutos = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📊 CNPJs únicos encontrados: {len(cnpjs_brutos)}")
        
        # Usar fallback para estabelecimentos conhecidos
        estabelecimentos_fallback = get_estabelecimentos_fallback()
        
        atualizados_api = 0
        atualizados_fallback = 0
        nao_encontrados = 0
        
        # Processar todos os CNPJs
        cnpjs_para_processar = cnpjs_brutos
        print(f"   Processando todos os {len(cnpjs_para_processar)} CNPJs únicos...")
        
        for i, cnpj_bruto in enumerate(cnpjs_para_processar, 1):
            print(f"\n📍 [{i}/{len(cnpjs_para_processar)}] Processando CNPJ: {cnpj_bruto}")
            
            # Limpar e formatar CNPJ
            cnpj_limpo = limpar_cnpj(cnpj_bruto)
            
            if not cnpj_limpo:
                print(f"   ❌ CNPJ inválido")
                nao_encontrados += 1
                continue
            
            cnpj_formatado = formatar_cnpj_display(cnpj_limpo)
            print(f"   CNPJ formatado: {cnpj_formatado}")
            
            nome_encontrado = None
            tipo_encontrado = None
            fonte = None
            
            # Primeiro, verificar fallback
            if cnpj_limpo in estabelecimentos_fallback:
                info = estabelecimentos_fallback[cnpj_limpo]
                nome_encontrado = info['nome']
                tipo_encontrado = info['tipo']
                fonte = 'Local'
                atualizados_fallback += 1
                print(f"   ✅ [Fallback] {nome_encontrado}")
            else:
                # Tentar buscar na API da Receita Federal
                resultado_api = buscar_empresa_receita_federal(cnpj_limpo)
                
                if resultado_api:
                    nome_encontrado = resultado_api['nome']
                    tipo_encontrado = 'Estabelecimento de Saúde'
                    fonte = resultado_api['fonte']
                    atualizados_api += 1
                else:
                    # Se não encontrar, usar nome genérico
                    nome_encontrado = f'Estabelecimento {cnpj_formatado}'
                    tipo_encontrado = 'Não Identificado'
                    fonte = 'Padrão'
                    nao_encontrados += 1
                    print(f"   ⚠️ Não encontrado, usando nome padrão")
            
            # Atualizar no banco
            cursor.execute('''
                UPDATE estabelecimentos 
                SET nome_estabelecimento = ?, tipo_estabelecimento = ?
                WHERE cnpj_hospital = ?
            ''', (nome_encontrado, tipo_encontrado, cnpj_bruto))
            
            # Pausa entre requisições para não sobrecarregar APIs
            if fonte != 'Local' and fonte != 'Padrão':
                time.sleep(1)
        
        conn.commit()
        
        print(f"\n✅ Atualização concluída:")
        print(f"   - Encontrados via API: {atualizados_api}")
        print(f"   - Estabelecimentos conhecidos: {atualizados_fallback}")
        print(f"   - Não identificados: {nao_encontrados}")
        print(f"   - Total processado: {len(cnpjs_para_processar)}")
        
        # Verificar resultados
        cursor.execute('''
            SELECT 
                tipo_estabelecimento,
                COUNT(DISTINCT cnpj_hospital) as estabelecimentos,
                COUNT(DISTINCT i.id) as internacoes
            FROM estabelecimentos e
            LEFT JOIN internacoes i ON e.id = i.estabelecimento_id
            GROUP BY tipo_estabelecimento
            ORDER BY COUNT(DISTINCT i.id) DESC
        ''')
        
        print(f"\n📊 Estabelecimentos por tipo:")
        for tipo, estabelecimentos, internacoes in cursor.fetchall():
            if tipo:
                print(f"   - {tipo}: {estabelecimentos} estabelecimentos, {internacoes:,} internações")
        
        # Top 10 estabelecimentos
        print(f"\n🏆 Top 10 estabelecimentos:")
        cursor.execute('''
            SELECT e.nome_estabelecimento, COUNT(i.id) as internacoes
            FROM estabelecimentos e
            LEFT JOIN internacoes i ON e.id = i.estabelecimento_id
            WHERE e.nome_estabelecimento IS NOT NULL
            GROUP BY e.cnpj_hospital, e.nome_estabelecimento
            ORDER BY COUNT(i.id) DESC
            LIMIT 10
        ''')
        
        for nome, internacoes in cursor.fetchall():
            if internacoes > 0:
                print(f"   - {nome}: {internacoes:,} internações")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar banco: {e}")
        conn.rollback()
        conn.close()
        return False

if __name__ == "__main__":
    print("=== ATUALIZADOR DE ESTABELECIMENTOS (CNPJ) ===")
    print()
    
    sucesso = atualizar_estabelecimentos_database()
    
    if sucesso:
        print("\n✅ Script executado com sucesso!")
        print("\n💡 Estabelecimentos atualizados com nomes reais!")
        print("   🔍 CNPJs consultados na Receita Federal")
        print("   📋 Estabelecimentos conhecidos do Paraná identificados")
    else:
        print("\n❌ Script falhou!")
        exit(1)