import sqlite3
import os
import requests
import json

def get_municipios_fallback():
    """
    Lista de fallback com os principais municípios do Paraná
    Usado caso a API do IBGE falhe
    """
    
    print("🔄 Usando lista local de municípios (fallback)...")
    
    municipios_pr = {
        # Principais municípios do Paraná com códigos IBGE
        '4106902': {'nome': 'Curitiba', 'uf': 'PR', 'eh_parana': True},
        '4113700': {'nome': 'Londrina', 'uf': 'PR', 'eh_parana': True},
        '4115200': {'nome': 'Maringá', 'uf': 'PR', 'eh_parana': True},
        '4119905': {'nome': 'Ponta Grossa', 'uf': 'PR', 'eh_parana': True},
        '4104808': {'nome': 'Cascavel', 'uf': 'PR', 'eh_parana': True},
        '4118006': {'nome': 'Paranaguá', 'uf': 'PR', 'eh_parana': True},
        '4127502': {'nome': 'Toledo', 'uf': 'PR', 'eh_parana': True},
        '4108304': {'nome': 'Foz do Iguaçu', 'uf': 'PR', 'eh_parana': True},
        '4109500': {'nome': 'Guarapuava', 'uf': 'PR', 'eh_parana': True},
        '4101408': {'nome': 'Apucarana', 'uf': 'PR', 'eh_parana': True},
        '4104303': {'nome': 'Campo Mourão', 'uf': 'PR', 'eh_parana': True},
        '4128104': {'nome': 'Umuarama', 'uf': 'PR', 'eh_parana': True},
        '4118204': {'nome': 'Paranavaí', 'uf': 'PR', 'eh_parana': True},
        '4126207': {'nome': 'Sarandi', 'uf': 'PR', 'eh_parana': True},
        '4102307': {'nome': 'Almirante Tamandaré', 'uf': 'PR', 'eh_parana': True},
        '4104204': {'nome': 'Campo Largo', 'uf': 'PR', 'eh_parana': True},
        '4105805': {'nome': 'Colombo', 'uf': 'PR', 'eh_parana': True},
        '4119004': {'nome': 'Pinhais', 'uf': 'PR', 'eh_parana': True},
        '4125456': {'nome': 'São José dos Pinhais', 'uf': 'PR', 'eh_parana': True},
        '4101804': {'nome': 'Araucária', 'uf': 'PR', 'eh_parana': True},
        '4118402': {'nome': 'Pato Branco', 'uf': 'PR', 'eh_parana': True},
        '4108502': {'nome': 'Francisco Beltrão', 'uf': 'PR', 'eh_parana': True},
        '4128203': {'nome': 'União da Vitória', 'uf': 'PR', 'eh_parana': True},
        '4126900': {'nome': 'Telêmaco Borba', 'uf': 'PR', 'eh_parana': True},
        '4101507': {'nome': 'Arapongas', 'uf': 'PR', 'eh_parana': True},
        # Adicionar mais conforme necessário
    }
    
    print(f"📋 {len(municipios_pr)} municípios principais do Paraná carregados")
    
    return municipios_pr

def buscar_municipios_ibge():
    """
    Busca todos os municípios do Brasil usando a API do IBGE
    """
    
    print("Buscando municípios na API do IBGE...")
    
    try:
        # API do IBGE para municípios
        url = "https://servicodados.ibge.gov.br/api/v1/localidades/municipios"
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        municipios_data = response.json()
        
        print(f"📡 Resposta da API recebida: {len(municipios_data) if municipios_data else 0} municípios")
        
        if not municipios_data:
            print("❌ API retornou lista vazia")
            return {}
        
        municipios_dict = {}
        erros_processamento = 0
        
        for i, municipio in enumerate(municipios_data):
            try:
                # Verificar se os campos obrigatórios existem
                if not municipio or 'id' not in municipio:
                    erros_processamento += 1
                    continue
                
                codigo = str(municipio['id'])
                nome = municipio.get('nome', f'Município {codigo}')
                
                # Navegar pela estrutura aninhada com verificações
                uf = 'XX'  # Default
                
                if 'microrregiao' in municipio and municipio['microrregiao']:
                    microrregiao = municipio['microrregiao']
                    if 'mesorregiao' in microrregiao and microrregiao['mesorregiao']:
                        mesorregiao = microrregiao['mesorregiao']
                        if 'UF' in mesorregiao and mesorregiao['UF']:
                            uf_obj = mesorregiao['UF']
                            if 'sigla' in uf_obj:
                                uf = uf_obj['sigla']
                
                municipios_dict[codigo] = {
                    'nome': nome,
                    'uf': uf,
                    'eh_parana': uf == 'PR'
                }
                
                # Debug dos primeiros municípios
                if i < 5:
                    print(f"   Município {i+1}: {codigo} - {nome} ({uf})")
                
            except Exception as e:
                erros_processamento += 1
                if erros_processamento <= 5:  # Mostrar apenas os primeiros 5 erros
                    print(f"   ⚠️ Erro ao processar município {i+1}: {e}")
        
        if erros_processamento > 0:
            print(f"   ⚠️ {erros_processamento} municípios com erro de processamento")
        
        print(f"✅ {len(municipios_dict)} municípios processados com sucesso")
        
        # Contar municípios do Paraná
        municipios_pr = sum(1 for m in municipios_dict.values() if m['eh_parana'])
        print(f"   - Municípios do Paraná: {municipios_pr}")
        print(f"   - Outros estados: {len(municipios_dict) - municipios_pr}")
        
        return municipios_dict
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao acessar API do IBGE: {e}")
        print("   💡 Verifique sua conexão com a internet")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Erro ao decodificar resposta JSON: {e}")
        return {}
    except Exception as e:
        print(f"❌ Erro inesperado ao processar dados da API: {e}")
        print(f"   Tipo do erro: {type(e).__name__}")
        return {}

