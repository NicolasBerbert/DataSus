from dashboard.pages.causas_principais import render_styled_metric
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import json
import numpy as np 
from datetime import datetime # Importar para obter o ano atual

def render(conn):

<<<<<<< HEAD
    st.subheader("Filtro Detalhado por Município Selecionado")

    # --- CARREGAMENTO DE DADOS BASE (SEM CACHE) ---
=======
    st.markdown("## Análise Geográfica")
    st.markdown("### Filtros")
>>>>>>> 9865d33bbf55e32bf099e76e0545f4db1ad0534d
    query_all_municipios_map = """
    SELECT codigo AS cod_municipio, nome AS municipio, regiao_saude, populacao
    FROM municipios ORDER BY nome;
    """
    df_all_municipios_map = pd.read_sql_query(query_all_municipios_map, conn)
    df_all_municipios_map['cod_municipio'] = df_all_municipios_map['cod_municipio'].astype(str).str.zfill(6)

    col_filters1, col_filters2 = st.columns(2) 

    with col_filters1:
        query_all_municipios_names = """
            SELECT DISTINCT nome FROM municipios ORDER BY nome;
        """
        df_all_municipios_names = pd.read_sql_query(query_all_municipios_names, conn)
        lista_municipios = sorted(df_all_municipios_names['nome'].unique().tolist())
        municipio_selecionado = st.selectbox(
            "Selecione um Município:",
            options=['Todos os Municípios'] + lista_municipios,
            key="municipio_filter"
        )

        cod_municipio_selecionado = None 
        municipio_filter_for_causas = ""
        municipio_join_for_causas = ""

        if municipio_selecionado != 'Todos os Municípios':
            query_municipio_codigo = f"SELECT codigo FROM municipios WHERE nome = '{municipio_selecionado.replace("'", "''")}'"
            df_municipio_codigo = pd.read_sql_query(query_municipio_codigo, conn)

            if not df_municipio_codigo.empty:
                cod_municipio_selecionado = df_municipio_codigo['codigo'].iloc[0]
                municipio_join_for_causas = """
                    JOIN internacoes i_filter ON c.codigo = i_filter.codigo_diagnostico_principal
                    JOIN pacientes p_filter ON i_filter.paciente_id = p_filter.id
                    JOIN municipios m_filter ON p_filter.codigo_municipio_residencia = m_filter.codigo
                """
                municipio_filter_for_causas = f"AND m_filter.codigo = '{cod_municipio_selecionado}'"

        query_causas = f"""
            SELECT DISTINCT c.codigo, c.descricao
            FROM cid_diagnosticos c
            {municipio_join_for_causas}
            WHERE 1=1 {municipio_filter_for_causas}
            GROUP BY c.codigo, c.descricao
            ORDER BY c.descricao;
        """
        df_causas = pd.read_sql_query(query_causas, conn)

    with col_filters2:
        causa_options = ['Todas as Causas'] + sorted(df_causas['descricao'].tolist())
        selected_causa_desc = st.selectbox(
            "Filtrar por Causa da Internação (CID):",
            options=causa_options,
            key="causa_cid_filter"
        )

    selected_cid_id = None
    if selected_causa_desc != 'Todas as Causas':
        selected_cid_row = df_causas[df_causas['descricao'] == selected_causa_desc]
        if not selected_cid_row.empty:
            selected_cid_id = selected_cid_row['codigo'].iloc[0]

    # --- Conectores para as Queries Principais (CID) ---
    cid_filter_join = ""
    cid_filter_where = ""
    if selected_cid_id is not None:
        cid_filter_join = "JOIN cid_diagnosticos c ON i.codigo_diagnostico_principal = c.codigo"
        cid_filter_where = f"AND c.codigo = '{selected_cid_id}'"
    
    # Consulta com código do município e contagem de internações
    query_contagem = f"""
        SELECT
            m.codigo AS cod_municipio,
            m.nome AS municipio,
            m.regiao_saude,
            m.populacao,
            COUNT(i.id) AS total_internacoes,
            COUNT(DISTINCT p.id) AS total_pacientes_residentes_internados
        FROM internacoes i
        JOIN pacientes p ON i.paciente_id = p.id
        JOIN municipios m ON m.codigo = p.codigo_municipio_residencia
        {cid_filter_join}
        WHERE 1=1 {cid_filter_where}
        GROUP BY m.codigo, m.nome, m.regiao_saude, m.populacao
        ORDER BY total_internacoes DESC;
    """
    df_municipios = pd.read_sql_query(query_contagem, conn)
    df_municipios['cod_municipio'] = df_municipios['cod_municipio'].astype(str).str.zfill(6)

    df_mapa_final = pd.merge(df_all_municipios_map, df_municipios[['cod_municipio', 'total_internacoes']], 
                             on='cod_municipio', how='left')
    df_mapa_final['total_internacoes'] = df_mapa_final['total_internacoes'].fillna(0) 

    # Consulta de regiões
    query_regioes = f"""
        SELECT
            m.regiao_saude AS regiao_saude,
            COUNT(i.id) AS total_internacoes_regiao
        FROM internacoes i
        JOIN pacientes p ON i.paciente_id = p.id
        JOIN municipios m ON m.codigo = p.codigo_municipio_residencia
        {cid_filter_join}
        WHERE m.regiao_saude IS NOT NULL AND m.regiao_saude != '' {cid_filter_where}
        GROUP BY m.regiao_saude
        ORDER BY total_internacoes_regiao DESC;
    """
    df_regioes = pd.read_sql_query(query_regioes, conn)
    
