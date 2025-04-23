import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import base64
import io
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title="Dashboard Meta Ads",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Aplicar tema escuro personalizado
st.markdown("""
<style>
    .main {
        background-color: #0f0f23;
        color: white;
    }
    .stApp {
        background-color: #0f0f23;
    }
    .css-1d391kg {
        background-color: #1e1e2f;
    }
    .st-bq {
        background-color: #252547;
    }
    .st-c0 {
        background-color: #252547;
    }
    .st-c3 {
        border-color: #2e2e4f;
    }
    .st-c4 {
        color: white;
    }
    .st-af {
        font-size: 1.2rem;
    }
    .metric-card {
        background-color: #252547;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
        color: white;
    }
    .metric-label {
        font-size: 14px;
        color: #aaa;
    }
    .metric-change-positive {
        font-size: 12px;
        color: green;
    }
    .metric-change-negative {
        font-size: 12px;
        color: red;
    }
    .metric-change-neutral {
        font-size: 12px;
        color: gray;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e1e2f;
        border-radius: 4px 4px 0px 0px;
        padding: 10px 20px;
        color: white;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3498db;
    }
    .stDataFrame {
        background-color: #252547;
    }
    .stDataFrame [data-testid="stTable"] {
        background-color: #252547;
    }
    .stDataFrame th {
        background-color: #1e1e2f;
        color: white;
    }
    .stDataFrame td {
        background-color: #252547;
        color: white;
    }
    .stDataFrame tr:nth-child(even) {
        background-color: #20203f;
    }
    .stButton>button {
        background-color: #3498db;
        color: white;
    }
    .stButton>button:hover {
        background-color: #2980b9;
    }
</style>
""", unsafe_allow_html=True)

# Título do dashboard
st.title("Dashboard Meta Ads")
st.markdown("Análise de métricas de campanhas do Meta Ads")

# Dados de exemplo para inicialização
@st.cache_data
def generate_sample_data():
    # Criar dados de exemplo para demonstração inicial
    dates = pd.date_range(start='2025-01-01', end='2025-01-31')
    campaigns = ['Campanha 1', 'Campanha 2', 'Campanha 3', 'Campanha 4', 'Campanha 5']
    
    data = []
    for campaign in campaigns:
        for date in dates:
            impressions = int(pd.np.random.randint(1000, 10000))
            reach = int(impressions * pd.np.random.uniform(0.7, 0.9))
            clicks = int(reach * pd.np.random.uniform(0.01, 0.1))
            messages = int(clicks * pd.np.random.uniform(0.1, 0.5))
            spend = round(pd.np.random.uniform(50, 500), 2)
            revenue = round(spend * pd.np.random.uniform(0.8, 4.0), 2)
            
            data.append({
                'data': date.strftime('%Y-%m-%d'),
                'campanha': campaign,
                'conjunto': f'Conjunto {date.day % 3 + 1}',
                'anuncio': f'Anúncio {date.day % 5 + 1}',
                'impressoes': impressions,
                'alcance': reach,
                'cliques': clicks,
                'mensagens': messages,
                'ctr': round(clicks / impressions * 100, 2),
                'cpc': round(spend / clicks, 2) if clicks > 0 else 0,
                'cpm': round(spend / impressions * 1000, 2),
                'gasto': spend,
                'receita': revenue,
                'roas': round(revenue / spend, 2),
                'roi': round((revenue - spend) / spend * 100, 2)
            })
    
    df = pd.DataFrame(data)
    return df

# Funções auxiliares para cálculos e processamento
def calculate_metrics(df):
    """Calcula métricas agregadas a partir do DataFrame"""
    metrics = {}
    
    # Métricas básicas
    metrics['gasto_total'] = df['gasto'].sum()
    metrics['impressoes_total'] = df['impressoes'].sum()
    metrics['alcance_total'] = df['alcance'].sum()
    metrics['cliques_total'] = df['cliques'].sum()
    metrics['mensagens_total'] = df['mensagens'].sum()
    metrics['receita_total'] = df['receita'].sum()
    
    # Métricas calculadas
    metrics['ctr'] = metrics['cliques_total'] / metrics['impressoes_total'] * 100 if metrics['impressoes_total'] > 0 else 0
    metrics['cpc'] = metrics['gasto_total'] / metrics['cliques_total'] if metrics['cliques_total'] > 0 else 0
    metrics['cpm'] = metrics['gasto_total'] / metrics['impressoes_total'] * 1000 if metrics['impressoes_total'] > 0 else 0
    metrics['taxa_mensagens'] = metrics['mensagens_total'] / metrics['cliques_total'] * 100 if metrics['cliques_total'] > 0 else 0
    metrics['roas'] = metrics['receita_total'] / metrics['gasto_total'] if metrics['gasto_total'] > 0 else 0
    metrics['roi'] = (metrics['receita_total'] - metrics['gasto_total']) / metrics['gasto_total'] * 100 if metrics['gasto_total'] > 0 else 0
    
    return metrics

