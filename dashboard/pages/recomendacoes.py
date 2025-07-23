import streamlit as st
import pandas as pd
import sqlite3
import google.generativeai as genai
import os
import json
from datetime import datetime
import re

# Configurar a API do Gemini
GEMINI_API_KEY = "AIzaSyA9qPHcOixkWQ5eiXs9sYQ_2NyBdz5I2MI"
genai.configure(api_key=GEMINI_API_KEY)

def get_database_connection():
    """Conecta ao banco de dados SQLite"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'internacoes_datasus.db')
    return sqlite3.connect(db_path, check_same_thread=False)

def get_database_schema():
    """Retorna o esquema do banco de dados"""
    return """
    ESTRUTURA DO BANCO DE DADOS:
    
    1. TABELA internacoes (principal):
       - id, numero_aih, paciente_id, estabelecimento_id
       - ano_competencia, mes_competencia
       - codigo_diagnostico_principal, codigo_diagnostico_secundario
       - codigo_carater_internacao, data_internacao, data_saida
       - dias_permanencia, dias_uti_total, gestacao_risco
    
    2. TABELA pacientes:
       - id, idade_anos, codigo_sexo, codigo_municipio_residencia
    
    3. TABELA estabelecimentos:
       - id, codigo_cnes, cnpj_hospital, codigo_municipio_movimento
       - codigo_especialidade, codigo_complexidade
    
    4. TABELA valores_financeiros:
       - internacao_id, valor_total, valor_servicos_hospitalares
       - valor_servicos_profissionais, valor_uti
    
    5. TABELAS DE APOIO:
       - cid_diagnosticos (codigo, descricao, sensivel_atencao_basica)
       - sexo (codigo, descricao) - 1=Masculino, 3=Feminino
       - carater_internacao (codigo, descricao) - 01=Eletiva, 02=Urgência
       - municipios (codigo, nome, regiao_saude)
       - especialidades (codigo, descricao)
       - complexidade (codigo, descricao) - 01=Baixa, 02=Média, 03=Alta
    
    EXEMPLOS DE JOINS COMUNS:
    - Para obter dados completos use JOINs entre as tabelas
    - Use LEFT JOIN para incluir dados mesmo se não houver correspondência
    - A tabela principal é 'internacoes' conectada com outras por chaves estrangeiras
    """

def execute_sql_query(query):
    """Executa uma query SQL no banco de dados"""
    try:
        conn = get_database_connection()
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df, None
    except Exception as e:
        return None, str(e)

def validate_sql_query(query):
    """Valida se a query é segura (apenas SELECT)"""
    query_clean = query.strip()
    
    # Remover quebras de linha e espaços extras
    query_clean = ' '.join(query_clean.split())
    query_upper = query_clean.upper()
    
    # Verificar se é apenas SELECT
    if not query_upper.startswith('SELECT'):
        return False, f"Apenas queries SELECT são permitidas. Query recebida: {query_clean[:100]}..."
    
    # Verificar comandos perigosos
    dangerous_commands = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
    for cmd in dangerous_commands:
        if f' {cmd} ' in f' {query_upper} ' or query_upper.startswith(f'{cmd} '):
            return False, f"Comando {cmd} não é permitido"
    
    return True, "Query válida"

def generate_sql_from_question(question):
    """Usa o Gemini para gerar SQL a partir da pergunta"""
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = f"""
    Você é um especialista em SQL e análise de dados de saúde. 
    Baseado na pergunta do usuário, gere uma query SQL para o banco de dados de internações hospitalares.
    
    {get_database_schema()}
    
    PERGUNTA DO USUÁRIO: {question}
    
    INSTRUÇÕES IMPORTANTES:
    1. Gere APENAS a query SQL, sem explicações extras
    2. Use apenas comandos SELECT
    3. Use JOINs quando necessário para obter descrições legíveis
    4. Limite resultados com LIMIT quando apropriado (máximo 100 registros)
    5. Use nomes de colunas descritivos nos resultados
    6. Para análises temporais, use ano_competencia e mes_competencia
    7. Para diagnósticos, use JOIN com cid_diagnosticos para obter descrições
    8. Para sexo, use JOIN com sexo para obter descrição (1=Masculino, 3=Feminino)
    9. Para custos, use JOIN com valores_financeiros
    
    EXEMPLOS DE QUERIES ÚTEIS:
    - Top diagnósticos: SELECT cid.descricao, COUNT(*) as total FROM internacoes i JOIN cid_diagnosticos cid ON i.codigo_diagnostico_principal = cid.codigo GROUP BY cid.descricao ORDER BY total DESC LIMIT 10
    - Análise por idade: SELECT CASE WHEN p.idade_anos < 18 THEN '0-17' WHEN p.idade_anos >= 60 THEN '60+' ELSE '18-59' END as faixa_etaria, COUNT(*) FROM internacoes i JOIN pacientes p ON i.paciente_id = p.id GROUP BY faixa_etaria
    - Custos por mês: SELECT ano_competencia, mes_competencia, SUM(vf.valor_total) as valor_total FROM internacoes i JOIN valores_financeiros vf ON i.id = vf.internacao_id GROUP BY ano_competencia, mes_competencia ORDER BY ano_competencia, mes_competencia
    
    Responda apenas com a query SQL:
    """
    
    try:
        response = model.generate_content(prompt)
        sql_query = response.text.strip()
        
        # Limpar a resposta caso venha com formatação markdown
        if sql_query.startswith('```sql'):
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
        elif sql_query.startswith('```'):
            sql_query = sql_query.replace('```', '').strip()
        
        return sql_query
    except Exception as e:
        return f"Erro ao gerar SQL: {str(e)}"

def explain_results(question, df):
    """Usa o Gemini para explicar os resultados"""
    
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Preparar resumo dos dados
    data_summary = f"""
    Resultados da consulta:
    - Total de registros: {len(df)}
    - Colunas: {', '.join(df.columns.tolist())}
    
    Primeiras 5 linhas:
    {df.head().to_string()}
    """
    
    if len(df) > 5:
        data_summary += f"\n\nEstatísticas básicas:\n{df.describe().to_string()}"
    
    prompt = f"""
    Você é um analista de dados de saúde. Baseado na pergunta do usuário e nos resultados da consulta SQL, 
    forneça uma explicação clara e insights relevantes.
    
    PERGUNTA ORIGINAL: {question}
    
    {data_summary}
    
    INSTRUÇÕES:
    1. Responda em português brasileiro
    2. Seja claro e objetivo
    3. Destaque os principais insights
    4. Se relevante, mencione implicações para a gestão de saúde
    5. Use formatação markdown quando apropriado
    6. Seja profissional e técnico, mas acessível
    
    Sua resposta:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erro ao explicar resultados: {str(e)}"

