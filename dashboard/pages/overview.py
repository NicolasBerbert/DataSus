import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

def render(data):
    """
    Página de Visão Geral - Overview do Dashboard
    
    Responsável: [NOME_DESENVOLVEDOR_1]
    Prazo: [DATA_PRAZO]
    
    Esta página deve conter:
    - Métricas principais (KPIs)
    - Gráficos resumo
    - Principais insights
    """
    
    st.title("📊 Visão Geral - Internações Hospitalares")
    st.markdown("---")
    
    # Placeholder para desenvolvimento
    st.info("🚧 **Área de Desenvolvimento - Overview**")
    st.markdown("""
    ### Tarefas para o Desenvolvedor:
    
    1. **Métricas Principais (KPIs)**:
       - Total de internações
       - Valor total gasto
       - Média de dias de permanência
       - Taxa de internações por 1000 habitantes
    
    2. **Gráficos Resumo**:
       - Gráfico de pizza com principais causas
       - Gráfico de barras com valores por mês
       - Linha temporal de internações
    
    3. **Cards Informativos**:
       - Resumo executivo
       - Principais achados
       - Alertas importantes
    
    4. **Filtros Básicos**:
       - Período
       - Faixa etária
       - Sexo
    """)
    
    # Exemplo de estrutura básica (para referência)
    st.markdown("### Exemplo de Estrutura:")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Internações", f"{len(data):,}")
    
    with col2:
        st.metric("Valor Total", f"R$ {data['val_tot'].sum():,.2f}")
    
    with col3:
        st.metric("Média Permanência", f"{data['dias_perm'].mean():.1f} dias")
    
    with col4:
        st.metric("Idade Média", f"{data['idade'].mean():.1f} anos")
    
    # Dados de exemplo para o desenvolvedor
    st.markdown("### Dados Disponíveis:")
    st.dataframe(data.head())
    
    st.markdown("### Colunas Disponíveis:")
    st.write(list(data.columns))