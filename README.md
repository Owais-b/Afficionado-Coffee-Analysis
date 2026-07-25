# ☕ Afficionado Coffee Roasters — Sales Trend & Time-Based Performance Analysis

### Turning raw transaction data into actionable insights for smarter coffee retail operations.

---

## 🚀 Live Dashboard

Explore the sales analytics dashboard and interact with the visualisations to understand how customer demand changes across dates, days, hours, and store locations.

---

## 📌 Project Overview

In coffee retail, understanding **when customers buy** can be just as important as understanding **what they buy**.

A large transaction dataset can contain valuable information about customer behaviour, but raw data alone does not provide an immediate understanding of operational demand.

This project transforms transaction-level coffee shop sales data into an interactive analytical solution that helps uncover:

- 📈 Sales trends over time
- 📅 Day-of-week performance
- ⏰ Peak and off-peak transaction hours
- 🏪 Store-level demand differences
- 💰 Revenue performance
- 📦 Transaction quantity patterns
- 🔥 High-demand and low-demand periods
- 📊 Temporal customer behaviour

The project combines **data preprocessing, exploratory data analysis, temporal feature engineering, data visualisation, and interactive dashboard development** to turn raw sales data into meaningful business insights.

---

# 🎯 Problem Statement

Coffee retail businesses often collect large amounts of transaction data but may lack an easy way to understand **when demand occurs and how it varies across locations**.

Without structured temporal analytics, operational decisions such as staffing, resource planning, and store management may rely heavily on assumptions or intuition.

For example:

> "Mornings are probably the busiest."

Instead of relying on assumptions, this project uses transaction data to investigate questions such as:

- Which days experience the highest customer demand?
- Which days are relatively slower?
- What are the busiest hours?
- When does demand decrease?
- Do different store locations have different peak periods?
- Are revenue and transaction quantities consistent across time?
- How can demand patterns support operational planning?

The goal is to provide a **data-driven view of customer demand** that can support more informed business decisions.

---

# 🎯 Project Objectives

## Primary Objectives

- Analyse overall sales trends across the available dataset period.
- Identify the busiest and slowest days of the week.
- Determine peak transaction hours.
- Analyse hourly customer demand patterns.

## Secondary Objectives

- Compare temporal demand across different store locations.
- Identify location-specific customer behaviour.
- Compare revenue and transaction quantity patterns.
- Support data-driven staff scheduling.
- Assist operational planning and resource allocation.
- Provide an interactive analytics platform for business stakeholders.

---

# 🔍 Key Questions

The project focuses on answering the following analytical questions:

### 📈 Sales Trends
- How does sales performance change over time?
- Are there noticeable increases or decreases in demand?
- How does revenue vary across the analysed period?

### 📅 Day-of-Week Performance
- Which days have the highest transaction activity?
- Which days have the lowest activity?
- How does customer behaviour differ between weekdays and weekends?

### ⏰ Time-of-Day Demand
- What are the busiest transaction hours?
- Are there identifiable morning rush periods?
- Are there slower midday periods?
- Does demand increase again during evening hours?

### 🏪 Store-Level Performance
- Do different store locations follow similar demand patterns?
- Which locations experience different peak periods?
- Are customer behaviours consistent across stores?

---

# 📊 Dataset

The project uses transaction-level coffee shop sales data containing information about transactions, dates, times, quantities, prices, products, and store locations.

The dataset enables analysis across multiple dimensions, including:

- Time
- Date
- Day of week
- Hour of day
- Revenue
- Transaction quantity
- Product categories
- Product types
- Store locations

### Dataset Features

| Feature | Description |
|---|---|
| `transaction_id` | Unique identifier for each transaction |
| `transaction_date` | Date on which the transaction occurred |
| `transaction_time` | Time at which the transaction occurred |
| `transaction_qty` | Number of items purchased |
| `unit_price` | Price per unit |
| `store_id` | Unique store identifier |
| `store_location` | Physical store location |
| `product_id` | Unique product identifier |
| `product_category` | Broad product category |
| `product_type` | Specific product type |
| `product_detail` | Detailed product information |

