import streamlit as st
import pandas as pd
import plotly.express as px

def render(data):

    st.title("🔍 Causas Principais de Internação")
    st.markdown("---")

    # ========== FILTROS ==========
    st.header("Filtros")
    col_ano, col_sexo, col_faixa, col_mun = st.columns(4)

    meses = sorted(data['mes_competencia'].unique())
    ano_filtro = col_ano.selectbox("Mês de Internação", ["Todos"] + meses, index=0)
    sexo_filtro = col_sexo.selectbox("Sexo", ["Todos", "Masculino", "Feminino"])
    faixa_etaria = col_faixa.selectbox("Faixa Etária", ["Todas", "0-17", "18-59", "60+"])
    municipio_filtro = col_mun.selectbox(
        "Município de Residência",
        ["Todos"] + sorted(data['municipio_residencia'].dropna().unique())
    )

    # ========== FILTRAGEM ==========
    if ano_filtro == "Todos":
        df_filtrado = data.copy()
    else:
        df_filtrado = data[data['mes_competencia'] == ano_filtro]

    if sexo_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado['sexo'] == sexo_filtro]

    if faixa_etaria != "Todas":
        if faixa_etaria == "0-17":
            df_filtrado = df_filtrado[df_filtrado['idade_anos'] <= 17]
        elif faixa_etaria == "18-59":
            df_filtrado = df_filtrado[(df_filtrado['idade_anos'] >= 18) & (df_filtrado['idade_anos'] <= 59)]
        elif faixa_etaria == "60+":
            df_filtrado = df_filtrado[df_filtrado['idade_anos'] >= 60]

    if municipio_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado['municipio_residencia'] == municipio_filtro]

    total_internacoes = len(df_filtrado)
    if total_internacoes == 0:
        st.warning("Nenhuma internação encontrada para os filtros selecionados.")
        return

    # Cria coluna faixa_etaria sem warning
    bins = [0, 18, 60, 130]
    labels = ['0-17', '18-59', '60+']
    df_filtrado = df_filtrado.copy()
    df_filtrado['faixa_etaria'] = pd.cut(df_filtrado['idade_anos'], bins=bins, labels=labels, right=False)

    # ========== CARDS DE KPIs ==========
    total_formatado = f"{total_internacoes:,}".replace(",", ".")
    media_custo = df_filtrado['valor_total'].mean() if 'valor_total' in df_filtrado.columns else 0
    media_formatada = f"R$ {media_custo:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    total_sensivel = df_filtrado['sensivel_atencao_basica'].sum() if 'sensivel_atencao_basica' in df_filtrado.columns else 0
    percentual_sensivel = total_sensivel / total_internacoes if total_internacoes > 0 else 0
    percentual_formatado = f"{percentual_sensivel:.1%}"

    st.markdown(f"""
    <div style="display: flex; gap: 20px; justify-content: center; flex-wrap: wrap; margin-bottom: 20px;">

    <div style="flex: 1; min-width: 220px; background-color: #f9f9f9; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 20px; text-align: center;">
        <div style="font-size: 30px;">🏥</div>
        <div style="font-size: 18px; font-weight: bold; margin-bottom: 5px;">Total de Internações</div>
        <div style="font-size: 24px; color: #333;">{total_formatado}</div>
    </div>

    <div style="flex: 1; min-width: 220px; background-color: #f9f9f9; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 20px; text-align: center;">
        <div style="font-size: 30px;">💸</div>
        <div style="font-size: 18px; font-weight: bold; margin-bottom: 5px;">Custo Médio</div>
        <div style="font-size: 24px; color: #333;">{media_formatada}</div>
    </div>

    <div style="flex: 1; min-width: 220px; background-color: #f9f9f9; border-radius: 12px; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 20px; text-align: center;">
        <div style="font-size: 30px;">🩺</div>
        <div style="font-size: 18px; font-weight: bold; margin-bottom: 5px;">% Sensível à AB</div>
        <div style="font-size: 24px; color: #333;">{percentual_formatado}</div>
    </div>

    </div>
    """, unsafe_allow_html=True)

    # ========== TOP 10 CAUSAS ==========
    st.subheader("📊 Top 10 Causas de Internação")
    top_10_causas = df_filtrado['diagnostico_principal'].value_counts().nlargest(10)
    percentuais_causas = (top_10_causas / total_internacoes) * 100
    df_top_causas = pd.DataFrame({
        'Diagnóstico': top_10_causas.index,
        'Frequência': top_10_causas.values,
        'Percentual (%)': percentuais_causas.values.round(2)
    })

    fig_ranking = px.bar(
        df_top_causas.sort_values('Frequência'), 
        x='Frequência', y='Diagnóstico', orientation='h',
        title='Top 10 Diagnósticos Mais Frequentes',
        labels={'Frequência':'Número de Internações', 'Diagnóstico':'CID-10'}
    )
    st.plotly_chart(fig_ranking, use_container_width=True)

    # ========== SENSIBILIDADE + FAIXA ETÁRIA ==========
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🩺 Sensibilidade à Atenção Básica")
        sensivel_counts = df_filtrado['sensivel_atencao_basica'].value_counts()
        if not sensivel_counts.empty:
            sensivel = sensivel_counts.get(1, 0)
            nao_sensivel = sensivel_counts.get(0, 0)
            labels = ["Sensíveis", "Não Sensíveis"]
            values = [sensivel, nao_sensivel]

            fig_sensibilidade = px.pie(
                names=labels, values=values,
                title='Distribuição de Internações',
                hole=0.4
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
        st.subheader("👶 Internações por Faixa Etária")

        df_faixa = df_filtrado['faixa_etaria'].value_counts().sort_index().reset_index()
        df_faixa.columns = ['Faixa Etária', 'Internações']

        fig_faixa = px.bar(
            df_faixa, x='Faixa Etária', y='Internações',
            title="Distribuição por Faixa Etária"
        )
        st.plotly_chart(fig_faixa, use_container_width=True)

        # ========== CAPÍTULOS DO CID-10 (TOP 5) ==========
    st.subheader("📂 Top 5 Capítulos do CID-10")
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
        title='Top 5 Capítulos com Mais Internações'
    )
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

    # ========== TABELA COMPLETA ==========
    st.subheader("📋 Tabela Completa de Internações Filtradas")

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