def parse_uploaded_file(uploaded_file):
    """Processa o arquivo CSV carregado"""
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file)
        else:
            return None, "Formato de arquivo não suportado. Use CSV ou Excel."
        
        # Verificar e padronizar nomes das colunas
        required_columns = ['data', 'campanha', 'conjunto', 'anuncio', 'impressoes', 
                           'alcance', 'cliques', 'mensagens', 'gasto', 'receita']
        
        # Mapeamento de possíveis nomes de colunas para os nomes padronizados
        column_mapping = {
            'date': 'data', 'data': 'data', 'dia': 'data',
            'campaign': 'campanha', 'campanha': 'campanha', 'campaign_name': 'campanha',
            'adset': 'conjunto', 'conjunto': 'conjunto', 'ad_set': 'conjunto', 'adset_name': 'conjunto',
            'ad': 'anuncio', 'anuncio': 'anuncio', 'ad_name': 'anuncio',
            'impressions': 'impressoes', 'impressoes': 'impressoes',
            'reach': 'alcance', 'alcance': 'alcance',
            'clicks': 'cliques', 'cliques': 'cliques',
            'messages': 'mensagens', 'mensagens': 'mensagens',
            'spend': 'gasto', 'gasto': 'gasto', 'custo': 'gasto',
            'revenue': 'receita', 'receita': 'receita', 'valor': 'receita'
        }
        
        # Renomear colunas com base no mapeamento
        df_columns_lower = {col: col.lower() for col in df.columns}
        df = df.rename(columns=df_columns_lower)
        
        for col in df.columns:
            if col.lower() in column_mapping:
                df = df.rename(columns={col: column_mapping[col.lower()]})
        
        # Verificar se todas as colunas necessárias estão presentes
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            # Para colunas ausentes, criar com valores padrão
            for col in missing_columns:
                if col == 'data':
                    df['data'] = datetime.now().strftime('%Y-%m-%d')
                elif col in ['impressoes', 'alcance', 'cliques', 'mensagens']:
                    df[col] = 0
                elif col in ['gasto', 'receita']:
                    df[col] = 0.0
                else:
                    df[col] = 'Não especificado'
        
        # Calcular métricas derivadas se não existirem
        if 'ctr' not in df.columns:
            df['ctr'] = df.apply(lambda row: row['cliques'] / row['impressoes'] * 100 if row['impressoes'] > 0 else 0, axis=1)
        
        if 'cpc' not in df.columns:
            df['cpc'] = df.apply(lambda row: row['gasto'] / row['cliques'] if row['cliques'] > 0 else 0, axis=1)
        
        if 'cpm' not in df.columns:
            df['cpm'] = df.apply(lambda row: row['gasto'] / row['impressoes'] * 1000 if row['impressoes'] > 0 else 0, axis=1)
        
        if 'roas' not in df.columns:
            df['roas'] = df.apply(lambda row: row['receita'] / row['gasto'] if row['gasto'] > 0 else 0, axis=1)
        
        if 'roi' not in df.columns:
            df['roi'] = df.apply(lambda row: (row['receita'] - row['gasto']) / row['gasto'] * 100 if row['gasto'] > 0 else 0, axis=1)
        
        return df, None
    except Exception as e:
        return None, f'Erro ao processar o arquivo: {str(e)}'