def atualizar_municipios_database():
    """
    Atualiza a tabela de municípios no banco de dados usando a API do IBGE
    """
    
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'internacoes_datasus.db')
    
    if not os.path.exists(db_path):
        print("❌ Banco de dados não encontrado!")
        print(f"   Esperado em: {db_path}")
        return False
    
    # Buscar municípios na API do IBGE
    municipios_ibge = buscar_municipios_ibge()
    
    if not municipios_ibge:
        print("🔄 API do IBGE falhou, usando lista local...")
        municipios_ibge = get_municipios_fallback()
        
        if not municipios_ibge:
            print("❌ Falha total: nem API nem fallback funcionaram")
            return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Verificar códigos de municípios no banco
        cursor.execute('SELECT DISTINCT codigo FROM municipios ORDER BY codigo')
        codigos_banco = [row[0] for row in cursor.fetchall()]
        
        print(f"\n📊 Códigos únicos no banco: {len(codigos_banco)}")
        
        # Atualizar nomes dos municípios
        atualizados_pr = 0
        atualizados_outros = 0
        nao_encontrados = 0
        
        for codigo_banco in codigos_banco:
            nome_atualizado = None
            regiao_atualizada = None
            
            # Criar variações do código para tentar mapear
            variacoes = [
                codigo_banco,  # Código original
                codigo_banco.zfill(7),  # 7 dígitos com zeros à esquerda
                codigo_banco + '0',  # Adicionar 0 ao final (6->7 dígitos)
                codigo_banco + '1',  # Adicionar 1 ao final
                codigo_banco + '2',  # Adicionar 2 ao final
                codigo_banco.lstrip('0'),  # Remove zeros à esquerda
            ]
            
            # Se for código que começa com 41 (possível Paraná), tentar mais variações
            if codigo_banco.startswith('41') and len(codigo_banco) == 6:
                # Para códigos como 410690 -> tentar 4106902, 4106901, etc.
                for digito in range(10):
                    variacoes.append(codigo_banco + str(digito))
            
            encontrado = False
            
            for variacao in variacoes:
                if variacao in municipios_ibge:
                    municipio_info = municipios_ibge[variacao]
                    
                    if municipio_info['eh_parana']:
                        nome_atualizado = municipio_info['nome']
                        regiao_atualizada = 'Paraná'
                        atualizados_pr += 1
                        encontrado = True
                        print(f"   ✅ {codigo_banco} -> {variacao} = {nome_atualizado}")
                        break
                    else:
                        nome_atualizado = 'Outros Estados'
                        regiao_atualizada = f"Outros Estados ({municipio_info['uf']})"
                        atualizados_outros += 1
                        encontrado = True
                        break
            
            if not encontrado:
                # Se começar com 41, é provável que seja Paraná mas não identificado
                if codigo_banco.startswith('41'):
                    nome_atualizado = f'Município PR {codigo_banco}'
                    regiao_atualizada = 'Paraná (não identificado)'
                    atualizados_pr += 1
                else:
                    nome_atualizado = 'Outros Estados'
                    regiao_atualizada = 'Outros Estados (não identificado)'
                    atualizados_outros += 1
            
            # Atualizar no banco
            if nome_atualizado:
                cursor.execute('''
                    UPDATE municipios 
                    SET nome = ?, regiao_saude = ?
                    WHERE codigo = ?
                ''', (nome_atualizado, regiao_atualizada, codigo_banco))
        
        conn.commit()
        
        print(f"\n✅ Atualização concluída:")
        print(f"   - Municípios do Paraná: {atualizados_pr}")
        print(f"   - Outros Estados: {atualizados_outros}")
        print(f"   - Não identificados: {nao_encontrados}")
        
        # Verificar resultados
        cursor.execute('''
            SELECT 
                CASE 
                    WHEN nome = 'Outros Estados' THEN 'Outros Estados'
                    WHEN nome = 'Município Não Identificado' THEN 'Não Identificado'
                    ELSE 'Paraná'
                END as categoria,
                COUNT(DISTINCT m.codigo) as municipios,
                COUNT(DISTINCT p.id) as pacientes
            FROM municipios m
            LEFT JOIN pacientes p ON m.codigo = p.codigo_municipio_residencia
            GROUP BY categoria
            ORDER BY COUNT(DISTINCT p.id) DESC
        ''')
        
        print(f"\n📊 Distribuição final:")
        for categoria, municipios, pacientes in cursor.fetchall():
            print(f"   - {categoria}: {municipios} municípios, {pacientes:,} pacientes")
        
        # Top 10 municípios do Paraná
        print(f"\n🏆 Top 10 municípios do Paraná:")
        cursor.execute('''
            SELECT m.nome, COUNT(p.id) as pacientes
            FROM municipios m
            LEFT JOIN pacientes p ON m.codigo = p.codigo_municipio_residencia
            WHERE m.regiao_saude = 'Paraná'
            GROUP BY m.codigo, m.nome
            ORDER BY COUNT(p.id) DESC
            LIMIT 10
        ''')
        
        for nome, pacientes in cursor.fetchall():
            print(f"   - {nome}: {pacientes:,} pacientes")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar banco: {e}")
        conn.rollback()
        conn.close()
        return False

if __name__ == "__main__":
    print("=== ATUALIZADOR DE MUNICÍPIOS - API IBGE ===")
    print()
    
    sucesso = atualizar_municipios_database()
    
    if sucesso:
        print("\n✅ Script executado com sucesso!")
    else:
        print("\n❌ Script falhou!")
        exit(1)