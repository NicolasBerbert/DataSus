import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
import joblib
import os
import sqlite3
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

@st.cache_resource
def get_database_connection():
    """Conecta ao banco de dados SQLite"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'database', 'internacoes_datasus.db')
    return sqlite3.connect(db_path, check_same_thread=False)

@st.cache_data
def load_ml_data():
    """Carrega dados otimizados para Machine Learning com descrições legíveis"""
    conn = get_database_connection()
    query = """
        SELECT 
            i.id as internacao_id,
            i.dias_permanencia,
            i.dias_uti_total,
            i.codigo_carater_internacao,
            i.ano_competencia,
            i.mes_competencia,
            i.gestacao_risco,
            
            -- Dados do paciente com descrições
            p.idade_anos,
            p.codigo_sexo,
            s.descricao as sexo,
            p.codigo_municipio_residencia,
            
            -- Dados clínicos
            i.codigo_diagnostico_principal,
            cid.sensivel_atencao_basica,
            cid.capitulo as capitulo_cid,
            
            -- Dados do estabelecimento com descrições
            e.codigo_especialidade,
            esp.descricao as especialidade,
            e.codigo_complexidade,
            comp.descricao as complexidade,
            e.nome_estabelecimento,
            e.tipo_estabelecimento,
            
            -- Valores financeiros
            vf.valor_total,
            vf.valor_servicos_hospitalares,
            vf.valor_uti
            
        FROM internacoes i
        LEFT JOIN pacientes p ON i.paciente_id = p.id
        LEFT JOIN sexo s ON p.codigo_sexo = s.codigo
        LEFT JOIN cid_diagnosticos cid ON i.codigo_diagnostico_principal = cid.codigo
        LEFT JOIN estabelecimentos e ON i.estabelecimento_id = e.id
        LEFT JOIN especialidades esp ON printf('%02d', e.codigo_especialidade) = esp.codigo
        LEFT JOIN complexidade comp ON printf('%02d', e.codigo_complexidade) = comp.codigo
        LEFT JOIN valores_financeiros vf ON i.id = vf.internacao_id
        
        WHERE p.idade_anos IS NOT NULL
        AND vf.valor_total IS NOT NULL
        AND vf.valor_total > 0
        AND i.dias_permanencia IS NOT NULL
        AND i.dias_permanencia >= 0
        AND esp.descricao IS NOT NULL
        AND comp.descricao IS NOT NULL
        AND s.descricao IS NOT NULL
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Preparar dados para ML
    df = prepare_ml_features(df)
    return df

def prepare_ml_features(df):
    """Prepara features para modelos de ML"""
    # Criar features derivadas
    df['tem_uti'] = (df['dias_uti_total'] > 0).astype(int)
    df['valor_por_dia'] = df['valor_total'] / (df['dias_permanencia'] + 1)  # +1 para evitar divisão por zero
    df['idade_grupo'] = pd.cut(df['idade_anos'], bins=[0, 18, 40, 60, 100], labels=['0-18', '19-40', '41-60', '60+'])
    df['urgencia'] = (df['codigo_carater_internacao'] == '2').astype(int)
    df['permanencia_longa'] = (df['dias_permanencia'] > 7).astype(int)
    df['custo_alto'] = (df['valor_total'] > df['valor_total'].quantile(0.75)).astype(int)
    
    # Tratar valores nulos
    df['codigo_especialidade'] = df['codigo_especialidade'].fillna('99')
    df['codigo_complexidade'] = df['codigo_complexidade'].fillna('9')
    df['gestacao_risco'] = df['gestacao_risco'].fillna(0).astype(int)
    df['sensivel_atencao_basica'] = df['sensivel_atencao_basica'].fillna(0).astype(int)
    
    return df

def encode_categorical_features(df, categorical_cols):
    """Codifica variáveis categóricas"""
    df_encoded = df.copy()
    encoders = {}
    
    for col in categorical_cols:
        if col in df_encoded.columns:
            # Remover valores nulos e converter para string
            df_encoded[col] = df_encoded[col].fillna('unknown').astype(str)
            
            le = LabelEncoder()
            df_encoded[col + '_encoded'] = le.fit_transform(df_encoded[col])
            encoders[col] = le
    
    return df_encoded, encoders

