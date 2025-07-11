"""
Configurações centralizadas do projeto DataSUS
"""
import os

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Caminhos dos diretórios
DIRS = {
    'data': os.path.join(BASE_DIR, 'data'),
    'data_raw': os.path.join(BASE_DIR, 'data', 'raw'),
    'data_processed': os.path.join(BASE_DIR, 'data', 'processed'),
    'database': os.path.join(BASE_DIR, 'database'),
    'docs': os.path.join(BASE_DIR, 'docs'),
    'scripts': os.path.join(BASE_DIR, 'scripts'),
    'dashboard': os.path.join(BASE_DIR, 'dashboard'),
}

# Arquivos principais
FILES = {
    'database': os.path.join(DIRS['database'], 'internacoes_datasus.db'),
    'csv_completo': os.path.join(DIRS['data_processed'], 'dados_completos_internacoes_pr_2025.csv'),
    'cid10_reference': os.path.join(DIRS['docs'], 'cid10_ultimaversaodisponivel_2012.txt'),
    'requirements': os.path.join(BASE_DIR, 'requirements.txt'),
}

# Configurações do banco de dados
DATABASE = {
    'name': 'internacoes_datasus.db',
    'path': FILES['database'],
    'version': '2.0',
}

# Configurações do dashboard
DASHBOARD = {
    'title': 'Dashboard - Internações Hospitalares por Causas Sensíveis',
    'icon': '🏥',
    'layout': 'wide',
    'persona': {
        'nome': 'Dr. Roberto',
        'funcao': 'Gestor de Unidade Básica de Saúde',
        'objetivo': 'Como gestor de UBS, quero entender as causas mais comuns de internações evitáveis para planejar melhor os recursos da unidade.'
    }
}

# Configurações de dados
DATA = {
    'periodo_analise': '2025 (Janeiro-Março)',
    'fonte': 'SIH/SUS - Sistema de Informações Hospitalares',
    'uf': 'Paraná (PR)',
    'total_meses': 3,
}

# Mapeamento de meses
MESES = {
    1: 'Janeiro',
    2: 'Fevereiro', 
    3: 'Março',
    4: 'Abril',
    5: 'Maio',
    6: 'Junho',
    7: 'Julho',
    8: 'Agosto',
    9: 'Setembro',
    10: 'Outubro',
    11: 'Novembro',
    12: 'Dezembro'
}

# Configurações de logging
LOGGING = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

def get_database_path():
    """Retorna o caminho para o banco de dados"""
    return FILES['database']

def get_csv_path():
    """Retorna o caminho para o CSV completo"""
    return FILES['csv_completo']

def ensure_directories():
    """Garante que todos os diretórios necessários existam"""
    for dir_name, dir_path in DIRS.items():
        os.makedirs(dir_path, exist_ok=True)
    return True