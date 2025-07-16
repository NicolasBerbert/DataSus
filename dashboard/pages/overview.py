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
    st.markdown("### Filtros")
    
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

def render_styled_metric(title, value, help_text, icon=None):
    """Renderiza uma métrica estilizada em card"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
    ">
        <h4 style="margin: 0 0 0.5rem 0; font-size: 0.9rem; opacity: 0.9;">{title}</h4>
        <div style="font-size: 1.8rem; font-weight: bold; margin: 0.5rem 0;">
            {value}
        </div>
        <div style="font-size: 0.8rem; opacity: 0.7;">
            {help_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_kpis(data):
    """Renderiza KPIs principais em cards estilizados"""
    st.markdown(f"<h2 style='text-align: center;'>Métricas Principais</h2>", unsafe_allow_html=True)

    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_internacoes = len(data)
        render_styled_metric(
            "Total de Internações",
            f"{total_internacoes:,}",
            "Número total de internações registradas"
        )
    
    with col2:
        valor_total = data['valor_total'].sum()
        render_styled_metric(
            "Valor Total",
            f"R$ {valor_total:,.2f}",
            "Valor total gasto com internações"
        )
    
    with col3:
        media_permanencia = data['dias_permanencia'].mean()
        render_styled_metric(
            "Permanência Média",
            f"{media_permanencia:.1f} dias",
            "Tempo médio de permanência hospitalar"
        )
    
    with col4:
        idade_media = data['idade_anos'].mean()
        render_styled_metric(
            "Idade Média",
            f"{idade_media:.1f} anos",
            "Idade média dos pacientes internados"
        )
    
    # Segunda linha de KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        custo_medio = data['valor_total'].mean()
        render_styled_metric(
            "Custo Médio por Internação",
            f"R$ {custo_medio:.2f}",
            "Custo médio por internação"
        )
    
    with col2:
        # Evitar divisão por zero e valores infinitos
        data_valida = data[(data['dias_permanencia'] > 0) & (data['valor_total'] > 0)]
        if len(data_valida) > 0:
            custo_dia = (data_valida['valor_total'] / data_valida['dias_permanencia']).mean()
            custo_dia_text = f"R$ {custo_dia:.2f}"
        else:
            custo_dia_text = "R$ 0,00"
        
        render_styled_metric(
            "Custo Médio por Dia",
            custo_dia_text,
            "Custo médio por dia de internação"
        )
    
    with col3:
        internacoes_urgencia = len(data[data['carater_internacao'] == 'Urgência'])
        perc_urgencia = (internacoes_urgencia / len(data)) * 100 if len(data) > 0 else 0
        render_styled_metric(
            "Percentual de Urgência",
            f"{perc_urgencia:.1f}%",
            "Percentual de internações de urgência"
        )
    
    with col4:
        idosos = len(data[data['idade_anos'] >= 60])
        perc_idosos = (idosos / len(data)) * 100 if len(data) > 0 else 0
        render_styled_metric(
            "Percentual de Idosos (60+)",
            f"{perc_idosos:.1f}%",
            "Percentual de pacientes idosos"
        )

def render_principais_causas(data):
    """Renderiza gráfico de principais causas"""
    st.markdown(f"<h2 style='text-align: center;'>Distribuição por Principais Causas</h2>", unsafe_allow_html=True)
    with st.container(border = True):
        st.markdown(f"<h3 style='text-align: center;'>Top Causas Mais Comuns</h3>", unsafe_allow_html=True)
        
        # Top 10 causas mais comuns
        top_causas = data['diagnostico_principal'].value_counts().head(10)
        
        # Gráfico de pizza com tons de azul
        cores_azuis = [
            '#1e3a8a', '#1e40af', '#1d4ed8', '#2563eb', '#3b82f6',
            '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff'
        ]
        
        fig = px.pie(
            values=top_causas.values,
            names=top_causas.index,
            color_discrete_sequence=cores_azuis
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
    # Ranking detalhado em cards horizontais
    st.markdown(f"<h2 style='text-align: center;'>Ranking Detalhado</h2>", unsafe_allow_html=True)

    
    for i, (diagnostico, casos) in enumerate(top_causas.items(), 1):
        percentual = (casos / len(data) * 100)
        
        # Gradiente de azul escuro para azul médio, mantendo visibilidade com texto branco
        cores_azul_gradiente = [
            "#0077CC", "#1A93FF", "#339FFF", "#4DABFF", "#66B7FF",
            "#80C3FF", "#99CFFF", "#B3DBFF", "#CCE7FF", "#E6F3FF"
        ]
        cor_fundo = cores_azul_gradiente[i-1] if i <= len(cores_azul_gradiente) else "#0f172a"
        cor_borda = "#2563eb"
        
        st.markdown(f"""
        <div style="
            background: {cor_fundo};
            padding: 1rem 1.5rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
            border-left: 4px solid {cor_borda};
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center;">
                    <div style="
                        background: {cor_borda};
                        color: white;
                        width: 40px;
                        height: 40px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 1rem;
                        font-weight: bold;
                        font-size: 1.2rem;
                    ">
                        {i}º
                    </div>
                    <div>
                        <h4 style="margin: 0; font-size: 1rem; color: #1a1a1a;">
                            {diagnostico}
                        </h4>
                    </div>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 1.4rem; font-weight: bold; color: #1a1a1a;">
                        {casos:,} casos
                    </div>
                    <div style="font-size: 0.9rem; color: rgba(26, 26, 26, 0.8);">
                        {percentual:.1f}% do total
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    """Renderiza análise por tipo de internação"""
    st.markdown(f"<h2 style='text-align: center;'>Análise por Tipo de Internação</h2>", unsafe_allow_html=True)

    
    col1, col2 = st.columns(2)
    
    with col1.container(border = True):
        st.markdown(f"<h3 style='text-align: center;'>Distribuição por Tipo de Internação</h3>", unsafe_allow_html=True)

        # Distribuição por tipo
        tipo_counts = data['carater_internacao'].value_counts()

        fig = px.bar(
            x=tipo_counts.index,
            y=tipo_counts.values,
            color_discrete_sequence=['#2563eb', '#60a5fa']
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2.container(border = True):
        st.markdown(f"<h3 style='text-align: center;'>Custo Médio por Tipo de Internação</h3>", unsafe_allow_html=True)
        # Custo médio por tipo
        custo_tipo = data.groupby('carater_internacao')['valor_total'].mean()
        
        fig = px.bar(
            x=custo_tipo.index,
            y=custo_tipo.values,
            color_discrete_sequence=['#1e40af', '#93c5fd']
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)




    


def render(data):
    """Renderiza a página de Visão Geral"""
    st.markdown(f"<h1 style='text-align: center;'>Visão Geral</h1>", unsafe_allow_html=True)
    
    # Renderizar filtros
    filters = render_filters()
    
    # Aplicar filtros aos dados
    filtered_data = apply_filters(data, filters)
    
    # Mostrar informações sobre filtros aplicados
    if len(filtered_data) < len(data):
        st.info(f"Mostrando {len(filtered_data):,} de {len(data):,} registros (filtros aplicados)")
    
    st.markdown("---")
    
    # Renderizar apenas as visualizações principais da visão geral
    render_kpis(filtered_data)
    st.markdown("---")
    
    render_principais_causas(filtered_data)