<<<<<<< HEAD
    # --- Carregamento GeoJSON ---
=======
    st.markdown("---")
    # --- Mapa Interativo com GeoJSON ---
    st.markdown("### Distribuição de Internações nos Municípios do Paraná")

>>>>>>> 9865d33bbf55e32bf099e76e0545f4db1ad0534d
    geojson_path = "data/geojson/municipios_pr.json"
    try:
        with open(geojson_path, "r", encoding="utf-8") as f:
            geojson = json.load(f)
        if geojson.get('features'):
            for feature in geojson['features']:
                if 'id' in feature['properties'] and isinstance(feature['properties']['id'], str):
                    feature['properties']['id'] = feature['properties']['id'][:-1]
                    feature['properties']['id'] = feature['properties']['id'].zfill(6)
    except FileNotFoundError:
        st.error(f"Erro: Arquivo GeoJSON não encontrado em '{geojson_path}'. Verifique o caminho.")
        return
    except json.JSONDecodeError:
        st.error(f"Erro: Arquivo '{geojson_path}' não é um JSON válido. Verifique o conteúdo.")
        return

    # Mapa com choropleth (sempre cria o mapa base)
    fig_map = px.choropleth(
        df_mapa_final,
        geojson=geojson,
        locations="cod_municipio",
        featureidkey="properties.id",
        color="total_internacoes",
        hover_name="municipio",
        hover_data=["total_internacoes", "regiao_saude", "populacao"],
        color_continuous_scale=['#eff6ff', '#1e3a8a']
    )
    fig_map.update_geos(fitbounds="locations", visible=False)


    # --- Lógica de Destaque e Big Numbers ---
    if municipio_selecionado != 'Todos os Municípios':
        df_selecionado_info = df_municipios[df_municipios['municipio'] == municipio_selecionado]

        if not df_selecionado_info.empty:
            df_selecionado_row = df_selecionado_info.iloc[0]
            st.markdown(f"### Dados para {municipio_selecionado}")
            col4, col5 = st.columns(2)
            with col4:
                render_styled_metric(
                    "Total de Internações",
                    f"{df_selecionado_row['total_internacoes']:,}".replace(",", "."),
                    "Número total de internações no município",
                    "🏥"
                )
            with col5:
                render_styled_metric(
                    "Pacientes Residentes Internados",
                    f"{df_selecionado_row['total_pacientes_residentes_internados']:,}".replace(",", "."),
                    "Pacientes residentes que foram internados",
                    "👥"
                )

            # Lógica de destaque no mapa
            cod_municipio_para_destacar = df_selecionado_row['cod_municipio']
            feature_municipio_destacado = next(
                (f for f in geojson['features'] if f['properties']['id'] == cod_municipio_para_destacar),
                None
            )

            if feature_municipio_destacado:
                highlight_trace = go.Choropleth(
                    geojson=feature_municipio_destacado,
                    locations=[cod_municipio_para_destacar],
                    featureidkey="properties.id",
                    z=[1],
                    colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']], 
                    marker_line_width=4,    
                    marker_line_color='blue', 
                    showscale=False,        
                    name=f'Destaque: {municipio_selecionado}'
                )