def render_chat_interface():
    """Renderiza a interface do chatbot"""
    st.markdown("### 🤖 Assistente de Análise de Dados")
    st.markdown("Faça perguntas sobre os dados de internações hospitalares e eu vou gerar consultas SQL para respondê-las.")
    
    # Exemplos de perguntas
    with st.expander("💡 Exemplos de perguntas que você pode fazer"):
        st.markdown("""
        **Análises Básicas:**
        - Quais são os 10 diagnósticos mais comuns?
        - Qual é a distribuição de internações por faixa etária?
        - Quantas internações tivemos por mês em 2025?
        
        **Análises Financeiras:**
        - Qual é o custo total das internações por mês?
        - Quais diagnósticos têm maior custo médio?
        - Qual é a média de gastos por faixa etária?
        
        **Análises Clínicas:**
        - Quantas internações são sensíveis à atenção básica?
        - Qual é o tempo médio de permanência por diagnóstico?
        - Qual é a distribuição de urgência vs eletiva?
        
        **Análises Geográficas:**
        - Quais municípios têm mais internações?
        - Qual é a distribuição por região de saúde?
        """)
    
    # Histórico de conversas
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Input do usuário
    user_question = st.text_input("💬 Faça sua pergunta:", placeholder="Ex: Quais são os 5 diagnósticos mais comuns?")
    
    if st.button("🔍 Analisar", type="primary"):
        if user_question.strip():
            with st.spinner("Gerando consulta SQL..."):
                # Gerar SQL
                sql_query = generate_sql_from_question(user_question)
                
                # Debug: mostrar query gerada
                st.write("**Debug - Query gerada:**")
                st.code(sql_query, language="sql")
                
                # Validar SQL
                is_valid, validation_message = validate_sql_query(sql_query)
                
                if not is_valid:
                    st.error(f"❌ Query inválida: {validation_message}")
                    st.write(f"**Query original:** `{repr(sql_query)}`")
                    return
                
                # Executar SQL
                with st.spinner("Executando consulta..."):
                    df, error = execute_sql_query(sql_query)
                
                if error:
                    st.error(f"❌ Erro na consulta: {error}")
                    st.code(sql_query, language="sql")
                else:
                    # Adicionar ao histórico
                    st.session_state.chat_history.append({
                        'question': user_question,
                        'sql': sql_query,
                        'results': df,
                        'timestamp': datetime.now()
                    })
                    
                    # Mostrar resultado
                    st.success(f"✅ Consulta executada com sucesso! Encontrados {len(df)} registros.")
                    
                    # Mostrar SQL gerado
                    with st.expander("📝 SQL Gerado"):
                        st.code(sql_query, language="sql")
                    
                    # Mostrar resultados
                    if len(df) > 0:
                        st.dataframe(df, use_container_width=True)
                        
                        # Gerar explicação
                        with st.spinner("Analisando resultados..."):
                            explanation = explain_results(user_question, df)
                            st.markdown("### 📊 Análise dos Resultados")
                            st.markdown(explanation)
                        
                        # Opção de download
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="📥 Baixar CSV",
                            data=csv,
                            file_name=f"consulta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )
                    else:
                        st.warning("⚠️ Nenhum registro encontrado para esta consulta.")
        else:
            st.warning("Por favor, digite uma pergunta.")

