import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Arthawise — Personal Finance",
    page_icon="💸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
.stApp { background-color: #0b0f1a; color: #e2e8f0; }

[data-testid="stSidebar"] {
    background-color: #0f1623;
    border-right: 1px solid #1a2235;
}
[data-testid="stSidebar"] * { color: #94a3b8 !important; }

/* Metric cards */
.kpi-card {
    background: #111827;
    border: 1px solid #1e2d45;
    border-radius: 14px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-card.green::after  { background: #10b981; }
.kpi-card.red::after    { background: #ef4444; }
.kpi-card.blue::after   { background: #3b82f6; }
.kpi-card.purple::after { background: #8b5cf6; }
.kpi-card.amber::after  { background: #f59e0b; }

.kpi-label { font-size:0.68rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#4b5563; margin-bottom:6px; }
.kpi-val   { font-family:'JetBrains Mono',monospace; font-size:1.45rem; font-weight:500; line-height:1.2; }
.kpi-val.g { color:#10b981; }
.kpi-val.r { color:#ef4444; }
.kpi-val.w { color:#f1f5f9; }
.kpi-sub   { font-size:0.7rem; color:#374151; margin-top:4px; }

/* Status badge */
.status-badge {
    display:inline-block; padding:4px 14px; border-radius:20px;
    font-size:0.75rem; font-weight:700; letter-spacing:0.05em;
}
.status-sehat   { background:#052e16; color:#10b981; border:1px solid #10b981; }
.status-waspada { background:#431407; color:#f59e0b; border:1px solid #f59e0b; }
.status-kritis  { background:#450a0a; color:#ef4444; border:1px solid #ef4444; }

/* Section title */
.sec-title {
    font-size:1rem; font-weight:700; color:#e2e8f0;
    margin:28px 0 16px 0; display:flex; align-items:center; gap:10px;
}
.sec-title::after {
    content:''; flex:1; height:1px;
    background:linear-gradient(90deg,#1e2535,transparent);
}

/* Insight */
.insight {
    background:#0d1f35; border-left:3px solid #3b82f6;
    border-radius:0 10px 10px 0; padding:14px 18px; margin-top:10px;
    font-size:0.82rem; color:#94a3b8; line-height:1.65;
}
.insight strong { color:#93c5fd; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background:#0f1623; border-bottom:1px solid #1a2235; gap:4px;
}
.stTabs [data-baseweb="tab"] {
    background:transparent; color:#4b5563;
    border-radius:8px 8px 0 0; padding:10px 20px;
    font-size:0.85rem; font-weight:600;
}
.stTabs [aria-selected="true"] {
    background:#111827 !important; color:#e2e8f0 !important;
    border-bottom:2px solid #3b82f6 !important;
}

#MainMenu, footer, header { visibility:hidden; }
.stDeployButton { display:none; }
</style>
""", unsafe_allow_html=True)

# ── Plotly theme ──────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor='#111827', plot_bgcolor='#111827',
    font=dict(family='Plus Jakarta Sans', color='#9ca3af', size=11),
    margin=dict(l=16, r=16, t=36, b=16),
    xaxis=dict(gridcolor='#1e2535', showline=False, zeroline=False),
    yaxis=dict(gridcolor='#1e2535', showline=False, zeroline=False),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#6b7280')),
    hoverlabel=dict(bgcolor='#1e2535', font_color='#e2e8f0', bordercolor='#374151'),
)

C = dict(
    green='#10b981', red='#ef4444', blue='#3b82f6',
    purple='#8b5cf6', amber='#f59e0b', teal='#14b8a6',
    indigo='#6366f1', pink='#ec4899', sky='#0ea5e9',
)
CAT_COLORS = {
    'Makan & Minum': C['amber'],  'Belanja':  C['purple'],
    'Tagihan':       C['blue'],   'Hiburan':  C['pink'],
    'Goals':         C['green'],  'Gaji':     C['teal'],
}

# ── Load & prep data ──────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv('Data_Finance_Final.csv')
    df['Date'] = pd.to_datetime(df['Date'])
    df = df[df['Category'] != 'Uncategorized'].reset_index(drop=True)

    month_id = {7:'Juli',8:'Agustus',9:'September',
                10:'Oktober',11:'November',12:'Desember'}
    if 'Month'     not in df.columns: df['Month']     = df['Date'].dt.month
    if 'DayOfWeek' not in df.columns: df['DayOfWeek'] = df['Date'].dt.dayofweek

    df['Month_Label'] = df['Month'].map(month_id)
    return df

df_raw = load_data()

MONTH_ORDER = ['Juli','Agustus','September','Oktober','November','Desember']
MONTH_MAP   = {7:'Juli',8:'Agustus',9:'September',10:'Oktober',11:'November',12:'Desember'}
DAY_MAP     = {0:'Senin',1:'Selasa',2:'Rabu',3:'Kamis',4:'Jumat',5:'Sabtu',6:'Minggu'}

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💸 Arthawise")
    st.markdown("<hr style='border-color:#1a2235;margin:12px 0'>", unsafe_allow_html=True)
    st.markdown("**Filter**")

    avail_months = [m for m in MONTH_ORDER if m in df_raw['Month_Label'].unique()]
    sel_months   = st.multiselect("Bulan", avail_months, default=avail_months, label_visibility='collapsed')

    all_cats = sorted(df_raw['Category'].unique())
    sel_cats = st.multiselect("Kategori", all_cats, default=all_cats, label_visibility='collapsed')

    all_accs = sorted(df_raw['Account'].unique())
    sel_accs = st.multiselect("Metode Bayar", all_accs, default=all_accs, label_visibility='collapsed')

    st.markdown("<hr style='border-color:#1a2235;margin:12px 0'>", unsafe_allow_html=True)
    st.caption("Data: Jul–Des 2025 · 968 transaksi")

# ── Filter ────────────────────────────────────────────────────────────────────
df = df_raw[
    df_raw['Month_Label'].isin(sel_months) &
    df_raw['Category'].isin(sel_cats) &
    df_raw['Account'].isin(sel_accs)
].copy()

exp = df[df['Type'] == 'EXPENSE'].copy()
inc = df[df['Type'] == 'INCOME'].copy()

total_inc  = inc['Amount'].sum()
total_exp  = exp['Amount'].sum()
net_cf     = total_inc - total_exp
savings_rt = (net_cf / total_inc * 100) if total_inc > 0 else 0
exp_ratio  = (total_exp / total_inc * 100) if total_inc > 0 else 0

# Status keuangan
if exp_ratio < 60:
    status, status_cls, status_icon = "Sehat", "status-sehat", "✅"
elif exp_ratio < 85:
    status, status_cls, status_icon = "Waspada", "status-waspada", "⚠️"
else:
    status, status_cls, status_icon = "Kritis", "status-kritis", "🚨"

# ── Header ────────────────────────────────────────────────────────────────────
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("""
    <div style='padding:20px 0 4px'>
      <div style='font-size:0.7rem;font-weight:700;letter-spacing:0.15em;
                  color:#374151;text-transform:uppercase;margin-bottom:6px'>
        PERSONAL FINANCE TRACKER
      </div>
      <h1 style='font-size:1.8rem;font-weight:800;color:#f1f5f9;margin:0'>
        Arthawise Dashboard
      </h1>
    </div>""", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"""
    <div style='padding:20px 0 4px;text-align:right'>
      <div style='font-size:0.7rem;color:#374151;margin-bottom:8px'>STATUS KEUANGAN</div>
      <span class='status-badge {status_cls}'>{status_icon} {status}</span>
      <div style='font-size:0.7rem;color:#374151;margin-top:6px'>
        Rasio pengeluaran {exp_ratio:.1f}%
      </div>
    </div>""", unsafe_allow_html=True)

# ── KPI Cards ─────────────────────────────────────────────────────────────────
st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)

cards = [
    (k1, "Total Pemasukan",    f"Rp {total_inc/1e6:.2f}jt",   f"{len(inc)} transaksi",         "g", "green"),
    (k2, "Total Pengeluaran",  f"Rp {total_exp/1e6:.2f}jt",   f"{len(exp)} transaksi",         "r", "red"),
    (k3, "Net Cash Flow",      f"{'+'if net_cf>=0 else ''}Rp {net_cf/1e6:.2f}jt",
                                                                 "Surplus" if net_cf>=0 else "Defisit",
                                                                 "g" if net_cf>=0 else "r",      "blue"),
    (k4, "Savings Rate",       f"{savings_rt:.1f}%",            "dari total pemasukan",         "g" if savings_rt>20 else "r", "purple"),
    (k5, "Total Transaksi",    f"{len(df):,}",                  f"rata-rata Rp {exp['Amount'].mean():,.0f}/transaksi" if len(exp)>0 else "-",
                                                                 "w", "amber"),
]
for col, label, val, sub, val_cls, card_cls in cards:
    with col:
        st.markdown(f"""
        <div class='kpi-card {card_cls}'>
          <div class='kpi-label'>{label}</div>
          <div class='kpi-val {val_cls}'>{val}</div>
          <div class='kpi-sub'>{sub}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊  Ringkasan", "💸  Pengeluaran", "💰  Pemasukan & Pembayaran"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — RINGKASAN
# ══════════════════════════════════════════════════════════════════════════════
with tab1:

    # Monthly cash flow
    monthly = df.groupby(['Year','Month','Type'])['Amount'].sum().unstack(fill_value=0).reset_index()
    for c in ['EXPENSE','INCOME']:
        if c not in monthly.columns: monthly[c] = 0
    monthly['NCF']   = monthly['INCOME'] - monthly['EXPENSE']
    monthly['Label'] = monthly['Month'].map(MONTH_MAP)
    monthly = monthly[monthly['Label'].isin(sel_months)]
    monthly['_ord'] = monthly['Label'].apply(lambda x: MONTH_ORDER.index(x) if x in MONTH_ORDER else 99)
    monthly = monthly.sort_values('_ord').reset_index(drop=True)

    st.markdown("<div class='sec-title'>Arus Kas Bulanan</div>", unsafe_allow_html=True)

    if len(monthly) >= 1:
        fig = make_subplots(rows=1, cols=2, subplot_titles=('Net Cash Flow per Bulan', 'Pemasukan vs Pengeluaran'),
                            column_widths=[0.45, 0.55])

        # Bar NCF
        bar_colors = [C['green'] if v >= 0 else C['red'] for v in monthly['NCF']]
        fig.add_trace(go.Bar(
            x=monthly['Label'], y=monthly['NCF'],
            marker_color=bar_colors, name='Net Cash Flow',
            text=[f"Rp{v/1e6:.2f}jt" for v in monthly['NCF']],
            textposition='outside', textfont=dict(size=10, color='#9ca3af'),
            hovertemplate='<b>%{x}</b><br>Net CF: Rp%{y:,.0f}<extra></extra>'
        ), row=1, col=1)
        fig.add_hline(y=0, line_dash='dot', line_color='#374151', row=1, col=1)

        # Line income vs expense
        fig.add_trace(go.Scatter(
            x=monthly['Label'], y=monthly['INCOME'],
            mode='lines+markers', name='Pemasukan',
            line=dict(color=C['green'], width=2.5),
            marker=dict(size=7), fill='tozeroy', fillcolor='rgba(16,185,129,0.08)',
            hovertemplate='<b>%{x}</b><br>Pemasukan: Rp%{y:,.0f}<extra></extra>'
        ), row=1, col=2)
        fig.add_trace(go.Scatter(
            x=monthly['Label'], y=monthly['EXPENSE'],
            mode='lines+markers', name='Pengeluaran',
            line=dict(color=C['red'], width=2.5),
            marker=dict(size=7), fill='tozeroy', fillcolor='rgba(239,68,68,0.08)',
            hovertemplate='<b>%{x}</b><br>Pengeluaran: Rp%{y:,.0f}<extra></extra>'
        ), row=1, col=2)

        fig.update_layout(**PLOTLY_LAYOUT, height=340, showlegend=True)
        fig.update_annotations(font=dict(color='#6b7280', size=11))
        st.plotly_chart(fig, use_container_width=True)

        if len(monthly) >= 2:
            first, last = monthly.iloc[0]['NCF'], monthly.iloc[-1]['NCF']
            pct = ((last - first) / abs(first) * 100) if first != 0 else 0
            worst = monthly.loc[monthly['NCF'].idxmin(), 'Label']
            st.markdown(f"""
            <div class='insight'>
              Net cash flow rata-rata bulanan <strong>Rp {monthly['NCF'].mean():,.0f}</strong>.
              Perubahan dari {monthly.iloc[0]['Label']} ke {monthly.iloc[-1]['Label']}:
              <strong>{'+'if pct>=0 else ''}{pct:.1f}%</strong>.
              Titik terendah: <strong>{worst} 2025</strong>.
            </div>""", unsafe_allow_html=True)

    # Ringkasan per bulan — tabel interaktif
    st.markdown("<div class='sec-title'>Rekap Bulanan</div>", unsafe_allow_html=True)

    if len(monthly) >= 1:
        tbl = monthly[['Label','INCOME','EXPENSE','NCF']].copy()
        tbl.columns = ['Bulan','Pemasukan','Pengeluaran','Net Cash Flow']
        tbl['Rasio (%)'] = (tbl['Pengeluaran'] / tbl['Pemasukan'] * 100).round(1)
        tbl['Status'] = tbl['Rasio (%)'].apply(
            lambda x: '✅ Sehat' if x < 60 else ('⚠️ Waspada' if x < 85 else '🚨 Kritis')
        )
        for c in ['Pemasukan','Pengeluaran','Net Cash Flow']:
            tbl[c] = tbl[c].apply(lambda x: f"Rp {x:,.0f}")
        st.dataframe(tbl.set_index('Bulan'), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — PENGELUARAN
# ══════════════════════════════════════════════════════════════════════════════
with tab2:

    if len(exp) == 0:
        st.info("Tidak ada data pengeluaran untuk filter yang dipilih.")
    else:
        # Baris 1: pie + bar kategori
        st.markdown("<div class='sec-title'>Distribusi per Kategori</div>", unsafe_allow_html=True)

        exp_by_cat = exp.groupby('Category')['Amount'].sum().sort_values(ascending=False)
        avg_by_cat = exp.groupby(['Month','Category'])['Amount'].sum().groupby('Category').mean().sort_values(ascending=False)
        top_cat    = exp_by_cat.idxmax()
        top_pct    = exp_by_cat.max() / exp_by_cat.sum() * 100

        col_pie, col_bar = st.columns([1, 1.3])
        with col_pie:
            colors_pie = [CAT_COLORS.get(c, C['blue']) for c in exp_by_cat.index]
            fig_pie = go.Figure(go.Pie(
                labels=exp_by_cat.index, values=exp_by_cat.values,
                marker=dict(colors=colors_pie, line=dict(color='#0b0f1a', width=2)),
                textinfo='label+percent', textfont=dict(size=10),
                hole=0.45,
                hovertemplate='<b>%{label}</b><br>Total: Rp%{value:,.0f}<br>%{percent}<extra></extra>'
            ))
            fig_pie.update_layout(**PLOTLY_LAYOUT, height=300,
                                  annotations=[dict(text=f'<b>{top_pct:.0f}%</b><br>{top_cat}',
                                                    x=0.5, y=0.5, font_size=12,
                                                    font_color='#e2e8f0', showarrow=False)])
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_bar:
            colors_bar = [CAT_COLORS.get(c, C['blue']) for c in avg_by_cat.index]
            fig_bar = go.Figure(go.Bar(
                x=avg_by_cat.values, y=avg_by_cat.index, orientation='h',
                marker_color=colors_bar,
                text=[f"Rp {v:,.0f}" for v in avg_by_cat.values],
                textposition='outside', textfont=dict(size=9, color='#6b7280'),
                hovertemplate='<b>%{y}</b><br>Rata-rata: Rp%{x:,.0f}/bulan<extra></extra>'
            ))
            fig_bar.update_layout(**PLOTLY_LAYOUT, height=300,
                                  title=dict(text='Rata-rata Pengeluaran per Bulan', font=dict(size=11, color='#6b7280')),
                                  yaxis=dict(autorange='reversed', gridcolor='#1e2535'))
            st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown(f"""
        <div class='insight'>
          Kategori terboros: <strong>{top_cat}</strong> ({top_pct:.1f}% dari total pengeluaran),
          rata-rata <strong>Rp {avg_by_cat.max():,.0f}/bulan</strong>.
          Kurangi frekuensi atau terapkan batas anggaran bulanan untuk kategori ini.
        </div>""", unsafe_allow_html=True)

        # Baris 2: tren bulanan per kategori + pola harian
        st.markdown("<div class='sec-title'>Pola Waktu Pengeluaran</div>", unsafe_allow_html=True)

        col_trend, col_day = st.columns(2)

        with col_trend:
            monthly_cat = exp.groupby(['Month','Category'])['Amount'].sum().reset_index()
            monthly_cat['Label'] = monthly_cat['Month'].map(MONTH_MAP)
            monthly_cat = monthly_cat[monthly_cat['Label'].isin(sel_months)]
            monthly_cat['_ord'] = monthly_cat['Label'].apply(lambda x: MONTH_ORDER.index(x) if x in MONTH_ORDER else 99)
            monthly_cat = monthly_cat.sort_values('_ord')

            fig_trend = go.Figure()
            for cat in monthly_cat['Category'].unique():
                sub = monthly_cat[monthly_cat['Category'] == cat]
                fig_trend.add_trace(go.Scatter(
                    x=sub['Label'], y=sub['Amount'],
                    mode='lines+markers', name=cat,
                    line=dict(color=CAT_COLORS.get(cat, C['blue']), width=2),
                    marker=dict(size=6),
                    hovertemplate=f'<b>{cat}</b><br>%{{x}}: Rp%{{y:,.0f}}<extra></extra>'
                ))
            fig_trend.update_layout(**PLOTLY_LAYOUT, height=300,
                                    title=dict(text='Tren Pengeluaran per Kategori', font=dict(size=11, color='#6b7280')))
            st.plotly_chart(fig_trend, use_container_width=True)

        with col_day:
            exp['DayName'] = exp['DayOfWeek'].map(DAY_MAP)
            daily = exp.groupby(['DayOfWeek','DayName'])['Amount'].sum().reset_index().sort_values('DayOfWeek')

            max_idx = daily['Amount'].idxmax()
            min_idx = daily['Amount'].idxmin()
            bar_cols = [C['red'] if i == max_idx else ('#374151' if i == min_idx else C['blue'])
                        for i in daily.index]

            fig_day = go.Figure(go.Bar(
                x=daily['DayName'], y=daily['Amount'],
                marker_color=bar_cols,
                text=[f"Rp{v/1e6:.1f}jt" for v in daily['Amount']],
                textposition='outside', textfont=dict(size=9, color='#6b7280'),
                hovertemplate='<b>%{x}</b><br>Total: Rp%{y:,.0f}<extra></extra>'
            ))
            fig_day.update_layout(**PLOTLY_LAYOUT, height=300,
                                  title=dict(text='Total Pengeluaran per Hari', font=dict(size=11, color='#6b7280')))
            st.plotly_chart(fig_day, use_container_width=True)

        max_day = daily.loc[daily['Amount'].idxmax(), 'DayName']
        min_day = daily.loc[daily['Amount'].idxmin(), 'DayName']
        selisih = daily['Amount'].max() - daily['Amount'].min()
        st.markdown(f"""
        <div class='insight'>
          Pengeluaran tertinggi: <strong>{max_day}</strong> —
          terendah: <strong>{min_day}</strong>,
          selisih <strong>Rp {selisih:,.0f}</strong>.
          Jadikan {min_day} sebagai hari evaluasi pengeluaran mingguan.
        </div>""", unsafe_allow_html=True)

        # Baris 3: Weekday vs Weekend
        st.markdown("<div class='sec-title'>Weekday vs Weekend</div>", unsafe_allow_html=True)

        exp['IsWeekend_f'] = exp['DayOfWeek'].isin([5,6])
        wkd = exp.groupby('IsWeekend_f')['Amount'].mean()
        wkd.index = wkd.index.map({False:'Weekday', True:'Weekend'})
        wkd_cnt = exp.groupby('IsWeekend_f')['Amount'].count()
        wkd_cnt.index = wkd_cnt.index.map({False:'Weekday', True:'Weekend'})

        col_wkd1, col_wkd2 = st.columns([1, 2])
        with col_wkd1:
            fig_wkd = go.Figure(go.Bar(
                x=list(wkd.index), y=list(wkd.values),
                marker_color=[C['blue'], C['red']],
                text=[f"Rp {v:,.0f}" for v in wkd.values],
                textposition='outside', textfont=dict(size=10, color='#6b7280'),
                hovertemplate='<b>%{x}</b><br>Rata-rata: Rp%{y:,.0f}<extra></extra>'
            ))
            fig_wkd.update_layout(**PLOTLY_LAYOUT, height=280,
                                  title=dict(text='Rata-rata per Transaksi', font=dict(size=11, color='#6b7280')))
            st.plotly_chart(fig_wkd, use_container_width=True)

        with col_wkd2:
            # Breakdown kategori weekday vs weekend
            exp_wkd_cat = exp.groupby(['IsWeekend_f','Category'])['Amount'].sum().reset_index()
            exp_wkd_cat['Period'] = exp_wkd_cat['IsWeekend_f'].map({False:'Weekday', True:'Weekend'})

            fig_wkd_cat = go.Figure()
            for cat in exp_wkd_cat['Category'].unique():
                sub = exp_wkd_cat[exp_wkd_cat['Category'] == cat]
                fig_wkd_cat.add_trace(go.Bar(
                    x=sub['Period'], y=sub['Amount'], name=cat,
                    marker_color=CAT_COLORS.get(cat, C['blue']),
                    hovertemplate=f'<b>{cat}</b><br>%{{x}}: Rp%{{y:,.0f}}<extra></extra>'
                ))
            fig_wkd_cat.update_layout(**PLOTLY_LAYOUT, height=280, barmode='stack',
                                      title=dict(text='Breakdown Kategori Weekday vs Weekend', font=dict(size=11, color='#6b7280')))
            st.plotly_chart(fig_wkd_cat, use_container_width=True)

        selisih_pct = ((wkd.get('Weekend',0) - wkd.get('Weekday',0)) / wkd.get('Weekday',1)) * 100
        direction   = "lebih tinggi" if selisih_pct > 0 else "lebih rendah"
        st.markdown(f"""
        <div class='insight'>
          Rata-rata pengeluaran per transaksi Weekend <strong>{direction} {abs(selisih_pct):.1f}%</strong>
          dibanding Weekday (Rp {wkd.get('Weekday',0):,.0f} vs Rp {wkd.get('Weekend',0):,.0f}).
        </div>""", unsafe_allow_html=True)

        # Tabel transaksi
        st.markdown("<div class='sec-title'>Detail Transaksi Pengeluaran</div>", unsafe_allow_html=True)
        tbl_exp = exp[['Date','Title','Category','Amount','Account']].copy()
        tbl_exp['Date']   = tbl_exp['Date'].dt.strftime('%d %b %Y')
        tbl_exp['Amount'] = tbl_exp['Amount'].apply(lambda x: f"Rp {x:,.0f}")
        tbl_exp = tbl_exp.sort_values('Date', ascending=False).reset_index(drop=True)
        st.dataframe(tbl_exp, use_container_width=True, height=300)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — PEMASUKAN & METODE PEMBAYARAN
# ══════════════════════════════════════════════════════════════════════════════
with tab3:

    col_l, col_r = st.columns(2)

    # Tren pemasukan
    with col_l:
        st.markdown("<div class='sec-title'>Tren Pemasukan Bulanan</div>", unsafe_allow_html=True)

        if len(inc) > 0:
            monthly_inc = inc.groupby(['Year','Month'])['Amount'].sum().reset_index()
            monthly_inc['Label'] = monthly_inc['Month'].map(MONTH_MAP)
            monthly_inc = monthly_inc[monthly_inc['Label'].isin(sel_months)]
            monthly_inc['_ord'] = monthly_inc['Label'].apply(lambda x: MONTH_ORDER.index(x) if x in MONTH_ORDER else 99)
            monthly_inc = monthly_inc.sort_values('_ord').reset_index(drop=True)

            max_inc = monthly_inc.loc[monthly_inc['Amount'].idxmax()]
            min_inc = monthly_inc.loc[monthly_inc['Amount'].idxmin()]

            bar_cols_inc = [C['red'] if v == monthly_inc['Amount'].min()
                            else C['green'] for v in monthly_inc['Amount']]

            fig_inc = go.Figure(go.Bar(
                x=monthly_inc['Label'], y=monthly_inc['Amount'],
                marker_color=bar_cols_inc,
                text=[f"Rp{v/1e6:.2f}jt" for v in monthly_inc['Amount']],
                textposition='outside', textfont=dict(size=9, color='#6b7280'),
                hovertemplate='<b>%{x}</b><br>Pemasukan: Rp%{y:,.0f}<extra></extra>'
            ))
            fig_inc.update_layout(**PLOTLY_LAYOUT, height=320,
                                  title=dict(text='Total Pemasukan per Bulan', font=dict(size=11, color='#6b7280')))
            st.plotly_chart(fig_inc, use_container_width=True)

            selisih_inc = max_inc['Amount'] - min_inc['Amount']
            st.markdown(f"""
            <div class='insight'>
              Tertinggi: <strong>{max_inc['Label']} (Rp {max_inc['Amount']:,.0f})</strong> —
              terendah: <strong>{min_inc['Label']} (Rp {min_inc['Amount']:,.0f})</strong>,
              selisih <strong>Rp {selisih_inc:,.0f}</strong>.
              Sisihkan surplus bulan pemasukan tinggi sebagai buffer untuk bulan rendah.
            </div>""", unsafe_allow_html=True)

    # Metode pembayaran
    with col_r:
        st.markdown("<div class='sec-title'>Metode Pembayaran</div>", unsafe_allow_html=True)

        if len(exp) > 0:
            pay = exp.groupby('Account').agg(
                Frekuensi=('Amount','count'),
                Total=('Amount','sum'),
                Rata_rata=('Amount','mean')
            ).sort_values('Frekuensi', ascending=False).reset_index()

            top_pay = pay.iloc[0]

            fig_pay = make_subplots(rows=1, cols=2,
                                    subplot_titles=('Frekuensi', 'Rata-rata Nilai'))

            fig_pay.add_trace(go.Bar(
                x=pay['Account'], y=pay['Frekuensi'],
                marker_color=[C['blue'], C['purple'], C['teal']][:len(pay)],
                text=pay['Frekuensi'].astype(str),
                textposition='outside', textfont=dict(size=10),
                hovertemplate='<b>%{x}</b><br>%{y} transaksi<extra></extra>'
            ), row=1, col=1)

            fig_pay.add_trace(go.Bar(
                x=pay['Account'], y=pay['Rata_rata'],
                marker_color=[C['amber'], C['pink'], C['indigo']][:len(pay)],
                text=[f"Rp{v:,.0f}" for v in pay['Rata_rata']],
                textposition='outside', textfont=dict(size=9),
                hovertemplate='<b>%{x}</b><br>Rata-rata: Rp%{y:,.0f}<extra></extra>'
            ), row=1, col=2)

            fig_pay.update_layout(**PLOTLY_LAYOUT, height=320, showlegend=False)
            fig_pay.update_annotations(font=dict(color='#6b7280', size=11))
            st.plotly_chart(fig_pay, use_container_width=True)

            st.markdown(f"""
            <div class='insight'>
              Metode paling sering: <strong>{top_pay['Account']}</strong>
              ({int(top_pay['Frekuensi'])} transaksi, rata-rata Rp {top_pay['Rata_rata']:,.0f}/transaksi).
              Aktifkan notifikasi real-time dan tetapkan limit top-up bulanan.
            </div>""", unsafe_allow_html=True)

    # Breakdown pemasukan per kategori
    st.markdown("<div class='sec-title'>Sumber Pemasukan</div>", unsafe_allow_html=True)

    if len(inc) > 0:
        inc_cat = inc.groupby('Category')['Amount'].sum().sort_values(ascending=False)

        col_inc1, col_inc2 = st.columns([1, 2])
        with col_inc1:
            fig_inc_pie = go.Figure(go.Pie(
                labels=inc_cat.index, values=inc_cat.values,
                marker=dict(colors=[C['green'], C['teal'], C['blue'], C['indigo']][:len(inc_cat)],
                            line=dict(color='#0b0f1a', width=2)),
                textinfo='label+percent', textfont=dict(size=10), hole=0.4,
                hovertemplate='<b>%{label}</b><br>Rp%{value:,.0f}<extra></extra>'
            ))
            fig_inc_pie.update_layout(**PLOTLY_LAYOUT, height=260,
                                      title=dict(text='Proporsi Sumber Pemasukan', font=dict(size=11, color='#6b7280')))
            st.plotly_chart(fig_inc_pie, use_container_width=True)

        with col_inc2:
            tbl_inc = inc[['Date','Title','Category','Amount','Account']].copy()
            tbl_inc['Date']   = tbl_inc['Date'].dt.strftime('%d %b %Y')
            tbl_inc['Amount'] = tbl_inc['Amount'].apply(lambda x: f"Rp {x:,.0f}")
            tbl_inc = tbl_inc.sort_values('Date', ascending=False).reset_index(drop=True)
            st.dataframe(tbl_inc, use_container_width=True, height=260)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
st.markdown("""
<div style='border-top:1px solid #1a2235;padding-top:16px;text-align:center;
            font-size:0.68rem;color:#374151'>
  Arthawise · Personal Finance Tracker · Capstone Project Dicoding 2025
</div>""", unsafe_allow_html=True)