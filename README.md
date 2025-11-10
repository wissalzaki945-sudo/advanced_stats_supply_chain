# Advanced Statistics — Supply Chain Dashboard (Starter Pack)

This repo is a **minimal, working template** for your Assignment 1.  
Open it in VS Code locally or push it to GitHub and deploy to Streamlit Cloud.

## Quick Start (Local)

1. **Install Python 3.11+** (or 3.10+). Make sure `python` and `pip` run in a terminal.
2. In a terminal, go to this folder and run:
   ```bash
   pip install -r requirements.txt
   streamlit run app.py
   ```
3. In the app sidebar, upload the CSV (see *Dataset* below) or paste the public URL.
4. Explore the pages (Dashboard, Products, Customers, Suppliers, Logistics) and export charts as PNG for the report.

## Dataset
- DataCoSupplyChainDataset.csv (≈95 MB).  
- If you have a public URL, paste it in the app (sidebar) and click *Load*.  
- Or place the file at `./data/DataCoSupplyChainDataset.csv` and tick *Use local file*.

## Project Structure
```
app.py                            # Streamlit app
requirements.txt                  # Python packages
README.md                         # How to run & features
report/report.tex                 # Overleaf/LaTeX report (minimal)
presentation/presentation.tex     # Beamer slides (minimal)
data/                             # Put your CSV here (optional)
```

## Features in this template
- Sidebar: file uploader or URL loader
- KPI metrics (revenue, orders, products)
- Pages for Products (RQ1), Suppliers (RQ2), Logistics (RQ3), Customers (RQ4)
- Correlation heatmap & missing values overview
- Export buttons (download filtered data as CSV)

## How to Deploy (GitHub → Streamlit Cloud)
1. Create a **public GitHub repo** and push these files.
2. Go to **share.streamlit.io** and connect your repo.
3. Set **Main file path** to `app.py` and deploy.

## Tips
- Start simple: verify the dataset loads, then add charts one by one.
- Commit frequently with clear messages.
- Take screenshots (PNG) of your final charts for the report/presentation.

---
Generated: 2025-11-08
