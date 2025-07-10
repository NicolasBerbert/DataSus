#!/usr/bin/env python3
"""
Script para limpeza e tratamento de dados dos arquivos CSV do DATASUS (Paraná - 2025)
Processa dados de internações de janeiro, fevereiro e março de 2025
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

def analyze_missing_data(df, filename):
    """Analisa dados faltantes em um DataFrame"""
    print(f"\n--- Análise de dados faltantes: {filename} ---")
    print(f"Total de linhas: {len(df)}")
    print(f"Total de colunas: {len(df.columns)}")
    
    # Calcula percentual de dados faltantes por coluna
    missing_stats = []
    for col in df.columns:
        missing_count = df[col].isna().sum() + (df[col] == '').sum() + (df[col] == '0').sum()
        missing_percent = (missing_count / len(df)) * 100
        missing_stats.append({
            'coluna': col,
            'faltantes': missing_count,
            'percentual': missing_percent
        })
    
    missing_df = pd.DataFrame(missing_stats)
    missing_df = missing_df.sort_values('percentual', ascending=False)
    
    print("\nTop 10 colunas com mais dados faltantes:")
    print(missing_df.head(10).to_string(index=False))
    
    return missing_df

def clean_data(df, filename):
    """Limpa dados do DataFrame"""
    print(f"\n--- Limpeza de dados: {filename} ---")
    original_rows = len(df)
    original_cols = len(df.columns)
    
    # Substitui valores vazios por NaN
    df = df.replace('', np.nan)
    df = df.replace('0', np.nan)
    df = df.replace('00', np.nan)
    df = df.replace('000', np.nan)
    df = df.replace('0000', np.nan)
    df = df.replace('00000', np.nan)
    df = df.replace('000000', np.nan)
    df = df.replace('0000000', np.nan)
    df = df.replace('00000000', np.nan)
    df = df.replace('000000000', np.nan)
    df = df.replace('0000000000', np.nan)
    df = df.replace('00000000000', np.nan)
    df = df.replace('000000000000', np.nan)
    df = df.replace('0000000000000', np.nan)
    df = df.replace('00000000000000', np.nan)
    df = df.replace('000000000000000', np.nan)
    
    # Remove colunas que estão completamente vazias ou quase vazias (>95% faltantes)
    cols_to_remove = []
    for col in df.columns:
        missing_percent = (df[col].isna().sum() / len(df)) * 100
        if missing_percent > 95:
            cols_to_remove.append(col)
            print(f"Removendo coluna '{col}' - {missing_percent:.1f}% faltantes")
    
    df = df.drop(columns=cols_to_remove)
    
    # Remove linhas com mais de 70% dos dados faltantes
    threshold = int(0.7 * len(df.columns))
    rows_to_remove = []
    
    for idx, row in df.iterrows():
        missing_count = row.isna().sum()
        missing_percent = (missing_count / len(df.columns)) * 100
        if missing_count > threshold:
            rows_to_remove.append(idx)
            print(f"Removendo linha {idx} - {missing_percent:.1f}% faltantes")
    
    df = df.drop(index=rows_to_remove)
    
    # Remove linhas duplicadas
    duplicated_rows = df.duplicated().sum()
    if duplicated_rows > 0:
        print(f"Removendo {duplicated_rows} linhas duplicadas")
        df = df.drop_duplicates()
    
    # Tratamento específico para colunas importantes
    # Converte colunas numéricas que deveriam ser números
    numeric_cols = ['IDADE', 'DIAS_PERM', 'QT_DIARIAS', 'VAL_TOT', 'VAL_SH', 'VAL_SP', 'SEQUENCIA']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Converte datas
    date_cols = ['DT_INTER', 'DT_SAIDA', 'NASC']
    for col in date_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format='%Y%m%d', errors='coerce')
    
    final_rows = len(df)
    final_cols = len(df.columns)
    removed_rows = original_rows - final_rows
    removed_cols = original_cols - final_cols
    
    print(f"\nResumo da limpeza:")
    print(f"Linhas originais: {original_rows}")
    print(f"Linhas finais: {final_rows}")
    print(f"Linhas removidas: {removed_rows}")
    print(f"Colunas originais: {original_cols}")
    print(f"Colunas finais: {final_cols}")
    print(f"Colunas removidas: {removed_cols}")
    
    return df

def main():
    """Função principal"""
    print("=== SCRIPT DE LIMPEZA DE DADOS DATASUS ===")
    print("Processando dados de internações do Paraná - 2025")
    print("Arquivos: Janeiro, Fevereiro e Março")
    
    # Arquivos CSV
    csv_files = [
        'data/raw/csv/RDPR2501.csv',  # Janeiro 2025
        'data/raw/csv/RDPR2502.csv',  # Fevereiro 2025
        'data/raw/csv/CSVs/RDPR2503.csv'   # Março 2025
    ]
    
    all_dataframes = []
    
    # Processa cada arquivo
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            print(f"\n{'='*50}")
            print(f"Processando: {csv_file}")
            
            try:
                # Lê o arquivo CSV
                df = pd.read_csv(csv_file, dtype=str, low_memory=False)
                
                # Analisa dados faltantes
                missing_stats = analyze_missing_data(df, os.path.basename(csv_file))
                
                # Limpa os dados
                df_cleaned = clean_data(df, os.path.basename(csv_file))
                
                # Adiciona coluna de origem
                df_cleaned['ARQUIVO_ORIGEM'] = os.path.basename(csv_file)
                
                all_dataframes.append(df_cleaned)
                
            except Exception as e:
                print(f"Erro ao processar {csv_file}: {e}")
        else:
            print(f"Arquivo não encontrado: {csv_file}")
    
    # Combina todos os DataFrames
    if all_dataframes:
        print(f"\n{'='*50}")
        print("COMBINANDO TODOS OS DADOS")
        
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        # Remove duplicatas finais
        original_combined = len(combined_df)
        combined_df = combined_df.drop_duplicates()
        final_combined = len(combined_df)
        
        print(f"Total de registros após combinação: {original_combined}")
        print(f"Total de registros após remoção de duplicatas: {final_combined}")
        print(f"Duplicatas removidas: {original_combined - final_combined}")
        
        # Salva arquivo final
        output_file = 'data/dados_limpos_internacoes_pr_2025.csv'
        combined_df.to_csv(output_file, index=False, encoding='utf-8')
        
        print(f"\n{'='*50}")
        print("RESULTADO FINAL")
        print(f"Arquivo gerado: {output_file}")
        print(f"Total de registros: {len(combined_df)}")
        print(f"Total de colunas: {len(combined_df.columns)}")
        
        # Estatísticas finais
        print(f"\nEstatísticas finais:")
        print(f"- Período: Janeiro a Março de 2025")
        print(f"- Estado: Paraná")
        print(f"- Tipo: Dados de internações hospitalares")
        print(f"- Dados prontos para inserção no banco de dados")
        
        # Salva relatório de limpeza
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f'data/relatorio_limpeza_{timestamp}.txt'
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE LIMPEZA DE DADOS DATASUS\n")
            f.write("="*50 + "\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Arquivo final: {output_file}\n")
            f.write(f"Registros finais: {len(combined_df)}\n")
            f.write(f"Colunas finais: {len(combined_df.columns)}\n")
            f.write("\nColunas do arquivo final:\n")
            for i, col in enumerate(combined_df.columns, 1):
                f.write(f"{i:2d}. {col}\n")
        
        print(f"Relatório salvo em: {report_file}")
        
    else:
        print("Nenhum arquivo foi processado com sucesso.")

if __name__ == "__main__":
    main()