<<<<<<< HEAD
                fig_map.add_trace(highlight_trace) 
                with st.container(border = True):
                    st.plotly_chart(fig_map, use_container_width=True)
=======
                fig_map.add_trace(highlight_trace) # Adiciona a camada de destaque ao mapa principal
                st.plotly_chart(fig_map, use_container_width=True)
>>>>>>> 9865d33bbf55e32bf099e76e0545f4db1ad0534d
        else:
            st.warning(f"Não foram encontrados dados para o município: {municipio_selecionado}. Verifique a seleção.")
    else: # Se 'Todos os Municípios' for selecionado
        st.markdown(f"### Dados Gerais de Internações no Paraná")
        total_internacoes_geral = df_municipios['total_internacoes'].sum()
        total_pacientes_geral = df_municipios['total_pacientes_residentes_internados'].sum()

        col6, col7 = st.columns(2)
<<<<<<< HEAD
        with col6.container(border = True):
            st.metric(label="Total de Internações (Geral)", value=f"{total_internacoes_geral:,}".replace(",", "."))
        with col7.container(border = True):
            st.metric(label="Pacientes Residentes Internados (Geral)", value=f"{total_pacientes_geral:,}".replace(",", "."))
        with st.container(border = True):
            st.plotly_chart(fig_map, use_container_width=True)
    st.subheader(" ",divider = True)

    # --- Gráficos de barra e Pizza ---
    col1, col2 = st.columns(2)
    with col1.container(border = True):
        #Gráfico de Barras (Top 10)
        st.subheader("Municípios com Mais Internações")

        top10 = df_municipios.sort_values("total_internacoes", ascending=False).head(10)
        fig_bar = px.bar(top10,
                         x='total_internacoes',
                         y='municipio',
                         orientation='h',
                         color='total_internacoes',
                         color_continuous_scale='Reds',
                         labels={'total_internacoes': 'Internações'}
                        )
        fig_bar.update_layout(coloraxis_showscale=False)
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'} )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2.container(border = True):
        st.subheader("Comparativo de Internações por Região de Saúde")
        df_regioes_filtrado = df_regioes[df_regioes['regiao_saude'] != 'Paraná'].copy()

        if not df_regioes_filtrado.empty:
            fig_regioes_pie = px.pie(
                df_regioes_filtrado,
                values='total_internacoes_regiao',
                names='regiao_saude',
                title='',
                hole=0.5 # Para criar um gráfico de rosca
            )
            st.plotly_chart(fig_regioes_pie, use_container_width=True)
        else:
            st.info("Não há dados de internações para comparar entre as regiões de saúde com os filtros atuais.")


    

    col8,col9 = st.columns(2)
    st.subheader(" ",divider = True)

    # Fluxo de Pacientes (apenas se um município específico for selecionado)
    with st.container(border = True): 
        if municipio_selecionado != 'Todos os Municípios':
            
            # --- Query para Fluxo de Destino (pacientes que chegam AQUI) ---
            query_fluxo_destino = f"""
                SELECT
                    mo.nome AS municipio_origem,
                    COUNT(i.id) AS total_internacoes_aqui
                FROM internacoes i
                JOIN pacientes p ON i.paciente_id = p.id
                JOIN municipios mo ON mo.codigo = p.codigo_municipio_residencia
                JOIN estabelecimentos e ON i.estabelecimento_id = e.id
                JOIN municipios mi ON mi.codigo = e.codigo_municipio_movimento
                {cid_filter_join}
                WHERE mi.nome = '{municipio_selecionado.replace("'", "''")}'
                      {cid_filter_where}
                GROUP BY mo.nome
                ORDER BY total_internacoes_aqui DESC
                LIMIT 10;
            """
            df_fluxo_destino = pd.read_sql_query(query_fluxo_destino, conn)

            # --- Query para Fluxo de Origem (pacientes que saem DAQUI para outro lugar) ---
            query_fluxo_origem = f"""
                SELECT
                    mi.nome AS municipio_internacao,
                    COUNT(i.id) AS total_internacoes_fora
                FROM internacoes i
                JOIN pacientes p ON i.paciente_id = p.id
                JOIN municipios mo ON mo.codigo = p.codigo_municipio_residencia
                JOIN estabelecimentos e ON i.estabelecimento_id = e.id
                JOIN municipios mi ON mi.codigo = e.codigo_municipio_movimento
                {cid_filter_join}
                WHERE mo.nome = '{municipio_selecionado.replace("'", "''")}'
                      AND mi.nome != '{municipio_selecionado.replace("'", "''")}'
                      {cid_filter_where}
                GROUP BY mi.nome
                ORDER BY total_internacoes_fora DESC
                LIMIT 10;
            """
            df_fluxo_origem = pd.read_sql_query(query_fluxo_origem, conn)

            # Verificando quais DataFrames têm dados
            has_destino_data = not df_fluxo_destino.empty
            has_origem_data = not df_fluxo_origem.empty
