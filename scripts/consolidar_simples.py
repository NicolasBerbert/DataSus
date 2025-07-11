import os
import csv

def consolidar_csvs_simples():
    """
    Consolida todos os 3 arquivos CSV usando Python padrão
    """
    
    # Caminhos
    base_dir = os.path.dirname(os.path.dirname(__file__))
    raw_dir = os.path.join(base_dir, 'data', 'raw', 'csv')
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    output_file = os.path.join(processed_dir, 'dados_completos_internacoes_pr_2025.csv')
    
    # Lista dos arquivos CSV
    csv_files = [
        'RDPR2501.csv',  # Janeiro
        'RDPR2502.csv',  # Fevereiro
        'RDPR2503.csv'   # Março
    ]
    
    print("Consolidando todos os 3 arquivos CSV...")
    
    header_written = False
    total_records = 0
    month_counts = {}
    
    with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
        writer = None
        
        for i, csv_file in enumerate(csv_files, 1):
            csv_path = os.path.join(raw_dir, csv_file)
            
            if os.path.exists(csv_path):
                print(f"Processando {csv_file}...")
                
                with open(csv_path, 'r', encoding='utf-8') as infile:
                    reader = csv.reader(infile)
                    
                    # Ler header
                    header = next(reader)
                    
                    # Adicionar coluna ARQUIVO_ORIGEM ao header se necessário
                    if 'ARQUIVO_ORIGEM' not in header:
                        header.append('ARQUIVO_ORIGEM')
                    
                    # Escrever header apenas uma vez
                    if not header_written:
                        writer = csv.writer(outfile)
                        writer.writerow(header)
                        header_written = True
                    
                    # Processar dados
                    file_records = 0
                    for row in reader:
                        # Adicionar nome do arquivo de origem
                        if len(row) == len(header) - 1:  # Se não tem ARQUIVO_ORIGEM
                            row.append(csv_file)
                        elif len(row) == len(header):  # Se já tem ARQUIVO_ORIGEM
                            row[-1] = csv_file  # Sobrescrever
                        
                        writer.writerow(row)
                        file_records += 1
                        total_records += 1
                        
                        # Contar por mês (assumindo que MES_CMPT é a 3ª coluna)
                        if len(row) >= 3:
                            month = row[2].strip('"')
                            month_counts[month] = month_counts.get(month, 0) + 1
                    
                    print(f"  - {file_records:,} registros processados")
            else:
                print(f"Arquivo não encontrado: {csv_path}")
    
    print(f"\n✅ Consolidação concluída!")
    print(f"Total de registros: {total_records:,}")
    print(f"Arquivo criado: {output_file}")
    
    print("\nDistribuição por mês:")
    for month in sorted(month_counts.keys()):
        print(f"  Mês {month}: {month_counts[month]:,} registros")
    
    return output_file

if __name__ == "__main__":
    resultado = consolidar_csvs_simples()
    print(f"\nArquivo consolidado: {resultado}")