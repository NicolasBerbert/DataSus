# Relatório de Desenvolvimento - Dashboard de Internações Hospitalares

## 📋 Resumo do Projeto

**Projeto:** Dashboard de Internações Hospitalares por Causas Sensíveis à Atenção Básica  
**Persona:** Dr. Roberto - Gestor de Unidade Básica de Saúde  
**Objetivo:** Entender as causas mais comuns de internações evitáveis para planejar melhor os recursos da unidade

## 🎯 Estrutura Implementada

### 1. Banco de Dados SQLite
- **Arquivo:** `internacoes_datasus.db`
- **Tabela Principal:** `internacoes` (98.603 registros)
- **Script ETL:** `scripts/create_database.py`
- **Índices Otimizados:** Por diagnóstico, município, idade, sexo, período e valores

### 2. Dashboard Streamlit
- **Aplicação Principal:** `dashboard/main.py`
- **Estrutura Modular:** 7 páginas separadas em arquivos individuais
- **Navegação:** Sidebar com informações da persona

## 📊 Divisão de Trabalho por Desenvolvedor

### Desenvolvedor 1 - Visão Geral (`pages/overview.py`)
**Prazo Sugerido:** 3-4 dias

**Responsabilidades:**
- Implementar KPIs principais (total internações, valores, médias)
- Criar gráficos resumo (pizza, barras, linha temporal)
- Desenvolver cards informativos com insights
- Implementar filtros básicos (período, idade, sexo)

**Entregas:**
- Métricas em tempo real
- Dashboard executivo
- Filtros funcionais

---

### Desenvolvedor 2 - Causas Principais (`pages/causas_principais.py`)
**Prazo Sugerido:** 4-5 dias

**Responsabilidades:**
- Ranking das principais causas CID-10
- Classificação por sensibilidade à atenção básica
- Análise por grupos/capítulos do CID
- Interpretação clínica dos dados

**Entregas:**
- Top 20 CIDs com percentuais
- Categorização sensível vs não sensível
- Recomendações específicas por causa

---

### Desenvolvedor 3 - Análise Demográfica (`pages/analise_demografica.py`)
**Prazo Sugerido:** 3-4 dias

**Responsabilidades:**
- Distribuição por faixa etária e sexo
- Pirâmide etária interativa
- Correlações demográficas
- Perfil típico do paciente

**Entregas:**
- Histogramas e pirâmides
- Análise por sexo e idade
- Grupos prioritários identificados

---

### Desenvolvedor 4 - Análise Geográfica (`pages/analise_geografica.py`)
**Prazo Sugerido:** 5-6 dias

**Responsabilidades:**
- Mapas interativos do Paraná
- Análise por município e região
- Fluxo de pacientes
- Integração com dados do IBGE

**Entregas:**
- Mapas de calor (choropleth)
- Ranking de municípios
- Análise de referenciamento

**Observações Técnicas:**
- Necessário integrar com dados do IBGE para coordenadas
- Usar bibliotecas como `geopandas` ou `plotly.graph_objects`
- Considerar APIs de mapas se necessário

---

### Desenvolvedor 5 - Análise Temporal (`pages/analise_temporal.py`)
**Prazo Sugerido:** 4-5 dias

**Responsabilidades:**
- Séries temporais de internações
- Análise de sazonalidade
- Padrões por dia da semana
- Projeções futuras (se aplicável)

**Entregas:**
- Gráficos de linha temporais
- Análise de tendências
- Identificação de picos sazonais

**Observações Técnicas:**
- Converter strings de data para datetime
- Usar `pandas.to_datetime()` para conversões
- Considerar bibliotecas de séries temporais

---

### Desenvolvedor 6 - Gestão de Recursos (`pages/gestao_recursos.py`)
**Prazo Sugerido:** 4-5 dias

**Responsabilidades:**
- Análise de custos por tipo de internação
- Identificação de outliers financeiros
- ROI da atenção básica
- Dashboards financeiros

**Entregas:**
- Análise custo-efetividade
- Identificação de casos de alto custo
- Projeções orçamentárias

---

### Desenvolvedor 7 - Recomendações (`pages/recomendacoes.py`)
**Prazo Sugerido:** 3-4 dias

**Responsabilidades:**
- Análise automatizada de padrões
- Recomendações priorizadas
- Planos de ação específicos
- Relatórios executivos

**Entregas:**
- Insights automáticos
- Planos de implementação
- Indicadores de monitoramento

## 🛠️ Configuração do Ambiente

### Dependências (requirements.txt)
```
pandas==2.0.3
streamlit==1.28.0
plotly==5.15.0
numpy==1.25.2
seaborn==0.12.2
matplotlib==3.7.2
```

### Instalação
```bash
pip install -r requirements.txt
```

### Execução do ETL
```bash
python scripts/create_database.py
```

### Execução do Dashboard
```bash
streamlit run dashboard/main.py
```

## 📁 Estrutura de Arquivos

```
DataSus/
├── data/
│   ├── processed/
│   │   └── dados_limpos_internacoes_pr_2025.csv
│   └── raw/
├── scripts/
│   └── create_database.py
├── dashboard/
│   ├── main.py
│   └── pages/
│       ├── __init__.py
│       ├── overview.py
│       ├── causas_principais.py
│       ├── analise_demografica.py
│       ├── analise_geografica.py
│       ├── analise_temporal.py
│       ├── gestao_recursos.py
│       └── recomendacoes.py
├── internacoes_datasus.db
├── requirements.txt
└── RELATORIO_DESENVOLVIMENTO.md
```

## 🔍 Dados Disponíveis

### Principais Campos
- **Demográficos:** idade, sexo, município de residência
- **Clínicos:** diagnóstico principal (CID-10), procedimentos
- **Temporais:** data internação, data saída, dias de permanência
- **Financeiros:** valor total, custos detalhados
- **Gestão:** caráter da internação, tipo de estabelecimento

### Estatísticas Gerais
- **Total de Registros:** 98.603 internações
- **Período:** 2025 (dados de janeiro)
- **Colunas:** 64 campos detalhados
- **Municípios:** Múltiplos municípios do Paraná

## 🚀 Próximos Passos

### Para Cada Desenvolvedor
1. **Clonar o repositório**
2. **Instalar dependências** (`pip install -r requirements.txt`)
3. **Executar ETL** (`python scripts/create_database.py`)
4. **Testar aplicação** (`streamlit run dashboard/main.py`)
5. **Desenvolver sua página específica**

### Coordenação da Equipe
- **Reuniões semanais** para alinhamento
- **Code reviews** antes de merge
- **Testes integrados** antes do deploy
- **Documentação** de cada módulo

## 📊 Métricas de Sucesso

### Técnicas
- Tempo de carregamento < 3 segundos
- Responsividade em diferentes telas
- Compatibilidade com browsers principais

### Funcionais
- Dashboard intuitivo para Dr. Roberto
- Insights acionáveis identificados
- Recomendações práticas implementáveis

## 🎨 Padrões de Design

### Cores e Tema
- Usar paleta médica/hospitalar
- Manter consistência entre páginas
- Destacar informações importantes

### Componentes
- Usar métricas do Streamlit para KPIs
- Gráficos interativos com Plotly
- Filtros consistentes em todas as páginas

## 📞 Suporte

### Documentação
- Código comentado em português
- README detalhado por página
- Exemplos de uso

### Troubleshooting
- Logs detalhados para debug
- Tratamento de erros robusto
- Mensagens de erro claras

---

**Data de Criação:** 2025-01-10  
**Última Atualização:** 2025-01-10  
**Versão:** 1.0