import streamlit as st
import pandas as pd
import plotly.express as px
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
    
    # Filtro por sexo
    if filters['sexo'] != 'Todos':
        if filters['sexo'] == 'Masculino':
            filtered_data = filtered_data[filtered_data['sexo'] == 'Masculino']
        elif filters['sexo'] == 'Feminino':
            filtered_data = filtered_data[filtered_data['sexo'] == 'Feminino']
    
    # Filtro por faixa etária
    if filters['faixa_etaria'] != 'Todas':
        if filters['faixa_etaria'] == '0-17':
            filtered_data = filtered_data[filtered_data['idade_anos'] <= 17]
        elif filters['faixa_etaria'] == '18-59':
            filtered_data = filtered_data[(filtered_data['idade_anos'] >= 18) & (filtered_data['idade_anos'] <= 59)]
        elif filters['faixa_etaria'] == '60+':
            filtered_data = filtered_data[filtered_data['idade_anos'] >= 60]
    
    # Filtro por município
    if filters['municipio'] != 'Todos':
        filtered_data = filtered_data[filtered_data['municipio_residencia'] == filters['municipio']]
    
    return filtered_data

def render_filters(data):
    """Renderiza os filtros da página"""
    st.markdown("### Filtros")
    
    col_periodo, col_sexo, col_faixa, col_mun = st.columns(4)
    
    with col_periodo:
        periodo = st.selectbox(
            "Período",
            ["Todos", "Janeiro 2025", "Fevereiro 2025", "Março 2025"],
            key="causas_periodo"
        )
    
    with col_sexo:
        sexo = st.selectbox("Sexo", ["Todos", "Masculino", "Feminino"], key="causas_sexo")
    
    with col_faixa:
        faixa_etaria = st.selectbox("Faixa Etária", ["Todas", "0-17", "18-59", "60+"], key="causas_faixa")
    
    with col_mun:
        municipio = st.selectbox(
            "Município de Residência",
            ["Todos"] + sorted(data['municipio_residencia'].dropna().unique()),
            key="causas_municipio"
        )
    
    return {
        'periodo': periodo,
        'sexo': sexo,
        'faixa_etaria': faixa_etaria,
        'municipio': municipio
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

def render(data):
    """Renderiza a página de Causas Principais"""
    
    st.markdown("## Causas Principais de Internação")
    
    # Renderizar filtros
    filters = render_filters(data)
    
    # Aplicar filtros aos dados
    filtered_data = apply_filters(data, filters)

    
    # Mostrar informações sobre filtros aplicados
    if len(filtered_data) < len(data):
        st.info(f"Mostrando {len(filtered_data):,} de {len(data):,} registros (filtros aplicados)")
    
    total_internacoes = len(filtered_data)
    if total_internacoes == 0:
        st.warning("Nenhuma internação encontrada para os filtros selecionados.")
        return
    
    st.markdown("---")

    # Cria coluna faixa_etaria sem warning
    bins = [0, 18, 60, 130]
    labels = ['0-17', '18-59', '60+']
    df_filtrado = filtered_data.copy()
    df_filtrado['faixa_etaria'] = pd.cut(df_filtrado['idade_anos'], bins=bins, labels=labels, right=False)

    # ========== CARDS DE KPIs ==========
    st.markdown("### Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_styled_metric(
            "Total de Internações",
            f"{total_internacoes:,}",
            "Número total de internações registradas"
        )
    
    with col2:
        media_custo = df_filtrado['valor_total'].mean() if 'valor_total' in df_filtrado.columns else 0
        render_styled_metric(
            "Custo Médio",
            f"R$ {media_custo:,.2f}",
            "Valor médio gasto por internação"
        )
    
    with col3:
        total_sensivel = df_filtrado['sensivel_atencao_basica'].sum() if 'sensivel_atencao_basica' in df_filtrado.columns else 0
        percentual_sensivel = (total_sensivel / total_internacoes) * 100 if total_internacoes > 0 else 0
        render_styled_metric(
            "Percentual Sensível à AB",
            f"{percentual_sensivel:.1f}%",
            "Percentual sensível à atenção básica"
        )
    
    with col4:
        media_permanencia = df_filtrado['dias_permanencia'].mean() if 'dias_permanencia' in df_filtrado.columns else 0
        render_styled_metric(
            "Permanência Média",
            f"{media_permanencia:.1f} dias",
            "Tempo médio de permanência hospitalar"
        )

    st.markdown("---")
    
    # ========== TOP 10 CAUSAS ==========
    st.markdown("### Top 10 Causas de Internação")
    
    top_10_causas = df_filtrado['diagnostico_principal'].value_counts().nlargest(10)
    percentuais_causas = (top_10_causas / total_internacoes) * 100
    
    # Gráfico de barras horizontal com cores azuis
    fig_ranking = px.bar(
        x=top_10_causas.values,
        y=top_10_causas.index,
        orientation='h',
        title='Top 10 Diagnósticos Mais Frequentes',
        labels={'x':'Número de Internações', 'y':'CID-10'},
        color=top_10_causas.values,
        color_continuous_scale=['#eff6ff', '#1e3a8a']
    )
    fig_ranking.update_layout(height=400, showlegend=False)
    fig_ranking.update_coloraxes(showscale=False)
    st.plotly_chart(fig_ranking, use_container_width=True)
    
    # Ranking detalhado em cards horizontais
    st.markdown("### Ranking Detalhado")
    
    for i, (diagnostico, casos) in enumerate(top_10_causas.items(), 1):
        percentual = (casos / total_internacoes * 100)
        
        # Cores em tons de azul para as posições
        cores_azuis_ranking = [
            "#1e3a8a", "#1e40af", "#1d4ed8", "#2563eb", "#3b82f6",
            "#60a5fa", "#93c5fd", "#bfdbfe", "#dbeafe", "#e0f2fe"
        ]
        cor = cores_azuis_ranking[i-1] if i <= len(cores_azuis_ranking) else "#64748b"
        
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
    
    # ========== SENSIBILIDADE + FAIXA ETÁRIA ==========
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Sensibilidade à Atenção Básica")
        sensivel_counts = df_filtrado['sensivel_atencao_basica'].value_counts()
        if not sensivel_counts.empty:
            sensivel = sensivel_counts.get(1, 0)
            nao_sensivel = sensivel_counts.get(0, 0)
            labels = ["Sensíveis", "Não Sensíveis"]
            values = [sensivel, nao_sensivel]

            fig_sensibilidade = px.pie(
                names=labels, values=values,
                title='Distribuição de Internações',
                hole=0.4,
                color_discrete_sequence=['#1e40af', '#60a5fa']
            )
            st.plotly_chart(fig_sensibilidade, use_container_width=True)

        with st.expander("ℹ️ O que são internações sensíveis à atenção básica?"):
            st.markdown("""
            **Internações por Condições Sensíveis à Atenção Básica (ICSAB)** são hospitalizações que poderiam ser evitadas com um cuidado eficaz e oportuno na **atenção primária à saúde**.

            👉 Exemplos comuns:
            - Asma
            - Diabetes descompensado
            - Hipertensão
            - Pneumonia inicial
            - Infecção urinária simples

            Quando bem estruturada, a atenção básica **previne** ou **controla** essas doenças, evitando que evoluam a ponto de necessitar internação.

            Isso torna o indicador uma forma importante de **avaliar o desempenho do SUS**.
            """)

    with col2:
        st.markdown("### Internações por Faixa Etária")

        df_faixa = df_filtrado['faixa_etaria'].value_counts().sort_index().reset_index()
        df_faixa.columns = ['Faixa Etária', 'Internações']

        fig_faixa = px.bar(
            df_faixa, x='Faixa Etária', y='Internações',
            title="Distribuição por Faixa Etária",
            color_discrete_sequence=['#1e40af', '#2563eb', '#60a5fa']
        )
        st.plotly_chart(fig_faixa, use_container_width=True)

    st.markdown("---")
    
    # ========== CAPÍTULOS DO CID-10 (TOP 5) ==========
    st.markdown("### Top 5 Capítulos do CID-10")
    df_filtrado['capitulo_cid'] = df_filtrado['diagnostico_principal'].str[0]

    capitulo_map = {
        'A': 'Doenças infecciosas e parasitárias',
        'B': 'Doenças infecciosas e parasitárias',
        'C': 'Neoplasias (tumores)',
        'D': 'Neoplasias e doenças do sangue',
        'E': 'Endócrinas e metabólicas',
        'F': 'Transtornos mentais',
        'G': 'Sistema nervoso',
        'H': 'Olhos e ouvidos',
        'I': 'Sistema circulatório',
        'J': 'Sistema respiratório',
        'K': 'Sistema digestivo',
        'L': 'Pele e tecido subcutâneo',
        'M': 'Osteomuscular',
        'N': 'Geniturinário',
        'O': 'Gravidez e parto',
        'P': 'Período perinatal',
        'Q': 'Malformações congênitas',
        'R': 'Sinais e sintomas gerais',
        'S': 'Lesões e envenenamentos',
        'T': 'Lesões e envenenamentos',
        'V': 'Causas externas',
        'W': 'Causas externas',
        'X': 'Causas externas',
        'Y': 'Causas externas',
        'Z': 'Fatores sociais e contato'
    }

    df_filtrado['nome_capitulo'] = df_filtrado['capitulo_cid'].map(capitulo_map).fillna('Outros')
    capitulo_counts = df_filtrado['nome_capitulo'].value_counts().nlargest(5).reset_index()
    capitulo_counts.columns = ['Capítulo CID', 'Internações']

    fig_capitulos = px.bar(
        capitulo_counts.sort_values('Internações'),
        x='Internações', y='Capítulo CID', orientation='h',
        title='Top 5 Capítulos com Mais Internações',
        color='Internações',
        color_continuous_scale=['#eff6ff', '#1e3a8a']
    )
    fig_capitulos.update_layout(showlegend=False)
    fig_capitulos.update_coloraxes(showscale=False)
    st.plotly_chart(fig_capitulos, use_container_width=True)
    
    with st.expander("📂 O que são capítulos do CID-10?"):
        st.markdown("""
        Os **capítulos do CID-10** agrupam doenças por **sistemas do corpo ou categorias clínicas**. Cada capítulo é identificado por uma letra (A a Z) e representa um conjunto de diagnósticos relacionados.

        ### Exemplos de capítulos:
        - **I**: Doenças do sistema circulatório
        - **J**: Doenças do sistema respiratório
        - **E**: Doenças endócrinas, nutricionais e metabólicas
        - **F**: Transtornos mentais e comportamentais

        Estes agrupamentos ajudam na **tomada de decisão** para políticas públicas e planejamento de saúde.
        """
        )

    st.markdown("---")
    
    # ========== TABELA COMPLETA ==========
    st.markdown("### Tabela Completa de Internações Filtradas")

    df_tabela = df_filtrado.copy()
    df_tabela['Sensível à AB'] = df_tabela['sensivel_atencao_basica'].map({1: "Sim", 0: "Não"})

    colunas_exibir = ['diagnostico_principal', 'sexo', 'idade_anos', 'municipio_residencia', 'faixa_etaria', 'Sensível à AB']

    st.dataframe(df_tabela[colunas_exibir].rename(columns={
        'diagnostico_principal': 'Diagnóstico',
        'sexo': 'Sexo',
        'idade_anos': 'Idade',
        'municipio_residencia': 'Município',
        'faixa_etaria': 'Faixa Etária'
    }), use_container_width=True)
