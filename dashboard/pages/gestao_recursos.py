import streamlit as st
import pandas as pd
import plotly.express as px
from main import get_database_connection

# Conecta ao banco de dados
conn = get_database_connection()

def render(data):
    """ Página de Gestão de Recursos | Responsável: [NOME_DESENVOLVEDOR_6] """

    st.title("💰 Gestão de Recursos")
    st.markdown("---")

    # Navegação por abas
    aba1, aba2, aba3, aba4 = st.tabs([
        "📋 Classificação & Filtros", 
        "📊 Diagnóstico", 
        "🚨 Outliers", 
        "🏥 Estabelecimentos"
    ])

    # =========== ABA 1 ===========
    with aba1:
        query_gravidade = """ 
        SELECT
            p.id AS paciente_id,
            p.idade_anos,
            s.descricao AS sexo,
            p.data_nascimento,
            m.nome AS municipio_residencia,
            cd.codigo AS cid_codigo,
            cd.descricao AS cid_descricao,
            CASE
                WHEN cd.codigo LIKE 'C%' OR cd.codigo LIKE 'I2%' OR i.dias_permanencia > 20 THEN 'Alta'
                WHEN cd.codigo LIKE 'J1%' OR cd.codigo LIKE 'I1%' OR i.dias_permanencia BETWEEN 10 AND 20 THEN 'Média'
                ELSE 'Baixa'
            END AS gravidade,
            SUM(vf.valor_total) AS total_gasto,
            AVG(i.dias_permanencia) AS media_dias,
            COUNT(i.id) AS total_internacoes
        FROM internacoes i
        JOIN pacientes p ON i.paciente_id = p.id
        JOIN valores_financeiros vf ON i.id = vf.internacao_id
        LEFT JOIN sexo s ON p.codigo_sexo = s.codigo
        LEFT JOIN municipios m ON p.codigo_municipio_residencia = m.codigo
        LEFT JOIN cid_diagnosticos cd ON i.codigo_diagnostico_principal = cd.codigo
        GROUP BY p.id, cd.codigo
        ORDER BY total_gasto DESC
        """  
        df_gravidade = pd.read_sql_query(query_gravidade, conn)

        st.markdown("#### 🎯 Filtros Interativos")

                # Filtros horizontais
        colf1, colf2, colf3, colf4 = st.columns(4)
        with colf1:
            sexo_opcao = st.selectbox("Sexo:", ["Todos"] + df_gravidade["sexo"].dropna().unique().tolist())
        with colf2:
            municipio_opcao = st.selectbox("Município:", ["Todos"] + df_gravidade["municipio_residencia"].dropna().unique().tolist())
        with colf3:
            gravidade_opcao = st.selectbox("Gravidade:", ["Todos"] + df_gravidade["gravidade"].dropna().unique().tolist())
        with colf4:
            idade_min, idade_max = st.slider("Faixa Etária (anos):", 0, 100, (0, 100))

        df_filtrado = df_gravidade.copy()
        if sexo_opcao != "Todos":
            df_filtrado = df_filtrado[df_filtrado["sexo"] == sexo_opcao]
        if municipio_opcao != "Todos":
            df_filtrado = df_filtrado[df_filtrado["municipio_residencia"] == municipio_opcao]
        if gravidade_opcao != "Todos":
            df_filtrado = df_filtrado[df_filtrado["gravidade"] == gravidade_opcao]
        df_filtrado = df_filtrado[(df_filtrado["idade_anos"] >= idade_min) & (df_filtrado["idade_anos"] <= idade_max)]

        col1, col2, col3 = st.columns(3)

        col1.metric("🔢 Total de Pacientes", df_filtrado["paciente_id"].nunique())
        col2.metric("💰 Gasto Total (R$)", f"{df_filtrado['total_gasto'].sum():,.2f}")
        col3.metric("📊 Média de Dias Internados", f"{df_filtrado['media_dias'].mean():.1f}")

        st.markdown("#### 📄 Tabela de Pacientes Filtrados")
        st.dataframe(df_filtrado, use_container_width=True)
        
        fig_bolhas = px.scatter(
            df_filtrado,
            x="media_dias",
            y="total_gasto",
            size="total_internacoes",
            color="gravidade",
            color_discrete_map={
                "Baixa": "#0000FF",   # Azul
                "Média": "#FFFF00",   # Amarelo
                "Alta": "#FF0000"     # Vermelho
            },
            hover_data=["paciente_id", "cid_descricao", "municipio_residencia"],
            labels={
                "media_dias": "Dias Internados",
                "total_gasto": "Gasto Total (R$)",
                "total_internacoes": "Internações"
            },
            title="🫧 Relação entre Tempo, Gasto e Volume de Internações"
        )

        st.plotly_chart(fig_bolhas, use_container_width=True)


    # =========== ABA 2 ===========
    with aba2:
        query_diag = """
        SELECT 
            cd.codigo AS cid,
            cd.descricao AS diagnostico,
            COUNT(i.id) AS total_internacoes,
            AVG(vf.valor_total) AS valor_medio,
            SUM(vf.valor_total) AS valor_total
        FROM internacoes i
        JOIN valores_financeiros vf ON i.id = vf.internacao_id
        JOIN cid_diagnosticos cd ON i.codigo_diagnostico_principal = cd.codigo
        GROUP BY cd.codigo, cd.descricao
        ORDER BY valor_medio DESC
        """

        df_diag = pd.read_sql_query(query_diag, conn)

        st.markdown("#### 🎛️ Filtros por Diagnóstico")

        # Filtros horizontais com ordem invertida
        colf1, colf2, colf3 = st.columns(3)

        with colf1:
            faixa_interv = {
                "Todas": (0, float("inf")),
                "Baixa (1–50)": (1, 50),
                "Média (51–200)": (51, 200),
                "Alta (201+)": (201, float("inf"))
            }
            faixa_opcao = st.selectbox("📊 Faixa de Internações", list(faixa_interv.keys()))
            interv_min, interv_max = faixa_interv[faixa_opcao]

        with colf2:
            faixa_custo = st.slider("💸 Faixa de Custo Médio (R$)",
                                    float(df_diag["valor_medio"].min()),
                                    float(df_diag["valor_medio"].max()),
                                    (float(df_diag["valor_medio"].min()), float(df_diag["valor_medio"].max())))

        with colf3:
            cid_opcao = st.selectbox("🧠 Diagnóstico", ["Todos"] + sorted(df_diag["diagnostico"].dropna().unique().tolist()))

        # Aplicando filtros
        df_filtrado = df_diag.copy()
        if cid_opcao != "Todos":
            df_filtrado = df_filtrado[df_filtrado["diagnostico"] == cid_opcao]
        df_filtrado = df_filtrado[
            (df_filtrado["valor_medio"] >= faixa_custo[0]) & (df_filtrado["valor_medio"] <= faixa_custo[1]) &
            (df_filtrado["total_internacoes"] >= interv_min) & (df_filtrado["total_internacoes"] <= interv_max)
        ]

        st.markdown("#### 📈 Custo Médio por Diagnóstico Principal (Filtrado)")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🧠 Diagnósticos Únicos", df_filtrado["cid"].nunique())
        col2.metric("📊 Total de Internações", int(df_filtrado["total_internacoes"].sum()))
        col3.metric("💸 Custo Médio Geral", f"R$ {df_filtrado['valor_medio'].mean():,.2f}")
        col4.metric("💰 Gasto Total", f"R$ {df_filtrado['valor_total'].sum():,.2f}")

        st.dataframe(df_filtrado, use_container_width=True)

        fig_diag = px.bar(df_filtrado, x="diagnostico", y="valor_medio",
                        title="💰 Custo Médio por Diagnóstico (Filtrado)",
                        labels={"valor_medio": "Valor Médio (R$)", "diagnostico": "CID"},
                        text_auto=".2s")
        st.plotly_chart(fig_diag, use_container_width=True)

    # =========== ABA 3 ===========
    with aba3:
        query_outliers = """
        SELECT 
            i.id AS internacao_id,
            p.id AS paciente_id,
            p.idade_anos,
            cd.codigo AS cid,
            cd.descricao AS diagnostico,
            m.nome AS municipio,
            e.nome_estabelecimento,
            tg.descricao AS tipo_gestao,
            i.dias_permanencia,
            vf.valor_total
        FROM internacoes i
        JOIN pacientes p ON i.paciente_id = p.id
        JOIN valores_financeiros vf ON i.id = vf.internacao_id
        JOIN estabelecimentos e ON i.estabelecimento_id = e.id
        LEFT JOIN municipios m ON e.codigo_municipio_movimento = m.codigo
        LEFT JOIN tipos_gestao tg ON e.codigo_tipo_gestao = tg.codigo
        LEFT JOIN cid_diagnosticos cd ON i.codigo_diagnostico_principal = cd.codigo
        """

        df_outliers = pd.read_sql_query(query_outliers, conn)

        # Cálculo do IQR
        q1 = df_outliers["valor_total"].quantile(0.25)
        q3 = df_outliers["valor_total"].quantile(0.75)
        iqr = q3 - q1
        limite_superior = q3 + 1.5 * iqr

        # Filtra outliers
        outliers = df_outliers[df_outliers["valor_total"] > limite_superior]

        st.markdown("### 🚨 Internações com Gasto Elevado (Outliers)")
        with st.expander("📌 O que são Outliers Financeiros?"):
            st.markdown("""
            Outliers são internações cujo **gasto total excede significativamente o padrão**, baseado no intervalo interquartil (IQR) da distribuição financeira.  
            Isso pode ocorrer por:

            - Permanência hospitalar prolongada 📆  
            - Diagnósticos complexos ou múltiplos 💉  
            - Diferenças de estrutura ou gestão hospitalar 🏥  
            - Erros ou inconsistências de registro 🔍  

            Esta análise é útil para identificar **anomalias, oportunidades de auditoria** ou processos que precisam ser revisados.
            """)
        
        # Filtros interativos
        st.markdown("#### 🎛️ Filtros")
        colf1, colf2, colf3 = st.columns(3)
        with colf1:
            municipio_outlier = st.selectbox("📍 Município", ["Todos"] + sorted(outliers["municipio"].dropna().unique().tolist()))
        with colf2:
            diag_outlier = st.selectbox("🧠 Diagnóstico", ["Todos"] + sorted(outliers["diagnostico"].dropna().unique().tolist()))
        with colf3:
            hospital_outlier = st.selectbox("🏥 Estabelecimento", ["Todos"] + sorted(outliers["nome_estabelecimento"].dropna().unique().tolist()))

        # Aplicando filtros
        df_filtered_outliers = outliers.copy()
        if municipio_outlier != "Todos":
            df_filtered_outliers = df_filtered_outliers[df_filtered_outliers["municipio"] == municipio_outlier]
        if diag_outlier != "Todos":
            df_filtered_outliers = df_filtered_outliers[df_filtered_outliers["diagnostico"] == diag_outlier]
        if hospital_outlier != "Todos":
            df_filtered_outliers = df_filtered_outliers[df_filtered_outliers["nome_estabelecimento"] == hospital_outlier]

        # KPIs Dinâmicos com base nos filtros
        col1, col2, col3 = st.columns(3)
        col1.metric("⚠️ Total de Outliers", df_filtered_outliers.shape[0])
        col2.metric("💰 Maior Gasto", f"R$ {df_filtered_outliers['valor_total'].max():,.2f}" if not df_filtered_outliers.empty else "—")
        col3.metric("⏱️ Permanência Máxima", f"{df_filtered_outliers['dias_permanencia'].max()} dias" if not df_filtered_outliers.empty else "—")

        st.markdown("#### 📋 Tabela de Outliers Filtrados")
        st.dataframe(df_filtered_outliers, use_container_width=True)

    # =========== ABA 4 ===========
    with aba4:
        # Consulta única para todos os dados
        query_estabs = """
        SELECT 
            e.nome_estabelecimento,
            e.cnpj_hospital,
            m.nome AS municipio,
            tg.descricao AS tipo_gestao,
            COUNT(i.id) AS total_internacoes,
            SUM(vf.valor_total) AS total_gasto,
            AVG(vf.valor_total) AS gasto_medio
        FROM internacoes i
        JOIN valores_financeiros vf ON i.id = vf.internacao_id
        JOIN estabelecimentos e ON i.estabelecimento_id = e.id
        LEFT JOIN municipios m ON e.codigo_municipio_movimento = m.codigo
        LEFT JOIN tipos_gestao tg ON e.codigo_tipo_gestao = tg.codigo
        GROUP BY e.nome_estabelecimento, e.cnpj_hospital, m.nome, tg.descricao
        ORDER BY total_gasto DESC
        """

        df_estabs = pd.read_sql_query(query_estabs, conn)

        st.markdown("#### 🎛️ Filtros de Estabelecimentos")

        # Filtros horizontais
        colf1, colf2, colf3 = st.columns(3)
        with colf1:
            municipio_opcao = st.selectbox("📍 Município", ["Todos"] + sorted(df_estabs["municipio"].dropna().unique().tolist()))
        with colf2:
            gestao_opcao = st.selectbox("🏢 Tipo de Gestão", ["Todos"] + sorted(df_estabs["tipo_gestao"].dropna().unique().tolist()))
        with colf3:
            estab_opcao = st.selectbox("🏥 Estabelecimento", ["Todos"] + sorted(df_estabs["nome_estabelecimento"].dropna().unique().tolist()))

        # Aplicando filtros
        df_filtrado = df_estabs.copy()
        if municipio_opcao != "Todos":
            df_filtrado = df_filtrado[df_filtrado["municipio"] == municipio_opcao]
        if gestao_opcao != "Todos":
            df_filtrado = df_filtrado[df_filtrado["tipo_gestao"] == gestao_opcao]
        if estab_opcao != "Todos":
            df_filtrado = df_filtrado[df_filtrado["nome_estabelecimento"] == estab_opcao]

        st.markdown("#### 🧾 Gastos por Estabelecimento Filtrado")

        col1, col2, col3 = st.columns(3)
        col1.metric("🏥 Estabelecimentos", df_filtrado["nome_estabelecimento"].nunique())
        col2.metric("📊 Internações Totais", df_filtrado["total_internacoes"].sum())
        col3.metric("💰 Gasto Total (R$)", f"{df_filtrado['total_gasto'].sum():,.2f}")

        st.dataframe(df_filtrado, use_container_width=True)

        # GRÁFICOS ESTÁTICOS BASEADOS NO DATAFRAME ORIGINAL (SEM FILTROS)
        st.markdown("#### 📈 Gráficos Globais")

        # Top 10 Estabelecimentos por Gasto
        top10 = df_estabs.head(10)
        fig_top10 = px.bar(top10, x="nome_estabelecimento", y="total_gasto",
                        title="🏥 Top 10 Estabelecimentos por Gasto (Geral)",
                        labels={"total_gasto": "Gasto Total (R$)", "nome_estabelecimento": "Estabelecimento"},
                        color="tipo_gestao", text_auto=".2s")
        st.plotly_chart(fig_top10, use_container_width=True)

        # Gasto Médio por Tipo de Gestão
        media_por_gestao = df_estabs.groupby("tipo_gestao")["gasto_medio"].mean().reset_index()
        fig_gestao = px.bar(media_por_gestao, x="tipo_gestao", y="gasto_medio",
                            title="💼 Gasto Médio por Tipo de Gestão (Geral)",
                            labels={"gasto_medio": "Valor Médio (R$)", "tipo_gestao": "Gestão"},
                            color="tipo_gestao",
                            text_auto=".2f")
        st.plotly_chart(fig_gestao, use_container_width=True)

