# Superstore User Engagement Dashboard

## Project Overview
The **Superstore User Engagement Dashboard** is an interactive web application built with **Streamlit** to analyze sales, profit, and customer behavior from a retail Superstore dataset. The dashboard provides key metrics, visualizations, and filters to help understand **user engagement, sales trends, and customer lifetime value**.

---

## Technologies & Tools
- **Python 3.10+**
- **Streamlit** – interactive dashboard framework
- **Pandas & NumPy** – data manipulation and preprocessing
- **Plotly Express** – interactive visualizations
- **Geopy** – geocoding for customer location mapping

---

## 📁 Dataset
- **Source:** Kaggle Superstore Dataset ([link to dataset]([https://www.kaggle.com/datasets/benhamner/superstore](https://www.kaggle.com/datasets/ishanshrivastava28/superstore-sales?resource=download)))
- **Files:**
  - `Superstore.csv` – main dataset
  - `city_coordinates.csv` – precomputed city latitude/longitude for mapping using api

**Note:** The `city_coordinates.csv` file is generated automatically using `geopy` to optimize map performance.

---

## Features
- **KPIs:**  
  - Average Order Value  
  - Repeat Purchase Rate  
  - Total Customers  
  - Customer Lifetime Value (CLV)  

- **Interactive Charts:**  
  - Sales Over Time  
  - Profit by Category  
  - Top 10 Customers by Sales  

- **Interactive Map:**  
  - Displays customer locations  
  - Color-coded by Profit and sized by Sales  

- **Filters:**  
  - Category  
  - Region  
  - Date Range  

- **Data Download:**  
  - Download filtered data as CSV  

---

## How to Run
1. Clone this repository:
```bash
git clone <repository-url>
cd superstore-dashboard
```
2. Download requirements
   ```bash
   pip install -r requirements.txt
   ```
3. Run App
   ```bash
   streamlit run app.py
   ```
4. Open local URL in browser

## Notes
Precomputing city coordinates improves performance and avoids repeated geocoding API calls.

Streamlit auto-reloads when changes are saved, making development fast and iterative.

## Author 
Lizbeth Sarabia
[LinkedIn](https://www.linkedin.com/in/lizbeth-sarabia-74767b228/)
