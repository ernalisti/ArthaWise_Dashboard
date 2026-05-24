
# =============================================================================
# IMPORT
# =============================================================================
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# =============================================================================
# PAGE CONFIG
# =============================================================================
st.set_page_config(
    page_title="Arthawise Dashboard",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CSS
# =============================================================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.stApp {
    background-color: #0f172a;
    color: #e2e8f0;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #111827;
    border-right: 1px solid #1e293b;
}

[data-testid="stSidebar"] * {
    color: #f1f5f9 !important;
}

/* MULTISELECT */
.stMultiSelect div[data-baseweb="select"] > div {
    background-color: #1e293b !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
    min-height: 52px !important;
}

.stMultiSelect span {
    color: white !important;
}

.stMultiSelect svg {
    fill: #94a3b8 !important;
}

.stMultiSelect input {
    color: white !important;
}

.stMultiSelect [data-baseweb="tag"] {
    background-color: #334155 !important;
    border-radius: 8px !important;
}

/* KPI CARD */
.kpi-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 20px;
    padding: 24px;
    margin-bottom: 16px;
}

.kpi-label {
    font-size: 0.8rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
    font-weight: 600;
}

.kpi-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.2;
}

.kpi-sub {
    margin-top: 10px;
    color: #64748b;
    font-size: 0.9rem;
}

