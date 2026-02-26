# Insurance Geo-AI Intelligence

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## 🌍 Project Overview

This project demonstrates a **geospatial AI solution** for the insurance industry. It combines client data, demographics, and geospatial information to:

1. Detect potential client leads  
2. Suggest optimal branch locations  
3. Score regions for business opportunity  
4. Provide interactive map visualizations  

The project leverages **Snowflake**, **Python**, **Folium**, and **AI scoring models** to create a fully interactive geospatial intelligence dashboard.

---

## 🧰 Features

### 1. Data Integration

- Clients, demographics, and geospatial reference data  
- Snowflake data warehouse for centralized storage  
- Python scripts for loading, processing, and enriching data  

### 2. AI Opportunity Scoring

- Weighted scoring using:  
  - Average monthly income  
  - Population density  
  - Annual growth rate  
- Scores highlight high-potential regions for new clients  

### 3. Clustering & Branch Suggestion

- K-means clustering to group clients by location  
- Suggested branch locations calculated from cluster centroids  
- Branch scoring indicates potential client reach  

### 4. Interactive Map Visualization

- Folium heatmap of client opportunity scores  
- Colored markers for clusters (green: high, orange: medium, red: low)  
- Branch locations highlighted with markers  
- Popups provide client and cluster details  
- Legend and table for clear interpretation  

**Live Map Demo:**  

- [Insurance Intelligence Map](https://zaya267.github.io/Insurance-Geo/maps/insurance_intelligence_map.html)  
- [Insurance AI Map](https://zaya267.github.io/Insurance-Geo/maps/insurance_ai_map.html)  
- [Insurance Map](https://zaya267.github.io/Insurance-Geo/maps/insurance_map.html)  

---

## 💻 Installation & Setup

1. Clone the repository:

```bash
git clone https://github.com/Zaya267/Insurance-Geo.git
cd Insurance-Geo


Create and activate a Python environment:
conda create -n snowgeo python=3.10 -y
conda activate snowgeo


Install required Python packages:
pip install -r requirements.txt


Run scripts locally:

python insurance_map.py
streamlit run insurance_dashboard.py


📁 Repository Structure

Insurance-Geo/
│
├─ maps/                        # All interactive HTML map files
│   ├─ insurance_ai_map.html
│   ├─ insurance_intelligence_map.html
│   └─ insurance_map.html
│
├─ assets/                      # CSS, JS, and other visual assets
├─ insurance_map.py              # Data processing & map generation
├─ insurance_dashboard.py        # Streamlit dashboard
├─ README.md
├─ requirements.txt
└─ .nojekyll                     # Required for GitHub Pages deployment



