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
    analise_temporal,
    gestao_recursos,
    recomendacoes
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
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'internacoes_datasus.db')
    return sqlite3.connect(db_path, check_same_thread=False)

# Função para carregar dados principais
@st.cache_data
def load_main_data():
    """Carrega dados principais do banco"""
    conn = get_database_connection()
    query = """
        SELECT 
            diag_princ,
            munic_res,
            idade,
            sexo,
            val_tot,
            dias_perm,
            dt_inter,
            dt_saida,
            ano_cmpt,
            mes_cmpt,
            car_int
        FROM internacoes
        WHERE diag_princ IS NOT NULL
        AND idade IS NOT NULL
        AND val_tot IS NOT NULL
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
        "📈 Análise Temporal",
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
        elif selected_page == "📈 Análise Temporal":
            analise_temporal.render(data)
        elif selected_page == "💰 Gestão de Recursos":
            gestao_recursos.render(data)
        elif selected_page == "💡 Recomendações":
            recomendacoes.render(data)
            
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        st.info("Certifique-se de que o banco de dados foi criado executando o script `scripts/create_database.py`")

if __name__ == "__main__":
    main()