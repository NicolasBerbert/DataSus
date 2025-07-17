# 🤖 Chatbot de Consultas - Instruções de Uso

## 📋 Resumo
Foi implementado um chatbot na aba "Chatbot" (anteriormente "Recomendações") que permite fazer consultas em linguagem natural sobre os dados de internações hospitalares do DataSUS.

## 🚀 Como Usar

### 1. Instalação das Dependências
```bash
pip install -r requirements.txt
```

### 2. Execução do Dashboard
```bash
streamlit run dashboard/main.py
```

### 3. Navegação
- Abra o dashboard no navegador
- Clique na aba "Chatbot"
- Digite suas perguntas na caixa de chat

## 💡 Exemplos de Perguntas

### Todas as Consultas (processadas via API do Gemini)
- "Quantas internações tivemos?"
- "Principais diagnósticos"
- "Diagnósticos mais comuns"
- "Valor total das internações"
- "Internações por município"
- "Pacientes com diabetes em Curitiba"
- "Listar pacientes do município de Londrina"
- "Internações com angina em Londrina"
- "Pacientes com pneumonia"
- "Internações com diabetes"
- "Qual o custo médio das internações por idade?"
- "Diagnósticos sensíveis à atenção básica"
- "Estabelecimentos com mais internações"
- "Internações por trimestre"

## 🔧 Funcionalidades Implementadas

### ✅ Integração Exclusiva com Gemini
- **Todas as consultas** são processadas via Google Generative AI
- Interpreta perguntas em linguagem natural
- Gera consultas SQL automaticamente com base no schema do banco
- Não usa parsers locais - apenas inteligência artificial

### ✅ Processamento Inteligente
- Reconhece automaticamente entidades (municípios, doenças, etc.)
- Gera consultas SQL sofisticadas com múltiplos JOINs
- Adapta-se a diferentes tipos de perguntas
- Prompt otimizado para dados de saúde do DataSUS

### ✅ Interface Amigável
- Chat interativo com histórico
- Exibição de resultados em tabelas formatadas
- Botão para limpar conversa
- Sidebar com informações úteis

### ✅ Segurança
- Proteção contra SQL Injection
- Queries limitadas (máximo 50 registros)
- Apenas operações SELECT permitidas

## 📊 Dados Disponíveis

- **Período:** Janeiro a Março 2025
- **Local:** Paraná, Brasil
- **Registros:** 118.627 internações
- **Estabelecimentos:** 253
- **Pacientes únicos:** 102.659

## 🗃️ Tabelas do Banco

- **internacoes:** Registros de internações
- **pacientes:** Dados dos pacientes
- **estabelecimentos:** Informações dos hospitais
- **cid_diagnosticos:** Códigos de diagnóstico
- **municipios:** Dados dos municípios
- **valores_financeiros:** Custos das internações

## 🔑 Configuração da API

A chave da API do Gemini está configurada no código:
```python
GEMINI_API_KEY = "AIzaSyDzlD3cvqJfAOB_vGXtT6wbc-_Gacd-9xw"
```

## 🎯 Melhorias Futuras

- Adicionar mais padrões de consulta ao parser básico
- Implementar cache de respostas frequentes
- Adicionar visualizações gráficas das respostas
- Permitir exportação de resultados
- Adicionar suporte a consultas em múltiplas linguagens

## 🐛 Solução de Problemas

### Erro de Dependências
```bash
pip install google-generativeai>=0.5.0
```

### Erro de Conexão com Banco
Verifique se o arquivo `database/internacoes_datasus.db` existe.

### API do Gemini não Funciona
- O chatbot **não funcionará** sem a API do Gemini
- Verifique se a chave da API está correta
- Verifique conectividade com a internet
- Tente reformular a pergunta se houver erro

## 📝 Exemplos de Uso

### Consulta Simples
```
Usuário: "Quantas internações tivemos?"
Chatbot: "📊 Resultado: 118627"
```

### Consulta com Tabela
```
Usuário: "Principais diagnósticos"
Chatbot: "📊 Encontrei 10 resultado(s):"
[Tabela com diagnósticos e quantidades]
```

### Consulta Complexa
```
Usuário: "Pacientes com diabetes em Curitiba"
Chatbot: "📊 Encontrei 20 resultado(s):"
[Tabela com idade, sexo, município, diagnóstico, data internação]
```

## 🔗 Arquivos Modificados

- `dashboard/pages/recomendacoes.py` - Implementação completa do chatbot
- `dashboard/main.py` - Alteração do nome da aba para "Chatbot"
- `requirements.txt` - Adicionada dependência `google-generativeai`

O chatbot está pronto para uso e pode responder a uma ampla variedade de perguntas sobre os dados de internações hospitalares!