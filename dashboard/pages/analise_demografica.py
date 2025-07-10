import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render(data):
    """
    Página de Análise Demográfica
    
    Responsável: [NOME_DESENVOLVEDOR_3]
    Prazo: [DATA_PRAZO]
    
    Esta página deve conter:
    - Distribuição por faixa etária
    - Análise por sexo
    - Padrões demográficos específicos
    """
    
    st.title("👥 Análise Demográfica")
    st.markdown("---")
    
    # Placeholder para desenvolvimento
    st.info("🚧 **Área de Desenvolvimento - Análise Demográfica**")
    st.markdown("""
    ### Tarefas para o Desenvolvedor:
    
    1. **Distribuição por Idade**:
       - Histograma de idades
       - Faixas etárias (0-18, 19-59, 60+)
       - Médias e medianas por grupo
    
    2. **Análise por Sexo**:
       - Distribuição geral por sexo
       - Causas específicas por sexo
       - Diferenças nos valores gastos
    
    3. **Pirâmide Etária**:
       - Visualização por sexo e idade
       - Comparação com população geral
       - Identificação de grupos de risco
    
    4. **Correlações Demográficas**:
       - Idade vs permanência hospitalar
       - Sexo vs tipo de internação
       - Padrões etários por causa
    
    5. **Perfil do Paciente**:
       - Características típicas
       - Grupos prioritários
       - Recomendações específicas
    """)
    
    # Exemplo de análise básica
    st.markdown("### Exemplo de Análise:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Distribuição por Sexo**")
        sexo_dist = data['sexo'].value_counts()
        sexo_labels = {1: 'Masculino', 3: 'Feminino'}
        sexo_dist.index = sexo_dist.index.map(sexo_labels)
        st.bar_chart(sexo_dist)
    
    with col2:
        st.markdown("**Estatísticas de Idade**")
        st.metric("Idade Média", f"{data['idade'].mean():.1f} anos")
        st.metric("Idade Mediana", f"{data['idade'].median():.1f} anos")
        st.metric("Idade Min/Max", f"{data['idade'].min():.0f} / {data['idade'].max():.0f} anos")
    
    # Faixas etárias
    st.markdown("### Faixas Etárias:")
    
    # Criar faixas etárias
    data_temp = data.copy()
    data_temp['faixa_etaria'] = pd.cut(data_temp['idade'], 
                                       bins=[0, 18, 60, 100], 
                                       labels=['0-18 anos', '19-59 anos', '60+ anos'])
    
    faixa_dist = data_temp['faixa_etaria'].value_counts()
    st.dataframe(faixa_dist.to_frame().reset_index())
    
    # Dados de exemplo para o desenvolvedor
    st.markdown("### Dados Disponíveis para Análise:")
    st.write(f"- Idade mínima: {data['idade'].min():.0f} anos")
    st.write(f"- Idade máxima: {data['idade'].max():.0f} anos")
    st.write(f"- Distribuição por sexo: {data['sexo'].value_counts().to_dict()}")
    
    st.markdown("### Amostra dos Dados:")
    st.dataframe(data[['idade', 'sexo', 'val_tot', 'dias_perm', 'diag_princ']].head(10))