# Sidebar para upload de arquivo e filtros
with st.sidebar:
    st.header("Configurações")
    
    # Upload de arquivo
    st.subheader("Importar Dados")
    uploaded_file = st.file_uploader("Carregar arquivo CSV ou Excel", type=["csv", "xlsx", "xls"])
    
    if uploaded_file is not None:
        df, error = parse_uploaded_file(uploaded_file)
        if error:
            st.error(error)
            df = generate_sample_data()
    else:
        df = generate_sample_data()
    
    # Filtros
    st.subheader("Filtros")
    
    # Filtro de data
    min_date = pd.to_datetime(df['data']).min().date()
    max_date = pd.to_datetime(df['data']).max().date()
    
    date_range = st.date_input(
        "Período",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df[(pd.to_datetime(df['data']).dt.date >= start_date) & 
                         (pd.to_datetime(df['data']).dt.date <= end_date)]
    else:
        df_filtered = df
    
    # Filtro de campanha
    campaigns = sorted(df_filtered['campanha'].unique())
    selected_campaigns = st.multiselect("Campanhas", campaigns, default=[])
    
    if selected_campaigns:
        df_filtered = df_filtered[df_filtered['campanha'].isin(selected_campaigns)]
    
    # Filtro de conjunto
    adsets = sorted(df_filtered['conjunto'].unique())
    selected_adsets = st.multiselect("Conjuntos", adsets, default=[])
    
    if selected_adsets:
        df_filtered = df_filtered[df_filtered['conjunto'].isin(selected_adsets)]
    
    # Filtro de anúncio
    ads = sorted(df_filtered['anuncio'].unique())
    selected_ads = st.multiselect("Anúncios", ads, default=[])
    
    if selected_ads:
        df_filtered = df_filtered[df_filtered['anuncio'].isin(selected_ads)]

# Calcular métricas
metrics = calculate_metrics(df_filtered)

# Métricas principais
st.header("Visão Geral | Principais Métricas")

# Criar layout de colunas para métricas
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Valor Investido</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">R$ {metrics["gasto_total"]:,.2f}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Alcance</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{int(metrics["alcance_total"]):,}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Impressões</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{int(metrics["impressoes_total"]):,}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">CPM</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">R$ {metrics["cpm"]:.2f}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

col5, col6, col7, col8 = st.columns(4)

with col5:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Cliques</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{int(metrics["cliques_total"]):,}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col6:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">Mensagens</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{int(metrics["mensagens_total"]):,}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col7:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">ROI</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{metrics["roi"]:.2f}%</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col8:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<p class="metric-label">ROAS</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="metric-value">{metrics["roas"]:.2f}</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Criar abas para diferentes visualizações
tab1, tab2, tab3 = st.tabs(["Tendências e Funil", "Desempenho de Campanhas", "Tabelas Detalhadas"])

with tab1:
    # Tendências temporais e Funil de Tráfego
    col_trend, col_funnel = st.columns([2, 1])
    
    with col_trend:
        st.subheader("Tendências Temporais")
        
        # Agrupar por data
        daily_data = df_filtered.groupby('data').agg({
            'impressoes': 'sum',
            'alcance': 'sum',
            'cliques': 'sum',
            'gasto': 'sum'
        }).reset_index()
        
        # Criar figura de tendências
        fig_trend = go.Figure()
        
        fig_trend.add_trace(go.Scatter(
            x=daily_data['data'],
            y=daily_data['impressoes'],
            mode='lines',
            name='Impressões',
            line=dict(color='#3498db', width=2)
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=daily_data['data'],
            y=daily_data['alcance'],
            mode='lines',
            name='Alcance',
            line=dict(color='#2ecc71', width=2)
        ))
        
        fig_trend.add_trace(go.Scatter(
            x=daily_data['data'],
            y=daily_data['cliques'],
            mode='lines',
            name='Cliques',
            line=dict(color='#e74c3c', width=2)
        ))
        
        fig_trend.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)'
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)'
            ),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_trend, use_container_width=True)
    
    with col_funnel:
        st.subheader("Funil de Tráfego")
        
        # Criar figura de funil
        fig_funnel = go.Figure(go.Funnel(
            y=['Impressões', 'Alcance', 'Cliques', 'Mensagens'],
            x=[metrics['impressoes_total'], metrics['alcance_total'], metrics['cliques_total'], metrics['mensagens_total']],
            textinfo='value+percent initial',
            marker=dict(color=['#3498db', '#2ecc71', '#e74c3c', '#f39c12'])
        ))
        
        fig_funnel.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            funnelmode='stack'
        )
        
        st.plotly_chart(fig_funnel, use_container_width=True)
    
    # Segunda linha de gráficos
    col_msg, col_cpl = st.columns(2)
    
    with col_msg:
        st.subheader("Maiores Taxas de Envio de Mensagens")
        
        # Agrupar por campanha
        campaign_data = df_filtered.groupby('campanha').agg({
            'mensagens': 'sum',
            'cliques': 'sum'
        }).reset_index()
        
        # Calcular taxa de mensagens
        campaign_data['taxa_mensagens'] = campaign_data['mensagens'] / campaign_data['cliques'] * 100
        campaign_data = campaign_data.sort_values('taxa_mensagens', ascending=False).head(10)
        
        # Criar figura de pizza
        fig_msg = go.Figure(go.Pie(
            labels=campaign_data['campanha'],
            values=campaign_data['taxa_mensagens'],
            hole=0.5,
            marker=dict(
                colors=px.colors.sequential.Blues_r,
                line=dict(color='#000000', width=1)
            ),
            textinfo='label+percent',
            textposition='outside'
        ))
        
        fig_msg.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False
        )
        
        st.plotly_chart(fig_msg, use_container_width=True)
    
    with col_cpl:
        st.subheader("Melhores CPL's")
        
        # Agrupar por campanha
        campaign_data = df_filtered.groupby('campanha').agg({
            'mensagens': 'sum',
            'gasto': 'sum'
        }).reset_index()
        
        # Calcular CPL (Custo por Lead/Mensagem)
        campaign_data['cpl'] = campaign_data['gasto'] / campaign_data['mensagens']
        campaign_data = campaign_data.replace([float('inf'), -float('inf')], float('nan')).dropna(subset=['cpl'])
        campaign_data = campaign_data.sort_values('cpl').head(10)
        
        # Criar figura de barras
        fig_cpl = go.Figure(go.Bar(
            x=campaign_data['cpl'],
            y=campaign_data['campanha'],
            orientation='h',
            marker=dict(
                color='#2ecc71',
                line=dict(color='#27ae60', width=1)
            ),
            text=campaign_data['cpl'].apply(lambda x: f'R$ {x:.2f}'),
            textposition='auto'
        ))
        
        fig_cpl.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title='Custo por Lead (R$)',
            yaxis=dict(
                title='',
                autorange='reversed'
            )
        )
        
        st.plotly_chart(fig_cpl, use_container_width=True)

