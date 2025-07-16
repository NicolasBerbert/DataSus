from datetime import datetime
from dashboard.pages.causas_principais import render_styled_metric # Certifique-se que render_styled_metric existe neste caminho e é importável
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sqlite3
import json

def render(conn):
    st.markdown(f"<h1 style='text-align: center;'>Análise Geográfica</h1>", unsafe_allow_html=True)
    st.markdown("### Filtros")
    query_all_municipios_map = """
    SELECT codigo AS cod_municipio, nome AS municipio, regiao_saude, populacao
    FROM municipios ORDER BY nome;
    """
    df_all_municipios_map = pd.read_sql_query(query_all_municipios_map, conn)
    df_all_municipios_map['cod_municipio'] = df_all_municipios_map['cod_municipio'].astype(str).str.zfill(6)

    col_filters1, col_filters2 = st.columns(2)

    # Definindo a variável antes do bloco if
    cod_municipio_selecionado = None # Inicializa com None para evitar UnboundLocalError

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
    df_mapa_final['total_internacoes'] = df_mapa_final['total_internacoes'].fillna(0) # Preenche NaN com 0 para coloração

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
    
    st.markdown("---")
    # --- Mapa Interativo com GeoJSON ---
    st.markdown(f"<h2 style='text-align: center;'>Distribuição de Internações nos Municípios do Paraná</h2>", unsafe_allow_html=True)

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
                    colorscale=[[0, 'rgba(0,0,0,0)'], [1, 'rgba(0,0,0,0)']], # Transparente no preenchimento
                    marker_line_width=4,    # Espessura da linha (contorno)
                    marker_line_color='blue', # Cor da linha
                    showscale=False,        # Não mostra a barra de colors para o destaque
                    name=f'Destaque: {municipio_selecionado}'
                )
                fig_map.add_trace(highlight_trace) # Adiciona a camada de destaque ao mapa principal
                with st.container(border = True):
                    st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.warning(f"Não foram encontrados dados para o município: {municipio_selecionado}. Verifique a seleção.")
    else: # Se 'Todos os Municípios' for selecionado
        total_internacoes_geral = df_municipios['total_internacoes'].sum()
        total_pacientes_geral = df_municipios['total_pacientes_residentes_internados'].sum()

        col6, col7 = st.columns(2)
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
        with st.container(border = True):
            st.plotly_chart(fig_map, use_container_width=True)
    

    col1, col2 = st.columns(2)
    with col1.container(border = True):
        st.markdown(f"<h3 style='text-align: center;'>Municípios com Mais Internações</h3>", unsafe_allow_html=True)


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

    with col2.container(border=True):
        st.markdown(f"<h3 style='text-align: center;'>Internações por Região de Residência (Excluindo Paraná)</h3>", unsafe_allow_html=True)


        total_internacoes_todas_regioes = df_regioes['total_internacoes_regiao'].sum()


        total_internacoes_fora_pr_para_titulo = df_regioes[
            df_regioes['regiao_saude'].astype(str).str.startswith("Outros Estados (")
        ]['total_internacoes_regiao'].sum()

        percentual_fora_pr = 0
        if total_internacoes_todas_regioes > 0:
            percentual_fora_pr = (total_internacoes_fora_pr_para_titulo / total_internacoes_todas_regioes) * 100


        df_rosca_final = df_regioes[df_regioes['regiao_saude'] != 'Paraná'].copy()


        titulo_rosca = f"Internaçoes:{total_internacoes_fora_pr_para_titulo}"
        if total_internacoes_todas_regioes > 0:
            titulo_rosca += f"(Aprox. {percentual_fora_pr:.1f}% de pacientes de fora do PR)"
        else:
            titulo_rosca += "(Sem dados de regiões para os filtros atuais)"

        if not df_rosca_final.empty and total_internacoes_todas_regioes > 0:
            cores_azuis_rosca = [
                '#1e3a8a', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff', '#cbd5e1' 
            ]
            fig_regioes_pie = px.pie(
                df_rosca_final, 
                values='total_internacoes_regiao',
                names='regiao_saude', 
                title=titulo_rosca, 
                hole=0.5, 
                color_discrete_sequence=cores_azuis_rosca 
            )
            
            fig_regioes_pie.update_traces(textinfo='percent')
            st.plotly_chart(fig_regioes_pie, use_container_width=True)
        else:
            st.info("Não há dados de internações para comparar entre as regiões de saúde (exceto 'Paraná') com os filtros atuais ou o total de internações é zero.")


    with st.container(border=True):
        st.markdown(f"<h3 style='text-align: center;'>Distribuição da Idade dos Pacientes por Faixa Etária</h3>", unsafe_allow_html=True)


        # Reutiliza current_month_day ou cria um novo para evitar confusão de escopo
        current_month_day_box = datetime.now().strftime('%m%d')

        query_idades = f"""
            SELECT
                CAST(strftime('%Y', 'now') - SUBSTR(p.data_nascimento, 1, 4) -
                     (SUBSTR(p.data_nascimento, 5, 4) > '{current_month_day_box}') AS INTEGER) AS idade
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

            bins = [0, 11, 17, 24, 34, 44, 54, 64, 74, 120] 
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

            df_idades['faixa_etaria'] = pd.cut(df_idades['idade'], bins=bins, labels=labels, right=True, include_lowest=True)
            df_idades['faixa_etaria'] = pd.Categorical(df_idades['faixa_etaria'], categories=labels, ordered=True)

            # Aplicação da paleta de cores azuis para o boxplot
            fig_idade_boxplot = px.box(
                df_idades,
                x='faixa_etaria', 
                y='idade',
                title='', 
                labels={'faixa_etaria': 'Faixa Etária', 'idade': 'Idade do Paciente'},
                points='outliers', 
                color='faixa_etaria', 
                category_orders={"faixa_etaria": labels},
                color_discrete_sequence=['#1e3a8a', '#2563eb', '#3b82f6', '#60a5fa', '#93c5fd', '#bfdbfe', '#dbeafe', '#eff6ff', '#cbd5e1'] # Exemplo de paleta
            )
            
            fig_idade_boxplot.update_layout(
                xaxis_title='Faixa Etária',
                yaxis_title='Idade do Paciente',
                xaxis_tickangle=-45 
            )

            st.plotly_chart(fig_idade_boxplot, use_container_width=True)
        else:
            st.info("Nenhum dado de idade encontrado para os filtros selecionados.")
            
    # --- Fluxo de Pacientes (apenas se um município específico for selecionado) ---
    if municipio_selecionado != 'Todos os Municípios':
        # Aqui, cod_municipio_selecionado JÁ ESTÁ DEFINIDO pelo bloco acima
        # Portanto, não precisamos nos preocupar com ele ser None.
            
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

        has_destino_data = not df_fluxo_destino.empty
        has_origem_data = not df_fluxo_origem.empty

        if has_destino_data and has_origem_data:
            col_fluxo_d, col_fluxo_o = st.columns(2)
            
            with col_fluxo_d.container(border = True): 
                st.markdown(f"<h3 style='text-align: center;'>Origem de Pacientes Internados em {municipio_selecionado}</h3>", unsafe_allow_html=True)
                fig_fluxo_destino = px.bar(df_fluxo_destino,
                                           x='municipio_origem',
                                           y='total_internacoes_aqui',
                                           orientation='v',
                                           labels={'total_internacoes_aqui': 'Total de Internações', 'municipio_origem': 'Município de Origem'},
                                           color='total_internacoes_aqui',
                                           color_continuous_scale=['#eff6ff', '#1e3a8a']) # Aplicando a paleta de cores
                fig_fluxo_destino.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_fluxo_destino, use_container_width=True)
            
            with col_fluxo_o.container(border = True): 
                st.markdown(f"<h3 style='text-align: center;'>Destino de Pacientes Residentes de {municipio_selecionado}</h3>", unsafe_allow_html=True)
                fig_fluxo_origem = px.bar(df_fluxo_origem,
                                           x='municipio_internacao',
                                           y='total_internacoes_fora',
                                           orientation='v',
                                           labels={'total_internacoes_fora': 'Total de Internações', 'municipio_internacao': 'Município de Internação'},
                                           color='total_internacoes_fora',
                                           color_continuous_scale=['#eff6ff', '#1e3a8a']) # Aplicando a paleta de cores
                fig_fluxo_origem.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_fluxo_origem, use_container_width=True)

        elif has_destino_data:
            with st.container(border = True):
                st.markdown(f"<h3 style='text-align: center;'>Origem de Pacientes Internados em {municipio_selecionado}</h3>", unsafe_allow_html=True)
                fig_fluxo_destino = px.bar(df_fluxo_destino,
                                        x='municipio_origem',
                                        y='total_internacoes_aqui',
                                        orientation='v',
                                        labels={'total_internacoes_aqui': 'Total de Internações', 'municipio_origem': 'Município de Origem'},
                                        color='total_internacoes_aqui',
                                        color_continuous_scale=['#eff6ff', '#1e3a8a']) # Aplicando a paleta de cores
                fig_fluxo_destino.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_fluxo_destino, use_container_width=True)

        elif has_origem_data:
            with st.container(border = True):
                st.markdown(f"<h3 style='text-align: center;'>Destino de Pacientes Residentes de {municipio_selecionado}</h3>", unsafe_allow_html=True)
                fig_fluxo_origem = px.bar(df_fluxo_origem,
                                        x='municipio_internacao',
                                        y='total_internacoes_fora',
                                        orientation='v',
                                        labels={'total_internacoes_fora': 'Total de Internações', 'municipio_internacao': 'Município de Internação'},
                                        color='total_internacoes_fora',
                                        color_continuous_scale=['#eff6ff', '#1e3a8a']) # Aplicando a paleta de cores
                fig_fluxo_origem.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_fluxo_origem, use_container_width=True)
        else:
            st.info(f"Não há registros de fluxo de pacientes para {municipio_selecionado} com os filtros atuais.")
    
    elif municipio_selecionado == 'Todos os Municípios':
        st.info("Selecione um município específico para ver os gráficos de fluxo de pacientes.")