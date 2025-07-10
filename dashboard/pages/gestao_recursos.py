import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def render(data):
    """
    Página de Gestão de Recursos
    
    Responsável: [NOME_DESENVOLVEDOR_6]
    Prazo: [DATA_PRAZO]
    
    Esta página deve conter:
    - Análise de custos por tipo de internação
    - Eficiência dos recursos
    - Análise de valor vs resultados
    """
    
    st.title("💰 Gestão de Recursos")
    st.markdown("---")
    
    # Placeholder para desenvolvimento
    st.info("🚧 **Área de Desenvolvimento - Gestão de Recursos**")
    st.markdown("""
    ### Tarefas para o Desenvolvedor:
    
    1. **Análise de Custos**:
       - Distribuição de valores por tipo de internação
       - Custo médio por diagnóstico
       - Análise de outliers financeiros
    
    2. **Eficiência Operacional**:
       - Custo por dia de internação
       - Relação custo vs permanência
       - Identificação de internações de alto custo
    
    3. **ROI da Atenção Básica**:
       - Comparação: prevenção vs tratamento
       - Custos evitáveis por melhor atenção primária
       - Análise de custo-efetividade
    
    4. **Análise por Caráter**:
       - Urgência vs eletiva
       - Diferenças nos custos
       - Padrões de utilização
    
    5. **Dashboards Financeiros**:
       - KPIs de gestão
       - Alertas de custo
       - Benchmarking
    
    6. **Projeções Orçamentárias**:
       - Estimativas de gastos futuros
       - Cenários de redução de custos
       - Planejamento financeiro
    """)
    
    # Exemplo de análise básica
    st.markdown("### Exemplo de Análise:")
    
    # Estatísticas financeiras
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Valor Total", f"R$ {data['val_tot'].sum():,.2f}")
    
    with col2:
        st.metric("Valor Médio", f"R$ {data['val_tot'].mean():,.2f}")
    
    with col3:
        st.metric("Valor Mediano", f"R$ {data['val_tot'].median():,.2f}")
    
    with col4:
        st.metric("Custo/Dia", f"R$ {(data['val_tot'] / data['dias_perm']).mean():,.2f}")
    
    # Análise por caráter da internação
    st.markdown("### Análise por Caráter da Internação:")
    
    if 'car_int' in data.columns:
        carater_map = {'01': 'Eletiva', '02': 'Urgência', '03': 'Acidente no trabalho', '04': 'Acidente no trânsito'}
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Distribuição por Caráter**")
            car_freq = data['car_int'].value_counts()
            st.dataframe(car_freq.to_frame().reset_index())
        
        with col2:
            st.markdown("**Valor Médio por Caráter**")
            valor_por_car = data.groupby('car_int')['val_tot'].mean().sort_values(ascending=False)
            st.dataframe(valor_por_car.to_frame().reset_index())
    
    # Análise de custo-efetividade
    st.markdown("### Análise de Custo-Efetividade:")
    
    # Criar faixas de custo
    data_temp = data.copy()
    data_temp['faixa_custo'] = pd.cut(data_temp['val_tot'], 
                                      bins=[0, 500, 1000, 5000, float('inf')], 
                                      labels=['Baixo (≤R$500)', 'Médio (R$501-1000)', 
                                             'Alto (R$1001-5000)', 'Muito Alto (>R$5000)'])
    
    custo_dist = data_temp['faixa_custo'].value_counts()
    st.dataframe(custo_dist.to_frame().reset_index())
    
    # Top diagnósticos mais caros
    st.markdown("### Top 10 Diagnósticos Mais Caros:")
    
    top_caros = data.groupby('diag_princ')['val_tot'].agg(['sum', 'mean', 'count']).sort_values('sum', ascending=False).head(10)
    top_caros.columns = ['Valor Total', 'Valor Médio', 'Quantidade']
    st.dataframe(top_caros.reset_index())
    
    # Análise de permanência vs custo
    st.markdown("### Relação Permanência vs Custo:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Correlação**")
        correlacao = data['dias_perm'].corr(data['val_tot'])
        st.metric("Correlação Permanência x Custo", f"{correlacao:.3f}")
    
    with col2:
        st.markdown("**Custo por Dia de Permanência**")
        custo_dia = data['val_tot'] / data['dias_perm']
        st.metric("Custo Médio/Dia", f"R$ {custo_dia.mean():.2f}")
    
    # Dados de exemplo para o desenvolvedor
    st.markdown("### Dados Disponíveis para Análise:")
    st.write(f"- Faixa de valores: R$ {data['val_tot'].min():.2f} - R$ {data['val_tot'].max():.2f}")
    st.write(f"- Internações com custo zero: {(data['val_tot'] == 0).sum()}")
    st.write(f"- Permanência média: {data['dias_perm'].mean():.1f} dias")
    
    st.markdown("### Amostra dos Dados:")
    st.dataframe(data[['val_tot', 'dias_perm', 'car_int', 'diag_princ']].head(10))
    
    st.markdown("### Observações para o Desenvolvedor:")
    st.info("""
    - Todos os valores estão em reais (R$)
    - Alguns registros podem ter valor zero (verificar se são válidos)
    - Considere análises de outliers para identificar casos atípicos
    - Útil criar dashboards interativos para diferentes níveis de gestão
    """)