with tab2:
    # Desempenho de Campanhas
    col_spend, col_day = st.columns(2)
    
    with col_spend:
        st.subheader("Campanhas com Maior Investimento")
        
        # Agrupar por campanha
        campaign_data = df_filtered.groupby('campanha').agg({
            'gasto': 'sum'
        }).reset_index()
        
        campaign_data = campaign_data.sort_values('gasto', ascending=False).head(10)
        
        # Criar figura de pizza
        fig_spend = go.Figure(go.Pie(
            labels=campaign_data['campanha'],
            values=campaign_data['gasto'],
            hole=0.5,
            marker=dict(
                colors=px.colors.sequential.Reds_r,
                line=dict(color='#000000', width=1)
            ),
            textinfo='label+percent',
            textposition='outside',
            hovertemplate='%{label}<br>R$ %{value:.2f}<br>%{percent}'
        ))
        
        fig_spend.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            showlegend=False
        )
        
        st.plotly_chart(fig_spend, use_container_width=True)
    
    with col_day:
        st.subheader("Desempenho por Dia da Semana")
        
        # Converter data para dia da semana
        df_filtered['dia_semana'] = pd.to_datetime(df_filtered['data']).dt.day_name()
        
        # Ordem dos dias da semana
        dias_semana_ordem = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dias_semana_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        dia_mapping = dict(zip(dias_semana_ordem, dias_semana_pt))
        
        # Mapear nomes em inglês para português
        df_filtered['dia_semana_pt'] = df_filtered['dia_semana'].map(dia_mapping)
        
        # Agrupar por dia da semana
        day_data = df_filtered.groupby('dia_semana_pt').agg({
            'mensagens': 'sum',
            'cliques': 'sum',
            'impressoes': 'sum',
            'gasto': 'sum'
        }).reset_index()
        
        # Reordenar os dias da semana
        day_data['dia_semana_ordem'] = day_data['dia_semana_pt'].map(dict(zip(dias_semana_pt, range(7))))
        day_data = day_data.sort_values('dia_semana_ordem')
        
        # Criar figura
        fig_day = go.Figure()
        
        # Adicionar barras para mensagens
        fig_day.add_trace(go.Bar(
            x=day_data['dia_semana_pt'],
            y=day_data['mensagens'],
            name='Mensagens',
            marker_color='#3498db'
        ))
        
        # Adicionar linha para CTR (Cliques / Impressões)
        day_data['ctr'] = day_data['cliques'] / day_data['impressoes'] * 100
        
        fig_day.add_trace(go.Scatter(
            x=day_data['dia_semana_pt'],
            y=day_data['ctr'],
            mode='lines+markers',
            name='CTR (%)',
            yaxis='y2',
            line=dict(color='#f39c12', width=3),
            marker=dict(size=8)
        ))
        
        # Configurar layout
        fig_day.update_layout(
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            yaxis=dict(
                title='Mensagens',
                showgrid=True,
                gridcolor='rgba(255,255,255,0.1)'
            ),
            yaxis2=dict(
                title='CTR (%)',
                overlaying='y',
                side='right',
                showgrid=False
            ),
            barmode='group'
        )
        
        st.plotly_chart(fig_day, use_container_width=True)
    
    # Gráfico de desempenho por campanha
    st.subheader("Desempenho por Campanha")
    
    # Agrupar por campanha
    campaign_perf = df_filtered.groupby('campanha').agg({
        'impressoes': 'sum',
        'alcance': 'sum',
        'cliques': 'sum',
        'mensagens': 'sum',
        'gasto': 'sum',
        'receita': 'sum'
    }).reset_index()
    
    # Calcular métricas adicionais
    campaign_perf['ctr'] = campaign_perf['cliques'] / campaign_perf['impressoes'] * 100
    campaign_perf['roas'] = campaign_perf['receita'] / campaign_perf['gasto']
    campaign_perf = campaign_perf.sort_values('gasto', ascending=False)
    
    # Criar figura de barras
    fig_perf = go.Figure()
    
    fig_perf.add_trace(go.Bar(
        x=campaign_perf['campanha'],
        y=campaign_perf['gasto'],
        name='Gasto (R$)',
        marker_color='#e74c3c'
    ))
    
    fig_perf.add_trace(go.Bar(
        x=campaign_perf['campanha'],
        y=campaign_perf['receita'],
        name='Receita (R$)',
        marker_color='#2ecc71'
    ))
    
    fig_perf.add_trace(go.Scatter(
        x=campaign_perf['campanha'],
        y=campaign_perf['roas'],
        mode='lines+markers',
        name='ROAS',
        yaxis='y2',
        line=dict(color='#f39c12', width=3),
        marker=dict(size=8)
    ))
    
    fig_perf.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            title='Valor (R$)',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)'
        ),
        yaxis2=dict(
            title='ROAS',
            overlaying='y',
            side='right',
            showgrid=False
        ),
        barmode='group'
    )
    
    st.plotly_chart(fig_perf, use_container_width=True)

