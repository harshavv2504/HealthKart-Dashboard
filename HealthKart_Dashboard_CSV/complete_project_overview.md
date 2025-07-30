# HealthKart Influencer Marketing ROI Dashboard: Project Report  

**Author:** [Your Name]  
**Date:** July 31, 2025  

---

## 1. Executive Summary  

This report details the design, architecture, and implementation of an open-source Influencer Marketing ROI Dashboard for HealthKart. The project's primary objective is to provide a robust, data-driven tool for tracking and visualizing the performance of influencer campaigns across multiple brands and social media platforms.

The solution encompasses a complete data pipeline, from synthetic data generation and cleaning to a sophisticated, interactive dashboard built with Streamlit. The dashboard delivers key insights into campaign performance, influencer effectiveness, product/brand traction, and crucial financial metrics like Return on Ad Spend (ROAS) and Return on Investment (ROI). The architecture is modular, separating data processing logic from the user interface, which ensures scalability and maintainability. This report will walk through the data models, analytical methodologies, technical implementation, and the key assumptions that underpin the project.

---

## 2. Project Architecture & Data Flow  

The project is logically structured into three main stages: Data Generation, Data Cleaning & Transformation (ETL), and Data Visualization (Dashboard).

```mermaid
flowchart TD
    A[Start] --> B(1. Data Generation);
    B --> C{Raw Data Files};
    C --> D(2. Data Cleaning & Transformation);
    D --> E{Cleaned & Enriched Data Files};
    E --> F(3. Data Visualization);
    F --> G[End: Interactive Dashboard];

    subgraph "generate_data.py"
        B
    end

    subgraph "clean_raw_data.py"
        D
    end

    subgraph "dashboard.py & components"
        F
    end

    subgraph "Raw Data ('/data')"
        C
    end

    subgraph "Processed Data ('/cleaned_data')"
        E
    end

### 2.1. Data Generation (`generate_data.py`)  
This script creates four foundational CSV files (`influencers.csv`, `posts.csv`, `tracking_data.csv`, `payouts.csv`) containing realistic, synthetic data. This raw data resides in the `/data` directory.

### 2.2. Data Cleaning & Transformation (`clean_raw_data.py`)  
This script acts as an orchestrator, executing a series of cleaning and enrichment modules (`payments_log.py`, `orders_tracking.py`, `influencer_performance.py`). These modules read the raw data, process it, and generate analysis-ready CSV files in the `/cleaned_data` directory.

### 2.3. Data Visualization (`dashboard.py`)  
This is the main Streamlit application. It loads the cleaned data, provides interactive filters, and presents the information across three distinct, specialized tabs: **Overview**, **Product & Brand Analysis**, and **Influencer Analysis**.

## 3. Data Modeling & Generation (`generate_data.py`)  
The foundation of the dashboard is a set of simulated datasets that mimic real-world influencer marketing data.

### 3.1. Assumptions in Data Generation  
- **Campaign Period:** Data is generated for a specific period: **January 1, 2025, to July 21, 2025**.  
- **Sponsored Content:** 70% of all posts are assumed to be sponsored and associated with a HealthKart brand.  
- **Influencer Tiers:** Influencers are realistically segmented into tiers (Nano, Micro, Mid, Macro, Mega) with corresponding follower counts and probabilities.  
- **Platform Distribution:** Platform choice is weighted, with Instagram being the most probable (70%), followed by YouTube (25%) and Twitter (5%).  
- **Sales Attribution:**  
  - **Influenced Sales:** The number of orders from a post is modeled as a factor of the post's 'likes', simulating a direct conversion from engagement. The order date is randomized to be 1–7 days after the post date.  
  - **Organic Sales:** A baseline organic conversion rate (0.02%) is applied to a total user base to simulate sales that are not directly attributable to an influencer campaign.  
- **Product Pricing:** Product prices are static and defined within a `BRANDS` dictionary.

### 3.2. Data Models  

#### a) `influencers.csv`  
**Purpose:** A master list of all influencers.  

**Fields:**  
- `influencer_id`: Unique identifier (e.g., `inf_001`)  
- `name`: Influencer's name  
- `category`: Niche (e.g., Fitness, Yoga)  
- `gender`: Male/Female  
- `follower_count`: Number of followers  
- `platform`: Primary social media platform  
- `payout_basis`: The model for payment (`Post` or `Order`)  

#### b) `posts.csv`  
**Purpose:** A log of all content published by influencers.  

**Fields:**  
- `post_id`: Unique identifier for the post  
- `influencer_id`: Foreign key linking to `influencers.csv`  
- `platform`, `date`, `brand`, `campaign`  
- `reach`, `likes`, `comments`: Key engagement metrics  

#### c) `tracking_data.csv`  
**Purpose:** A transactional log of all sales, distinguishing between influenced and organic.  

**Fields:**  
- `source`: Tracking code or `'organic'`  
- `campaign`, `influencer_id`, `user_id`  
- `product`, `date`, `orders`, `revenue`  
- `attribution_type`: Critical flag (`Influenced` or `Organic`)  
- `brand`  

#### d) `payouts.csv`  
**Purpose:** A summary of total payouts to influencers.  

**Fields:**  
- `payout_id`: Unique identifier for the payout record  
- `influencer_id`: Foreign key  
- `basis`: `Post` or `Order`  
- `rate`: The rate per post or commission rate  
- `orders`: Number of orders (for `'Order'` basis)  
- `total_payout`: The final calculated payout amount for that entry  

## 4. Data Cleaning & Transformation Pipeline  
The `clean_raw_data.py` script orchestrates the transformation of raw data into three analysis-ready tables. This ETL (Extract, Transform, Load) process is crucial for calculating metrics and ensuring data integrity.

### 4.1. `payments_log.py`  
**Input:** `influencers.csv`, `posts.csv`, `tracking_data.csv`  
**Output:** `payment_log.csv`  

**Logic:**  
This script creates a highly granular, itemized log of every single payable event.  

- **For 'Post' basis:** It iterates through every post made by a `'Post'`-based influencer and calculates a payment for that specific post based on a progressive multiplier tied to their follower count.  
- **For 'Order' basis:** It iterates through every `'Influenced'` sale and calculates a commission (8% of revenue) for that specific transaction.  

**Key Assumption:**  
Post-based influencers are paid per post, regardless of whether the post was sponsored or not. This assumes their contract is for general content creation.

---

### 4.2. `orders_tracking.py`  
**Input:** All four raw data files  
**Output:** `enriched_orders.csv`  

**Logic:**  
This is a critical enrichment step. It merges the `tracking_data.csv` with `posts.csv` and `influencers.csv` to create a unified view for each order.

- It links each influenced order back to the specific post that generated it.  
- It adds influencer details (name, category, etc.) to each order row.  
- It calculates the Cost of Goods for each order, assuming a **55% cost margin**.

---

### 4.3. `influencer_performance.py`  
**Input:** All four raw data files  
**Output:** `influencer_performance.csv`  

**Logic:**  
This script aggregates data from all sources to create a comprehensive performance summary for each influencer.

- **Metrics from `posts.csv`:** It sums total Posts, Reach, Likes, and Comments for each influencer.  
- **Metrics from `tracking_data.csv`:** It sums total Orders and Revenue from `'Influenced'` sales.  
- **Metrics from `payouts.csv`:** It sums the `total_payout` to get the final Payout amount.  

**Derived Metrics:**  
It then calculates crucial KPIs like **Engagement Rate**, **Gross Profit**, **Net Profit**, **ROAS**, and **ROI** at the individual influencer level.

## 5. Dashboard Implementation (`dashboard.py`)  
The user-facing component is a multi-page interactive application built with Streamlit.

### 5.1. Core Structure  
- **Main Script (`dashboard.py`):** This script acts as the entry point. It handles page configuration, loads the cleaned data, sets up the sidebar filters, and defines the tab structure.  
- **Modular Components (`/components`):** The content of each tab is encapsulated in its own Python script (`overview_tab.py`, `detailed_analysis_tab.py`, `influencer_analysis_tab.py`). This makes the code clean and easy to manage.  
- **Utilities & Constants (`/utils`, `constants.py`):** Helper functions (like data loading, filtering logic, KPI calculations) and constants (like colors, file paths) are stored in separate files for reusability and maintainability.

---

### 5.2. Interactive Filters  
The sidebar provides a global filtering mechanism that affects all charts and KPIs across the dashboard. Users can filter by:  
- **Date Range:** To analyze specific time periods.  
- **Brand:** To focus on a single brand (e.g., MuscleBlaze).  
- **Product:** To drill down to a specific product's performance.  
- **Platform:** To compare performance across Instagram, YouTube, etc.

---

### 5.3. Dashboard Tabs  

#### a) 📈 Overview Tab (`overview_tab.py`)  
**Purpose:** To provide a high-level, "30,000-foot view" of the overall health of the influencer marketing program.  

**Key Visualizations:**  
- **KPI Cards:** At-a-glance metrics like Total Revenue, Total Payout, Net Profit, ROI, and Incremental ROAS.  
- **Pie Charts:** Breakdowns of Order Source (Influenced vs. Organic), Brand Revenue, and Platform Revenue.  
- **Time Series Chart:** A line chart showing the trend of Revenue, Payout, and Net Profit over time, allowing for the identification of seasonal trends or campaign impact spikes.  
- **Stacked Bar Chart:** Shows product revenue broken down by the platform it was generated on.

---

#### b) 📄 Product & Brand Analysis Tab (`detailed_analysis_tab.py`)  
**Purpose:** To allow for a deep dive into the performance of specific products, brands, and campaigns.  

**Key Visualizations:**  
- The tab is logically divided into three sections: Product, Brand, and Campaign analysis.  
- Each section features a **Donut Chart** showing the revenue contribution of each item (e.g., revenue per product).  
- Alongside each chart is a **detailed data table** providing the exact revenue and calculated net profit figures.  
- This structure allows for quick visual comparison followed by detailed quantitative analysis.

---

#### c) 🧑‍💻 Influencer Analysis Tab (`influencer_analysis_tab.py`)  
**Purpose:** To analyze and compare the performance of individual influencers. This is the core of the dashboard for making decisions about which influencers to continue working with.

**Key Visualizations:**  
- **KPI Cards:** Specific to influencers, showing metrics like Total Active Influencers, Average Engagement Rate, and Average Revenue per Influencer.  
- **Top/Worst Performers Charts:**  
  - A **horizontal bar chart** showcasing the Top 10 Influencers by Revenue.  
  - A **color-graded horizontal bar chart** showing the Worst 10 Influencers by ROI (only showing those with negative ROI), immediately highlighting inefficient spending.  
- **Detailed Metrics Table:** A comprehensive, sortable table displaying all key performance indicators for every influencer, from engagement metrics to financial returns. This is the most granular view for performance management.

## 6. Key Metrics & Calculations  
The analytical power of the dashboard comes from its robust calculation of key performance indicators.

- **Net Profit:**  
  `(Total Revenue * (1 - Cost of Goods Percentage)) - Total Payout`  
  - **Assumption:** A flat 55% Cost of Goods has been assumed.

- **Return on Investment (ROI):**  
  `(Net Profit / Total Payout) * 100`  
  - This measures the profitability of the investment. An ROI of 100% means the profit was equal to the cost.

- **Return on Ad Spend (ROAS):**  
  `Total Revenue / Total Payout`  
  - This is a top-line metric showing how many rupees of revenue were generated for every rupee spent on payouts.

- **Incremental ROAS:**  
  `Influencer-Driven Revenue / Total Payout`  
  - This is a more accurate measure of an influencer's direct impact. It isolates the revenue generated specifically by influencers (excluding organic sales) and compares it to the payout.  
  - This answers the question: "For the money we spent on influencers, what direct revenue did they bring in?"

- **Engagement Rate:**  
  `((Total Likes + Total Comments) / Total Reach) * 100`  
  - A standard industry metric to measure the quality of an influencer's audience interaction.

---

## 7. Conclusion & Next Steps  
This project successfully delivers a comprehensive and functional influencer marketing dashboard. The modular architecture, detailed data simulation, and insightful KPI calculations provide a powerful tool for the HealthKart marketing team. The dashboard enables data-driven decision-making by clearly visualizing campaign effectiveness, identifying top-performing influencers, and highlighting areas of inefficient spending.

**Potential Next Steps:**

- **Connect to Live Database:**  
  Replace the CSV loading mechanism with a direct connection to a production database (e.g., PostgreSQL, BigQuery) for real-time data.

- **Advanced Attribution Models:**  
  Implement more sophisticated attribution models beyond last-touch, such as multi-touch attribution or time-decay models, to better understand the customer journey.

- **Predictive Analytics:**  
  Incorporate machine learning models to forecast campaign performance or predict which influencer personas are likely to yield the highest ROI for a given product.

- **User Authentication & Export:**  
  Add user login functionality and enable exporting of charts and data tables to PDF or CSV for reporting purposes.



