# Dashboard DataSUS - Análise de Internações Hospitalares

Dashboard interativo para análise de dados de internações hospitalares do DataSUS, com funcionalidades de Machine Learning e Chatbot inteligente.

## 🚀 Funcionalidades

- **Visão Geral**: Métricas principais e KPIs
- **Causas Principais**: Análise dos principais diagnósticos
- **Análise Geográfica**: Visualização por municípios com mapas
- **Gestão de Recursos**: Análise de custos e recursos hospitalares
- **Machine Learning**: Predição de permanência e custos com Gradient Boosting
- **Chatbot**: Consultas em linguagem natural usando Google Gemini

## 🛠️ Instalação

### 1. Clonar o repositório
```bash
git clone <url-do-repositorio>
cd DataSus
```

### 2. Criar ambiente virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar banco de dados
```bash
python scripts/create_database.py
```

### 5. Configurar API do Gemini (para chatbot)
```bash
cp .env.example .env
# Editar .env e adicionar sua chave da API do Google Gemini
```

## 🔑 Configuração da API

### Google Gemini API
1. Acesse [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crie uma nova API key
3. Adicione no arquivo `.env`:
```
GEMINI_API_KEY=sua_chave_aqui
```

## 🚦 Executar o Dashboard

```bash
streamlit run dashboard/main.py
```

O dashboard estará disponível em `http://localhost:8501`

## 📊 Dados

O projeto utiliza dados do DataSUS de internações hospitalares:
- **Período**: Janeiro a Março 2025
- **Local**: Paraná, Brasil
- **Registros**: ~118.627 internações

## 🤖 Machine Learning

### Modelos Implementados
- **Gradient Boosting Regressor**: Modelo principal para predições
- **Isolation Forest**: Detecção de anomalias em custos

### Funcionalidades ML
- Predição de tempo de permanência
- Predição de custos de internação
- Detecção de anomalias em valores

## 💬 Chatbot

O chatbot utiliza a API do Google Gemini para:
- Consultas em linguagem natural
- Geração automática de consultas SQL
- Análise de dados em tempo real

## 📁 Estrutura do Projeto

```
DataSus/
├── config/              # Configurações
├── dashboard/           # Aplicação Streamlit
│   ├── main.py         # Arquivo principal
│   └── pages/          # Páginas do dashboard
├── data/               # Dados brutos e processados
├── database/           # Banco de dados SQLite
├── docs/               # Documentação
├── scripts/            # Scripts de processamento
├── .env.example        # Exemplo de configuração
├── .gitignore         # Arquivos ignorados pelo Git
├── README.md          # Este arquivo
└── requirements.txt   # Dependências Python
```

## 🔧 Desenvolvimento

### Adicionar nova funcionalidade
1. Criar nova página em `dashboard/pages/`
2. Adicionar import em `dashboard/main.py`
3. Adicionar rota no menu de navegação

### Executar testes
```bash
python -m pytest tests/
```

## 📝 Licença

Este projeto está sob licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no GitHub
- Consulte a documentação em `docs/`

---

**Nota**: Este projeto foi desenvolvido para fins educacionais e de pesquisa com dados públicos do DataSUS.