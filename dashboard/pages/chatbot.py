import streamlit as st
import sqlite3
import pandas as pd
import re
import os
import sys

# Verificar se a biblioteca do Gemini está disponível
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print("✅ DEBUG: google.generativeai importado com sucesso")
    
    # Verificar versão da biblioteca
    try:
        import google.generativeai
        version = google.generativeai.__version__
        print(f"🔍 DEBUG: Versão da biblioteca: {version}")
    except:
        print("⚠️  DEBUG: Não foi possível verificar versão da biblioteca")
        
except ImportError as e:
    GEMINI_AVAILABLE = False
    print(f"❌ DEBUG: Erro ao importar google.generativeai: {e}")
    print("❌ DEBUG: Execute: pip install google-generativeai>=0.5.0")

# Configurar API do Gemini
GEMINI_API_KEY = "AIzaSyC2b5xyyXkZDu_8AcVVjIlFxUFP9QM8eZU"
if GEMINI_AVAILABLE:
    genai.configure(api_key=GEMINI_API_KEY)
    print("✅ DEBUG: API do Gemini configurada")
else:
    print("❌ DEBUG: API do Gemini não pode ser configurada - biblioteca não disponível")

def get_database_connection():
    """Conecta ao banco de dados SQLite"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'internacoes_datasus.db')
    return sqlite3.connect(db_path, check_same_thread=False)

def get_database_schema():
    """Retorna o schema do banco de dados para o contexto do chatbot"""
    return """
    BANCO DE DADOS - INTERNAÇÕES DATASUS:
    
    TABELAS PRINCIPAIS:
    
    1. internacoes: Registros de internações hospitalares
       - id, numero_aih, paciente_id, estabelecimento_id
       - ano_competencia, mes_competencia
       - codigo_diagnostico_principal, codigo_diagnostico_secundario
       - data_internacao, data_saida, dias_permanencia, dias_uti_total
       - gestacao_risco
    
    2. pacientes: Informações dos pacientes
       - id, idade_anos, codigo_sexo, codigo_municipio_residencia
       - data_nascimento, cep, codigo_raca_cor
    
    3. estabelecimentos: Dados dos estabelecimentos de saúde
       - id, codigo_cnes, nome_estabelecimento, tipo_estabelecimento
       - codigo_municipio_movimento, codigo_especialidade
       - codigo_complexidade, codigo_tipo_gestao
    
    4. cid_diagnosticos: Classificação Internacional de Doenças
       - codigo, descricao, capitulo, grupo
       - sensivel_atencao_basica (boolean)
    
    5. municipios: Dados dos municípios
       - codigo, nome, regiao_saude, populacao
    
    6. valores_financeiros: Valores relacionados às internações
       - internacao_id, valor_total, valor_servicos_hospitalares
       - valor_servicos_profissionais, valor_uti, valor_em_dolares
    
    7. sexo: Códigos de sexo
       - codigo, descricao
    
    8. especialidades: Especialidades médicas
       - codigo, descricao
    
    9. complexidade: Níveis de complexidade
       - codigo, descricao
    
    PERIOD DE DADOS: Janeiro, Fevereiro e Março de 2025
    LOCALIZAÇÃO: Paraná, Brasil
    TOTAL DE REGISTROS: 118.627 internações
    """

# Função removida para simplificar - usamos apenas modelos conhecidos que funcionam

def generate_sql_with_gemini(user_question, schema):
    """Gera consulta SQL usando Gemini baseada na pergunta do usuário"""
    print(f"🔍 DEBUG: Iniciando generate_sql_with_gemini")
    print(f"🔍 DEBUG: user_question = '{user_question}'")
    print(f"🔍 DEBUG: API_KEY configurada = {GEMINI_API_KEY[:10]}...")
    print(f"🔍 DEBUG: GEMINI_AVAILABLE = {GEMINI_AVAILABLE}")
    
    if not GEMINI_AVAILABLE:
        print("❌ DEBUG: Biblioteca google-generativeai não está disponível")
        return None
    
    try:
        # Usar apenas modelos atuais (não depreciados)
        models_to_try = [
            'gemini-1.5-flash',  # Modelo recomendado mais atual
            'gemini-1.5-pro'     # Modelo alternativo atual
        ]
        
        print(f"🔍 DEBUG: Tentando apenas modelos atuais: {models_to_try}")
        
        model = None
        for model_name in models_to_try:
            try:
                print(f"🔍 DEBUG: Tentando modelo {model_name}...")
                model = genai.GenerativeModel(model_name)
                print(f"🔍 DEBUG: Modelo {model_name} criado com sucesso")
                break
            except Exception as e:
                print(f"⚠️  DEBUG: Modelo {model_name} falhou: {str(e)}")
                continue
        
        if model is None:
            print(f"❌ DEBUG: Nenhum modelo atual funcionou")
            print(f"❌ DEBUG: Modelos testados: {models_to_try}")
            print(f"❌ DEBUG: Soluções possíveis:")
            print(f"❌ DEBUG: 1. Atualizar biblioteca: pip install --upgrade google-generativeai")
            print(f"❌ DEBUG: 2. Verificar se a chave da API está correta")
            print(f"❌ DEBUG: 3. Verificar conectividade com a internet")
            return None
        
        prompt = f"""
        Você é um especialista em SQL e análise de dados de saúde do DataSUS. 
        
        CONTEXTO DO BANCO DE DADOS:
        {schema}
        
        PERGUNTA DO USUÁRIO: {user_question}
        
        REGRAS OBRIGATÓRIAS:
        1. Gere APENAS a consulta SQL, sem explicações, comentários ou formatação markdown
        2. Use apenas SELECT - NUNCA use DROP, DELETE, UPDATE ou INSERT
        3. Sempre use JOIN apropriados para conectar tabelas relacionadas
        4. Use LIMIT para limitar resultados (máximo 50 registros)
        5. Para descrições de diagnósticos, use LIKE com % para busca parcial (ex: LIKE '%diabetes%')
        6. Para nomes de municípios, use LIKE com % para busca parcial (ex: LIKE '%Curitiba%')
        7. Use aliases descritivos em português para as colunas
        8. Sempre inclua ORDER BY para ordenar resultados
        9. Use COUNT(*) para contagens
        10. Para valores monetários, use ROUND para 2 casas decimais
        11. Para datas, use formato YYYY-MM-DD
        
        EXEMPLOS DE CONSULTAS CORRETAS:
        - Para "quantas internações": SELECT COUNT(*) as total_internacoes FROM internacoes
        - Para "pacientes com diabetes": WHERE cd.descricao LIKE '%diabetes%'
        - Para "internações em Curitiba": WHERE m.nome LIKE '%Curitiba%'
        - Para "diagnósticos mais comuns": GROUP BY cd.descricao ORDER BY COUNT(*) DESC
        
        IMPORTANTE: Responda APENAS com a consulta SQL válida, sem ``` ou outras formatações.
        """
        
        print(f"🔍 DEBUG: Enviando prompt para Gemini...")
        print(f"🔍 DEBUG: Tamanho do prompt: {len(prompt)} caracteres")
        
        response = model.generate_content(prompt)
        print(f"🔍 DEBUG: Resposta recebida do Gemini!")
        print(f"🔍 DEBUG: Resposta completa: '{response.text}'")
        
        sql_query = response.text.strip()
        print(f"🔍 DEBUG: SQL query limpa: '{sql_query}'")
        
        return sql_query
    
    except Exception as e:
        print(f"❌ DEBUG: ERRO no generate_sql_with_gemini: {str(e)}")
        print(f"❌ DEBUG: Tipo do erro: {type(e).__name__}")
        import traceback
        print(f"❌ DEBUG: Traceback completo:")
        traceback.print_exc()
        return None

def execute_sql_query(conn, query):
    """Executa consulta SQL e retorna DataFrame"""
    print(f"🔍 DEBUG: Executando SQL query...")
    print(f"🔍 DEBUG: Query original: '{query}'")
    
    try:
        # Limpa a query removendo possíveis caracteres especiais
        query = query.strip()
        if query.startswith('```sql'):
            query = query[6:]
        if query.endswith('```'):
            query = query[:-3]
        
        query = query.strip()
        print(f"🔍 DEBUG: Query limpa: '{query}'")
        
        df = pd.read_sql_query(query, conn)
        print(f"🔍 DEBUG: Query executada com sucesso!")
        print(f"🔍 DEBUG: Resultado: {len(df)} linhas, {len(df.columns)} colunas")
        if not df.empty:
            print(f"🔍 DEBUG: Primeiras linhas: {df.head(2).to_dict()}")
        
        return df, None
    
    except Exception as e:
        print(f"❌ DEBUG: ERRO na execute_sql_query: {str(e)}")
        print(f"❌ DEBUG: Tipo do erro: {type(e).__name__}")
        import traceback
        print(f"❌ DEBUG: Traceback completo:")
        traceback.print_exc()
        return None, str(e)