with tab3:
    # Tabelas Detalhadas
    st.subheader("Campanhas Publicadas")
    
    # Agrupar por campanha
    campaign_data = df_filtered.groupby('campanha').agg({
        'alcance': 'sum',
        'impressoes': 'sum',
        'cliques': 'sum',
        'mensagens': 'sum',
        'gasto': 'sum',
        'receita': 'sum'
    }).reset_index()
    
    # Calcular métricas adicionais
    campaign_data['ctr'] = campaign_data['cliques'] / campaign_data['impressoes'] * 100
    campaign_data['cpc'] = campaign_data['gasto'] / campaign_data['cliques']
    campaign_data['cpm'] = campaign_data['gasto'] / campaign_data['impressoes'] * 1000
    campaign_data['roas'] = campaign_data['receita'] / campaign_data['gasto']
    campaign_data['roi'] = (campaign_data['receita'] - campaign_data['gasto']) / campaign_data['gasto'] * 100
    
    # Substituir infinitos e NaN
    campaign_data = campaign_data.replace([float('inf'), -float('inf')], 0).fillna(0)
    
    # Formatar valores para exibição
    campaign_data_display = campaign_data.copy()
    campaign_data_display['alcance'] = campaign_data_display['alcance'].apply(lambda x: f"{int(x):,}".replace(',', '.'))
    campaign_data_display['impressoes'] = campaign_data_display['impressoes'].apply(lambda x: f"{int(x):,}".replace(',', '.'))
    campaign_data_display['cliques'] = campaign_data_display['cliques'].apply(lambda x: f"{int(x):,}".replace(',', '.'))
    campaign_data_display['mensagens'] = campaign_data_display['mensagens'].apply(lambda x: f"{int(x):,}".replace(',', '.'))
    campaign_data_display['gasto'] = campaign_data_display['gasto'].apply(lambda x: f"R$ {x:.2f}")
    campaign_data_display['ctr'] = campaign_data_display['ctr'].apply(lambda x: f"{x:.2f}%")
    campaign_data_display['cpc'] = campaign_data_display['cpc'].apply(lambda x: f"R$ {x:.2f}")
    campaign_data_display['cpm'] = campaign_data_display['cpm'].apply(lambda x: f"R$ {x:.2f}")
    campaign_data_display['roas'] = campaign_data_display['roas'].apply(lambda x: f"{x:.2f}")
    campaign_data_display['roi'] = campaign_data_display['roi'].apply(lambda x: f"{x:.2f}%")
    
    # Renomear colunas para exibição
    campaign_data_display = campaign_data_display.rename(columns={
        'campanha': 'Campanha',
        'alcance': 'Alcance',
        'impressoes': 'Impressões',
        'cliques': 'Cliques',
        'mensagens': 'Mensagens',
        'gasto': 'Gasto',
        'ctr': 'CTR',
        'cpc': 'CPC',
        'cpm': 'CPM',
        'roas': 'ROAS',
        'roi': 'ROI'
    })
    
    st.dataframe(campaign_data_display, use_container_width=True)
    
    st.subheader("Criativos Validados")
    
    # Agrupar por anúncio
    ad_data = df_filtered.groupby('anuncio').agg({
        'alcance': 'sum',
        'impressoes': 'sum',
        'cliques': 'sum',
        'mensagens': 'sum',
        'gasto': 'sum'
    }).reset_index()
    
    # Calcular métricas adicionais
    ad_data['ctr'] = ad_data['cliques'] / ad_data['impressoes'] * 100
    ad_data['cpc'] = ad_data['gasto'] / ad_data['cliques']
    ad_data['cpm'] = ad_data['gasto'] / ad_data['impressoes'] * 1000
    ad_data['cpl'] = ad_data['gasto'] / ad_data['mensagens']
    
    # Substituir infinitos e NaN
    ad_data = ad_data.replace([float('inf'), -float('inf')], 0).fillna(0)
    
    # Formatar valores para exibição
    ad_data_display = ad_data.copy()
    ad_data_display['alcance'] = ad_data_display['alcance'].apply(lambda x: f"{int(x):,}".replace(',', '.'))
    ad_data_display['impressoes'] = ad_data_display['impressoes'].apply(lambda x: f"{int(x):,}".replace(',', '.'))
    ad_data_display['cliques'] = ad_data_display['cliques'].apply(lambda x: f"{int(x):,}".replace(',', '.'))
    ad_data_display['mensagens'] = ad_data_display['mensagens'].apply(lambda x: f"{int(x):,}".replace(',', '.'))
    ad_data_display['gasto'] = ad_data_display['gasto'].apply(lambda x: f"R$ {x:.2f}")
    ad_data_display['ctr'] = ad_data_display['ctr'].apply(lambda x: f"{x:.2f}%")
    ad_data_display['cpc'] = ad_data_display['cpc'].apply(lambda x: f"R$ {x:.2f}")
    ad_data_display['cpm'] = ad_data_display['cpm'].apply(lambda x: f"R$ {x:.2f}")
    ad_data_display['cpl'] = ad_data_display['cpl'].apply(lambda x: f"R$ {x:.2f}")
    
    # Renomear colunas para exibição
    ad_data_display = ad_data_display.rename(columns={
        'anuncio': 'Anúncio',
        'alcance': 'Alcance',
        'impressoes': 'Impressões',
        'cliques': 'Cliques',
        'mensagens': 'Mensagens',
        'gasto': 'Gasto',
        'ctr': 'CTR',
        'cpc': 'CPC',
        'cpm': 'CPM',
        'cpl': 'CPL'
    })
    
    st.dataframe(ad_data_display, use_container_width=True)

# Rodapé
st.markdown("---")
st.markdown("Dashboard Meta Ads - Versão Online")

# Botão para download dos dados
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv = convert_df_to_csv(df_filtered)
st.download_button(
    label="Baixar Dados Filtrados (CSV)",
    data=csv,
    file_name='meta_ads_data.csv',
    mime='text/csv',
)
