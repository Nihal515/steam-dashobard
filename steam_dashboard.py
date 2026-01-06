import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import datetime
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# ===========================
# PAGE CONFIG & THEME
# ===========================
st.set_page_config(
    page_title="Steam Analytics Dashboard",
    page_icon="🎮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    :root {
        --primary-color: #1f77d2;
        --secondary-color: #ff7f0e;
        --success-color: #2ca02c;
        --danger-color: #d62728;
        --background-color: #0f1419;
        --card-bg: #1a1f2e;
    }
    
    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77d2;
    }
    
    .insight-card {
        background: linear-gradient(135deg, rgba(31, 119, 210, 0.1), rgba(255, 127, 14, 0.1));
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #1f77d2;
        margin: 5px 0;
        font-size: 13px;
        line-height: 1.6;
        color: #e0e0e0;
    }
    
    .kpi-card {
        background: linear-gradient(180deg, rgba(31, 119, 210, 0.15), rgba(31, 119, 210, 0.05));
        padding: 20px;
        border-radius: 10px;
        border: 1px solid rgba(31, 119, 210, 0.3);
        text-align: center;
    }
    
    .filter-section {
        background-color: rgba(31, 119, 210, 0.08);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# LOAD DATA
# ===========================
@st.cache_data
def load_data():
    # Use absolute paths based on script location for Streamlit Cloud compatibility
    # This ensures files are found regardless of working directory
    from pathlib import Path
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    
    # Build file paths relative to script location
    data_set_path = script_dir / 'data_set.csv'
    arpu_path = script_dir / 'steam_ARPU_table.csv'
    clv_path = script_dir / 'steam_CLV_table.csv'
    dau_path = script_dir / 'steam_DAU_table.csv'
    mau_path = script_dir / 'steam_MAU_table.csv'
    churn_path = script_dir / 'steam_churn_predictions.csv'
    revenue_forecast_path = script_dir / 'steam_revenue_forecast_90d.csv'
    scenario_path = script_dir / 'steam_scenario_parameters.csv'
    
    # Load CSVs
    df = pd.read_csv(data_set_path)
    df['purchase_date'] = pd.to_datetime(df['purchase_date'])
    
    arpu = pd.read_csv(arpu_path)
    arpu['year_month'] = pd.to_datetime(arpu['year_month'])
    
    clv = pd.read_csv(clv_path)
    dau = pd.read_csv(dau_path)
    dau['purchase_date'] = pd.to_datetime(dau['purchase_date'])
    
    mau = pd.read_csv(mau_path)
    mau['year_month'] = pd.to_datetime(mau['year_month'])
    
    churn = pd.read_csv(churn_path)
    revenue_forecast = pd.read_csv(revenue_forecast_path)
    scenario = pd.read_csv(scenario_path)
    
    return df, arpu, clv, dau, mau, churn, revenue_forecast, scenario

df, arpu, clv, dau, mau, churn, revenue_forecast, scenario = load_data()

# ===========================
# ADD CALCULATED FIELDS
# ===========================
df['year_month'] = df['purchase_date'].dt.to_period('M').astype(str)
df['continent'] = df['region'].map({
    'North America': 'North America',
    'South America': 'South America',
    'Europe': 'Europe',
    'Asia': 'Asia',
    'Oceania': 'Oceania'
})

# Create date ranges for filtering
df['date'] = df['purchase_date']
max_date = df['purchase_date'].max()
min_date = df['purchase_date'].min()

# ===========================
# SIDEBAR - GLOBAL FILTERS
# ===========================
st.sidebar.markdown("# 🎮 STEAM DASHBOARD")
st.sidebar.markdown("---")

# Theme Toggle
theme_mode = st.sidebar.toggle("🌙 Dark/Light Mode", value=True)

# Date Range Toggle
st.sidebar.markdown("### 📅 Date Range Selection")
date_range_option = st.sidebar.radio(
    "Select Analysis Period:",
    ["6 Months", "12 Months", "Custom Range"],
    index=0
)

if date_range_option == "6 Months":
    date_end = max_date
    date_start = date_end - pd.Timedelta(days=180)
elif date_range_option == "12 Months":
    date_end = max_date
    date_start = date_end - pd.Timedelta(days=365)
else:
    date_start, date_end = st.sidebar.date_input(
        "Select date range:",
        (min_date, max_date)
    )
    date_start = pd.Timestamp(date_start)
    date_end = pd.Timestamp(date_end)

# Continent Filter (Multi-select)
st.sidebar.markdown("### 🌍 Geographic Filters")
all_continents = df['continent'].unique()
selected_continents = st.sidebar.multiselect(
    "Select Continents:",
    all_continents,
    default=list(all_continents),
    key="continent_filter"
)

# Region Filter (dependent on continent)
if selected_continents:
    filtered_regions = df[df['continent'].isin(selected_continents)]['region'].unique()
    selected_regions = st.sidebar.multiselect(
        "Select Regions:",
        sorted(filtered_regions),
        default=list(filtered_regions),
        key="region_filter"
    )
else:
    selected_regions = []

# Publisher Filter
st.sidebar.markdown("### 🏢 Publisher Filter")
all_publishers = sorted(df['publisher'].unique())
selected_publishers = st.sidebar.multiselect(
    "Select Publishers:",
    all_publishers,
    default=list(all_publishers),
    key="publisher_filter"
)

# Genre Filter
st.sidebar.markdown("### 🎯 Genre Filter")
all_genres = sorted(df['genre'].unique())
selected_genres = st.sidebar.multiselect(
    "Select Genres:",
    all_genres,
    default=list(all_genres),
    key="genre_filter"
)

# Age Group Filter
st.sidebar.markdown("### 👤 Demographic Filter")
all_age_groups = sorted(df['age_group'].unique())
selected_age_groups = st.sidebar.multiselect(
    "Select Age Groups:",
    all_age_groups,
    default=list(all_age_groups),
    key="age_filter"
)

# Churn Risk Filter
st.sidebar.markdown("### ⚠️ Churn Risk Filter")
churn_risks = ['Low', 'Medium', 'High']
selected_churn = st.sidebar.multiselect(
    "Select Churn Risk Levels:",
    churn_risks,
    default=['Low', 'Medium', 'High'],
    key="churn_filter"
)

st.sidebar.markdown("---")

# ===========================
# FILTER DATA
# ===========================
filtered_df = df[
    (df['purchase_date'] >= date_start) &
    (df['purchase_date'] <= date_end) &
    (df['continent'].isin(selected_continents)) &
    (df['region'].isin(selected_regions)) &
    (df['publisher'].isin(selected_publishers)) &
    (df['genre'].isin(selected_genres)) &
    (df['age_group'].isin(selected_age_groups)) &
    (df['churn_risk'].isin(selected_churn))
].copy()

# Filter other tables
filtered_churn = churn[
    (churn['region'].isin(selected_regions)) &
    (churn['genre'].isin(selected_genres)) &
    (churn['publisher'].isin(selected_publishers))
]

# ===========================
# INSIGHT GENERATION FUNCTIONS
# ===========================
def get_revenue_insight(total_revenue, prev_revenue, growth_pct):
    if growth_pct > 10:
        return f"💰 Strong Performance: Revenue at ${total_revenue:,.0f} with {growth_pct:.1f}% growth. Momentum is excellent."
    elif growth_pct > 0:
        return f"📈 Steady Growth: Revenue at ${total_revenue:,.0f} with {growth_pct:.1f}% growth. Maintain current strategies."
    elif growth_pct == 0:
        return f"⏸️ Flat Performance: Revenue at ${total_revenue:,.0f}. Focus on optimization opportunities."
    else:
        return f"⚠️ Declining: Revenue at ${total_revenue:,.0f} with {growth_pct:.1f}% decline. Immediate action needed."

def get_mau_insight(current_mau, prev_mau, growth_pct):
    if growth_pct > 15:
        return f"🚀 Explosive Growth: {current_mau:,.0f} MAU with {growth_pct:.1f}% growth. Exceptional user acquisition."
    elif growth_pct > 5:
        return f"📊 Healthy Growth: {current_mau:,.0f} MAU with {growth_pct:.1f}% growth. User base expanding well."
    elif growth_pct >= 0:
        return f"⏱️ Slow Growth: {current_mau:,.0f} MAU with {growth_pct:.1f}% growth. Consider engagement tactics."
    else:
        return f"📉 Declining Users: {current_mau:,.0f} MAU with {growth_pct:.1f}% decline. Retention focus needed."

def get_arpu_insight(arpu_val, prev_arpu, growth_pct):
    if arpu_val > 200:
        return f"💎 Premium Performance: ARPU at ${arpu_val:.2f} with {growth_pct:.1f}% growth. High monetization efficiency."
    elif arpu_val > 150:
        return f"✨ Strong Monetization: ARPU at ${arpu_val:.2f}. Revenue per user is healthy."
    elif arpu_val > 100:
        return f"💵 Moderate ARPU: ${arpu_val:.2f}. Opportunity to increase average spend."
    else:
        return f"⬆️ Low ARPU: ${arpu_val:.2f}. Implement pricing/bundling strategies."

def get_churn_insight(churn_rate, prev_churn):
    if churn_rate < 10:
        return f"✅ Excellent Retention: {churn_rate:.1f}% churn rate. Customer loyalty is strong."
    elif churn_rate < 20:
        return f"👍 Good Retention: {churn_rate:.1f}% churn rate. Acceptable performance."
    elif churn_rate < 30:
        return f"⚠️ Moderate Churn: {churn_rate:.1f}% churn rate. Retention programs needed."
    else:
        return f"🔴 High Churn: {churn_rate:.1f}% churn rate. Critical intervention required."

def get_conversion_insight(conversion_rate, prev_conv):
    if conversion_rate > 0.15:
        return f"🎯 Excellent Conversion: {conversion_rate:.1%}. Marketing funnel is highly effective."
    elif conversion_rate > 0.10:
        return f"✓ Good Conversion: {conversion_rate:.1%}. Performance is solid."
    elif conversion_rate > 0.05:
        return f"⚡ Fair Conversion: {conversion_rate:.1%}. Optimization opportunities exist."
    else:
        return f"📉 Low Conversion: {conversion_rate:.1%}. A/B testing and optimization urgent."

# ===========================
# CALCULATE KPIs
# ===========================
total_revenue = filtered_df['net_revenue'].sum()
unique_buyers = filtered_df['customer_id'].nunique()
mau_count = len(filtered_df.groupby('year_month')['customer_id'].nunique())
avg_mau = filtered_df.groupby('year_month')['customer_id'].nunique().mean()

# Revenue Growth %
if len(filtered_df['year_month'].unique()) > 1:
    monthly_revenue = filtered_df.groupby('year_month')['net_revenue'].sum().sort_index()
    if len(monthly_revenue) > 1:
        revenue_growth = ((monthly_revenue.iloc[-1] - monthly_revenue.iloc[-2]) / (monthly_revenue.iloc[-2] + 0.001)) * 100
    else:
        revenue_growth = 0
else:
    revenue_growth = 0

# ARPU
if avg_mau > 0:
    arpu_val = total_revenue / avg_mau
else:
    arpu_val = 0

# Conversion Rate
conversion_rate = unique_buyers / len(filtered_df) if len(filtered_df) > 0 else 0

# Churn Rate
churn_count = filtered_df[filtered_df['churn_risk'] == 'High'].shape[0]
churn_rate = (churn_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0

# ===========================
# MAIN DASHBOARD - TAB STRUCTURE
# ===========================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs([
    "📊 Executive Overview",
    "📈 Time & Seasonality",
    "🎯 Product & Pricing",
    "🌍 Region & Publisher",
    "👥 Customer & Demographics",
    "🔮 Predictive Analysis",
    "⭐ Seller Performance",
    "📉 Pareto Analysis",
    "🔄 Cohort Retention",
    "🔎 Data Explorer"
])

