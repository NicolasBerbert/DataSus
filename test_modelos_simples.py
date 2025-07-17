#!/usr/bin/env python3
"""
🤖 Teste SIMPLES e ROBUSTO de Modelos ML - DataSUS

Versão simplificada para evitar erros e focar nos resultados.
"""

import pandas as pd
import numpy as np
import sqlite3
import os
import time
import warnings
warnings.filterwarnings('ignore')

# Modelos ML
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR

# Métricas e utilitários
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder, StandardScaler

def print_header(title):
    print("=" * 70)
    print(f"🎯 {title}")
    print("=" * 70)

def get_database_connection():
    db_path = os.path.join('database', 'internacoes_datasus.db')
    if not os.path.exists(db_path):
        print(f"❌ Erro: Banco de dados não encontrado em {db_path}")
        return None
    return sqlite3.connect(db_path)

def load_data_simple():
    """Carrega dados de forma simples"""
    conn = get_database_connection()
    if conn is None:
        return None
    
    query = """
        SELECT 
            i.dias_permanencia,
            i.dias_uti_total,
            i.codigo_carater_internacao,
            i.mes_competencia,
            i.gestacao_risco,
            p.idade_anos,
            p.codigo_sexo,
            e.codigo_especialidade,
            e.codigo_complexidade,
            cid.sensivel_atencao_basica,
            vf.valor_total
        FROM internacoes i
        LEFT JOIN pacientes p ON i.paciente_id = p.id
        LEFT JOIN cid_diagnosticos cid ON i.codigo_diagnostico_principal = cid.codigo
        LEFT JOIN estabelecimentos e ON i.estabelecimento_id = e.id
        LEFT JOIN valores_financeiros vf ON i.id = vf.internacao_id
        WHERE p.idade_anos IS NOT NULL
        AND vf.valor_total IS NOT NULL
        AND vf.valor_total > 0
        AND i.dias_permanencia IS NOT NULL
        AND i.dias_permanencia > 0
        LIMIT 3000
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def prepare_data_simple(df):
    """Prepara dados de forma simples"""
    # Preencher valores nulos
    df = df.fillna(0)
    
    # Criar features básicas
    df['tem_uti'] = (df['dias_uti_total'] > 0).astype(int)
    df['urgencia'] = (df['codigo_carater_internacao'] == 2).astype(int)
    df['gestacao_risco'] = df['gestacao_risco'].astype(int)
    df['sensivel_atencao_basica'] = df['sensivel_atencao_basica'].astype(int)
    
    # Codificar variáveis categóricas
    le_sexo = LabelEncoder()
    df['sexo_encoded'] = le_sexo.fit_transform(df['codigo_sexo'].astype(str))
    
    le_esp = LabelEncoder()
    df['especialidade_encoded'] = le_esp.fit_transform(df['codigo_especialidade'].astype(str))
    
    le_comp = LabelEncoder()
    df['complexidade_encoded'] = le_comp.fit_transform(df['codigo_complexidade'].astype(str))
    
    return df

def test_models_simple(X, y, target_name):
    """Testa modelos de forma simples"""
    print(f"🔄 Testando {target_name} com {len(X)} registros...")
    
    # Dividir dados
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Normalizar para SVM
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Modelos
    models = {
        'Random Forest': RandomForestRegressor(n_estimators=50, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=50, random_state=42),
        'Linear Regression': LinearRegression(),
        'Ridge Regression': Ridge(alpha=1.0),
        'Decision Tree': DecisionTreeRegressor(max_depth=10, random_state=42),
        'K-Neighbors': KNeighborsRegressor(n_neighbors=5),
        'SVM': SVR(kernel='rbf', C=1.0)
    }
    
    results = {}
    
    for name, model in models.items():
        try:
            start_time = time.time()
            
            # Usar dados normalizados apenas para SVM e KNN
            if name in ['SVM', 'K-Neighbors']:
                X_train_use = X_train_scaled
                X_test_use = X_test_scaled
            else:
                X_train_use = X_train
                X_test_use = X_test
            
            # Treinar
            model.fit(X_train_use, y_train)
            
            # Predizer
            y_pred = model.predict(X_test_use)
            
            # Calcular métricas
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            training_time = time.time() - start_time
            
            results[name] = {
                'R²': r2,
                'MAE': mae,
                'RMSE': rmse,
                'Time': training_time
            }
            
            print(f"   ✅ {name}: R² = {r2:.3f}, MAE = {mae:.2f}")
            
        except Exception as e:
            print(f"   ❌ {name}: Erro - {str(e)}")
            results[name] = {
                'R²': -999,
                'MAE': 999,
                'RMSE': 999,
                'Time': 0
            }
    
    return results

def show_results(results, title):
    """Mostra resultados formatados"""
    print(f"\n📊 {title}")
    print("-" * 60)
    
    # Ordenar por R²
    sorted_results = sorted(results.items(), key=lambda x: x[1]['R²'], reverse=True)
    
    print(f"{'Modelo':<20} {'R²':<8} {'MAE':<8} {'RMSE':<8} {'Tempo':<8}")
    print("-" * 60)
    
    for name, metrics in sorted_results:
        r2 = metrics['R²']
        mae = metrics['MAE']
        rmse = metrics['RMSE']
        time_sec = metrics['Time']
        
        if r2 == -999:
            print(f"{name:<20} {'ERRO':<8} {'ERRO':<8} {'ERRO':<8} {'ERRO':<8}")
        else:
            print(f"{name:<20} {r2:<8.3f} {mae:<8.2f} {rmse:<8.2f} {time_sec:<8.2f}")
    
    # Melhor modelo
    best_model = sorted_results[0][0]
    best_r2 = sorted_results[0][1]['R²']
    
    print(f"\n🏆 MELHOR: {best_model} (R² = {best_r2:.3f})")
    
    if best_r2 > 0.7:
        print("   ✅ EXCELENTE performance!")
    elif best_r2 > 0.5:
        print("   ⚠️ BOA performance")
    elif best_r2 > 0.3:
        print("   🟡 MODERADA performance")
    else:
        print("   ❌ BAIXA performance")
    
    return best_model, best_r2

def main():
    print_header("TESTE SIMPLES DE MODELOS ML - DATASUS")
    
    # Carregar dados
    print("🔧 Carregando dados...")
    data = load_data_simple()
    
    if data is None:
        print("❌ Erro ao carregar dados")
        return
    
    print(f"✅ {len(data)} registros carregados")
    
    # Preparar dados
    print("🔧 Preparando dados...")
    data = prepare_data_simple(data)
    
    # Limpar outliers extremos
    data = data[data['dias_permanencia'] <= 30]
    data = data[data['valor_total'] <= 50000]
    
    print(f"✅ {len(data)} registros após limpeza")
    
    # TESTE 1: Predição de Permanência
    print("\n" + "="*50)
    print("🏥 TESTE 1: PREDIÇÃO DE PERMANÊNCIA")
    print("="*50)
    
    features_perm = ['idade_anos', 'sexo_encoded', 'urgencia', 'tem_uti', 
                     'gestacao_risco', 'especialidade_encoded', 'complexidade_encoded',
                     'sensivel_atencao_basica', 'mes_competencia']
    
    X_perm = data[features_perm]
    y_perm = data['dias_permanencia']
    
    results_perm = test_models_simple(X_perm, y_perm, "Permanência")
    best_perm, r2_perm = show_results(results_perm, "RESULTADOS - PERMANÊNCIA")
    
    # TESTE 2: Predição de Custos
    print("\n" + "="*50)
    print("💰 TESTE 2: PREDIÇÃO DE CUSTOS")
    print("="*50)
    
    features_cost = ['idade_anos', 'dias_permanencia', 'sexo_encoded', 'urgencia', 
                     'tem_uti', 'gestacao_risco', 'especialidade_encoded', 
                     'complexidade_encoded', 'sensivel_atencao_basica']
    
    X_cost = data[features_cost]
    y_cost = data['valor_total']
    
    results_cost = test_models_simple(X_cost, y_cost, "Custos")
    best_cost, r2_cost = show_results(results_cost, "RESULTADOS - CUSTOS")
    
    # RESUMO FINAL
    print("\n" + "="*50)
    print("🎯 RESUMO FINAL")
    print("="*50)
    
    print(f"🏥 Melhor para PERMANÊNCIA: {best_perm} (R² = {r2_perm:.3f})")
    print(f"💰 Melhor para CUSTOS: {best_cost} (R² = {r2_cost:.3f})")
    
    if best_perm == best_cost:
        print(f"\n✅ RECOMENDAÇÃO: Use {best_perm} para ambos!")
    else:
        print(f"\n⚠️ RECOMENDAÇÃO: Use modelos diferentes:")
        print(f"   - Permanência: {best_perm}")
        print(f"   - Custos: {best_cost}")
    print("\n✅ ANÁLISE CONCLUÍDA!")

if __name__ == "__main__":
    main()