def render_chat_history():
    """Renderiza o histórico de conversas"""
    if st.session_state.chat_history:
        st.markdown("### 📜 Histórico de Consultas")
        
        for i, chat in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(f"🕒 {chat['timestamp'].strftime('%H:%M')} - {chat['question'][:50]}..."):
                st.markdown(f"**Pergunta:** {chat['question']}")
                st.code(chat['sql'], language="sql")
                st.dataframe(chat['results'], use_container_width=True)
        
        if st.button("🗑️ Limpar Histórico"):
            st.session_state.chat_history = []
            st.rerun()

def render_database_info():
    """Renderiza informações sobre o banco de dados"""
    st.markdown("### 🗄️ Informações do Banco de Dados")
    
    try:
        conn = get_database_connection()
        
        # Estatísticas gerais
        stats_query = """
        SELECT 
            COUNT(*) as total_internacoes,
            MIN(ano_competencia) as ano_inicial,
            MAX(ano_competencia) as ano_final,
            COUNT(DISTINCT codigo_diagnostico_principal) as total_diagnosticos,
            COUNT(DISTINCT paciente_id) as total_pacientes
        FROM internacoes
        """
        
        stats_df = pd.read_sql_query(stats_query, conn)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Internações", f"{stats_df['total_internacoes'].iloc[0]:,}")
        
        with col2:
            st.metric("Período", f"{stats_df['ano_inicial'].iloc[0]}-{stats_df['ano_final'].iloc[0]}")
        
        with col3:
            st.metric("Diagnósticos Únicos", f"{stats_df['total_diagnosticos'].iloc[0]:,}")
        
        with col4:
            st.metric("Pacientes Únicos", f"{stats_df['total_pacientes'].iloc[0]:,}")
        
        with col5:
            # Última atualização
            last_update_query = "SELECT MAX(criado_em) as ultima_atualizacao FROM internacoes"
            last_update_df = pd.read_sql_query(last_update_query, conn)
            if last_update_df['ultima_atualizacao'].iloc[0]:
                last_update = pd.to_datetime(last_update_df['ultima_atualizacao'].iloc[0])
                st.metric("Última Atualização", last_update.strftime('%d/%m/%Y'))
            else:
                st.metric("Última Atualização", "N/A")
        
        conn.close()
        
    except Exception as e:
        st.error(f"Erro ao carregar informações do banco: {str(e)}")

def render(data):
    """Renderiza a página do Chatbot"""
    
    st.markdown("## 🤖 Chatbot - Análise de Dados")
    st.markdown("**Assistente inteligente para consultas no banco de dados de internações hospitalares**")
    st.markdown("---")
    
    # Verificar se a API está configurada
    if not GEMINI_API_KEY:
        st.error("⚠️ API Key do Gemini não configurada. Configure a chave para usar o chatbot.")
        return
    
    # Abas
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📜 Histórico", "🗄️ Banco de Dados"])
    
    with tab1:
        render_chat_interface()
    
    with tab2:
        render_chat_history()
    
    with tab3:
        render_database_info()
    
    # Rodapé
    st.markdown("---")
    st.markdown("⚠️ **Aviso:** Este chatbot executa consultas SQL no banco de dados. Apenas comandos SELECT são permitidos por segurança.")