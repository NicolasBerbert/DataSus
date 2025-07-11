import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

def apply_filters(data, filters):
    """Aplica filtros aos dados"""
    filtered_data = data.copy()
    
    # Filtro por período
    if filters['periodo'] != 'Todos':
        if filters['periodo'] == 'Janeiro 2025':
            filtered_data = filtered_data[(filtered_data['ano_competencia'] == 2025) & (filtered_data['mes_competencia'] == 1)]
        elif filters['periodo'] == 'Fevereiro 2025':
            filtered_data = filtered_data[(filtered_data['ano_competencia'] == 2025) & (filtered_data['mes_competencia'] == 2)]
        elif filters['periodo'] == 'Março 2025':
            filtered_data = filtered_data[(filtered_data['ano_competencia'] == 2025) & (filtered_data['mes_competencia'] == 3)]
    
    # Filtro por faixa etária
    if filters['faixa_etaria'] != 'Todas':
        if filters['faixa_etaria'] == '0-18 anos':
            filtered_data = filtered_data[filtered_data['idade_anos'] <= 18]
        elif filters['faixa_etaria'] == '19-59 anos':
            filtered_data = filtered_data[(filtered_data['idade_anos'] >= 19) & (filtered_data['idade_anos'] <= 59)]
        elif filters['faixa_etaria'] == '60+ anos':
            filtered_data = filtered_data[filtered_data['idade_anos'] >= 60]
    
    # Filtro por sexo
    if filters['sexo'] != 'Todos':
        if filters['sexo'] == 'Masculino':
            filtered_data = filtered_data[filtered_data['sexo'] == 'Masculino']
        elif filters['sexo'] == 'Feminino':
            filtered_data = filtered_data[filtered_data['sexo'] == 'Feminino']
    
    # Filtro por tipo de internação
    if filters['tipo_internacao'] != 'Todos':
        if filters['tipo_internacao'] == 'Eletiva':
            filtered_data = filtered_data[filtered_data['carater_internacao'] == 'Eletiva']
        elif filters['tipo_internacao'] == 'Urgência':
            filtered_data = filtered_data[filtered_data['carater_internacao'] == 'Urgência']
    
    return filtered_data

def render_filters():
    """Renderiza os filtros da página"""
    st.markdown("### 🔍 Filtros")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        periodo = st.selectbox(
            "Período",
            ["Todos", "Janeiro 2025", "Fevereiro 2025", "Março 2025"],
            key="overview_periodo"
        )
    
    with col2:
        faixa_etaria = st.selectbox(
            "Faixa Etária",
            ["Todas", "0-18 anos", "19-59 anos", "60+ anos"],
            key="overview_faixa_etaria"
        )
    
    with col3:
        sexo = st.selectbox(
            "Sexo",
            ["Todos", "Masculino", "Feminino"],
            key="overview_sexo"
        )
    
    with col4:
        tipo_internacao = st.selectbox(
            "Tipo de Internação",
            ["Todos", "Eletiva", "Urgência"],
            key="overview_tipo_internacao"
        )
    
    return {
        'periodo': periodo,
        'faixa_etaria': faixa_etaria,
        'sexo': sexo,
        'tipo_internacao': tipo_internacao
    }

def render_options_selector():
    """Renderiza seletor de opções de visualização"""
    st.markdown("### 📊 Escolha as Informações para Visualizar")
    
    available_options = [
        "📈 Métricas Principais (KPIs)",
        "🥧 Distribuição por Principais Causas",
        "📊 Análise Temporal de Internações",
        "💰 Análise de Custos e Valores",
        "👥 Perfil Demográfico dos Pacientes",
        "🏥 Análise por Tipo de Internação",
        "⏱️ Tempo de Permanência",
        "🗺️ Top Municípios por Internações",
        "⚡ Insights e Alertas Importantes"
    ]
    
    # Usar multiselect para permitir múltiplas seleções
    selected_options = st.multiselect(
        "Selecione as visualizações que deseja ver:",
        available_options,
        default=available_options[:4],  # Primeiras 4 opções selecionadas por padrão
        key="overview_selected_options"
    )
    
    return selected_options