def format_dataframe_for_display(df):
    """Formata DataFrame para exibição amigável"""
    if df is None or df.empty:
        return df
    
    # Renomear colunas para português
    column_mapping = {
        'total_internacoes': 'Total de Internações',
        'valor_total_reais': 'Valor Total (R$)',
        'diagnostico': 'Diagnóstico',
        'quantidade': 'Quantidade',
        'municipio': 'Município',
        'internacoes': 'Internações',
        'idade_anos': 'Idade',
        'idade': 'Idade',
        'sexo': 'Sexo',
        'municipio_residencia': 'Município de Residência',
        'diagnostico_principal': 'Diagnóstico Principal',
        'data_internacao': 'Data de Internação',
        'dias_permanencia': 'Dias de Permanência',
        'valor_total': 'Valor Total (R$)',
        'quantidade_internacoes': 'Quantidade de Internações',
        'valor_medio': 'Valor Médio (R$)',
        'quantidade_pacientes': 'Quantidade de Pacientes',
        'idade_media': 'Idade Média',
        'municipio_mais_comum': 'Município Mais Comum',
        'dias_media': 'Dias Médios de Permanência'
    }
    
    # Aplicar mapeamento de colunas
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns:
            df = df.rename(columns={old_name: new_name})
    
    # Formatar valores monetários
    for col in df.columns:
        if 'valor' in col.lower() or 'r$' in col.lower():
            if df[col].dtype in ['float64', 'float32', 'int64', 'int32']:
                df[col] = df[col].apply(lambda x: f"R$ {x:,.2f}" if pd.notna(x) else "")
    
    return df

