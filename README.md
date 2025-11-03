# ⚙️ AZURE_BATCH-4_BACKEND 📊

## 🎯 Project Overview
This repository delivers a complete end-to-end Azure cloud usage analytics pipeline, integrating internal resource metrics with external market factors. It combines data processing workflows, exploratory data analysis, and a production-ready REST API backend for advanced insights.

## 📁 Repository Structure
```
AZURE_BATCH-4_BACKEND/
├── Data/
│   ├── raw/
│   │   ├── azure_usage.csv          # Raw Azure resource metrics
│   │   └── external_factors.csv     # Economic and market indicators
│   └── cleaned_merged.csv           # Processed and merged dataset
├── Notebook/
│   ├── Data_Cleaning.ipynb          # Data preprocessing pipeline
│   └── Data_Loading_EDA.ipynb       # Exploratory data analysis
└── scripts/
    └── app.py                       # Flask REST API backend
```

## 📊 Data Description

**Azure Usage Data:**
- Tracks daily CPU, memory, storage metrics, and cost for regions/resource types
- Spans 91 days (Jan 1–Mar 31, 2023)
- Highly granular, multi-region

**External Factors Data:**
- Daily economic_index, cloud_market_demand, holiday flags
- Enables correlational and seasonal cloud usage analysis

**Merged Dataset:**
- Combines all metrics and market factors
- Ready for analytics and machine learning

## 📓 Notebooks

**Data_Cleaning.ipynb:**
- Loads/raw/cleans both datasets
- Handles missing values/duplicates
- Integrates all external and internal metrics
- Output: cleaned_merged.csv

**Data_Loading_EDA.ipynb:**
- Describes dataset, analyzes temporal trends/correlations
- Visualizes daily/region-wise performance
- Flags outliers and monthly peaks
- Reveals key Azure cost optimization patterns

## 🚀 REST API (app.py)
- **GET /data**: Returns full merged data
- **GET /data/filter**: Filter by date/holiday/criteria
- **GET /stats**: Dataset summary stats
- **GET /cost-analysis**: Cost analytics

Clear endpoints for data, filtering, stats, and cost analysis.

## 🛠️ Technologies Used
- Python (Jupyter, Flask, Pandas, NumPy, Matplotlib/Seaborn)


## 📈 Key Findings & Insights
- 91 days of usage, multi-region, all major Azure metrics
- Strong cost/resource patterns correlated with market factors
- API and notebooks enable flexible interactive analytics
- Outlier and peak detection for robust forecasting
