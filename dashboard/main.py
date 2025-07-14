import streamlit as st
import sqlite3
import pandas as pd
import os
import sys

# Adiciona o diretório raiz ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Importa as páginas do dashboard
from pages import (
    overview,
    causas_principais,
    analise_demografica,
    analise_geografica,
    gestao_recursos,
    recomendacoes,
    machine_learning
)

# Configuração da página
st.set_page_config(
    page_title="Dashboard - Internações Hospitalares por Causas Sensíveis",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Função para conectar ao banco de dados
@st.cache_resource
def get_database_connection():
    """Conecta ao banco de dados SQLite"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'internacoes_datasus.db')
    return sqlite3.connect(db_path, check_same_thread=False)

# Função para carregar dados principais
@st.cache_data
def load_main_data():
    """Carrega dados principais do banco normalizado com descrições legíveis"""
    conn = get_database_connection()
    query = """
        SELECT 
            i.id as internacao_id,
            i.numero_aih,
            i.ano_competencia,
            i.mes_competencia,
            i.data_internacao,
            i.data_saida,
            i.dias_permanencia,
            i.dias_uti_total,
            i.gestacao_risco,
            
            -- Dados do paciente
            p.idade_anos,
            s.descricao as sexo,
            p.codigo_municipio_residencia,
            m.nome as municipio_residencia,

            -- Dados clínicos com descrições
            cid.descricao as diagnostico_principal,
            cid.capitulo as capitulo_cid,
            cid.sensivel_atencao_basica,
            ci.descricao as carater_internacao,
            
            -- Dados do estabelecimento
            e.codigo_cnes,
            esp.descricao as especialidade,
            comp.descricao as complexidade,
            tg.descricao as tipo_gestao,
            
            -- Valores financeiros
            vf.valor_total,
            vf.valor_servicos_hospitalares,
            vf.valor_servicos_profissionais,
            vf.valor_uti,
            vf.valor_em_dolares
            
        FROM internacoes i
        LEFT JOIN pacientes p ON i.paciente_id = p.id
        LEFT JOIN municipios m ON p.codigo_municipio_residencia = m.codigo
        LEFT JOIN sexo s ON p.codigo_sexo = s.codigo
        LEFT JOIN cid_diagnosticos cid ON i.codigo_diagnostico_principal = cid.codigo
        LEFT JOIN carater_internacao ci ON printf('%02d', i.codigo_carater_internacao) = ci.codigo
        LEFT JOIN estabelecimentos e ON i.estabelecimento_id = e.id
        LEFT JOIN especialidades esp ON e.codigo_especialidade = esp.codigo
        LEFT JOIN complexidade comp ON e.codigo_complexidade = comp.codigo
        LEFT JOIN tipos_gestao tg ON e.codigo_tipo_gestao = tg.codigo
        LEFT JOIN valores_financeiros vf ON i.id = vf.internacao_id
        
        WHERE i.codigo_diagnostico_principal IS NOT NULL
        AND p.idade_anos IS NOT NULL
        AND vf.valor_total IS NOT NULL
        AND vf.valor_total > 0
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Função de navegação com pills
def navigation():
    # Header do dashboard
    st.title("🏥 Dashboard - Internações Hospitalares")
    st.markdown("**Causas Sensíveis à Atenção Básica**")
    
    # Informações da persona
    with st.expander("👨‍⚕️ Persona - Dr. Roberto", expanded=False):
        st.markdown("""
        **Dr. Roberto** - Gestor de Unidade Básica de Saúde
        
        *"Como gestor de UBS, quero entender as causas mais comuns de internações evitáveis para planejar melhor os recursos da unidade."*
        """)
    
    st.markdown("---")
    
    # Navegação com pills
    pages = [
        "📊 Visão Geral",
        "🔍 Causas Principais", 
        "👥 Análise Demográfica",
        "🗺️ Análise Geográfica",
        "🤖 Machine Learning",
        "💰 Gestão de Recursos",
        "💡 Recomendações"
    ]
    
    # Inicializa o estado da sessão se não existir
    if 'selected_page' not in st.session_state:
        st.session_state.selected_page = pages[0]
    
    # Cria as pills de navegação
    selected_page = st.pills(
        "Navegação",
        pages,
        selection_mode="single",
        default=st.session_state.selected_page
    )
    
    # Atualiza o estado da sessão
    if selected_page:
        st.session_state.selected_page = selected_page
        return selected_page
    else:
        return st.session_state.selected_page

# Função principal
def main():
    # Navegação com pills
    selected_page = navigation()
    
    st.markdown("---")
    
    # Carrega dados principais
    try:
        data = load_main_data()
        
        # Roteamento das páginas
        if selected_page == "📊 Visão Geral":
            overview.render(data)
        elif selected_page == "🔍 Causas Principais":
            causas_principais.render(data)
        elif selected_page == "👥 Análise Demográfica":
            analise_demografica.render(data)
        elif selected_page == "🗺️ Análise Geográfica":
            analise_geografica.render(data)
        elif selected_page == "🤖 Machine Learning":
            machine_learning.render(data)
        elif selected_page == "💰 Gestão de Recursos":
            gestao_recursos.render(data)
        elif selected_page == "💡 Recomendações":
            recomendacoes.render(data)
            
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        st.info("Certifique-se de que o banco de dados foi criado executando o script `scripts/create_database.py`")

if __name__ == "__main__":
    main()