The availability of both **date and time information** makes it possible to perform detailed temporal analysis across daily, weekly, and hourly patterns.

---

# 🔬 Analytical Methodology

The project follows a structured data analytics workflow.

```text
Raw Transaction Data
        │
        ▼
Data Ingestion
        │
        ▼
Data Validation & Cleaning
        │
        ▼
Feature Engineering
        │
        ├── Revenue
        ├── Hour
        ├── Day of Week
        └── Time Buckets
        │
        ▼
Exploratory Data Analysis
        │
        ├── Sales Trends
        ├── Day-of-Week Analysis
        ├── Hourly Demand
        └── Store Comparison
        │
        ▼
Interactive Streamlit Dashboard
        │
        ▼
Actionable Business Insights
```

---

## 1️⃣ Data Ingestion & Validation

The dataset is loaded and examined using Python and Pandas.

The validation process checks for:

- Missing values
- Duplicate transaction records
- Duplicate transaction IDs
- Incorrect data types
- Invalid date formats
- Invalid time formats
- Non-positive quantities
- Invalid pricing values

---

## 2️⃣ Feature Engineering

Additional features are derived from the raw transaction data to enable temporal analysis.

### Revenue per Transaction

Revenue is calculated as:

```text
Revenue = Transaction Quantity × Unit Price
```

### Temporal Features

The analysis derives:

- Hour of day
- Day of week
- Date
- Revenue
- Transaction quantity
- Time-based demand categories

### Time Buckets

Transactions can be grouped into meaningful time periods:

| Time Bucket | Hours |
|---|---|
| Morning | 06:00 – 11:59 |
| Afternoon | 12:00 – 16:59 |
| Evening | 17:00 – 21:59 |
| Late Hours | 22:00 – 05:59 |

These categories help provide a high-level understanding of customer activity throughout the day.

---

# 📈 Exploratory Data Analysis

The EDA process investigates several dimensions of coffee shop performance.

### Sales Trend Analysis

- Daily revenue trends
- Transaction volume over time
- Revenue distribution
- Identification of upward and downward patterns
- Store-level performance comparison

### Day-of-Week Analysis

- Average revenue by day
- Average transaction count by day
- Busiest and slowest days
- Weekday versus weekend comparison
- Behavioural interpretation of demand patterns

### Time-of-Day Analysis

- Hourly transaction volume
- Hourly revenue distribution
- Peak transaction hours
- Low-demand periods
- Morning and evening demand patterns

### Cross-Location Analysis

- Store-level demand comparison
- Hourly demand patterns by location
- Peak-hour alignment
- Location-specific customer behaviour

---

# 🖥️ Interactive Streamlit Dashboard

The project includes an interactive web-based dashboard developed using **Streamlit**.

The dashboard converts the analytical workflow into an accessible interface where users can explore sales performance without directly interacting with the underlying Python code.

## Core Dashboard Modules

### 📊 Overall Sales Trends

Provides a visual overview of sales performance across the analysed period.

### 📅 Day-of-Week Performance

Helps identify the strongest and weakest days based on selected performance metrics.

### ⏰ Hourly Demand Analysis

Visualises customer demand across different hours of the day.

### 🔥 Demand Heatmaps

Provides a visual representation of demand patterns across time and store locations.

### 🏪 Store Location Comparison

Allows users to compare demand behaviour between different store locations.

---

# 🎛️ Interactive Features

The dashboard provides interactive controls for exploring the data.

Users can analyse the data using:

- 🏪 Store location filters
- 📅 Day-of-week selection
- ⏱️ Hour-range filtering
- 💰 Revenue-based analysis
- 📦 Transaction quantity analysis

These controls allow users to move from a high-level business overview to more detailed temporal and store-level analysis.

---

# 💡 Business Value

The analytical insights generated by this project can support several operational decisions.

## 👥 Staff Scheduling

Understanding peak hours can help managers allocate more staff during periods of high demand and optimise staffing during slower periods.

## 🏪 Store-Level Planning

Different locations may exhibit different customer behaviours. Store-specific analysis can help managers design location-specific operational strategies.

## ⏱️ Operational Planning

Understanding when demand occurs can help businesses align staffing and operational resources with actual customer activity.