/* COLORS */
.green { color: #10b981; }
.red { color: #ef4444; }
.blue { color: #3b82f6; }
.purple { color: #a855f7; }
.white { color: #f8fafc; }

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #111827;
    padding: 8px;
    border-radius: 14px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 10px;
    padding: 14px 28px;
    font-size: 0.95rem;
    color: #94a3b8;
}

.stTabs [aria-selected="true"] {
    background-color: #1e293b !important;
    color: white !important;
}

/* HIDE */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# =============================================================================
# LOAD DATA
# =============================================================================
@st.cache_data
def load_data():

    BASE_DIR = Path(__file__).parent
    CSV_PATH = BASE_DIR / "Data_Finance_Final.csv"

    df = pd.read_csv(CSV_PATH)

    # DATE
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

    # DROP INVALID DATE
    df = df.dropna(subset=['Date'])

    # AUTO CREATE COLUMN
    if 'Year' not in df.columns:
        df['Year'] = df['Date'].dt.year

    if 'Month' not in df.columns:
        df['Month'] = df['Date'].dt.month

    if 'DayOfWeek' not in df.columns:
        df['DayOfWeek'] = df['Date'].dt.dayofweek

    # CLEANING
    if 'Category' in df.columns:
        df = df[df['Category'] != 'Uncategorized']

    # MONTH LABEL
    month_id = {
        1:'Januari',
        2:'Februari',
        3:'Maret',
        4:'April',
        5:'Mei',
        6:'Juni',
        7:'Juli',
        8:'Agustus',
        9:'September',
        10:'Oktober',
        11:'November',
        12:'Desember'
    }

    df['Month_Label'] = df['Month'].map(month_id)

    return df.reset_index(drop=True)

df_raw = load_data()

# =============================================================================
# EMPTY CHECK
# =============================================================================
if len(df_raw) == 0:
    st.error("Dataset kosong.")
    st.stop()

# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:

    st.markdown("## 💸 Arthawise")

    st.markdown("---")

    st.markdown("### Filter")

    months = sorted(df_raw['Month_Label'].dropna().unique())

    selected_months = st.multiselect(
        "Bulan",
        months,
        default=months
    )

    categories = sorted(df_raw['Category'].dropna().unique())

    selected_categories = st.multiselect(
        "Kategori",
        categories,
        default=categories
    )

    accounts = sorted(df_raw['Account'].dropna().unique())

    selected_accounts = st.multiselect(
        "Metode Pembayaran",
        accounts,
        default=accounts
    )

# =============================================================================
# FILTER DATA
# =============================================================================
df = df_raw[
    (df_raw['Month_Label'].isin(selected_months)) &
    (df_raw['Category'].isin(selected_categories)) &
    (df_raw['Account'].isin(selected_accounts))
]

# EMPTY FILTER CHECK
if len(df) == 0:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

# =============================================================================
# SPLIT DATA
# =============================================================================
income = df[df['Type'] == 'INCOME']
expense = df[df['Type'] == 'EXPENSE']

# =============================================================================
# METRICS
# =============================================================================
total_income = income['Amount'].sum()
total_expense = expense['Amount'].sum()

net_cashflow = total_income - total_expense

savings_rate = (
    (net_cashflow / total_income) * 100
    if total_income > 0 else 0
)

avg_expense = (
    expense['Amount'].mean()
    if len(expense) > 0 else 0
)

# =============================================================================
# HEADER
# =============================================================================
st.markdown(f"""
<div style="
    background: linear-gradient(135deg,#111827,#1e293b);
    padding:32px;
    border-radius:24px;
    border:1px solid #1e293b;
    margin-bottom:28px;
">

    <div style="
        color:#94a3b8;
        font-size:0.9rem;
        letter-spacing:1px;
        text-transform:uppercase;
        margin-bottom:12px;
    ">
        PERSONAL FINANCE TRACKER
    </div>

    <div style="
        font-size:2.4rem;
        font-weight:800;
        color:white;
        margin-bottom:10px;
    ">
        Arthawise Dashboard
    </div>

    <div style="
        color:#cbd5e1;
        font-size:1rem;
    ">
        Savings rate saat ini
        <b>{savings_rate:.1f}%</b>
        dengan net cash flow
        <b>Rp {net_cashflow:,.0f}</b>
    </div>

</div>
""", unsafe_allow_html=True)

# =============================================================================
# KPI
# =============================================================================
top1, top2, top3 = st.columns(3)
bot1, bot2 = st.columns(2)

cards = [
    (
        top1,
        "Total Pemasukan",
        f"Rp {total_income/1e6:.2f}jt",
        f"{len(income)} transaksi",
        "green"
    ),
    (
        top2,
        "Total Pengeluaran",
        f"Rp {total_expense/1e6:.2f}jt",
        f"{len(expense)} transaksi",
        "red"
    ),
    (
        top3,
        "Net Cash Flow",
        f"Rp {net_cashflow/1e6:.2f}jt",
        "Surplus" if net_cashflow >= 0 else "Defisit",
        "blue"
    ),
    (
        bot1,
        "Savings Rate",
        f"{savings_rate:.1f}%",
        "dari total pemasukan",
        "purple"
    ),
    (
        bot2,
        "Total Transaksi",
        f"{len(df):,}",
        f"rata-rata Rp {avg_expense:,.0f}",
        "white"
    )
]

for col, label, value, sub, color in cards:

    with col:

        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>

            <div class="kpi-val {color}">
                {value}
            </div>

            <div class="kpi-sub">
                {sub}
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# TABS
# =============================================================================
tab1, tab2, tab3 = st.tabs([
    "📊 Ringkasan",
    "💸 Pengeluaran",
    "💰 Pemasukan"
])

# =============================================================================
# TAB 1
# =============================================================================
with tab1:

    st.subheader("Income vs Expense")

    monthly = df.groupby(
        ['Month_Label', 'Type']
    )['Amount'].sum().unstack(fill_value=0)

    fig = go.Figure()

    if 'INCOME' in monthly.columns:
        fig.add_trace(go.Scatter(
            x=monthly.index,
            y=monthly['INCOME'],
            mode='lines+markers',
            name='Income'
        ))

    if 'EXPENSE' in monthly.columns:
        fig.add_trace(go.Scatter(
            x=monthly.index,
            y=monthly['EXPENSE'],
            mode='lines+markers',
            name='Expense'
        ))

    fig.update_layout(
        paper_bgcolor='#111827',
        plot_bgcolor='#111827',
        font_color='white',
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

# =============================================================================
# TAB 2
# =============================================================================
with tab2:

    st.subheader("Distribusi Pengeluaran")

    if len(expense) > 0:

        cat_exp = expense.groupby('Category')['Amount'].sum()

        fig2 = go.Figure(
            go.Pie(
                labels=cat_exp.index,
                values=cat_exp.values,
                hole=0.5
            )
        )

        fig2.update_layout(
            paper_bgcolor='#111827',
            font_color='white',
            height=450
        )

        st.plotly_chart(fig2, use_container_width=True)

# =============================================================================
# TAB 3
# =============================================================================
with tab3:

    st.subheader("Metode Pembayaran")

    if len(expense) > 0:

        payment = expense.groupby('Account')['Amount'].sum()

        fig3 = go.Figure(
            go.Bar(
                x=payment.index,
                y=payment.values
            )
        )

        fig3.update_layout(
            paper_bgcolor='#111827',
            plot_bgcolor='#111827',
            font_color='white',
            height=450
        )

        st.plotly_chart(fig3, use_container_width=True)

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("""
<div style='margin-top:50px'></div>

<div style="
    text-align:center;
    color:#64748b;
    font-size:0.85rem;
    padding-bottom:20px;
">
    Arthawise • Personal Finance Dashboard
</div>
""", unsafe_allow_html=True)