def render(data):
    """Página do Chatbot de Consultas"""
    
    st.title("Chatbot de Consultas - Dados de Saúde")
    st.markdown("---")
    
    # Verificar se o Gemini está disponível
    if not GEMINI_AVAILABLE:
        st.error("❌ **Biblioteca google-generativeai não está instalada!**")
        st.markdown("""
        **Para usar o chatbot, execute:**
        ```bash
        pip install google-generativeai>=0.5.0
        ```
        Depois reinicie o dashboard.
        """)
        return
    
    st.markdown("""
    ### Como usar o chatbot:
    - Faça perguntas sobre internações hospitalares no Paraná (Jan-Mar 2025)
    - Exemplos: "Quantas internações tivemos?", "Principais diagnósticos", "Pacientes com diabetes em Curitiba"
    - Todas as respostas são geradas via inteligência artificial
    """)
    
    # Inicializar histórico do chat
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Exibir mensagens anteriores
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            if message["type"] == "text":
                st.markdown(message["content"])
            elif message["type"] == "dataframe":
                st.markdown(message["content_text"])
                st.dataframe(message["content_data"], use_container_width=True)
            elif message["type"] == "error":
                st.error(message["content"])
    
    # Entrada do usuário
    user_input = st.chat_input("Faça uma pergunta sobre os dados de internação (processado via API Gemini)")
    
    if user_input:
        # Adicionar mensagem do usuário
        st.session_state.chat_messages.append({
            "role": "user", 
            "type": "text", 
            "content": user_input
        })
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        with st.chat_message("assistant"):
            with st.spinner("Processando sua pergunta..."):
                print(f"🔍 DEBUG: ========== INÍCIO DO PROCESSAMENTO ==========")
                print(f"🔍 DEBUG: Input do usuário: '{user_input}'")
                
                conn = get_database_connection()
                print(f"🔍 DEBUG: Conexão com banco obtida")
                
                # Usar apenas API Gemini para gerar consultas SQL
                print(f"🔍 DEBUG: Chamando generate_sql_with_gemini...")
                sql_query = generate_sql_with_gemini(user_input, get_database_schema())
                print(f"🔍 DEBUG: Retorno do Gemini: '{sql_query}'")
                
                if sql_query:
                    print(f"🔍 DEBUG: SQL query válida encontrada, executando...")
                    # Executar consulta
                    result_df, error = execute_sql_query(conn, sql_query)
                    
                    if error:
                        print(f"❌ DEBUG: Erro na execução SQL: {error}")
                        error_msg = f"❌ Erro ao executar consulta: {error}"
                        st.error(error_msg)
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "type": "error",
                            "content": error_msg
                        })
                    
                    elif result_df is not None and not result_df.empty:
                        print(f"🔍 DEBUG: Resultado obtido com sucesso!")
                        # Formatar e exibir resultados
                        formatted_df = format_dataframe_for_display(result_df)
                        
                        if len(formatted_df) == 1 and len(formatted_df.columns) == 1:
                            # Resultado único (ex: contagem)
                            value = formatted_df.iloc[0, 0]
                            response_text = f"📊 **Resultado:** {value}"
                            st.markdown(response_text)
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "type": "text",
                                "content": response_text
                            })
                        else:
                            # Múltiplos resultados
                            response_text = f"📊 **Encontrei {len(formatted_df)} resultado(s):**"
                            st.markdown(response_text)
                            st.dataframe(formatted_df, use_container_width=True)
                            st.session_state.chat_messages.append({
                                "role": "assistant",
                                "type": "dataframe",
                                "content_text": response_text,
                                "content_data": formatted_df
                            })
                    
                    else:
                        response_text = "❌ Nenhum resultado encontrado para sua consulta."
                        st.markdown(response_text)
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "type": "text",
                            "content": response_text
                        })
                
                else:
                    print(f"❌ DEBUG: Nenhuma SQL query gerada pelo Gemini")
                    response_text = """❌ Não consegui processar sua pergunta com a API do Gemini. 
                    
**Possíveis causas:**
- Modelo Gemini não encontrado (erro 404)
- Problema temporário com a API do Gemini
- Pergunta muito complexa ou ambígua
- Versão da API incompatível

**Soluções:**
- Verifique os logs no console para detalhes do erro
- Tente uma pergunta mais simples
- Aguarde alguns minutos e tente novamente

**Tente perguntas como:**
- "Quantas internações tivemos?"
- "Principais diagnósticos"
- "Pacientes com diabetes em Curitiba"
- "Listar pacientes de Londrina"
- "Internações com pneumonia"
- "Valor total das internações"
- "Internações com angina em Londrina"
"""
                    st.markdown(response_text)
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "type": "text",
                        "content": response_text
                    })
                
                conn.close()
                print(f"🔍 DEBUG: ========== FIM DO PROCESSAMENTO ==========")
                print()
    
    # Sidebar com informações úteis
    with st.sidebar:
        st.markdown("### 📊 Informações do Banco")
        
        if st.button("🔄 Limpar Conversa"):
            st.session_state.chat_messages = []
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("""
        **Dados Disponíveis:**
        - 118.627 internações
        - Janeiro a Março 2025
        - Estado do Paraná
        - 253 estabelecimentos
        - 102.659 pacientes únicos
        """)
        
        st.markdown("---")
        
        st.markdown("""
        **Exemplos de Perguntas:**
        - Quantas internações tivemos?
        - Principais diagnósticos
        - Pacientes com diabetes em Curitiba
        - Listar pacientes de Londrina
        - Internações com pneumonia
        - Valor total das internações
        - Internações com angina em Londrina
        - Pacientes com diabetes
        """)
        
        st.markdown("---")
        
        st.markdown("""
        **Tabelas Principais:**
        - internacoes
        - pacientes  
        - estabelecimentos
        - cid_diagnosticos
        - municipios
        - valores_financeiros
        """)