import streamlit as st
import pandas as pd
import numpy as np
import requests
from datetime import datetime
#import plotly as px
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Financial Control Pro",
    page_icon="📈",
    layout="wide"
)

# Função para obter dados econômicos
def get_economic_indicators():
    try:
        # Taxa Selic
        selic = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados/ultimos/1?formato=json").json()[0]['valor']
        
        # IPCA
        ipca = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados/ultimos/1?formato=json").json()[0]['valor']
        
        # Dólar comercial
        dolar = requests.get("https://economia.awesomeapi.com.br/json/last/USD-BRL").json()['USDBRL']['bid']
        
        return {
            'Selic': float(selic),
            'IPCA': float(ipca),
            'Dólar': float(dolar)
        }
    except:
        return {
            'Selic': 13.75,
            'IPCA': 4.50,
            'Dólar': 5.20
        }

# Sidebar
with st.sidebar:
    st.title("⚙️ Configurações")
    start_date = st.date_input("Data Inicial", datetime(2023, 1, 1))
    end_date = st.date_input("Data Final", datetime.today())
    
    st.divider()
    st.subheader("📊 Indicadores Econômicos")
    economic_data = get_economic_indicators()
    st.metric("Taxa Selic", f"{economic_data['Selic']}%")
    st.metric("IPCA Acumulado", f"{economic_data['IPCA']}%")
    st.metric("Câmbio (USD/BRL)", f"R$ {economic_data['Dólar']:.2f}")

# Gerar dados simulados
@st.cache_data
def generate_data(start, end):
    date_range = pd.date_range(start=start, end=end, freq='M')
    n_months = len(date_range)
    
    return pd.DataFrame({
        'Data': date_range,
        'Receita': np.random.normal(150000, 30000, n_months).cumsum(),
        'Despesa': np.random.normal(80000, 15000, n_months).cumsum(),
        'Investimentos': np.random.normal(30000, 5000, n_months).cumsum()
    })

df = generate_data(start_date, end_date)
df['Saldo'] = df['Receita'] - df['Despesa']
df['Selic'] = economic_data['Selic']

# Cálculos de rentabilidade
daily_selic = (1 + economic_data['Selic']/100) ** (1/252) - 1
df['Dias'] = (datetime.today() - df['Data']).dt.days
df['Rentabilidade'] = df['Saldo'] * (1 + daily_selic) ** df['Dias']
df['Acumulado'] = df['Rentabilidade'].cumsum()

# Interface principal
st.title("📊 Financial Control Pro")
st.markdown("---")

# Métricas rápidas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Saldo Atual", f"R$ {df['Saldo'].iloc[-1]:,.2f}")
col2.metric("Rentabilidade Total", f"R$ {df['Acumulado'].iloc[-1]:,.2f}")
col3.metric("Custo Selic Mensal", f"{daily_selic*30*100:.2f}%")
col4.metric("Eficiência Financeira", 
           f"{(df['Acumulado'].iloc[-1]/df['Saldo'].iloc[-1]*100):.1f}%")

# Gráficos
tab1, tab2, tab3 = st.tabs(["📈 Tendências", "🔍 Detalhes", "📤 Exportar"])

with tab1:
    fig = px.line(df, x='Data', y=['Receita', 'Despesa', 'Investimentos'],
                 title="Evolução Financeira")
    st.plotly_chart(fig, use_container_width=True)
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df['Data'], y=df['Acumulado'],
                            mode='lines', name='Rentabilidade'))
    fig2.add_trace(go.Bar(x=df['Data'], y=df['Saldo'], name='Saldo Mensal'))
    fig2.update_layout(title="Rentabilidade vs Saldo")
    st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("Análise Detalhada")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Distribuição de Gastos**")
        fig3 = px.pie(df, values='Despesa', names=df['Data'].dt.strftime('%b-%Y'),
                     hole=0.4)
        st.plotly_chart(fig3, use_container_width=True)
    
    with col2:
        st.write("**Comparativo Mensal**")
        fig4 = px.bar(df, x='Data', y=['Receita', 'Despesa'],
                     barmode='group')
        st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("Exportação de Dados")
    edited_df = st.data_editor(df)
    
    csv = edited_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exportar CSV",
        data=csv,
        file_name='dados_financeiros.csv',
        mime='text/csv'
    )

# Rodapé
st.markdown("---")
st.caption("Desenvolvido por Financial Control Pro • Dados atualizados automaticamente via API do Banco Central")