=======
        with col6:
            render_styled_metric(
                "Total de Internações (Geral)",
                f"{total_internacoes_geral:,}".replace(",", "."),
                "Número total de internações no estado",
                "🏥"
            )
        with col7:
            render_styled_metric(
                "Pacientes Residentes Internados (Geral)",
                f"{total_pacientes_geral:,}".replace(",", "."),
                "Total de pacientes residentes internados",
                "👥"
            )
        st.plotly_chart(fig_map, use_container_width=True)
    

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Municípios com Mais Internações")

            top10 = df_municipios.sort_values("total_internacoes", ascending=False).head(10)
            fig_bar = px.bar(top10,
                             x='total_internacoes',
                             y='municipio',
                             orientation='h',
                             color='total_internacoes',
                             color_continuous_scale=['#eff6ff', '#1e3a8a'],
                             labels={'total_internacoes': 'Internações'}
                            )
            fig_bar.update_layout(coloraxis_showscale=False)
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'} )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col2:
            st.markdown("### Comparativo por Região de Saúde")
            df_regioes_filtrado = df_regioes[df_regioes['regiao_saude'] != 'Paraná'].copy()

            if not df_regioes_filtrado.empty:
                # Cores em tons de azul para consistência
                cores_azuis = [
                    '#1e3a8a', '#1e40af', '#1d4ed8', '#2563eb', '#3b82f6',
                    '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff'
                ]
                fig_regioes_pie = px.pie(
                    df_regioes_filtrado,
                    values='total_internacoes_regiao',
                    names='regiao_saude',
                    title='',
                    hole=0.5,
                    color_discrete_sequence=cores_azuis
                )
                st.plotly_chart(fig_regioes_pie, use_container_width=True)
            else:
                st.info("Não há dados de internações para comparar entre as regiões de saúde com os filtros atuais.")
>>>>>>> 9865d33bbf55e32bf099e76e0545f4db1ad0534d

            # --- Lógica Condicional para o Layout das Sub-colunas de Fluxo ---
            if has_destino_data and has_origem_data:
                # Ambas as queries retornaram dados: criar 2 colunas DENTRO de col_fluxo_geral
                col_fluxo_d, col_fluxo_o = st.columns(2)
                
                with col_fluxo_d: # Não precisa de novo container com borda aqui, pois já estamos no container de col_fluxo_geral
                    st.subheader(f"Origem de Pacientes Internados em {municipio_selecionado}")
                    fig_fluxo_destino = px.bar(df_fluxo_destino,
                                               x='municipio_origem',
                                               y='total_internacoes_aqui',
                                               orientation='v',
                                               labels={'total_internacoes_aqui': 'Total de Internações', 'municipio_origem': 'Município de Origem'},
                                               color='total_internacoes_aqui',
                                               color_continuous_scale='Viridis')
                    fig_fluxo_destino.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_fluxo_destino, use_container_width=True)
                
                with col_fluxo_o: # Não precisa de novo container com borda
                    st.subheader(f"Destino de Pacientes Residentes de {municipio_selecionado}")
                    fig_fluxo_origem = px.bar(df_fluxo_origem,
                                               x='municipio_internacao',
                                               y='total_internacoes_fora',
                                               orientation='v',
                                               labels={'total_internacoes_fora': 'Total de Internações', 'municipio_internacao': 'Município de Internação'},
                                               color='total_internacoes_fora',
                                               color_continuous_scale='Plasma')
                    fig_fluxo_origem.update_layout(yaxis={'categoryorder':'total ascending'})
                    st.plotly_chart(fig_fluxo_origem, use_container_width=True)