def safe_transform_categorical(encoders, col_name, value):
    """Transforma valor categórico de forma segura"""
    if col_name in encoders:
        encoder = encoders[col_name]
        # Verificar se o valor existe nas classes conhecidas
        if str(value) in encoder.classes_:
            return encoder.transform([str(value)])[0]
        else:
            # Usar o primeiro valor conhecido como fallback
            return encoder.transform([encoder.classes_[0]])[0]
    return 0

def render_model_metrics(y_true, y_pred, model_type="regression"):
    """Renderiza métricas do modelo"""
    col1, col2, col3 = st.columns(3)
    
    if model_type == "regression":
        mae = mean_absolute_error(y_true, y_pred)
        mse = mean_squared_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        
        with col1:
            st.metric("MAE (Erro Médio Absoluto)", f"{mae:.2f}")
        with col2:
            st.metric("RMSE (Raiz do Erro Quadrático)", f"{np.sqrt(mse):.2f}")
        with col3:
            st.metric("R² Score", f"{r2:.3f}")
    
    elif model_type == "classification":
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)
        recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)
        
        with col1:
            st.metric("Acurácia", f"{accuracy:.3f}")
        with col2:
            st.metric("Precisão", f"{precision:.3f}")
        with col3:
            st.metric("Recall", f"{recall:.3f}")

def traduzir_nomes_features(feature_names):
    """Traduz nomes técnicos das features para nomes amigáveis"""
    traducoes = {
        'idade_anos': 'Idade (anos)',
        'dias_permanencia': 'Dias de Permanência',
        'codigo_sexo_encoded': 'Sexo',
        'urgencia': 'Urgência',
        'tem_uti': 'UTI',
        'gestacao_risco': 'Risco Gestação',
        'codigo_especialidade_encoded': 'Especialidade',
        'codigo_complexidade_encoded': 'Complexidade',
        'sensivel_atencao_basica': 'Sensível Atenção Básica',
        'mes_competencia': 'Mês'
    }
    
    return [traducoes.get(feature, feature) for feature in feature_names]