## 📦 Resource Allocation

Historical demand patterns can provide useful evidence for planning inventory, supplies, and operational resources.

## 📈 Data-Driven Decision Making

The project replaces assumptions with measurable evidence by providing quantitative insights into customer demand patterns.

---

# 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Pandas | Data manipulation and analysis |
| NumPy | Numerical processing |
| Matplotlib | Data visualisation |
| Seaborn | Statistical visualisation |
| Streamlit | Interactive dashboard |
| Jupyter Notebook | Exploratory Data Analysis |
| Git | Version control |
| GitHub | Source code management and collaboration |

---

# 📂 Project Structure

```text
Afficionado-Coffee-Analysis/
│
├── dashboard/
│   └── dashboard.py
│
├── data/
│   └── Coffee Shop Sales New.xlsx
│
├── notebooks/
│   └── EDA.ipynb
│
├── outputs/
│   └── Dashboard screenshots and visualisations
│
├── reports/
│   └── Project reports and documentation
│
├── .gitignore
├── requirements.txt
├── README.md
└── Project Feedback Video Script.docx
```

---

# ⚙️ Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/Owais-b/Afficionado-Coffee-Analysis.git
```

## 2. Navigate to the Project Directory

```bash
cd Afficionado-Coffee-Analysis
```

## 3. Create a Virtual Environment

```bash
python -m venv venv
```

## 4. Activate the Virtual Environment

### Windows

```bash
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

## 5. Install Dependencies

```bash
pip install -r requirements.txt
```

## 6. Launch the Dashboard

```bash
streamlit run dashboard/dashboard.py
```

The application will open in your default web browser.

---

# 📓 Exploratory Data Analysis

The complete exploratory analysis is available in:

```text
notebooks/EDA.ipynb
```

The notebook covers:

- Data loading
- Data validation
- Data preprocessing
- Feature engineering
- Statistical exploration
- Temporal analysis
- Visualisation
- Business insights

---

---

# 📦 Project Deliverables

This project includes:

- ✅ Cleaned and analysed transaction data
- ✅ Exploratory Data Analysis notebook
- ✅ Temporal feature engineering
- ✅ Sales trend analysis
- ✅ Day-of-week analysis
- ✅ Hourly demand analysis
- ✅ Store-level comparison
- ✅ Interactive Streamlit dashboard
- ✅ Data visualisations
- ✅ Business insights and recommendations
- ✅ Project documentation

---

# 🔮 Future Enhancements

The project can be extended into a more advanced intelligent retail analytics platform.

### 🤖 Demand Forecasting

Implement machine learning and time-series models to forecast future customer demand.

### 👥 Automated Staff Scheduling

Develop an optimisation system that recommends staffing levels based on predicted demand.

### 📦 Inventory Forecasting

Predict future product demand to support automated inventory planning.

### 🔔 Real-Time Demand Monitoring

Integrate live transaction data to monitor demand and generate operational alerts.

### 🧠 AI-Powered Business Recommendations

Use AI to automatically generate recommendations based on observed sales patterns.

### 📊 Automated Executive Reports

Generate periodic management reports containing key performance indicators, trends, and recommendations.

### 🗺️ Advanced Location Analytics

Integrate geographic visualisations to analyse spatial patterns in store performance.

---

# 🎓 Project Context

This project was developed as a practical data analytics solution in the context of the **Afficionado Coffee Roasters project**.

It demonstrates the application of:

- Data Analytics
- Exploratory Data Analysis
- Business Intelligence
- Temporal Analysis
- Data Visualisation
- Interactive Dashboard Development

The project focuses on transforming raw transactional information into insights that can support **operational planning, staffing decisions, and data-driven business strategy**.

---

# 👨‍💻 Author

## Owais Batte

**B.Tech — Computer Science & Engineering (Artificial Intelligence & Machine Learning)**

### Interests

- Artificial Intelligence
- Machine Learning
- Data Analytics
- Computer Vision
- Cybersecurity
- Software Development

---


# 📜 License

This project is intended for educational, academic, and portfolio purposes.

If the dataset contains proprietary or restricted business information, it should not be redistributed without appropriate permission.