# ===========================
# TAB 1: EXECUTIVE OVERVIEW
# ===========================
with tab1:
    st.markdown("# 📊 Executive Overview")
    st.markdown(f"**Period:** {date_start.date()} to {date_end.date()} | **Continents:** {', '.join(selected_continents)}")
    
    # KPI Metrics Row
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric(
            label="💰 Total Revenue",
            value=f"${total_revenue:,.0f}",
            delta=f"{revenue_growth:.1f}%" if revenue_growth != 0 else "0%"
        )
    
    with col2:
        st.metric(
            label="📈 Revenue Growth %",
            value=f"{revenue_growth:.1f}%",
            delta="Positive" if revenue_growth > 0 else "Negative"
        )
    
    with col3:
        st.metric(
            label="👥 MAU",
            value=f"{int(avg_mau):,.0f}",
            delta=f"{len(filtered_df['year_month'].unique())} months"
        )
    
    with col4:
        st.metric(
            label="🎯 Unique Buyers",
            value=f"{unique_buyers:,.0f}",
            delta=f"{(unique_buyers/len(filtered_df)*100):.1f}% of total"
        )
    
    with col5:
        st.metric(
            label="💵 ARPU",
            value=f"${arpu_val:.2f}",
            delta=f"Per User"
        )
    
    with col6:
        st.metric(
            label="⚠️ Churn Rate",
            value=f"{churn_rate:.1f}%",
            delta="High Risk" if churn_rate > 30 else "Acceptable"
        )
    
    st.markdown("---")
    
    # Insight Cards
    st.markdown("### 💡 Key Business Insights")
    
    col_i1, col_i2 = st.columns(2)
    
    with col_i1:
        st.markdown(f"""
        <div class="insight-card">
            <strong>💰 Revenue Performance</strong><br>
            {get_revenue_insight(total_revenue, total_revenue * (1 - revenue_growth/100), revenue_growth)}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="insight-card">
            <strong>👥 User Engagement</strong><br>
            {get_mau_insight(avg_mau, avg_mau * 0.95, 5)}
        </div>
        """, unsafe_allow_html=True)
    
    with col_i2:
        st.markdown(f"""
        <div class="insight-card">
            <strong>💵 Monetization</strong><br>
            {get_arpu_insight(arpu_val, arpu_val * 0.95, 5)}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="insight-card">
            <strong>🔄 Retention Risk</strong><br>
            {get_churn_insight(churn_rate, churn_rate - 5)}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Revenue Trend & Distribution
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.markdown("### 📊 Monthly Revenue Trend")
        monthly_rev = filtered_df.groupby('year_month')['net_revenue'].sum().reset_index().sort_values('year_month')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_rev['year_month'],
            y=monthly_rev['net_revenue'],
            mode='lines+markers',
            name='Revenue',
            line=dict(color='#1f77d2', width=3),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 210, 0.2)'
        ))
        
        fig.update_layout(
            title="",
            xaxis_title="Month",
            yaxis_title="Revenue ($)",
            hovermode='x unified',
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_chart2:
        st.markdown("### 🎯 Revenue by Genre")
        genre_rev = filtered_df.groupby('genre')['net_revenue'].sum().sort_values(ascending=False)
        
        fig = go.Figure(data=[go.Bar(
            x=genre_rev.index,
            y=genre_rev.values,
            marker=dict(
                color=genre_rev.values,
                colorscale='Viridis',
                showscale=True
            ),
            text=genre_rev.values.round(0),
            textposition='auto'
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Genre",
            yaxis_title="Revenue ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Revenue by Region Pie Chart
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        st.markdown("### 🌍 Revenue Distribution by Region")
        region_rev = filtered_df.groupby('region')['net_revenue'].sum()
        
        fig = go.Figure(data=[go.Pie(
            labels=region_rev.index,
            values=region_rev.values,
            hole=0.3,
            textposition='inside',
            textinfo='label+percent'
        )])
        
        fig.update_layout(
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_chart4:
        st.markdown("### 🏢 Revenue by Publisher")
        pub_rev = filtered_df.groupby('publisher')['net_revenue'].sum().sort_values(ascending=False).head(10)
        
        fig = go.Figure(data=[go.Bar(
            y=pub_rev.index,
            x=pub_rev.values,
            orientation='h',
            marker=dict(color='#ff7f0e'),
            text=pub_rev.values.round(0),
            textposition='auto'
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Revenue ($)",
            yaxis_title="Publisher",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

# ===========================
# TAB 2: TIME & SEASONALITY
# ===========================
with tab2:
    st.markdown("# 📈 Time & Seasonality Analysis")
    
    col_ts1, col_ts2 = st.columns(2)
    
    with col_ts1:
        st.markdown("### 📅 Daily Active Users (DAU) Trend")
        daily_users = filtered_df.groupby('purchase_date')['customer_id'].count().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_users['purchase_date'],
            y=daily_users['customer_id'],
            mode='lines',
            name='DAU',
            line=dict(color='#2ca02c', width=2),
            fill='tozeroy',
            fillcolor='rgba(44, 160, 44, 0.2)'
        ))
        
        fig.update_layout(
            title="",
            xaxis_title="Date",
            yaxis_title="Active Users",
            hovermode='x unified',
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_ts2:
        st.markdown("### 📊 Monthly Active Users (MAU) Trend")
        monthly_users = filtered_df.groupby('year_month')['customer_id'].nunique().reset_index().sort_values('year_month')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_users['year_month'],
            y=monthly_users['customer_id'],
            mode='lines+markers',
            name='MAU',
            line=dict(color='#1f77d2', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(31, 119, 210, 0.2)'
        ))
        
        fig.update_layout(
            title="",
            xaxis_title="Month",
            yaxis_title="Monthly Active Users",
            hovermode='x unified',
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Seasonal Heatmap
    st.markdown("### 🔥 Monthly Revenue Heatmap by Region")
    
    # Create pivot table for heatmap
    filtered_df['month'] = pd.to_datetime(filtered_df['year_month']).dt.month
    heatmap_data = filtered_df.pivot_table(
        values='net_revenue',
        index='region',
        columns='month',
        aggfunc='sum'
    )
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        y=heatmap_data.index,
        colorscale='RdYlGn',
        colorbar=dict(title="Revenue ($)")
    ))
    
    fig.update_layout(
        title="",
        xaxis_title="Month",
        yaxis_title="Region",
        template='plotly_dark' if theme_mode else 'plotly',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Day of week analysis
    col_dow1, col_dow2 = st.columns(2)
    
    with col_dow1:
        st.markdown("### 📆 Revenue by Day of Week")
        filtered_df['day_of_week'] = filtered_df['purchase_date'].dt.day_name()
        dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_rev = filtered_df.groupby('day_of_week')['net_revenue'].sum().reindex(dow_order)
        
        fig = go.Figure(data=[go.Bar(
            x=dow_rev.index,
            y=dow_rev.values,
            marker=dict(color=['#1f77d2' if x in ['Saturday', 'Sunday'] else '#ff7f0e' for x in dow_rev.index])
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Day of Week",
            yaxis_title="Revenue ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_dow2:
        st.markdown("### 🎮 Genre Performance by Month")
        genre_monthly = filtered_df.pivot_table(
            values='net_revenue',
            index='year_month',
            columns='genre',
            aggfunc='sum'
        ).fillna(0)
        
        fig = go.Figure()
        for genre in genre_monthly.columns:
            fig.add_trace(go.Scatter(
                x=genre_monthly.index,
                y=genre_monthly[genre],
                mode='lines+markers',
                name=genre
            ))
        
        fig.update_layout(
            title="",
            xaxis_title="Month",
            yaxis_title="Revenue ($)",
            hovermode='x unified',
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

# ===========================
# TAB 3: PRODUCT & PRICING
# ===========================
with tab3:
    st.markdown("# 🎯 Product & Pricing Analysis")
    
    col_pp1, col_pp2 = st.columns(2)
    
    with col_pp1:
        st.markdown("### 💰 Average Price by Genre")
        genre_price = filtered_df.groupby('genre')['avg_game_price'].mean().sort_values(ascending=False)
        
        fig = go.Figure(data=[go.Bar(
            x=genre_price.index,
            y=genre_price.values,
            marker=dict(color='#ff7f0e'),
            text=[f"${x:.2f}" for x in genre_price.values],
            textposition='auto'
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Genre",
            yaxis_title="Average Price ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_pp2:
        st.markdown("### 🏷️ Discount Impact on Sales")
        discount_bins = pd.cut(filtered_df['discount_pct'], bins=5)
        discount_impact = filtered_df.groupby(discount_bins)[['net_revenue', 'games_purchased']].agg({
            'net_revenue': 'sum',
            'games_purchased': 'mean'
        }).reset_index()
        discount_impact['discount_range'] = discount_impact['discount_pct'].astype(str)
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(x=discount_impact['discount_range'], y=discount_impact['net_revenue'], name='Revenue', marker=dict(color='#1f77d2')),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=discount_impact['discount_range'], y=discount_impact['games_purchased'], name='Avg Games Purchased', line=dict(color='#ff7f0e', width=3), mode='lines+markers'),
            secondary_y=True
        )
        
        fig.update_layout(
            title="",
            xaxis_title="Discount Range (%)",
            yaxis_title="Revenue ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            hovermode='x unified',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Revenue by Genre with breakdown
    col_pp3, col_pp4 = st.columns(2)
    
    with col_pp3:
        st.markdown("### 📊 Revenue by Genre")
        genre_stats = filtered_df.groupby('genre').agg({
            'net_revenue': 'sum',
            'customer_id': 'nunique',
            'games_purchased': 'sum'
        }).sort_values('net_revenue', ascending=False)
        
        fig = go.Figure(data=[go.Pie(
            labels=genre_stats.index,
            values=genre_stats['net_revenue'],
            textposition='inside',
            textinfo='label+percent',
            marker=dict(line=dict(color='#0f1419', width=2))
        )])
        
        fig.update_layout(
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_pp4:
        st.markdown("### 🎮 Genre Performance Table")
        genre_table = filtered_df.groupby('genre').agg({
            'net_revenue': 'sum',
            'customer_id': 'nunique',
            'games_purchased': 'mean',
            'avg_game_price': 'mean'
        }).round(2)
        genre_table.columns = ['Total Revenue', 'Unique Customers', 'Avg Games/Customer', 'Avg Price']
        genre_table = genre_table.sort_values('Total Revenue', ascending=False)
        
        st.dataframe(genre_table, use_container_width=True)
    
    # Price Elasticity Analysis
    st.markdown("### 💹 Price Elasticity by Genre")
    
    price_elasticity = filtered_df.groupby('genre').agg({
        'avg_game_price': 'mean',
        'games_purchased': 'mean',
        'net_revenue': 'mean'
    }).round(2)
    price_elasticity.columns = ['Avg Price ($)', 'Games/Customer', 'Revenue/Customer']
    
    fig = go.Figure()
    
    for genre in price_elasticity.index:
        fig.add_trace(go.Scatter(
            x=[price_elasticity.loc[genre, 'Avg Price ($)']],
            y=[price_elasticity.loc[genre, 'Games/Customer']],
            mode='markers+text',
            name=genre,
            marker=dict(size=20),
            text=genre,
            textposition='top center'
        ))
    
    fig.update_layout(
        title="",
        xaxis_title="Average Price ($)",
        yaxis_title="Games per Customer",
        template='plotly_dark' if theme_mode else 'plotly',
        height=400,
        hovermode='closest'
    )
    st.plotly_chart(fig, use_container_width=True)

# ===========================
# TAB 4: REGION & PUBLISHER
# ===========================
with tab4:
    st.markdown("# 🌍 Region & Publisher Analysis")
    
    col_rp1, col_rp2 = st.columns(2)
    
    with col_rp1:
        st.markdown("### 🌎 Revenue by Continent")
        continent_rev = filtered_df.groupby('continent')['net_revenue'].sum().sort_values(ascending=False)
        
        fig = go.Figure(data=[go.Bar(
            x=continent_rev.values,
            y=continent_rev.index,
            orientation='h',
            marker=dict(color='#1f77d2'),
            text=[f"${x:,.0f}" for x in continent_rev.values],
            textposition='auto'
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Revenue ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_rp2:
        st.markdown("### 🏢 Top 10 Publishers by Revenue")
        pub_top = filtered_df.groupby('publisher')['net_revenue'].sum().sort_values(ascending=False).head(10)
        
        fig = go.Figure(data=[go.Bar(
            y=pub_top.index,
            x=pub_top.values,
            orientation='h',
            marker=dict(color='#ff7f0e'),
            text=[f"${x:,.0f}" for x in pub_top.values],
            textposition='auto'
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Revenue ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Region drill-down
    st.markdown("### 🔍 Region Hierarchy Analysis")
    
    col_rp3, col_rp4 = st.columns(2)
    
    with col_rp3:
        st.markdown("#### Revenue by Region")
        region_rev = filtered_df.groupby('region').agg({
            'net_revenue': 'sum',
            'customer_id': 'nunique',
            'games_purchased': 'mean'
        }).sort_values('net_revenue', ascending=False)
        region_rev.columns = ['Total Revenue', 'Unique Customers', 'Avg Games/Customer']
        
        st.dataframe(region_rev, use_container_width=True)
    
    with col_rp4:
        st.markdown("#### Top Publishers by Region")
        selected_region = st.selectbox("Select Region for Publisher Analysis:", filtered_df['region'].unique())
        
        region_pub = filtered_df[filtered_df['region'] == selected_region].groupby('publisher')['net_revenue'].sum().sort_values(ascending=False).head(10)
        
        fig = go.Figure(data=[go.Bar(
            x=region_pub.index,
            y=region_pub.values,
            marker=dict(color='#2ca02c')
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Publisher",
            yaxis_title="Revenue ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Publisher Performance Matrix
    st.markdown("### 📊 Publisher Performance Matrix")
    
    pub_matrix = filtered_df.groupby('publisher').agg({
        'net_revenue': 'sum',
        'customer_id': 'nunique',
        'games_purchased': 'mean',
        'avg_game_price': 'mean'
    }).round(2)
    pub_matrix['Revenue/Customer'] = (pub_matrix['net_revenue'] / pub_matrix['customer_id']).round(2)
    pub_matrix = pub_matrix.sort_values('net_revenue', ascending=False).head(15)
    
    fig = go.Figure()
    
    for publisher in pub_matrix.index:
        fig.add_trace(go.Scatter(
            x=[pub_matrix.loc[publisher, 'avg_game_price']],
            y=[pub_matrix.loc[publisher, 'net_revenue']],
            mode='markers+text',
            name=publisher,
            marker=dict(size=15, opacity=0.7),
            text=publisher,
            textposition='top center'
        ))
    
    fig.update_layout(
        title="",
        xaxis_title="Average Game Price ($)",
        yaxis_title="Total Revenue ($)",
        template='plotly_dark' if theme_mode else 'plotly',
        height=400,
        hovermode='closest'
    )
    st.plotly_chart(fig, use_container_width=True)

# ===========================
# TAB 5: CUSTOMER & DEMOGRAPHICS
# ===========================
with tab5:
    st.markdown("# 👥 Customer & Demographics Analysis")
    
    col_cd1, col_cd2 = st.columns(2)
    
    with col_cd1:
        st.markdown("### 📊 Revenue by Age Group")
        age_rev = filtered_df.groupby('age_group')['net_revenue'].sum().sort_values(ascending=False)
        
        fig = go.Figure(data=[go.Bar(
            x=age_rev.index,
            y=age_rev.values,
            marker=dict(color='#1f77d2'),
            text=[f"${x:,.0f}" for x in age_rev.values],
            textposition='auto'
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Age Group",
            yaxis_title="Revenue ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_cd2:
        st.markdown("### 👤 Customer Count by Age Group")
        age_count = filtered_df.groupby('age_group')['customer_id'].nunique().sort_values(ascending=False)
        
        fig = go.Figure(data=[go.Pie(
            labels=age_count.index,
            values=age_count.values,
            textposition='inside',
            textinfo='label+percent'
        )])
        
        fig.update_layout(
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # RFM Segmentation
    st.markdown("### 🎯 RFM Customer Segmentation")
    
    # Calculate RFM scores
    rfm_data = filtered_df.groupby('customer_id').agg({
        'purchase_date': 'max',
        'games_purchased': 'sum',
        'net_revenue': 'sum'
    }).reset_index()
    
    rfm_data.columns = ['customer_id', 'last_purchase', 'frequency', 'monetary']
    
    # Recency (days since last purchase)
    rfm_data['recency'] = (filtered_df['purchase_date'].max() - rfm_data['last_purchase']).dt.days
    
    # Scoring (1-5, where 5 is best for R and F/M)
    rfm_data['r_score'] = pd.qcut(rfm_data['recency'], 5, labels=[5, 4, 3, 2, 1], duplicates='drop')
    rfm_data['f_score'] = pd.qcut(rfm_data['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    rfm_data['m_score'] = pd.qcut(rfm_data['monetary'], 5, labels=[1, 2, 3, 4, 5], duplicates='drop')
    
    rfm_data['rfm_segment'] = ''
    
    # Segmentation logic
    def get_segment(r, f, m):
        r, f, m = int(r), int(f), int(m)
        if r >= 4 and f >= 4 and m >= 4:
            return 'Champions'
        elif r >= 3 and f >= 3 and m >= 3:
            return 'Loyal Customers'
        elif r >= 4 and f <= 2:
            return 'At Risk'
        elif r <= 2 and f >= 3:
            return 'Churned'
        elif r >= 3 and f <= 2:
            return 'Need Attention'
        else:
            return 'Potential'
    
    rfm_data['rfm_segment'] = rfm_data.apply(lambda x: get_segment(x['r_score'], x['f_score'], x['m_score']), axis=1)
    
    # RFM visualization
    col_rfm1, col_rfm2 = st.columns(2)
    
    with col_rfm1:
        st.markdown("#### Customer Segments Distribution")
        segment_count = rfm_data['rfm_segment'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=segment_count.index,
            values=segment_count.values,
            textposition='inside',
            textinfo='label+percent',
            marker=dict(colors=['#2ca02c', '#1f77d2', '#ff7f0e', '#d62728', '#9467bd', '#8c564b'])
        )])
        
        fig.update_layout(
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_rfm2:
        st.markdown("#### RFM Segment Value")
        segment_value = rfm_data.groupby('rfm_segment')['monetary'].sum().sort_values(ascending=False)
        
        fig = go.Figure(data=[go.Bar(
            y=segment_value.index,
            x=segment_value.values,
            orientation='h',
            marker=dict(color=['#2ca02c', '#1f77d2', '#ff7f0e', '#d62728', '#9467bd', '#8c564b'][:len(segment_value)])
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Total Value ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # RFM Segment Insights
    st.markdown("#### 💡 Segment Insights & Recommendations")
    
    for segment in ['Champions', 'Loyal Customers', 'At Risk', 'Churned', 'Need Attention', 'Potential']:
        segment_data = rfm_data[rfm_data['rfm_segment'] == segment]
        if len(segment_data) > 0:
            avg_value = segment_data['monetary'].mean()
            count = len(segment_data)
            
            if segment == 'Champions':
                insight = f"🏆 {count} customers generating ${count * avg_value:,.0f}. VIP treatment and exclusive perks essential."
            elif segment == 'Loyal Customers':
                insight = f"👑 {count} customers with ${count * avg_value:,.0f} value. Retention programs and upsell opportunities."
            elif segment == 'At Risk':
                insight = f"⚠️ {count} customers showing decline. Win-back campaigns and special offers needed."
            elif segment == 'Churned':
                insight = f"❌ {count} customers lost. Re-engagement campaigns and surveys to understand churn reasons."
            elif segment == 'Need Attention':
                insight = f"📌 {count} customers recently inactive. Engagement campaigns and personalized offers."
            else:
                insight = f"🌱 {count} potential customers with ${count * avg_value:,.0f} value. Nurture and convert strategies."
            
            st.markdown(f"""
            <div class="insight-card">
                <strong>{segment}</strong><br>
                {insight}
            </div>
            """, unsafe_allow_html=True)
    
    # Demographic breakdown
    st.markdown("---")
    st.markdown("### 📈 Demographic Performance Table")
    
    demo_table = filtered_df.groupby('age_group').agg({
        'customer_id': 'nunique',
        'net_revenue': 'sum',
        'games_purchased': 'mean',
        'playtime_hours': 'mean',
        'avg_game_price': 'mean'
    }).round(2)
    demo_table.columns = ['Unique Customers', 'Total Revenue', 'Avg Games/Customer', 'Avg Playtime (hrs)', 'Avg Price ($)']
    demo_table = demo_table.sort_values('Total Revenue', ascending=False)
    
    st.dataframe(demo_table, use_container_width=True)

# ===========================
# TAB 6: PREDICTIVE ANALYSIS
# ===========================
with tab6:
    st.markdown("# 🔮 Predictive Analysis")
    
    col_pred1, col_pred2 = st.columns(2)
    
    with col_pred1:
        st.markdown("### 📊 Churn Prediction Distribution")
        
        fig = go.Figure(data=[go.Pie(
            labels=filtered_churn['predicted_churn_flag'].value_counts().index,
            values=filtered_churn['predicted_churn_flag'].value_counts().values,
            marker=dict(colors=['#2ca02c', '#ff7f0e', '#d62728'])
        )])
        
        fig.update_layout(
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_pred2:
        st.markdown("### ⚠️ Churn Probability Distribution")
        
        fig = go.Figure(data=[go.Histogram(
            x=filtered_churn['churn_probability'],
            nbinsx=20,
            marker=dict(color='#ff7f0e')
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Churn Probability",
            yaxis_title="Customer Count",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 90-Day Revenue Forecast
    st.markdown("### 📈 90-Day Revenue Forecast by Genre & Region")
    
    col_forecast1, col_forecast2 = st.columns(2)
    
    with col_forecast1:
        forecast_genre = revenue_forecast.groupby('genre')['forecasted_revenue_90d'].sum().sort_values(ascending=False)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=forecast_genre.index,
            y=forecast_genre.values,
            name='Forecast',
            marker=dict(color='#1f77d2'),
            text=[f"${x:,.0f}" for x in forecast_genre.values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="",
            xaxis_title="Genre",
            yaxis_title="Forecasted Revenue ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_forecast2:
        forecast_region = revenue_forecast.groupby('region')['forecasted_revenue_90d'].sum().sort_values(ascending=False)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=forecast_region.index,
            y=forecast_region.values,
            name='Forecast',
            marker=dict(color='#ff7f0e'),
            text=[f"${x:,.0f}" for x in forecast_region.values],
            textposition='auto'
        ))
        
        fig.update_layout(
            title="",
            xaxis_title="Region",
            yaxis_title="Forecasted Revenue ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False,
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Forecast with confidence intervals
    st.markdown("### 🎯 Revenue Forecast with Confidence Intervals")
    
    forecast_viz = revenue_forecast.groupby('region').agg({
        'forecasted_revenue_90d': 'sum',
        'forecast_low': 'sum',
        'forecast_high': 'sum'
    }).sort_values('forecasted_revenue_90d', ascending=False)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=forecast_viz.index,
        y=forecast_viz['forecasted_revenue_90d'],
        name='Forecast',
        marker=dict(color='#1f77d2')
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_viz.index,
        y=forecast_viz['forecast_high'],
        fill=None,
        mode='lines',
        line_color='rgba(0,0,0,0)',
        showlegend=False,
        name='Upper Bound'
    ))
    
    fig.add_trace(go.Scatter(
        x=forecast_viz.index,
        y=forecast_viz['forecast_low'],
        fill='tonexty',
        mode='lines',
        line_color='rgba(0,0,0,0)',
        name='Confidence Range',
        fillcolor='rgba(31, 119, 210, 0.2)'
    ))
    
    fig.update_layout(
        title="",
        xaxis_title="Region",
        yaxis_title="Revenue ($)",
        template='plotly_dark' if theme_mode else 'plotly',
        hovermode='x unified',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Churn by Demographics
    st.markdown("### 👥 Churn Risk by Demographics")
    
    col_churn1, col_churn2 = st.columns(2)
    
    with col_churn1:
        st.markdown("#### Churn by Genre")
        churn_genre = filtered_churn.groupby('genre')['churn_probability'].mean().sort_values(ascending=False)
        
        fig = go.Figure(data=[go.Bar(
            x=churn_genre.index,
            y=churn_genre.values * 100,
            marker=dict(color='#ff7f0e')
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Genre",
            yaxis_title="Avg Churn Probability (%)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_churn2:
        st.markdown("#### Churn by Publisher")
        churn_pub = filtered_churn.groupby('publisher')['churn_probability'].mean().sort_values(ascending=False).head(10)
        
        fig = go.Figure(data=[go.Bar(
            y=churn_pub.index,
            x=churn_pub.values * 100,
            orientation='h',
            marker=dict(color='#d62728')
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Avg Churn Probability (%)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # What-If Simulator
    st.markdown("---")
    st.markdown("### 🎮 What-If Scenario Simulator")
    
    st.info("Adjust parameters below to simulate different business scenarios and see their impact on key metrics.")
    
    col_sim1, col_sim2, col_sim3 = st.columns(3)
    
    with col_sim1:
        sim_churn_reduction = st.slider(
            "Churn Reduction %",
            min_value=0,
            max_value=30,
            value=5,
            step=1,
            help="Reduction in customer churn rate"
        )
    
    with col_sim2:
        sim_price_increase = st.slider(
            "Price Increase %",
            min_value=0,
            max_value=20,
            value=5,
            step=1,
            help="Increase in average game price"
        )
    
    with col_sim3:
        sim_mau_growth = st.slider(
            "MAU Growth %",
            min_value=0,
            max_value=25,
            value=8,
            step=1,
            help="Projected increase in monthly active users"
        )
    
    # Calculate scenario impact
    current_revenue = filtered_df['net_revenue'].sum()
    current_churn = (filtered_df[filtered_df['churn_risk'] == 'High'].shape[0] / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    current_mau = filtered_df.groupby('year_month')['customer_id'].nunique().mean()
    
    # Scenario calculations
    churn_impact = (sim_churn_reduction / 100) * current_churn
    price_impact = (sim_price_increase / 100) * current_revenue
    mau_impact = (sim_mau_growth / 100) * current_revenue
    
    # Total impact
    scenario_revenue = current_revenue + price_impact + mau_impact
    scenario_churn = max(current_churn - churn_impact, 0)
    scenario_mau = current_mau * (1 + sim_mau_growth / 100)
    scenario_clv = scenario_revenue / scenario_mau if scenario_mau > 0 else 0
    
    col_impact1, col_impact2, col_impact3, col_impact4 = st.columns(4)
    
    with col_impact1:
        st.metric(
            "Scenario Revenue",
            f"${scenario_revenue:,.0f}",
            f"+${scenario_revenue - current_revenue:,.0f}"
        )
    
    with col_impact2:
        st.metric(
            "Scenario Churn Rate",
            f"{scenario_churn:.1f}%",
            f"{scenario_churn - current_churn:.1f}%"
        )
    
    with col_impact3:
        st.metric(
            "Scenario MAU",
            f"{int(scenario_mau):,.0f}",
            f"+{int(scenario_mau - current_mau):,.0f}"
        )
    
    with col_impact4:
        st.metric(
            "Scenario CLV",
            f"${scenario_clv:.2f}",
            f"vs ${current_revenue/current_mau:.2f}"
        )
    
    # Comparison chart
    scenarios_data = {
        'Metric': ['Revenue', 'Churn Rate (%)', 'MAU', 'CLV'],
        'Current': [current_revenue, current_churn, current_mau, current_revenue/current_mau],
        'Scenario': [scenario_revenue, scenario_churn, scenario_mau, scenario_clv]
    }
    
    fig = go.Figure(data=[
        go.Bar(name='Current', x=scenarios_data['Metric'][:2], y=scenarios_data['Current'][:2]),
        go.Bar(name='Scenario', x=scenarios_data['Metric'][:2], y=scenarios_data['Scenario'][:2])
    ])
    
    fig.update_layout(
        title="",
        barmode='group',
        template='plotly_dark' if theme_mode else 'plotly',
        height=400,
        xaxis_title="Metric",
        yaxis_title="Value"
    )
    st.plotly_chart(fig, use_container_width=True)

# ===========================
# TAB 7: SELLER PERFORMANCE
# ===========================
with tab7:
    st.markdown("# ⭐ Seller (Publisher) Performance")
    
    # Publisher KPIs
    st.markdown("### 🏆 Top Publishers Performance Scorecard")
    
    publisher_stats = filtered_df.groupby('publisher').agg({
        'net_revenue': 'sum',
        'customer_id': 'nunique',
        'games_purchased': 'sum',
        'avg_game_price': 'mean',
        'playtime_hours': 'mean'
    }).round(2)
    
    publisher_stats['Revenue/Customer'] = (publisher_stats['net_revenue'] / publisher_stats['customer_id']).round(2)
    publisher_stats['Conversion'] = (publisher_stats['customer_id'] / len(filtered_df) * 100).round(2)
    
    publisher_stats = publisher_stats.sort_values('net_revenue', ascending=False)
    publisher_stats.columns = ['Total Revenue', 'Unique Customers', 'Total Games', 'Avg Price', 'Avg Playtime', 'Revenue/Customer', 'Conversion %']
    
    st.dataframe(publisher_stats.head(15), use_container_width=True)
    
    # Growth Analysis
    col_seller1, col_seller2 = st.columns(2)
    
    with col_seller1:
        st.markdown("### 📈 Publisher Revenue Trend")
        pub_selected = st.selectbox("Select Publisher:", filtered_df['publisher'].unique())
        
        pub_trend = filtered_df[filtered_df['publisher'] == pub_selected].groupby('year_month')['net_revenue'].sum().reset_index().sort_values('year_month')
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=pub_trend['year_month'],
            y=pub_trend['net_revenue'],
            mode='lines+markers',
            name=pub_selected,
            line=dict(color='#1f77d2', width=3),
            fill='tozeroy'
        ))
        
        fig.update_layout(
            title="",
            xaxis_title="Month",
            yaxis_title="Revenue ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_seller2:
        st.markdown("### 🎯 Publisher Genre Mix")
        pub_genre = filtered_df[filtered_df['publisher'] == pub_selected].groupby('genre')['net_revenue'].sum()
        
        fig = go.Figure(data=[go.Pie(
            labels=pub_genre.index,
            values=pub_genre.values,
            textposition='inside',
            textinfo='label+percent'
        )])
        
        fig.update_layout(
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Market Share
    st.markdown("### 🥇 Market Share Analysis")
    
    col_mkt1, col_mkt2 = st.columns(2)
    
    with col_mkt1:
        st.markdown("#### Revenue Market Share")
        mkt_share = filtered_df.groupby('publisher')['net_revenue'].sum().sort_values(ascending=False)
        top_pubs = mkt_share.head(10)
        
        fig = go.Figure(data=[go.Pie(
            labels=top_pubs.index,
            values=top_pubs.values,
            textposition='inside',
            textinfo='label+percent',
            hole=0.3
        )])
        
        fig.update_layout(
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_mkt2:
        st.markdown("#### Customer Acquisition by Publisher")
        cust_acq = filtered_df.groupby('publisher')['customer_id'].nunique().sort_values(ascending=False).head(10)
        
        fig = go.Figure(data=[go.Bar(
            y=cust_acq.index,
            x=cust_acq.values,
            orientation='h',
            marker=dict(color='#ff7f0e')
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Unique Customers",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Publisher Rating Matrix
    st.markdown("### 📊 Publisher Performance Matrix")
    
    pub_matrix_data = filtered_df.groupby('publisher').agg({
        'net_revenue': 'sum',
        'customer_id': 'nunique',
        'playtime_hours': 'mean',
        'churn_risk': lambda x: (x == 'High').sum() / len(x) * 100
    }).round(2)
    pub_matrix_data.columns = ['Revenue', 'Customers', 'Avg Playtime', 'Churn Rate']
    pub_matrix_data = pub_matrix_data[pub_matrix_data['Revenue'] > pub_matrix_data['Revenue'].quantile(0.25)]
    
    fig = go.Figure()
    
    for pub in pub_matrix_data.index:
        fig.add_trace(go.Scatter(
            x=[pub_matrix_data.loc[pub, 'Avg Playtime']],
            y=[pub_matrix_data.loc[pub, 'Churn Rate']],
            mode='markers+text',
            name=pub,
            marker=dict(size=20, opacity=0.7),
            text=pub,
            textposition='top center'
        ))
    
    fig.update_layout(
        title="",
        xaxis_title="Average Playtime (hours)",
        yaxis_title="Churn Rate (%)",
        template='plotly_dark' if theme_mode else 'plotly',
        height=400,
        hovermode='closest'
    )
    st.plotly_chart(fig, use_container_width=True)

# ===========================
# TAB 8: PARETO ANALYSIS
# ===========================
with tab8:
    st.markdown("# 📉 Pareto Analysis (80/20 Rule)")
    
    col_pareto1, col_pareto2 = st.columns(2)
    
    # Pareto by Publishers
    with col_pareto1:
        st.markdown("### 🏢 Pareto Analysis by Publishers")
        
        pub_revenue = filtered_df.groupby('publisher')['net_revenue'].sum().sort_values(ascending=False)
        pub_cumsum = pub_revenue.cumsum()
        pub_cumsum_pct = (pub_cumsum / pub_cumsum.iloc[-1] * 100)
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(x=pub_revenue.index[:20], y=pub_revenue.values[:20], name='Revenue', marker=dict(color='#1f77d2')),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=pub_revenue.index[:20], y=pub_cumsum_pct[:20], name='Cumulative %', line=dict(color='#ff7f0e', width=3), mode='lines+markers'),
            secondary_y=True
        )
        
        fig.update_layout(
            title="",
            xaxis_title="Publisher",
            yaxis_title="Revenue ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            hovermode='x unified'
        )
        fig.update_xaxes(tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
    
    # Pareto by Genres
    with col_pareto2:
        st.markdown("### 🎯 Pareto Analysis by Genres")
        
        genre_revenue = filtered_df.groupby('genre')['net_revenue'].sum().sort_values(ascending=False)
        genre_cumsum = genre_revenue.cumsum()
        genre_cumsum_pct = (genre_cumsum / genre_cumsum.iloc[-1] * 100)
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(x=genre_revenue.index, y=genre_revenue.values, name='Revenue', marker=dict(color='#2ca02c')),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=genre_revenue.index, y=genre_cumsum_pct, name='Cumulative %', line=dict(color='#d62728', width=3), mode='lines+markers'),
            secondary_y=True
        )
        
        fig.update_layout(
            title="",
            xaxis_title="Genre",
            yaxis_title="Revenue ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Pareto by Regions
    col_pareto3, col_pareto4 = st.columns(2)
    
    with col_pareto3:
        st.markdown("### 🌍 Pareto Analysis by Regions")
        
        region_revenue = filtered_df.groupby('region')['net_revenue'].sum().sort_values(ascending=False)
        region_cumsum = region_revenue.cumsum()
        region_cumsum_pct = (region_cumsum / region_cumsum.iloc[-1] * 100)
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(x=region_revenue.index, y=region_revenue.values, name='Revenue', marker=dict(color='#ff7f0e')),
            secondary_y=False
        )
        
        fig.add_trace(
            go.Scatter(x=region_revenue.index, y=region_cumsum_pct, name='Cumulative %', line=dict(color='#1f77d2', width=3), mode='lines+markers'),
            secondary_y=True
        )
        
        fig.update_layout(
            title="",
            xaxis_title="Region",
            yaxis_title="Revenue ($)",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_pareto4:
        st.markdown("### 👥 Pareto Analysis by Customers")
        
        cust_revenue = filtered_df.groupby('customer_id')['net_revenue'].sum().sort_values(ascending=False)
        cust_cumsum = cust_revenue.cumsum()
        cust_cumsum_pct = (cust_cumsum / cust_cumsum.iloc[-1] * 100)
        
        # Find 80/20 point
        twenty_pct_idx = (cust_cumsum_pct >= 80).idxmax()
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=range(len(cust_cumsum_pct)),
            y=cust_cumsum_pct,
            mode='lines',
            name='Cumulative Revenue %',
            line=dict(color='#1f77d2', width=3),
            fill='tozeroy'
        ))
        
        fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="80% Revenue")
        fig.add_vline(x=twenty_pct_idx, line_dash="dash", line_color="orange", annotation_text=f"Top {((twenty_pct_idx+1)/len(cust_cumsum_pct)*100):.1f}% Customers")
        
        fig.update_layout(
            title="",
            xaxis_title="Customer Rank",
            yaxis_title="Cumulative Revenue %",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Insights
    st.markdown("---")
    st.markdown("### 💡 Pareto Insights")
    
    # Calculate key metrics
    total_pub = filtered_df['publisher'].nunique()
    top_20_pub_count = int(total_pub * 0.2)
    top_20_pub_revenue = filtered_df.groupby('publisher')['net_revenue'].sum().sort_values(ascending=False).head(top_20_pub_count).sum()
    total_revenue_all = filtered_df['net_revenue'].sum()
    pub_concentration = (top_20_pub_revenue / total_revenue_all * 100)
    
    total_genre = filtered_df['genre'].nunique()
    top_20_genre_count = int(total_genre * 0.2)
    top_20_genre_revenue = filtered_df.groupby('genre')['net_revenue'].sum().sort_values(ascending=False).head(top_20_genre_count).sum()
    genre_concentration = (top_20_genre_revenue / total_revenue_all * 100)
    
    col_insight1, col_insight2, col_insight3 = st.columns(3)
    
    with col_insight1:
        st.markdown(f"""
        <div class="insight-card">
            <strong>🏢 Publisher Concentration</strong><br>
            Top 20% of publishers ({top_20_pub_count} publishers) generate {pub_concentration:.1f}% of revenue. 
            {("Highly concentrated - focus on top performers." if pub_concentration > 75 else "Balanced distribution across publishers.")}
        </div>
        """, unsafe_allow_html=True)
    
    with col_insight2:
        st.markdown(f"""
        <div class="insight-card">
            <strong>🎯 Genre Concentration</strong><br>
            Top 20% of genres ({top_20_genre_count} genres) generate {genre_concentration:.1f}% of revenue.
            {("Strong focus on few genres" if genre_concentration > 75 else "Diverse genre portfolio")}
        </div>
        """, unsafe_allow_html=True)
    
    with col_insight3:
        top_10_pct_customers = int(len(filtered_df) * 0.1)
        top_10_customer_revenue = filtered_df.groupby('customer_id')['net_revenue'].sum().sort_values(ascending=False).head(top_10_pct_customers).sum()
        customer_concentration = (top_10_customer_revenue / total_revenue_all * 100)
        
        st.markdown(f"""
        <div class="insight-card">
            <strong>👥 Customer Concentration</strong><br>
            Top 10% of customers generate {customer_concentration:.1f}% of revenue.
            {("VIP customer focus essential" if customer_concentration > 60 else "Healthy customer distribution")}
        </div>
        """, unsafe_allow_html=True)

# ===========================
# TAB 9: COHORT RETENTION
# ===========================
with tab9:
    st.markdown("# 🔄 Cohort Retention Analysis")
    
    # Create cohorts based on first purchase month
    cohort_data = filtered_df.copy()
    cohort_data['cohort'] = cohort_data.groupby('customer_id')['purchase_date'].transform('min').dt.to_period('M').astype(str)
    cohort_data['period'] = cohort_data['purchase_date'].dt.to_period('M').astype(str)
    
    # Calculate cohort size and retention
    cohorts = cohort_data.groupby('cohort')['customer_id'].nunique()
    
    cohort_retention = cohort_data.groupby(['cohort', 'period'])['customer_id'].nunique().unstack(fill_value=0)
    cohort_retention_pct = cohort_retention.div(cohorts, axis=0) * 100
    
    col_cohort1, col_cohort2 = st.columns(2)
    
    with col_cohort1:
        st.markdown("### 📊 Cohort Size")
        
        fig = go.Figure(data=[go.Bar(
            x=cohorts.index,
            y=cohorts.values,
            marker=dict(color='#1f77d2')
        )])
        
        fig.update_layout(
            title="",
            xaxis_title="Cohort (Month)",
            yaxis_title="Customer Count",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_cohort2:
        st.markdown("### 🔥 Cohort Retention Heatmap")
        
        # Limit to recent cohorts for readability
        cohort_retention_viz = cohort_retention_pct.iloc[-10:, :10]
        
        fig = go.Figure(data=go.Heatmap(
            z=cohort_retention_viz.values,
            x=range(len(cohort_retention_viz.columns)),
            y=cohort_retention_viz.index,
            colorscale='RdYlGn',
            colorbar=dict(title="Retention %")
        ))
        
        fig.update_layout(
            title="",
            xaxis_title="Period",
            yaxis_title="Cohort",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Genre-based cohort retention
    st.markdown("### 🎯 Cohort Retention by Genre")
    
    genre_select = st.selectbox("Select Genre for Cohort Analysis:", filtered_df['genre'].unique())
    
    genre_cohort = cohort_data[cohort_data['genre'] == genre_select].copy()
    genre_cohorts = genre_cohort.groupby('cohort')['customer_id'].nunique()
    genre_retention = genre_cohort.groupby(['cohort', 'period'])['customer_id'].nunique().unstack(fill_value=0)
    genre_retention_pct = genre_retention.div(genre_cohorts, axis=0) * 100
    
    if len(genre_retention_pct) > 0:
        # Plot retention curves for top cohorts
        fig = go.Figure()
        
        for cohort in genre_retention_pct.index[-5:]:  # Last 5 cohorts
            fig.add_trace(go.Scatter(
                x=range(len(genre_retention_pct.columns)),
                y=genre_retention_pct.loc[cohort],
                mode='lines+markers',
                name=str(cohort)
            ))
        
        fig.update_layout(
            title="",
            xaxis_title="Period",
            yaxis_title="Retention %",
            template='plotly_dark' if theme_mode else 'plotly',
            height=400,
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Retention metrics
    st.markdown("---")
    st.markdown("### 📈 Retention Metrics Summary")
    
    col_ret1, col_ret2, col_ret3 = st.columns(3)
    
    # Calculate key retention metrics
    latest_cohort = cohort_retention_pct.index[-1]
    latest_retention = cohort_retention_pct.loc[latest_cohort]
    month_1_retention = latest_retention.iloc[1] if len(latest_retention) > 1 else 100
    month_3_retention = latest_retention.iloc[3] if len(latest_retention) > 3 else latest_retention.iloc[-1]
    
    with col_ret1:
        st.metric(
            "Latest Cohort (M1 Retention)",
            f"{month_1_retention:.1f}%",
            "Healthy" if month_1_retention > 70 else "At Risk"
        )
    
    with col_ret2:
        avg_m1_retention = cohort_retention_pct.iloc[:, 1].mean() if cohort_retention_pct.shape[1] > 1 else 100
        st.metric(
            "Avg M1 Retention",
            f"{avg_m1_retention:.1f}%",
            "Strong" if avg_m1_retention > 75 else "Needs Focus"
        )
    
    with col_ret3:
        churn_risk_high = filtered_df[filtered_df['churn_risk'] == 'High'].shape[0] / len(filtered_df) * 100
        st.metric(
            "High Churn Risk %",
            f"{churn_risk_high:.1f}%",
            "Monitor" if churn_risk_high > 15 else "Good"
        )
    
    # Retention insights by demographics
    st.markdown("---")
    st.markdown("### 👥 Retention by Age Group")
    
    age_retention = filtered_df.groupby('age_group').agg({
        'retention_days': 'mean',
        'churn_risk': lambda x: (x == 'Low').sum() / len(x) * 100,
        'customer_id': 'nunique'
    }).round(2)
    age_retention.columns = ['Avg Retention Days', 'Low Risk %', 'Customer Count']
    age_retention = age_retention.sort_values('Avg Retention Days', ascending=False)
    
    st.dataframe(age_retention, use_container_width=True)

# ===========================
# TAB 10: DATA EXPLORER
# ===========================
with tab10:
    st.markdown("# 🔎 Data Explorer")
    
    # Data summary
    st.markdown("### 📊 Dataset Overview")
    
    col_explorer1, col_explorer2, col_explorer3, col_explorer4 = st.columns(4)
    
    with col_explorer1:
        st.metric("Total Records", f"{len(filtered_df):,}")
    
    with col_explorer2:
        st.metric("Unique Customers", f"{filtered_df['customer_id'].nunique():,}")
    
    with col_explorer3:
        st.metric("Date Range", f"{(filtered_df['purchase_date'].max() - filtered_df['purchase_date'].min()).days} days")
    
    with col_explorer4:
        st.metric("Avg Transaction Value", f"${filtered_df['net_revenue'].mean():.2f}")
    
    st.markdown("---")
    
    # Data table with search and filter
    st.markdown("### 🔍 Transaction Data")
    
    search_col = st.selectbox(
        "Search by column:",
        ['customer_id', 'region', 'genre', 'publisher', 'age_group']
    )
    search_term = st.text_input(f"Search {search_col}:")
    
    if search_term:
        filtered_search = filtered_df[filtered_df[search_col].astype(str).str.contains(search_term, case=False)]
    else:
        filtered_search = filtered_df
    
    display_cols = ['customer_id', 'region', 'age_group', 'genre', 'publisher', 
                    'games_purchased', 'net_revenue', 'playtime_hours', 'churn_risk', 'purchase_date']
    
    st.dataframe(
        filtered_search[display_cols].sort_values('purchase_date', ascending=False).head(500),
        use_container_width=True,
        height=500
    )
    
    # Summary statistics
    st.markdown("---")
    st.markdown("### 📈 Summary Statistics")
    
    summary_stats = filtered_df[['games_purchased', 'net_revenue', 'avg_game_price', 'playtime_hours', 'retention_days']].describe().round(2)
    
    st.dataframe(summary_stats, use_container_width=True)
    
    # Distribution charts
    st.markdown("---")
    st.markdown("### 📊 Distribution Analysis")
    
    col_dist1, col_dist2, col_dist3 = st.columns(3)
    
    with col_dist1:
        st.markdown("#### Revenue Distribution")
        fig = go.Figure(data=[go.Histogram(
            x=filtered_df['net_revenue'],
            nbinsx=50,
            marker=dict(color='#1f77d2')
        )])
        fig.update_layout(
            title="",
            xaxis_title="Revenue ($)",
            yaxis_title="Frequency",
            template='plotly_dark' if theme_mode else 'plotly',
            height=350,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_dist2:
        st.markdown("#### Playtime Distribution")
        fig = go.Figure(data=[go.Histogram(
            x=filtered_df['playtime_hours'],
            nbinsx=50,
            marker=dict(color='#ff7f0e')
        )])
        fig.update_layout(
            title="",
            xaxis_title="Playtime (hours)",
            yaxis_title="Frequency",
            template='plotly_dark' if theme_mode else 'plotly',
            height=350,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col_dist3:
        st.markdown("#### Games Purchased Distribution")
        fig = go.Figure(data=[go.Histogram(
            x=filtered_df['games_purchased'],
            nbinsx=20,
            marker=dict(color='#2ca02c')
        )])
        fig.update_layout(
            title="",
            xaxis_title="Games Purchased",
            yaxis_title="Frequency",
            template='plotly_dark' if theme_mode else 'plotly',
            height=350,
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Correlation matrix
    st.markdown("---")
    st.markdown("### 🔗 Correlation Analysis")
    
    corr_cols = ['games_purchased', 'net_revenue', 'avg_game_price', 'playtime_hours', 'retention_days']
    corr_matrix = filtered_df[corr_cols].corr()
    
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_cols,
        y=corr_cols,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values.round(2),
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))
    
    fig.update_layout(
        title="",
        template='plotly_dark' if theme_mode else 'plotly',
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

# ===========================
# FOOTER
# ===========================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; font-size: 12px; padding: 20px;">
    <p>Steam Analytics Dashboard | Data as of {}</p>
    <p>🎮 Built with Streamlit | 📊 Powered by Plotly</p>
</div>
""".format(max_date.date()), unsafe_allow_html=True)