<<<<<<< HEAD
            elif has_destino_data:
                # Apenas o fluxo de destino tem dados: ocupa a largura total de col_fluxo_geral
                st.subheader(f"Origem de Pacientes Internados em {municipio_selecionado}")
=======


    # --- Fluxo de Pacientes (apenas se um município específico for selecionado) ---
    if municipio_selecionado != 'Todos os Municípios':
        
        query_fluxo_destino = f"""
            SELECT
                mo.nome AS municipio_origem,
                COUNT(i.id) AS total_internacoes_aqui
            FROM internacoes i
            JOIN pacientes p ON i.paciente_id = p.id
            JOIN municipios mo ON mo.codigo = p.codigo_municipio_residencia
            JOIN estabelecimentos e ON i.estabelecimento_id = e.id
            JOIN municipios mi ON mi.codigo = e.codigo_municipio_movimento
            {cid_filter_join}
            WHERE mi.nome = '{municipio_selecionado.replace("'", "''")}'
                  {cid_filter_where}
            GROUP BY mo.nome
            ORDER BY total_internacoes_aqui DESC
            LIMIT 10;
        """
        df_fluxo_destino = pd.read_sql_query(query_fluxo_destino, conn)

        st.markdown("---")
        st.markdown("### Fluxo de Pacientes")
        
        col8, col9 = st.columns(2)
        with col8:
            if not df_fluxo_destino.empty:
>>>>>>> 9865d33bbf55e32bf099e76e0545f4db1ad0534d
                fig_fluxo_destino = px.bar(df_fluxo_destino,
                                           x='municipio_origem',
                                           y='total_internacoes_aqui',
                                           orientation='v',
                                           labels={'total_internacoes_aqui': 'Total de Internações', 'municipio_origem': 'Município de Origem'},
                                           color='total_internacoes_aqui',
                                           color_continuous_scale=['#eff6ff', '#1e3a8a'])
                fig_fluxo_destino.update_layout(yaxis={'categoryorder':'total ascending'})
<<<<<<< HEAD
=======
                st.markdown(f"#### Origem de Pacientes Internados em {municipio_selecionado}")
>>>>>>> 9865d33bbf55e32bf099e76e0545f4db1ad0534d
                st.plotly_chart(fig_fluxo_destino, use_container_width=True)

<<<<<<< HEAD
            elif has_origem_data:
                # Apenas o fluxo de origem tem dados: ocupa a largura total de col_fluxo_geral
                st.subheader(f"Destino de Pacientes Residentes de {municipio_selecionado}")
=======
        
        

        query_fluxo_origem = f"""
            SELECT
                mi.nome AS municipio_internacao,
                COUNT(i.id) AS total_internacoes_fora
            FROM internacoes i
            JOIN pacientes p ON i.paciente_id = p.id
            JOIN municipios mo ON mo.codigo = p.codigo_municipio_residencia
            JOIN estabelecimentos e ON i.estabelecimento_id = e.id
            JOIN municipios mi ON mi.codigo = e.codigo_municipio_movimento
            {cid_filter_join}
            WHERE mo.nome = '{municipio_selecionado.replace("'", "''")}'
                  AND mi.nome != '{municipio_selecionado.replace("'", "''")}'
                  {cid_filter_where}
            GROUP BY mi.nome
            ORDER BY total_internacoes_fora DESC
            LIMIT 10;
        """
        df_fluxo_origem = pd.read_sql_query(query_fluxo_origem, conn)
        with col9:
            if not df_fluxo_origem.empty:
                
