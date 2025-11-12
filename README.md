🤖 Smart E-Commerce Chat Analyst

Gemini + DuckDB + Streamlit + Web Knowledge

🧩 Overview

Smart E-Commerce Chat Analyst is an intelligent, chat-based analytics tool that enables users to ask natural-language questions about their e-commerce data.
The app automatically generates SQL queries, executes them on a DuckDB in-memory database, and returns interactive results with insights, charts, and business-friendly explanations — all powered by Gemini/OpenAI models.

It bridges the gap between business teams and data analytics, allowing anyone to perform data exploration and gain insights without writing code.

🚀 Features

✅ Conversational Analytics – Ask business questions in natural language.

✅ Automatic SQL Generation – Converts queries into optimized DuckDB SQL.

✅ Real-Time Query Execution – Instant answers from your local or cloud data.

✅ Intelligent Explanations – Each result includes an AI-written insight.

✅ Web Knowledge Fallback – Expands context using Gemini’s reasoning.

✅ Interactive Charts – Auto-generated graphs and exportable CSVs.

🏗️ System Architecture

graph TD
    A[🧑‍💼 User] -->|Question in natural language| B[💬 Streamlit Chat UI]
    B --> C[🧠 Gemini Model (SQL Generator)]
    C --> D[🗃️ DuckDB Engine]
    D --> E[📊 DataFrame + Visualization]
    E --> F[🧾 Explanation + Insights]
    C --> G[🌐 Web Knowledge (if no local data)]
    F --> H[💻 Streamlit Frontend Display]


Flow Summary:

User enters a question through Streamlit chat.

Gemini converts it into a valid SQL query.

Query executes on DuckDB using the Olist dataset.

Results and plots are displayed.

Explanation and optional web insights enhance understanding.

🗂️ Dataset

This app uses the Olist E-Commerce Dataset (publicly available on Kaggle), which includes multiple CSV files:

olist_orders_dataset.csv

olist_order_items_dataset.csv

olist_products_dataset.csv

olist_customers_dataset.csv

olist_sellers_dataset.csv

olist_order_payments_dataset.csv

product_category_name_translation.csv

These datasets represent real-world Brazilian e-commerce transactions, including orders, payments, products, and sellers.

⚙️ Tech Stack

Component - Technology

Frontend - Streamlit

Backend	- Python

Query Engine -	DuckDB

AI Model- Gemini/OpenAI API

Deployment - Streamlit Cloud

Data Source - Olist E-Commerce Dataset (CSV)


🧠 How It Works

The user asks a business or analytical question in plain English.

The Gemini model generates an SQL query dynamically.

DuckDB executes the query on the loaded CSV datasets.

The results are visualized in Streamlit.

A business-friendly explanation is displayed below.

If data is missing or the query is invalid, the system falls back to web-informed reasoning to provide context.


▶️ How to Run Locally

Clone the repository

git clone https://github.com/Mahiiiii215/smart-ecommerce-chat-analyst.git
cd smart-ecommerce-chat-analyst


Install dependencies

pip install -r requirements.txt


Add your API key
Create a .streamlit/secrets.toml file:

GEMINI_API_KEY = "your_api_key_here"


Run the app

streamlit run app.py


Open the app in your browser (default: http://localhost:8501
)

🌐 Deployment

This app is deployed on Streamlit Cloud, which hosts the interactive chatbot UI and executes queries dynamically via DuckDB.
Once changes are pushed to GitHub, Streamlit automatically rebuilds and redeploys the latest version.

💡 Example Queries

Try asking:

“Show total number of orders.”

“Top 5 product categories by sales.”

“Average payment value by state.”

“Define CLV.”

“Translate valor do frete.”

“E-commerce trends in 2025.”

🔮 Future Work

✨ Voice Input Support – Enable speech-to-text queries.
✨ Real-Time Dashboards – Live updates for sales KPIs.
✨ Multi-Database Support – Add BigQuery, Snowflake, or PostgreSQL.
✨ Authentication & Profiles – Personalized insights per user.
✨ Automated Insights – Detect trends and anomalies in sales data.

👩‍💻 Author

Developed by: Mahathee Penugonda
Platform: Streamlit Cloud
Repository: GitHub – Smart E-Commerce Chat Analyst