def render_feature_importance(model, feature_names):
    """Renderiza importância das features"""
    if hasattr(model, 'feature_importances_'):
        # Traduzir nomes das features
        feature_names_traduzidos = traduzir_nomes_features(feature_names)
        
        importance_df = pd.DataFrame({
            'feature': feature_names_traduzidos,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=True).tail(10)
        
        fig = px.bar(
            importance_df,
            x='importance',
            y='feature',
            orientation='h',
            title="Top 10 Variáveis Mais Importantes",
            color=importance_df['importance'],
            color_continuous_scale=['#eff6ff', '#1e3a8a']
        )
        fig.update_layout(height=400, showlegend=False)
        fig.update_coloraxes(showscale=False)
        fig.update_xaxes(title="Importância")
        fig.update_yaxes(title="Variáveis")
        st.plotly_chart(fig, use_container_width=True)

# ========== MODELOS DE ML ==========

def modelo_predicao_permanencia(data):
    """Predição de Tempo de Permanência"""
    render_styled_section_card(
        "Predição de Tempo de Permanência",
        "Estimativa do tempo de internação baseada em características do paciente e procedimento",
        "🏥"
    )
    
    # Simulador interativo
    st.markdown("#### 🎯 Simulador de Predição")
    
    # Obter opções únicas dos dados
    sexos_unicos = sorted(data['sexo'].dropna().unique())
    especialidades_unicas = sorted(data['especialidade'].dropna().unique()) 
    complexidades_unicas = sorted(data['complexidade'].dropna().unique())
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sim_idade = st.slider("Idade do Paciente", 0, 100, 45)
        sim_sexo = st.selectbox("Sexo", sexos_unicos)
        sim_urgencia = st.selectbox("Tipo de Internação", ["Eletiva", "Urgência"])
    
    with col2:
        sim_uti = st.selectbox("UTI", ["Não", "Sim"])
        sim_gestacao = st.selectbox("Gestação de Risco", ["Não", "Sim"])
        sim_especialidade = st.selectbox("Especialidade", especialidades_unicas)
    
    with col3:
        sim_complexidade = st.selectbox("Complexidade", complexidades_unicas)
        sim_sensivel = st.selectbox("Sensível Atenção Básica", ["Não", "Sim"])
        sim_mes = st.slider("Mês", 1, 12, 6)
    
    # Botão estilizado
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        fazer_predicao = st.button("🔮 Fazer Predição", key="pred_permanencia", use_container_width=True)
    
    if fazer_predicao:
        with st.spinner("Treinando modelo e fazendo predição..."):
            # Preparar dados para treinamento
            features = ['idade_anos', 'codigo_sexo', 'urgencia', 'tem_uti', 'gestacao_risco',
                        'codigo_especialidade', 'codigo_complexidade', 'sensivel_atencao_basica',
                        'mes_competencia']
            
            # Codificar variáveis categóricas
            categorical_cols = ['codigo_sexo', 'codigo_especialidade', 'codigo_complexidade']
            data_encoded, encoders = encode_categorical_features(data, categorical_cols)
            
            # Features finais (usando versões codificadas)
            feature_cols = [col + '_encoded' if col in categorical_cols else col for col in features]
            X = data_encoded[feature_cols].fillna(0)
            y = data_encoded['dias_permanencia']
            
            # Remover outliers extremos (permanência > 30 dias)
            mask = y <= 30
            X, y = X[mask], y[mask]
            
            # Treinar modelo
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            model.fit(X_train, y_train)
            
            # Predições para métricas
            y_pred = model.predict(X_test)
            
            # Converter inputs do usuário para códigos
            sim_sexo_cod = data[data['sexo'] == sim_sexo]['codigo_sexo'].iloc[0] if len(data[data['sexo'] == sim_sexo]) > 0 else '1'
            sim_especialidade_cod = data[data['especialidade'] == sim_especialidade]['codigo_especialidade'].iloc[0] if len(data[data['especialidade'] == sim_especialidade]) > 0 else '1'
            sim_complexidade_cod = data[data['complexidade'] == sim_complexidade]['codigo_complexidade'].iloc[0] if len(data[data['complexidade'] == sim_complexidade]) > 0 else '1'
            
            # Preparar dados para predição
            sim_data = pd.DataFrame({
                'idade_anos': [sim_idade],
                'codigo_sexo': [sim_sexo_cod],
                'urgencia': [1 if sim_urgencia == "Urgência" else 0],
                'tem_uti': [1 if sim_uti == "Sim" else 0],
                'gestacao_risco': [1 if sim_gestacao == "Sim" else 0],
                'codigo_especialidade': [sim_especialidade_cod],
                'codigo_complexidade': [sim_complexidade_cod],
                'sensivel_atencao_basica': [1 if sim_sensivel == "Sim" else 0],
                'mes_competencia': [sim_mes]
            })
            
            # Codificar usando transformação segura
            for col in categorical_cols:
                if col in encoders:
                    sim_data[col + '_encoded'] = safe_transform_categorical(encoders, col, sim_data[col].iloc[0])
            
            sim_features = [col + '_encoded' if col in categorical_cols else col for col in features]
            X_sim = sim_data[sim_features].fillna(0)
            
            predicao = model.predict(X_sim)[0]
            
            # Mostrar resultados
            col1, col2 = st.columns(2)
            
            with col1:
                # Resultado principal com estilo
                render_styled_ml_metric(
                    "Tempo de Permanência Predito",
                    f"{predicao:.1f} dias",
                    "Estimativa baseada no modelo treinado",
                    "🏥"
                )
                
                # Interpretação com estilo
                if predicao <= 2:
                    st.info("🔵 Internação de curta duração - baixo risco")
                elif predicao <= 7:
                    st.warning("🟡 Internação de duração média - monitorar recursos")
                else:
                    st.error("🔴 Internação de longa duração - atenção especial")
                
                # Métricas do modelo
                render_model_metrics(y_test, y_pred, "regression")
            
            with col2:
                # Gráfico de predição vs real
                fig = px.scatter(
                    x=y_test, 
                    y=y_pred,
                    labels={'x': 'Dias Reais', 'y': 'Dias Preditos'},
                    title="Predição vs Realidade"
                )
                fig.add_shape(type="line", x0=0, y0=0, x1=30, y1=30, line=dict(dash="dash"))
                st.plotly_chart(fig, use_container_width=True)
            
            # Importância das features
            render_feature_importance(model, feature_cols)

def modelo_predicao_custos(data):
    """Predição de Custos de Internação"""
    render_styled_section_card(
        "Predição de Custos de Internação",
        "Estimativa de custos baseada em características clínicas e demográficas",
        "💰"
    )
    
    # Simulador de custos
    st.markdown("#### 💳 Simulador de Custos")
    
    # Obter opções únicas dos dados
    sexos_unicos = sorted(data['sexo'].dropna().unique())
    especialidades_unicas = sorted(data['especialidade'].dropna().unique()) 
    complexidades_unicas = sorted(data['complexidade'].dropna().unique())
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        sim_idade = st.slider("Idade", 0, 100, 45, key="custo_idade")
        sim_permanencia = st.slider("Dias de Permanência", 1, 30, 5, key="custo_permanencia")
        sim_sexo = st.selectbox("Sexo", sexos_unicos, key="custo_sexo")
    
    with col2:
        sim_urgencia = st.selectbox("Tipo", ["Eletiva", "Urgência"], key="custo_urgencia")
        sim_uti = st.selectbox("UTI", ["Não", "Sim"], key="custo_uti")
        sim_gestacao = st.selectbox("Gestação Risco", ["Não", "Sim"], key="custo_gestacao")
    
    with col3:
        sim_especialidade = st.selectbox("Especialidade", especialidades_unicas, key="custo_esp")
        sim_complexidade = st.selectbox("Complexidade", complexidades_unicas, key="custo_comp")
        sim_sensivel = st.selectbox("Sensível AB", ["Não", "Sim"], key="custo_sensivel")
    
    # Botão estilizado
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        fazer_predicao = st.button("💰 Calcular Custo Estimado", key="pred_custos", use_container_width=True)
    
    if fazer_predicao:
        with st.spinner("Treinando modelo e calculando custo..."):
            # Preparar dados para treinamento
            features = ['idade_anos', 'dias_permanencia', 'codigo_sexo', 'urgencia', 'tem_uti',
                        'gestacao_risco', 'codigo_especialidade', 'codigo_complexidade',
                        'sensivel_atencao_basica']
            
            # Codificar variáveis categóricas
            categorical_cols = ['codigo_sexo', 'codigo_especialidade', 'codigo_complexidade']
            data_encoded, encoders = encode_categorical_features(data, categorical_cols)
            
            # Features finais
            feature_cols = [col + '_encoded' if col in categorical_cols else col for col in features]
            X = data_encoded[feature_cols].fillna(0)
            y = data_encoded['valor_total']
            
            # Remover outliers extremos (valor > R$ 50.000)
            mask = y <= 50000
            X, y = X[mask], y[mask]
            
            # Treinar modelo
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            model = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=12)
            model.fit(X_train, y_train)
            
            # Predições para métricas
            y_pred = model.predict(X_test)
            
            # Converter inputs do usuário para códigos
            sim_sexo_cod = data[data['sexo'] == sim_sexo]['codigo_sexo'].iloc[0] if len(data[data['sexo'] == sim_sexo]) > 0 else '1'
            sim_especialidade_cod = data[data['especialidade'] == sim_especialidade]['codigo_especialidade'].iloc[0] if len(data[data['especialidade'] == sim_especialidade]) > 0 else '1'
            sim_complexidade_cod = data[data['complexidade'] == sim_complexidade]['codigo_complexidade'].iloc[0] if len(data[data['complexidade'] == sim_complexidade]) > 0 else '1'
            
            # Preparar dados para predição
            sim_data = pd.DataFrame({
                'idade_anos': [sim_idade],
                'dias_permanencia': [sim_permanencia],
                'codigo_sexo': [sim_sexo_cod],
                'urgencia': [1 if sim_urgencia == "Urgência" else 0],
                'tem_uti': [1 if sim_uti == "Sim" else 0],
                'gestacao_risco': [1 if sim_gestacao == "Sim" else 0],
                'codigo_especialidade': [sim_especialidade_cod],
                'codigo_complexidade': [sim_complexidade_cod],
                'sensivel_atencao_basica': [1 if sim_sensivel == "Sim" else 0]
            })
            
            # Codificar usando transformação segura
            for col in categorical_cols:
                if col in encoders:
                    sim_data[col + '_encoded'] = safe_transform_categorical(encoders, col, sim_data[col].iloc[0])
            
            sim_features = [col + '_encoded' if col in categorical_cols else col for col in features]
            X_sim = sim_data[sim_features].fillna(0)
            
            custo_pred = model.predict(X_sim)[0]
            
            # Mostrar resultados
            col1, col2 = st.columns(2)
            
            with col1:
                # Resultado principal com estilo
                render_styled_ml_metric(
                    "Custo Estimado",
                    f"R$ {custo_pred:,.2f}",
                    "Valor previsto para a internação",
                    "💰"
                )
                
                # Comparação com média
                custo_medio = data['valor_total'].mean()
                diferenca = ((custo_pred - custo_medio) / custo_medio) * 100
                
                if diferenca > 20:
                    st.warning(f"🟡 Custo {diferenca:.1f}% acima da média (R$ {custo_medio:,.2f})")
                elif diferenca < -20:
                    st.info(f"🔵 Custo {abs(diferenca):.1f}% abaixo da média (R$ {custo_medio:,.2f})")
                else:
                    st.success(f"🟢 Custo próximo à média (R$ {custo_medio:,.2f})")
                
                # Métricas do modelo
                render_model_metrics(y_test, y_pred, "regression")
            
            with col2:
                # Gráfico de predição vs real
                fig = px.scatter(
                    x=y_test, 
                    y=y_pred,
                    labels={'x': 'Custo Real (R$)', 'y': 'Custo Predito (R$)'},
                    title="Predição de Custos vs Realidade"
                )
                fig.add_shape(type="line", x0=0, y0=0, x1=50000, y1=50000, line=dict(dash="dash"))
                st.plotly_chart(fig, use_container_width=True)
            
            # Importância das features
            render_feature_importance(model, feature_cols)