>>>>>>> 9865d33bbf55e32bf099e76e0545f4db1ad0534d
                fig_fluxo_origem = px.bar(df_fluxo_origem,
                                           x='municipio_internacao',
                                           y='total_internacoes_fora',
                                           orientation='v',
                                           labels={'total_internacoes_fora': 'Total de Internações', 'municipio_internacao': 'Município de Internação'},
                                           color='total_internacoes_fora',
                                           color_continuous_scale=['#eff6ff', '#2563eb'])
                fig_fluxo_origem.update_layout(yaxis={'categoryorder':'total ascending'})
<<<<<<< HEAD
=======
                st.markdown(f"#### Destino de Pacientes Residentes de {municipio_selecionado}")
>>>>>>> 9865d33bbf55e32bf099e76e0545f4db1ad0534d
                st.plotly_chart(fig_fluxo_origem, use_container_width=True)
            else:
                # Nenhuma das queries retornou dados
                st.info(f"Não há registros de fluxo de pacientes para {municipio_selecionado} com os filtros atuais.")
        
        elif municipio_selecionado == 'Todos os Municípios':
            st.info("Selecione um município específico para ver os gráficos de fluxo de pacientes.")


    #Boxplot de idades 
    st.subheader(" ",divider = True)
    with st.container(border=True):
        st.subheader("Distribuição da Idade dos Pacientes por Faixa Etária")

        current_month_day = datetime.now().strftime('%m%d')

        query_idades = f"""
            SELECT
                CAST(strftime('%Y', 'now') - SUBSTR(p.data_nascimento, 1, 4) -
                    (SUBSTR(p.data_nascimento, 5, 4) > '{current_month_day}') AS INTEGER) AS idade
            FROM pacientes p
            JOIN internacoes i ON i.paciente_id = p.id
            JOIN municipios m ON p.codigo_municipio_residencia = m.codigo
            {cid_filter_join}
            WHERE p.data_nascimento IS NOT NULL AND LENGTH(p.data_nascimento) = 8
            {cid_filter_where}
            {f"AND m.codigo = '{cod_municipio_selecionado}'" if cod_municipio_selecionado else ""}
            ;
        """
        df_idades = pd.read_sql_query(query_idades, conn)

        if not df_idades.empty:
            df_idades = df_idades[(df_idades['idade'] >= 0) & (df_idades['idade'] <= 120)]

            # Definindo as faixas etárias
            bins = [0, 11, 17, 24, 34, 44, 54, 64, 74, 120] # Limites superiores das faixas
            labels = [
                '0-11 anos (Crianças)',
                '12-17 anos (Adolescentes)',
                '18-24 anos (Jovens Adultos)',
                '25-34 anos (Adultos Jovens)',
                '35-44 anos (Adultos)',
                '45-54 anos (Meia-idade)',
                '55-64 anos (Idosos Jovens)',
                '65-74 anos (Idosos)',
                '75+ anos (Idosos Avançados)'
            ]

            # Criando a coluna de faixa etária
            df_idades['faixa_etaria'] = pd.cut(df_idades['idade'], bins=bins, labels=labels, right=True, include_lowest=True)
            
            # Ordenar as faixas etárias para o gráfico
            df_idades['faixa_etaria'] = pd.Categorical(df_idades['faixa_etaria'], categories=labels, ordered=True)

            # Criando o Box Plot de idade por faixa etária
            fig_idade_boxplot = px.box(
                df_idades,
                x='faixa_etaria', # Eixo X agora é a faixa etária
                y='idade',
                title='', 
                labels={'faixa_etaria': 'Faixa Etária', 'idade': 'Idade do Paciente'},
                points='outliers', 
                color='faixa_etaria', # Cores diferentes para cada faixa
                category_orders={"faixa_etaria": labels}
            )
            
            fig_idade_boxplot.update_layout(
                xaxis_title='Faixa Etária',
                yaxis_title='Idade do Paciente',
                xaxis_tickangle=-45 # Para evitar sobreposição dos rótulos
            )

            st.plotly_chart(fig_idade_boxplot, use_container_width=True)
        else:
            st.info("Nenhum dado de idade encontrado para os filtros selecionados.")