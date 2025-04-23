# Dashboard Meta Ads - Guia de Implantação Permanente

Este repositório contém um dashboard interativo para análise de métricas do Meta Ads, desenvolvido com Streamlit.

## Visão Geral

O Dashboard Meta Ads é uma ferramenta completa para visualização e análise de dados de campanhas publicitárias do Meta Ads (Facebook, Instagram). Ele oferece:

- Visualização de métricas principais (investimento, alcance, impressões, CPM, cliques, ROI, ROAS)
- Gráficos interativos (tendências temporais, funil de tráfego, etc.)
- Tabelas detalhadas de campanhas e criativos
- Filtros por data, campanha, conjunto e anúncio
- Importação de dados via CSV ou Excel

## Opções de Implantação Permanente

Existem várias maneiras de implantar este dashboard como um site permanente:

### 1. Streamlit Cloud (Recomendado)

A maneira mais fácil de implantar o dashboard permanentemente:

1. Crie uma conta em [Streamlit Cloud](https://streamlit.io/cloud)
2. Crie um repositório no GitHub com estes arquivos
3. Conecte o Streamlit Cloud ao seu repositório GitHub
4. Selecione o arquivo `app.py` como ponto de entrada
5. Clique em "Deploy"

### 2. Heroku

Para implantar no Heroku:

1. Crie uma conta no [Heroku](https://heroku.com)
2. Instale o [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)
3. Clone este repositório localmente
4. Navegue até a pasta do repositório e execute:
   ```
   heroku login
   heroku create seu-dashboard-meta-ads
   git init
   heroku git:remote -a seu-dashboard-meta-ads
   git add .
   git commit -m "Implantação inicial"
   git push heroku master
   ```

### 3. Render

Para implantar no Render:

1. Crie uma conta no [Render](https://render.com)
2. Clique em "New Web Service"
3. Conecte ao seu repositório GitHub ou faça upload dos arquivos
4. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Clique em "Create Web Service"

### 4. PythonAnywhere

Para implantar no PythonAnywhere:

1. Crie uma conta no [PythonAnywhere](https://www.pythonanywhere.com)
2. Faça upload dos arquivos
3. Configure um novo aplicativo web
4. Configure o WSGI para executar o Streamlit

## Execução Local

Para executar o dashboard localmente:

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

2. Execute o aplicativo:
   ```
   streamlit run app.py
   ```

3. Acesse o dashboard em seu navegador:
   ```
   http://localhost:8501
   ```

## Estrutura de Arquivos

- `app.py`: Código principal do dashboard
- `requirements.txt`: Dependências necessárias
- `Procfile`: Configuração para Heroku (se aplicável)
- `runtime.txt`: Versão do Python (se aplicável)

## Personalização

Você pode personalizar o dashboard editando o arquivo `app.py`:

- Alterar cores e estilos
- Adicionar ou remover visualizações
- Modificar cálculos de métricas
- Adicionar novas funcionalidades

## Importação de Dados

O dashboard aceita arquivos CSV ou Excel com os seguintes campos:

- data: Data da campanha (formato YYYY-MM-DD)
- campanha: Nome da campanha
- conjunto: Nome do conjunto de anúncios
- anuncio: Nome do anúncio
- impressoes: Número de impressões
- alcance: Número de pessoas alcançadas
- cliques: Número de cliques
- mensagens: Número de mensagens/conversões
- gasto: Valor gasto na campanha
- receita: Receita gerada (opcional)

## Suporte

Para dúvidas ou suporte, entre em contato através do email: seu-email@exemplo.com