# Função removida para simplificar o dashboard

# Função removida para simplificar o dashboard

# Função removida para simplificar o dashboard

def modelo_deteccao_anomalias(data):
    """Detecção de Anomalias em Custos"""
    render_styled_section_card(
        "Detecção de Anomalias em Custos",
        "Identificação de internações com custos atípicos para análise e auditoria",
        "🔍"
    )
    
    # Preparar dados para detecção de anomalias
    features = ['dias_permanencia', 'idade_anos', 'tem_uti', 'urgencia',
                'codigo_especialidade_encoded', 'codigo_complexidade_encoded']
    
    # Codificar se necessário
    data_encoded = data.copy()
    if 'codigo_especialidade_encoded' not in data_encoded.columns:
        le_esp = LabelEncoder()
        data_encoded['codigo_especialidade_encoded'] = le_esp.fit_transform(data_encoded['codigo_especialidade'].astype(str))
    if 'codigo_complexidade_encoded' not in data_encoded.columns:
        le_comp = LabelEncoder()
        data_encoded['codigo_complexidade_encoded'] = le_comp.fit_transform(data_encoded['codigo_complexidade'].astype(str))
    
    # Preparar dados (remover outliers extremos primeiro)
    mask = (data_encoded['valor_total'] <= 50000) & (data_encoded['dias_permanencia'] <= 30)
    data_clean = data_encoded[mask].copy()
    
    X = data_clean[features].fillna(0)
    y_custo = data_clean['valor_total']
    
    # Normalizar features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Treinar modelo de detecção de anomalias
    model = IsolationForest(contamination=0.1, random_state=42)
    anomalias = model.fit_predict(X_scaled)
    
    # Adicionar resultados ao dataframe
    data_clean['anomalia'] = anomalias
    data_clean['anomalia_label'] = data_clean['anomalia'].map({1: 'Normal', -1: 'Anomalia'})
    
    # Estatísticas principais com estilo
    n_anomalias = (anomalias == -1).sum()
    n_total = len(anomalias)
    prop_anomalias = (n_anomalias / n_total) * 100
    
    col1, col2, col3 = st.columns(3)
    with col1:
        render_styled_ml_metric(
            "Total de Anomalias",
            f"{n_anomalias:,}",
            "Internações com custos atípicos",
            "🚨"
        )
    with col2:
        render_styled_ml_metric(
            "Proporção de Anomalias",
            f"{prop_anomalias:.1f}%",
            "Percentual sobre total de internações",
            "📊"
        )
    with col3:
        custo_medio_anomalia = data_clean[data_clean['anomalia'] == -1]['valor_total'].mean()
        render_styled_ml_metric(
            "Custo Médio das Anomalias",
            f"R$ {custo_medio_anomalia:,.2f}",
            "Valor médio das internações anômalas",
            "💰"
        )
    
    st.markdown("---")
    
    # Análise por especialidade com estilo
    render_styled_section_card(
        "Análise por Especialidade",
        "Distribuição de anomalias por área médica",
        "🏥"
    )
    
    anomalias_por_esp = data_clean.groupby(['especialidade', 'anomalia_label']).size().unstack(fill_value=0)
    anomalias_por_esp['total'] = anomalias_por_esp.sum(axis=1)
    anomalias_por_esp['percentual_anomalia'] = (anomalias_por_esp.get('Anomalia', 0) / anomalias_por_esp['total'] * 100).round(1)
    anomalias_por_esp = anomalias_por_esp.sort_values('percentual_anomalia', ascending=False).head(10)
    
    fig = px.bar(
        x=anomalias_por_esp['percentual_anomalia'],
        y=anomalias_por_esp.index,
        orientation='h',
        title="Percentual de Anomalias por Especialidade (Top 10)",
        labels={'x': 'Percentual de Anomalias (%)', 'y': 'Especialidade'},
        color=anomalias_por_esp['percentual_anomalia'],
        color_continuous_scale=['#eff6ff', '#1e3a8a']
    )
    fig.update_layout(height=400, showlegend=False)
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Análise de custo vs tempo
    render_styled_section_card(
        "Análise de Custo vs Tempo",
        "Relação entre custo e tempo de permanência",
        "📊"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Violin plot para melhor visualização da distribuição
        fig = px.violin(
            data_clean,
            x='anomalia_label',
            y='valor_total',
            title="Distribuição de Custos por Tipo",
            labels={'anomalia_label': 'Tipo', 'valor_total': 'Valor Total (R$)'},
            color='anomalia_label',
            color_discrete_map={'Normal': '#3498db', 'Anomalia': '#e74c3c'}
        )
        fig.update_layout(height=350, showlegend=False)
        fig.update_xaxes(title="Tipo de Internação")
        fig.update_yaxes(title="Valor Total (R$)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Scatter plot mais limpo
        fig = px.scatter(
            data_clean,
            x='dias_permanencia',
            y='valor_total',
            color='anomalia_label',
            title="Custo vs Tempo de Permanência",
            labels={'dias_permanencia': 'Dias de Permanência', 'valor_total': 'Valor Total (R$)'},
            color_discrete_map={'Normal': '#3498db', 'Anomalia': '#e74c3c'}
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Filtrar anomalias para a tabela
    anomalias_df = data_clean[data_clean['anomalia'] == -1].copy()
    
    if len(anomalias_df) > 0:
        # Usar os dados já carregados para evitar problemas de conexão
        # Filtrar apenas as anomalias dos dados originais
        anomalias_ids = anomalias_df['internacao_id'].tolist()
        anomalias_completas = data[data['internacao_id'].isin(anomalias_ids)].copy()
        
        # Preparar colunas necessárias
        anomalias_completas['tem_uti'] = anomalias_completas['dias_uti_total'].apply(lambda x: 'Sim' if x > 0 else 'Não')
        anomalias_completas['urgencia'] = anomalias_completas['codigo_carater_internacao'].apply(lambda x: 'Sim' if x == '2' else 'Não')
        
        # Top anomalias com estabelecimentos
        render_styled_section_card(
            "Principais Anomalias Detectadas",
            "Internações com maiores desvios de custo para análise",
            "🚨"
        )
        
        # Preparar dados para exibição
        anomalias_display = anomalias_completas.nlargest(20, 'valor_total').copy()
        anomalias_display['valor_total'] = anomalias_display['valor_total'].round(2)
        
        # Calcular desvio do custo médio
        custo_medio_geral = data_clean[data_clean['anomalia'] == 1]['valor_total'].mean()
        anomalias_display['desvio_percentual'] = ((anomalias_display['valor_total'] - custo_medio_geral) / custo_medio_geral * 100).round(1)
        
        # Reorganizar colunas
        colunas_exibir = {
            'internacao_id': 'ID Internação',
            'nome_estabelecimento': 'Estabelecimento',
            'especialidade': 'Especialidade', 
            'complexidade': 'Complexidade',
            'idade_anos': 'Idade',
            'dias_permanencia': 'Dias',
            'valor_total': 'Valor (R$)',
            'desvio_percentual': 'Desvio (%)',
            'tem_uti': 'UTI',
            'urgencia': 'Urgência'
        }
        
        anomalias_final = anomalias_display[list(colunas_exibir.keys())].copy()
        anomalias_final.columns = list(colunas_exibir.values())
        
        # Aplicar formatação
        def format_currency(val):
            return f"R$ {val:,.2f}"
        
        def format_percentage(val):
            return f"{val:+.1f}%"
        
        # Exibir tabela com formatação
        st.dataframe(
            anomalias_final.style.format({
                'Valor (R$)': format_currency,
                'Desvio (%)': format_percentage
            }),
            use_container_width=True
        )
    else:
        st.info("Nenhuma anomalia detectada nos dados atuais.")
    

# Função removida para simplificar o dashboard

# Função removida para simplificar o dashboard

def render_styled_ml_metric(title, value, help_text, icon="📊"):
    """Renderiza uma métrica estilizada para ML"""
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
        <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.2rem; margin-right: 0.5rem;">{icon}</span>
            <h4 style="margin: 0; font-size: 0.9rem; opacity: 0.9;">{title}</h4>
        </div>
        <div style="font-size: 1.8rem; font-weight: bold; margin: 0.5rem 0;">
            {value}
        </div>
        <div style="font-size: 0.8rem; opacity: 0.7;">
            {help_text}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_styled_section_card(title, content, icon="📊"):
    """Renderiza uma seção estilizada"""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #667eea;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 1rem;">
            <span style="font-size: 1.5rem; margin-right: 1rem;">{icon}</span>
            <h3 style="margin: 0; color: #2c3e50;">{title}</h3>
        </div>
        <div style="color: #495057;">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render(data):
    """Renderiza a página de Machine Learning"""
    
    st.markdown("## 🤖 Análises de Machine Learning")
    st.markdown("**Modelos preditivos e análises avançadas para otimização da gestão hospitalar**")
    
    # Menu de seleção de análises com estilo
    st.markdown("### Selecione a Análise")
    
    analises_disponiveis = {
        "🏥 Predição de Tempo de Permanência": modelo_predicao_permanencia,
        "💰 Predição de Custos de Internação": modelo_predicao_custos,
        "🔍 Detecção de Anomalias em Custos": modelo_deteccao_anomalias
    }
    
    analise_selecionada = st.selectbox(
        "Escolha uma análise:",
        list(analises_disponiveis.keys()),
        help="Cada análise utiliza diferentes modelos de Machine Learning para insights específicos"
    )
    
    st.markdown("---")
    
    # Carregar dados otimizados para ML apenas quando necessário
    try:
        # Carregar dados do main.py (já carregados) e preparar para ML
        ml_data = load_ml_data()
        
        # Executar análise selecionada
        analises_disponiveis[analise_selecionada](ml_data)
        
    except Exception as e:
        st.error(f"Erro ao executar análise: {str(e)}")
        st.info("Verifique se os dados estão disponíveis e tente novamente.")
    
    # Informações técnicas
    with st.expander("Informações Técnicas"):
        st.markdown("""
        **Modelos Utilizados:**
        - Random Forest (Regressão e Classificação)
        - Isolation Forest (Detecção de Anomalias)
        - Logistic Regression (Classificação Binária)
        
        **Métricas de Avaliação:**
        - Regressão: MAE, RMSE, R²
        - Classificação: Acurácia, Precisão, Recall, F1-Score
        - Detecção de Anomalias: Taxa de Detecção
        
        **Dados Utilizados:**
        - Registros de internações com variáveis expandidas
        - Variáveis: idade, diagnóstico, tipo de internação, valores, etc.
        - Período: Janeiro a Março 2025
        - Treinamento acontece a cada predição para garantir dados atualizados
        """)