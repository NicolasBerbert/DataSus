import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render(data):
    """
    Página de Análise das Causas Principais
    
    Responsável: [NOME_DESENVOLVEDOR_2]
    Prazo: [DATA_PRAZO]
    
    Esta página deve conter:
    - Ranking das principais causas (CID-10)
    - Análise de causas sensíveis vs não sensíveis
    - Detalhamento por grupos de CID
    """
    
    st.title("🔍 Causas Principais de Internação")
    st.markdown("---")
    
    # Placeholder para desenvolvimento
    st.info("🚧 **Área de Desenvolvimento - Causas Principais**")
    st.markdown("""
    ### Tarefas para o Desenvolvedor:
    
    1. **Ranking de Causas**:
       - Top 20 CIDs mais frequentes
       - Percentual de cada causa
       - Gráfico de barras horizontais
    
    2. **Classificação por Sensibilidade**:
       - Identificar causas sensíveis à atenção básica
       - Comparar com causas não sensíveis
       - Criar categorização baseada em literatura médica
    
    3. **Análise por Grupos CID**:
       - Agrupamento por capítulos do CID-10
       - Distribuição por sistemas orgânicos
       - Análise de complexidade
    
    4. **Filtros Específicos**:
       - Por grupo de CID
       - Por complexidade
       - Por faixa etária
    
    5. **Insights Médicos**:
       - Interpretação clínica dos dados
       - Recomendações específicas por causa
       - Potencial de prevenção
    """)
    
    # Exemplo de análise básica
    st.markdown("### Exemplo de Análise:")
    
    # Análise das principais causas
    causas_freq = data['diag_princ'].value_counts().head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top 10 Diagnósticos Principais**")
        st.dataframe(causas_freq.to_frame().reset_index())
    
    with col2:
        st.markdown("**Distribuição por Valor**")
        valor_por_causa = data.groupby('diag_princ')['val_tot'].sum().sort_values(ascending=False).head(10)
        st.dataframe(valor_por_causa.to_frame().reset_index())
    
    # Dados de exemplo para o desenvolvedor
    st.markdown("### Dados Disponíveis para Análise:")
    st.write(f"- Total de CIDs únicos: {data['diag_princ'].nunique()}")
    st.write(f"- Diagnósticos mais comuns: {causas_freq.index[0]} ({causas_freq.iloc[0]} casos)")
    
    st.markdown("### Amostra dos Dados:")
    st.dataframe(data[['diag_princ', 'val_tot', 'dias_perm', 'idade', 'sexo']].head(10))