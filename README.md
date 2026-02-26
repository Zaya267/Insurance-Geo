# Insurance Geo-AI Intelligence

[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

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

**Live Map Demo:** [View Here](https://Zaya267.github.io/Insurance-Geo/)

---

## 💻 Installation & Setup

1. Clone the repository:

```bash
git clone https://github.com/Zaya267/Insurance-Geo.git
cd Insurance-Geo
