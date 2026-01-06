# 🎮 Steam Analytics Dashboard

**A production-ready, interactive Streamlit dashboard for comprehensive Steam gaming platform analytics and business intelligence.**

![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Plotly](https://img.shields.io/badge/Plotly-5.17+-blue?logo=plotly)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🎯 Overview

This dashboard provides Steam stakeholders with a comprehensive, interactive platform to analyze gaming revenue, user behavior, publisher performance, and make data-driven business decisions. It includes 10 distinct analysis modules with real-time filtering, predictive analytics, and advanced visualizations.

### Key Highlights:
- ✅ **10 Interactive Analysis Modules** (Executive Overview, Seasonality, Products, Region, Demographics, Predictions, Sellers, Pareto, Cohorts, Data Explorer)
- ✅ **Real-Time Responsive Filters** (6/12-month toggle, multi-select continents/regions, genre/publisher/age group/churn filters)
- ✅ **Advanced Visualizations** (Pie charts, bar charts, heatmaps, waterfall charts, pareto charts, scatter plots)
- ✅ **RFM Customer Segmentation** (6 segments with actionable insights)
- ✅ **Predictive Analytics** (90-day revenue forecasts, churn predictions)
- ✅ **What-If Scenario Simulator** (Test churn reduction, price changes, MAU growth impacts)
- ✅ **Business Insight Flashcards** (AI-generated insights for every KPI)
- ✅ **Pareto 80/20 Analysis** (Focus areas by publisher, genre, region, customer)
- ✅ **Professional Theme** (Dark mode optimized for stakeholders)

---

## 📊 Dashboard Modules

### 1. 📊 Executive Overview
The command center for stakeholders showing:
- **KPI Strips:**
  - 💰 Total Revenue
  - 📈 Revenue Growth %
  - 👥 Monthly Active Users (MAU)
  - 🎯 Unique Buyers
  - 💵 Average Revenue Per User (ARPU)
  - ⚠️ Churn Rate

- **Business Insight Cards:**
  - Revenue performance analysis with growth classification
  - User engagement trends
  - Monetization efficiency assessment
  - Retention risk evaluation

- **Key Visualizations:**
  - Monthly revenue trend (line chart)
  - Revenue by genre (bar chart)
  - Revenue distribution by region (pie chart)
  - Revenue by publisher (horizontal bar)

### 2. 📈 Time & Seasonality Analysis
Track patterns and trends over time:
- DAU (Daily Active Users) trends
- MAU (Monthly Active Users) trends
- Monthly revenue heatmap by region
- Day-of-week revenue analysis
- Genre performance by month
- Seasonal patterns identification

### 3. 🎯 Product & Pricing Analysis
Understand product performance and pricing dynamics:
- Average price by genre
- Discount impact on sales volume
- Revenue distribution across genres
- Genre performance comparison table
- Price elasticity analysis
- Games per customer by genre

### 4. 🌍 Region & Publisher Analysis
Hierarchical drill-down analysis:
- Revenue by continent
- Top 10 publishers by revenue
- Region-level breakdown
- Publisher ranking by region
- Publisher performance matrix
- Geographic concentration analysis

### 5. 👥 Customer & Demographics Analysis
Understand your customer base:
- Revenue by age group
- Customer distribution by demographics
- **RFM Segmentation:**
  - 🏆 Champions (Most valuable, high frequency)
  - 👑 Loyal Customers (Consistent value)
  - ⚠️ At Risk (Recent decline)
  - ❌ Churned (Lost customers)
  - 📌 Need Attention (Inactive recently)
  - 🌱 Potential (New, low value)

- Segment-specific recommendations
- Demographic performance metrics
- RFM distribution pie charts
- Segment value analysis

### 6. 🔮 Predictive Analysis
Machine learning insights and forecasting:
- Churn prediction distribution
- Churn probability histogram
- 90-day revenue forecast by genre
- 90-day revenue forecast by region
- Forecast confidence intervals
- Churn risk by demographics
- **What-If Scenario Simulator:**
  - Adjust churn reduction (0-30%)
  - Adjust price increases (0-20%)
  - Adjust MAU growth (0-25%)
  - See real-time impact on:
    - Scenario Revenue
    - Scenario Churn Rate
    - Scenario MAU
    - Scenario CLV (Customer Lifetime Value)

### 7. ⭐ Seller (Publisher) Performance
Track publisher success metrics:
- Top publishers performance scorecard
- Publisher revenue trends
- Publisher genre mix analysis
- Market share distribution
- Customer acquisition by publisher
- Publisher performance matrix
- Playtime vs. churn scatter plot

### 8. 📉 Pareto Analysis (80/20 Rule)
Identify focus areas for maximum ROI:
- **Publisher Concentration:** Which top publishers drive most revenue
- **Genre Concentration:** Which genres are most profitable
- **Region Concentration:** Geographic revenue distribution
- **Customer Concentration:** Top customer value concentration
- Cumulative revenue % by segment
- Actionable insights on where to focus efforts

### 9. 🔄 Cohort Retention Analysis
Track customer retention over time:
- Cohort size tracking
- Retention heatmap (percentage retained by cohort month)
- Cohort retention curves by genre
- Retention metrics by age group
- Month-1, Month-3, Month-6 retention rates
- Churn risk distribution by demographics
- Cohort-specific insights and recommendations

### 10. 🔎 Data Explorer
Raw data exploration and analysis:
- Full transaction data table with search functionality
- Filter by: customer_id, region, genre, publisher, age_group
- Summary statistics (mean, std, min, max, 25/50/75 percentiles)
- Distribution analysis:
  - Revenue distribution histogram
  - Playtime distribution histogram
  - Games purchased distribution histogram
- Correlation matrix heatmap
- Data export capabilities

---

## 🎛️ Global Filters

All filters update the dashboard in **real-time** without page reloads:

### Date Range Selection
- **6-Month Analysis** (default) - Last 6 months of data
- **12-Month Analysis** - Last 12 months of data
- **Custom Range** - Select any date range

### Geographic Filters
- **Multi-select Continents:**
  - North America
  - South America
  - Europe
  - Asia
  - Oceania

- **Multi-select Regions** (dependent on selected continents)

### Business Filters
- **Publishers:** Multi-select all publishers
- **Genres:** Multi-select all game genres
- **Age Groups:** Multi-select customer age groups
- **Churn Risk:** Filter by Low/Medium/High risk levels

### Theme Toggle
- **Dark Mode** (default, optimized for stakeholders)
- **Light Mode** (optional)

---

## 📥 Installation & Setup

### Quick Start (Recommended)

#### For Windows:
```bash
# 1. Download and extract project
# 2. Double-click quick_start.bat
# 3. Dashboard opens at http://localhost:8501
```

#### For macOS/Linux:
```bash
# 1. Download and extract project
# 2. chmod +x quick_start.sh
# 3. ./quick_start.sh
# 4. Dashboard opens at http://localhost:8501
```

### Manual Installation

#### Prerequisites:
- Python 3.8+
- pip (usually comes with Python)

#### Steps:
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Ensure all CSV files are in the current directory

# 5. Run dashboard
streamlit run steam_dashboard.py

# 6. Open browser to http://localhost:8501
```

---

## 📦 Required Data Files

Ensure all CSV files are in the **same directory** as `steam_dashboard.py`:

| File | Purpose | Records |
|------|---------|---------|
| `data_set.csv` | Base transaction data | 500 |
| `steam_ARPU_table.csv` | Monthly ARPU calculations | 12 |
| `steam_CLV_table.csv` | Customer Lifetime Value | 500 |
| `steam_DAU_table.csv` | Daily Active Users | 279 |
| `steam_MAU_table.csv` | Monthly Active Users | 12 |
| `steam_churn_predictions.csv` | Churn predictions | 500 |
| `steam_revenue_forecast_90d.csv` | 90-day revenue forecast | 26 |
| `steam_scenario_parameters.csv` | Scenario simulation parameters | 7 |

---

## 🚀 Deployment Options

### Option 1: Local Development
```bash
streamlit run steam_dashboard.py
```
Best for: Testing, development, local stakeholder demos

### Option 2: Streamlit Cloud (Recommended for Production)
1. Push code to GitHub
2. Go to https://streamlit.io/cloud
3. Connect repository and deploy
4. Share public URL with stakeholders

### Option 3: Docker
```bash
docker build -t steam-dashboard .
docker run -p 8501:8501 steam-dashboard
```

### Option 4: AWS/Azure/Google Cloud
See `SETUP_GUIDE.md` for detailed cloud deployment instructions

---

## 📊 Key Features Explained

### RFM Segmentation
**R**ecency × **F**requency × **M**onetary scoring creates 6 customer segments:

| Segment | Description | Strategy |
|---------|-------------|----------|
| 🏆 Champions | High R, F, M | VIP treatment, exclusive perks |
| 👑 Loyal | Good R, F, M | Retention programs, upsells |
| ⚠️ At Risk | Low R, High F | Win-back campaigns |
| ❌ Churned | Low R, Low F | Re-engagement surveys |
| 📌 Need Attention | Low R, Med F | Engagement campaigns |
| 🌱 Potential | High R, Low F | Nurture strategies |

### Pareto Analysis (80/20)
Identifies that ~80% of results come from ~20% of effort:
- Top 20% of publishers drive X% of revenue
- Top 20% of genres drive Y% of revenue
- Top 10% of customers drive Z% of revenue

### What-If Simulator
Test business scenarios:
1. Adjust churn reduction (reduce customer loss)
2. Adjust price increase (test pricing power)
3. Adjust MAU growth (test marketing investments)
4. See impact on Revenue, Churn, MAU, CLV in real-time

### Business Insight Flashcards
AI-generated insights for every KPI:
- Revenue cards: "Declining: -5% vs last period. Immediate action needed."
- MAU cards: "Explosive growth: +18% MAU. Exceptional user acquisition."
- ARPU cards: "Premium performance: $185 ARPU. High monetization efficiency."
- Churn cards: "Excellent retention: 8% churn. Customer loyalty strong."

---

## 🔧 Customization

### Modify Insight Logic
Edit insight generation functions (lines 140-200):
```python
def get_revenue_insight(total_revenue, prev_revenue, growth_pct):
    # Customize thresholds and messaging
    if growth_pct > 15:
        return "Your custom insight message"
```

### Add New Visualizations
Add new charts in any tab:
```python
fig = go.Figure(data=[go.Bar(...)])
fig.update_layout(template='plotly_dark' if theme_mode else 'plotly')
st.plotly_chart(fig, use_container_width=True)
```

### Change Color Scheme
Modify CSS in the style section:
```python
st.markdown("""
<style>
    :root {
        --primary-color: #YOUR_COLOR;
        ...
    }
</style>
""", unsafe_allow_html=True)
```

---

## 📈 Performance Optimization

- **Data Caching:** Dashboard uses @st.cache_data for instant data loads
- **Real-time Filtering:** Efficient pandas operations for <100ms filter updates
- **Lazy Loading:** Visualizations load on-demand as tabs are opened
- **Responsive Design:** Works on desktop, tablet, mobile screens

**For Large Datasets (100k+ records):**
- Use date filters to limit data range
- Consider data sampling or aggregation
- Deploy on higher-spec servers

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Data files not found | Ensure all CSVs in same directory as script |
| Slow dashboard | Clear browser cache, update pandas/plotly |
| Filters not working | Refresh page (Ctrl+Shift+R), clear cache |
| Import errors | Run `pip install --upgrade -r requirements.txt` |
| Connection errors | Check internet, restart Streamlit (`Ctrl+C`, rerun) |

---

## 📚 Documentation

- **SETUP_GUIDE.md** - Detailed setup and deployment instructions
- **This README** - Feature overview and quick start
- **Code Comments** - Inline documentation in steam_dashboard.py

---

## 🎓 Usage Tips for Stakeholders

1. **Start with Executive Overview** - Get the big picture
2. **Use Filters to Drill Down** - Select regions/genres/publishers of interest
3. **Check Predictive Analysis** - Understand future revenue and churn risks
4. **Review RFM Segments** - Understand customer base composition
5. **Explore Pareto Analysis** - Identify 80/20 focus areas
6. **Run What-If Scenarios** - Test business decisions
7. **Export Data** - Use Data Explorer to export custom reports

---

## 🔐 Security & Privacy

- All data processing happens locally
- No data sent to external services
- Browser-based, no server logs
- For production, use:
  - Streamlit Cloud authentication
  - VPN/firewall restrictions
  - Regular data backups

---

## 📞 Support

For issues, feature requests, or customization help:
1. Check SETUP_GUIDE.md for detailed troubleshooting
2. Review code comments for function explanations
3. Test locally before production deployment
4. Validate data files before deployment

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024 | Initial release with 10 modules, RFM, What-If, Pareto |
| 1.1 | TBD | Enhanced predictive models, additional metrics |
| 2.0 | TBD | Mobile optimization, real-time data sync |

---

## 📄 License

MIT License - Feel free to customize and extend for your organization's needs.

---

## 🎯 Quick Links

- [Streamlit Documentation](https://docs.streamlit.io)
- [Plotly Documentation](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/)
- [Setup Guide](./SETUP_GUIDE.md)

---

## 🚀 Next Steps

1. ✅ Download/clone the project
2. ✅ Run quick_start.sh or quick_start.bat
3. ✅ Explore all 10 analysis modules
4. ✅ Test filters and What-If simulator
5. ✅ Deploy to Streamlit Cloud
6. ✅ Share with stakeholders
7. ✅ Gather feedback and iterate

---

**Built with ❤️ for Steam Analytics | Powered by Streamlit & Plotly**

