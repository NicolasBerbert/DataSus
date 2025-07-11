import sqlite3
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import streamlit as st

def create_municipios_table(cursor):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS municipios (
            codigo TEXT PRIMARY KEY,
            nome TEXT,
            regiao_saude TEXT,
            populacao INTEGER
        )
    ''')

def populate_municipios_from_csv(cursor, csv_path):
    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT OR IGNORE INTO municipios (codigo, nome, regiao_saude, populacao)
            VALUES (?, ?, ?, ?)
        ''', (
            str(row['codigo']),
            row['nome'],
            row.get('regiao_saude', 'Desconhecida'),
            int(row['populacao']) if not pd.isna(row['populacao']) else None
        ))

def atualizar_metadata(cursor, fonte_dados):
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tabela TEXT,
            total_registros INTEGER,
            ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            fonte_dados TEXT,
            versao_estrutura TEXT DEFAULT '2.0'
        )
    ''')

    cursor.execute('''
        INSERT INTO metadata (tabela, total_registros, fonte_dados)
        VALUES (
            'municipios',
            (SELECT COUNT(*) FROM municipios),
            ?
        )
    ''', (fonte_dados,))

def gerar_graficos_municipios(cursor):
    st.title("📍 Distribuição por Município")

    df = pd.read_sql_query('''
        SELECT nome, populacao,
               (SELECT COUNT(*) FROM pacientes p WHERE p.codigo_municipio_residencia = m.codigo) AS total_internacoes
        FROM municipios m
        WHERE populacao IS NOT NULL AND populacao > 0
    ''', conn)

    df['taxa_internacao'] = (df['total_internacoes'] / df['populacao']) * 1000
    df = df.sort_values(by='total_internacoes', ascending=False)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🏥 Ranking de Municípios com Mais Internações")
        st.dataframe(df[['nome', 'total_internacoes']].head(10))

    with col2:
        st.subheader("📊 Top Municípios por Taxa (por 1000 habitantes)")
        fig_bar = px.bar(df.sort_values('taxa_internacao', ascending=False).head(10),
                         x='nome', y='taxa_internacao',
                         labels={'taxa_internacao': 'Taxa por 1000 hab.'},
                         title='Taxa de Internação por Município')
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("🗺️ Mapa de Calor - Internações no Paraná")

    # Supondo que há um geojson apropriado com nome dos municípios
    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"

    df['geocodigo'] = df['nome']  # Esse campo deve corresponder ao "properties.name" do geojson

    fig_map = px.choropleth(
        df,
        geojson=geojson_url,
        locations='geocodigo',
        featureidkey="properties.name",
        color='total_internacoes',
        color_continuous_scale="Reds",
        title="Mapa Interativo de Internações por Município"
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_map, use_container_width=True)

def render():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    db_path = os.path.join(base_dir, 'database', 'internacoes_datasus.db')
    municipios_csv = os.path.join(base_dir, 'data', 'municipios_pr_ibge.csv')

    st.write("📂 Caminho do banco de dados:", db_path)
    st.write("📄 Caminho do CSV de municípios:", municipios_csv)

    if not os.path.exists(db_path):
        st.error(f"❌ O banco de dados não foi encontrado em: {db_path}")
        return

    global conn
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    create_municipios_table(cursor)
    populate_municipios_from_csv(cursor, municipios_csv)
    atualizar_metadata(cursor, municipios_csv)
    conn.commit()

    gerar_graficos_municipios(cursor)
    conn.close()


if __name__ == "__main__":
    render()
