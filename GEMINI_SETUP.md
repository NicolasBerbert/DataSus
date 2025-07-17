# 🔧 Configuração do Gemini para o Chatbot

## ❌ Problemas Identificados

### 1. Biblioteca não instalada
O chatbot não estava funcionando porque a biblioteca `google-generativeai` não estava instalada no ambiente.

### 2. Modelo Gemini não encontrado (Erro 404)
O modelo `gemini-pro` não está disponível na versão atual da API. Erro: `404 models/gemini-pro is not found for API version v1beta`

### 3. Modelos Depreciados
Erro: `404 Gemini 1.0 Pro Vision has been deprecated on July 12, 2024. Consider switching to different model, for example gemini-1.5-flash.`

## ✅ Soluções Implementadas

### 1. Instalar a Dependência

```bash
pip install google-generativeai>=0.5.0
```

### 2. Verificar Instalação

```bash
python3 -c "import google.generativeai; print('✅ Biblioteca instalada com sucesso!')"
```

### 3. Correção do Modelo Gemini

**ATUALIZAÇÃO**: Simplificado para usar apenas modelos atuais (não depreciados):

1. `gemini-1.5-flash` (modelo recomendado)
2. `gemini-1.5-pro` (modelo alternativo)

**Removidos**: Todos os modelos antigos e depreciados (`gemini-pro`, `gemini-1.0-pro-vision`, etc.)

### 4. Executar o Dashboard

```bash
streamlit run dashboard/main.py
```

## 🔍 Logs de Debug Implementados

Adicionei logs detalhados para rastrear problemas:

### Na Função `generate_sql_with_gemini`:
- ✅ Verifica se a biblioteca está disponível
- ✅ Mostra a pergunta do usuário
- ✅ Rastreia criação do modelo Gemini
- ✅ Mostra resposta completa da API
- ✅ Captura erros detalhados

### Na Função `execute_sql_query`:
- ✅ Mostra query original e limpa
- ✅ Rastreia execução SQL
- ✅ Mostra resultados obtidos
- ✅ Captura erros de SQL

### No Fluxo Principal:
- ✅ Rastreia início e fim do processamento
- ✅ Mostra input do usuário
- ✅ Verifica conexão com banco
- ✅ Monitora chamadas para Gemini

## 🔑 Nova Chave da API

Chave atualizada para: `AIzaSyC2b5xyyXkZDu_8AcVVjIlFxUFP9QM8eZU`

## 📋 Próximos Passos

1. **Instalar dependência**: `pip install google-generativeai>=0.5.0`
2. **Executar dashboard**: `streamlit run dashboard/main.py`
3. **Testar chatbot**: Ir para aba "Chatbot"
4. **Verificar logs**: Os logs aparecerão no console do terminal

## 🐛 Verificação de Problemas

### Se a biblioteca não instalar:
```bash
pip3 install google-generativeai>=0.5.0
```

### Se der erro de permissions:
```bash
pip install --user google-generativeai>=0.5.0
```

### Se estiver em virtual environment:
```bash
# Ativar venv primeiro
source venv/bin/activate
pip install google-generativeai>=0.5.0
```

## 🎯 Teste Rápido

### Opção 1: Teste Manual
```python
import google.generativeai as genai

# Configurar API
genai.configure(api_key="AIzaSyC2b5xyyXkZDu_8AcVVjIlFxUFP9QM8eZU")

# Testar modelo ATUALIZADO
model = genai.GenerativeModel('gemini-1.5-flash')
response = model.generate_content("Responda apenas: OK")
print(response.text)
```

### Opção 2: Usar Script de Teste
```bash
python3 test_gemini.py
```

Este script testa:
- Importação da biblioteca
- Configuração da API
- Modelo `gemini-1.5-flash`
- Geração de SQL simples

## 📊 Logs Esperados

### ✅ Quando funcionando corretamente:

```
✅ DEBUG: google.generativeai importado com sucesso
✅ DEBUG: API do Gemini configurada
🔍 DEBUG: ========== INÍCIO DO PROCESSAMENTO ==========
🔍 DEBUG: Input do usuário: 'Quantas internações tivemos?'
🔍 DEBUG: Conexão com banco obtida
🔍 DEBUG: Chamando generate_sql_with_gemini...
🔍 DEBUG: Iniciando generate_sql_with_gemini
🔍 DEBUG: GEMINI_AVAILABLE = True
🔍 DEBUG: Tentando modelo gemini-1.5-flash...
🔍 DEBUG: Modelo gemini-1.5-flash criado com sucesso
🔍 DEBUG: Enviando prompt para Gemini...
🔍 DEBUG: Resposta recebida do Gemini!
🔍 DEBUG: Resposta completa: 'SELECT COUNT(*) as total_internacoes FROM internacoes'
🔍 DEBUG: SQL query válida encontrada, executando...
🔍 DEBUG: Query executada com sucesso!
🔍 DEBUG: Resultado obtido com sucesso!
🔍 DEBUG: ========== FIM DO PROCESSAMENTO ==========
```

### ⚠️ Quando há problemas com modelos:

```
🔍 DEBUG: Tentando modelo gemini-1.5-flash...
🔍 DEBUG: Modelo gemini-1.5-flash criado com sucesso
🔍 DEBUG: Enviando prompt para Gemini...
🔍 DEBUG: Resposta recebida do Gemini!
```

### ❌ Quando há erro 404 (modelos depreciados):

```
🔍 DEBUG: Tentando apenas modelos atuais: ['gemini-1.5-flash', 'gemini-1.5-pro']
🔍 DEBUG: Tentando modelo gemini-1.5-flash...
⚠️  DEBUG: Modelo gemini-1.5-flash falhou: 404 Gemini 1.0 Pro Vision has been deprecated on July 12, 2024
🔍 DEBUG: Tentando modelo gemini-1.5-pro...
🔍 DEBUG: Modelo gemini-1.5-pro criado com sucesso
```

### 🔧 Se nenhum modelo funcionar:

```
❌ DEBUG: Nenhum modelo atual funcionou
❌ DEBUG: Modelos testados: ['gemini-1.5-flash', 'gemini-1.5-pro']
❌ DEBUG: Soluções possíveis:
❌ DEBUG: 1. Atualizar biblioteca: pip install --upgrade google-generativeai
❌ DEBUG: 2. Verificar se a chave da API está correta
❌ DEBUG: 3. Verificar conectividade com a internet
```

O chatbot está pronto para funcionar assim que a dependência for instalada!