def render_kpis(data):
    """Renderiza KPIs principais"""
    st.markdown("### 📈 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_internacoes = len(data)
        st.metric(
            "Total de Internações",
            f"{total_internacoes:,}",
            delta=None,
            help="Número total de internações registradas"
        )
    
    with col2:
        valor_total = data['valor_total'].sum()
        st.metric(
            "Valor Total",
            f"R$ {valor_total:,.2f}",
            delta=None,
            help="Valor total gasto com internações"
        )
    
    with col3:
        media_permanencia = data['dias_permanencia'].mean()
        st.metric(
            "Média de Permanência",
            f"{media_permanencia:.1f} dias",
            delta=None,
            help="Tempo médio de permanência hospitalar"
        )
    
    with col4:
        idade_media = data['idade_anos'].mean()
        st.metric(
            "Idade Média",
            f"{idade_media:.1f} anos",
            delta=None,
            help="Idade média dos pacientes internados"
        )
    
    # Segunda linha de KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        custo_medio = data['valor_total'].mean()
        st.metric(
            "Custo Médio/Internação",
            f"R$ {custo_medio:.2f}",
            help="Custo médio por internação"
        )
    
    with col2:
        custo_dia = (data['valor_total'] / data['dias_permanencia']).mean()
        st.metric(
            "Custo Médio/Dia",
            f"R$ {custo_dia:.2f}",
            help="Custo médio por dia de internação"
        )
    
    with col3:
        internacoes_urgencia = len(data[data['carater_internacao'] == 'Urgência'])
        perc_urgencia = (internacoes_urgencia / len(data)) * 100 if len(data) > 0 else 0
        st.metric(
            "% Urgência",
            f"{perc_urgencia:.1f}%",
            help="Percentual de internações de urgência"
        )
    
    with col4:
        idosos = len(data[data['idade_anos'] >= 60])
        perc_idosos = (idosos / len(data)) * 100 if len(data) > 0 else 0
        st.metric(
            "% Idosos (60+)",
            f"{perc_idosos:.1f}%",
            help="Percentual de pacientes idosos"
        )

def render_principais_causas(data):
    """Renderiza gráfico de principais causas"""
    st.markdown("### 🥧 Distribuição por Principais Causas")
    
    # Top 10 causas mais comuns
    top_causas = data['diagnostico_principal'].value_counts().head(10)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico de pizza
        fig = px.pie(
            values=top_causas.values,
            names=top_causas.index,
            title="Top 10 Diagnósticos Mais Frequentes"
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Tabela com números
        st.markdown("**Ranking Detalhado:**")
        df_causas = pd.DataFrame({
            'Diagnóstico': top_causas.index,
            'Casos': top_causas.values,
            'Percentual': (top_causas.values / len(data) * 100).round(1)
        })
        st.dataframe(df_causas, use_container_width=True)

def render_analise_temporal(data):
    """Renderiza análise temporal"""
    st.markdown("### 📊 Análise Temporal de Internações")
    
    # Preparar dados temporais
    data_temp = data.copy()
    data_temp['periodo'] = data_temp['ano_competencia'].astype(str) + '-' + data_temp['mes_competencia'].astype(str).str.zfill(2)
    
    # Agrupar por período
    internacoes_tempo = data_temp.groupby('periodo').size().reset_index(name='internacoes')
    valores_tempo = data_temp.groupby('periodo')['valor_total'].sum().reset_index(name='valor_total')
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de linha - Internações
        fig = px.line(
            internacoes_tempo,
            x='periodo',
            y='internacoes',
            title="Número de Internações por Período",
            markers=True
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Gráfico de linha - Valores
        fig = px.line(
            valores_tempo,
            x='periodo',
            y='valor_total',
            title="Valor Total por Período",
            markers=True
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def render_analise_custos(data):
    """Renderiza análise de custos"""
    st.markdown("### 💰 Análise de Custos e Valores")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição de custos
        fig = px.histogram(
            data,
            x='valor_total',
            nbins=30,
            title="Distribuição de Custos das Internações"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top 10 diagnósticos mais caros
        custos_cid = data.groupby('diagnostico_principal')['valor_total'].sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=custos_cid.values,
            y=custos_cid.index,
            orientation='h',
            title="Top 10 Diagnósticos por Custo Total"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def render_perfil_demografico(data):
    """Renderiza perfil demográfico"""
    st.markdown("### 👥 Perfil Demográfico dos Pacientes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por idade
        fig = px.histogram(
            data,
            x='idade_anos',
            nbins=20,
            title="Distribuição por Idade"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribuição por sexo
        sexo_counts = data['sexo'].value_counts()
        
        fig = px.pie(
            values=sexo_counts.values,
            names=sexo_counts.index,
            title="Distribuição por Sexo"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def render_tipo_internacao(data):
    """Renderiza análise por tipo de internação"""
    st.markdown("### 🏥 Análise por Tipo de Internação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por tipo
        tipo_counts = data['carater_internacao'].value_counts()
        
        fig = px.bar(
            x=tipo_counts.index,
            y=tipo_counts.values,
            title="Distribuição por Tipo de Internação"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Custo médio por tipo
        custo_tipo = data.groupby('carater_internacao')['valor_total'].mean()
        
        fig = px.bar(
            x=custo_tipo.index,
            y=custo_tipo.values,
            title="Custo Médio por Tipo de Internação"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def render_tempo_permanencia(data):
    """Renderiza análise de tempo de permanência"""
    st.markdown("### ⏱️ Tempo de Permanência")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição de permanência
        fig = px.histogram(
            data,
            x='dias_permanencia',
            nbins=30,
            title="Distribuição de Tempo de Permanência"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Permanência por faixa etária
        data_temp = data.copy()
        data_temp['faixa_etaria'] = pd.cut(data_temp['idade_anos'], 
                                          bins=[0, 18, 60, 100], 
                                          labels=['0-18', '19-59', '60+'])
        
        perm_idade = data_temp.groupby('faixa_etaria')['dias_permanencia'].mean()
        
        fig = px.bar(
            x=perm_idade.index,
            y=perm_idade.values,
            title="Permanência Média por Faixa Etária"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def render_top_municipios(data):
    """Renderiza top municípios"""
    st.markdown("### 🗺️ Top Municípios por Internações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Top 10 municípios por quantidade
        top_munic = data['codigo_municipio_residencia'].value_counts().head(10)
        
        fig = px.bar(
            x=top_munic.values,
            y=top_munic.index,
            orientation='h',
            title="Top 10 Municípios por Quantidade"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Top 10 municípios por custo
        custo_munic = data.groupby('codigo_municipio_residencia')['valor_total'].sum().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=custo_munic.values,
            y=custo_munic.index,
            orientation='h',
            title="Top 10 Municípios por Custo Total"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def render_insights_alertas(data):
    """Renderiza insights e alertas"""
    st.markdown("### ⚡ Insights e Alertas Importantes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🔍 Insights Principais")
        
        # Calcular insights
        total_internacoes = len(data)
        valor_total = data['valor_total'].sum()
        causa_principal = data['diagnostico_principal'].value_counts().index[0] if len(data) > 0 else "N/A"
        perc_urgencia = (len(data[data['carater_internacao'] == 'Urgência']) / len(data)) * 100 if len(data) > 0 else 0
        
        st.info(f"""
        **Resumo Executivo:**
        - Total de {total_internacoes:,} internações registradas
        - Investimento total de R$ {valor_total:,.2f}
        - Principal causa: {causa_principal}
        - {perc_urgencia:.1f}% das internações são de urgência
        """)
    
    with col2:
        st.markdown("#### 🚨 Alertas e Recomendações")
        
        # Alertas baseados nos dados
        alertas = []
        
        if perc_urgencia > 70:
            alertas.append("⚠️ Alto percentual de internações de urgência")
        
        custo_medio = data['valor_total'].mean()
        if custo_medio > 1000:
            alertas.append("💰 Custo médio por internação elevado")
        
        idosos_perc = (len(data[data['idade_anos'] >= 60]) / len(data)) * 100 if len(data) > 0 else 0
        if idosos_perc > 40:
            alertas.append("👴 Alto percentual de pacientes idosos")
        
        if alertas:
            for alerta in alertas:
                st.warning(alerta)
        else:
            st.success("✅ Nenhum alerta crítico identificado")

def render(data):
    """Renderiza a página de Visão Geral"""
    
    st.markdown("## 📊 Visão Geral")
    
    # Renderizar seletor de opções
    selected_options = render_options_selector()
    
    st.markdown("---")
    
    # Renderizar filtros
    filters = render_filters()
    
    # Aplicar filtros aos dados
    filtered_data = apply_filters(data, filters)
    
    # Mostrar informações sobre filtros aplicados
    if len(filtered_data) < len(data):
        st.info(f"📊 Mostrando {len(filtered_data):,} de {len(data):,} registros (filtros aplicados)")
    
    st.markdown("---")
    
    # Renderizar visualizações selecionadas
    if "📈 Métricas Principais (KPIs)" in selected_options:
        render_kpis(filtered_data)
        st.markdown("---")
    
    if "🥧 Distribuição por Principais Causas" in selected_options:
        render_principais_causas(filtered_data)
        st.markdown("---")
    
    if "📊 Análise Temporal de Internações" in selected_options:
        render_analise_temporal(filtered_data)
        st.markdown("---")
    
    if "💰 Análise de Custos e Valores" in selected_options:
        render_analise_custos(filtered_data)
        st.markdown("---")
    
    if "👥 Perfil Demográfico dos Pacientes" in selected_options:
        render_perfil_demografico(filtered_data)
        st.markdown("---")
    
    if "🏥 Análise por Tipo de Internação" in selected_options:
        render_tipo_internacao(filtered_data)
        st.markdown("---")
    
    if "⏱️ Tempo de Permanência" in selected_options:
        render_tempo_permanencia(filtered_data)
        st.markdown("---")
    
    if "🗺️ Top Municípios por Internações" in selected_options:
        render_top_municipios(filtered_data)
        st.markdown("---")
    
    if "⚡ Insights e Alertas Importantes" in selected_options:
        render_insights_alertas(filtered_data)