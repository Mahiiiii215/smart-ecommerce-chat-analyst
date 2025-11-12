import streamlit as st
import google.generativeai as genai
import duckdb
import pandas as pd
import os
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from typing import Optional



# ============================================================
# 1️⃣ Configure Gemini API Key
# ============================================================
genai.configure(api_key="AIzaSyDLbeiUqaAYM3mhXFjRbgGgo6MgR0M7L2I")  # Replace with your valid key

# ============================================================
# 2️⃣ Connect to DuckDB
# ============================================================
con = duckdb.connect("ecommerce.duckdb")
# ============================================================
# ✅ Load Olist Dataset into DuckDB (if not already loaded)
# ============================================================


# ✅ Use relative path (works both locally and on Streamlit Cloud)
DATA_PATH = os.path.join(os.getcwd(), "data")

  # Folder where your CSVs are stored (change if needed)

# Mapping of table names to filenames
olist_files = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv"
}

# Check and create tables if they don't exist
existing_tables = [t[0] for t in con.execute("SHOW TABLES").fetchall()]

for table, filename in olist_files.items():
    if table not in existing_tables:
        file_path = os.path.join(DATA_PATH, filename)
        if os.path.exists(file_path):
            print(f"📥 Loading {filename} → {table}")
            con.execute(f"""
                CREATE TABLE {table} AS
                SELECT * FROM read_csv_auto('{file_path}', header=True)
            """)
        else:
            print(f"⚠️ File not found: {file_path}")
    else:
        print(f"✅ Table already exists: {table}")

# ============================================================
# 3️⃣ Initialize Gemini Model
# ============================================================
model = genai.GenerativeModel("models/gemini-2.5-flash")

# ============================================================
# 🧠 Conversational Memory Configuration
# ============================================================
MEMORY_WINDOW = 6  # keep last 6 exchanges for context

# ============================================================
# 4️⃣ Query History Helpers
# ============================================================
HISTORY_FILE = "query_history.csv"

def log_query_history(question, sql_query, explanation):
    with open(HISTORY_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), question, sql_query, explanation])

def load_query_history():
    if os.path.exists(HISTORY_FILE):
        return pd.read_csv(HISTORY_FILE, names=["Time", "Question", "SQL", "Explanation"])
    return pd.DataFrame(columns=["Time", "Question", "SQL", "Explanation"])

def clear_query_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
        st.sidebar.success("🧹 Query history cleared!")
        st.rerun()

# ============================================================
# 5️⃣ Smart SQL Generator
# ============================================================
def generate_sql(question, context=""):
    schema_text = ""
    for (table_name,) in con.execute("SHOW TABLES;").fetchall():
        columns = con.execute(f"DESCRIBE {table_name}").fetchall()
        schema_text += f"\nTable: {table_name}\n"
        for col in columns:
            schema_text += f" - {col[0]} ({col[1]})\n"

    prompt = f"""
    You are a senior e-commerce data analyst assistant.
    Use prior user context to understand the intent.

    Context:
    {context}

    Schema:
    {schema_text}

    Write a valid DuckDB SQL query for:
    "{question}"
    Return only the SQL query without markdown or commentary.
    """

    response = model.generate_content(prompt)
    return response.text.strip().replace("```sql", "").replace("```", "").strip()

# ============================================================
# 6️⃣ Execute & Explain SQL
# ============================================================
def execute_query(sql_query):
    try:
        df = con.execute(sql_query).fetchdf()
        return df
    except Exception as e:
        return f"❌ SQL Error: {e}"

def explain_query(sql_query):
    prompt = f"Explain in 2–3 sentences what this SQL query reveals in business terms:\n{sql_query}"
    response = model.generate_content(prompt)
    return response.text.strip()

# ============================================================
# 7️⃣ Smart Tools (Translate, Define, Location)
# ============================================================
def smart_tool_response(user_input):
    if "translate" in user_input.lower():
        prompt = f"Translate to English (keep e-commerce meaning): {user_input}"
    elif "define" in user_input.lower() or "what is" in user_input.lower():
        prompt = f"Provide a short business definition for this term: {user_input}"
    elif "where" in user_input.lower() and "location" in user_input.lower():
        prompt = f"Give possible location insights based on: {user_input}"
    else:
        prompt = f"You are an intelligent e-commerce assistant. Respond conversationally to: {user_input}"
    response = model.generate_content(prompt)
    return response.text.strip()


# ============================================================
# 🌍 External Knowledge (Web Fallback)
# ============================================================
def external_trend_response(user_input):
    """
    If the question sounds global/industry-level (e.g., '2025 market trends'),
    answer using external web context instead of SQL.
    """
    trigger_words = ["global", "industry", "market trends", "ecommerce trends", "in 2025", "future", "forecast", "global trends"]

    if any(word in user_input.lower() for word in trigger_words):
        prompt = f"""
        You are an expert e-commerce industry analyst.
        Based on external market research and 2025 trends, answer this question factually and conversationally:
        {user_input}
        """
        try:
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            return f"🌐 Unable to fetch external insights: {e}"
    return None


# ============================================================
# 8️⃣ Web Knowledge Fallback
# ============================================================
def fetch_web_answer(question: str) -> Optional[str]:
    """
    When no relevant SQL result or data exists, use Gemini's web-aware reasoning
    to bring in external business intelligence.
    """
    prompt = f"""
    The user asked: "{question}"
    Please provide a web-informed, factual and current explanation or summary
    relevant to e-commerce, market trends, or analytics insights.
    Keep it under 5 sentences.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception:
        return None

# ============================================================
# 9️⃣ Memory & Session State
# ============================================================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def add_chat(role, content, df=None):
    st.session_state.chat_history.append({"role": role, "content": content, "df": df})
    if len(st.session_state.chat_history) > MEMORY_WINDOW:
        st.session_state.chat_history = st.session_state.chat_history[-MEMORY_WINDOW:]

# ============================================================
# 🔟 Visualization Helper (Auto Chart Type)
# ============================================================
def plot_from_df(df):
    try:
        if df is not None and len(df.columns) >= 2:
            x_col, y_col = df.columns[:2]
            # Auto-select chart type
            if df[y_col].dtype in ["int64", "float64"]:
                kind = "line" if len(df) > 5 else "bar"
            else:
                kind = "bar"

            fig, ax = plt.subplots()
            df.plot(kind=kind, x=x_col, y=y_col, ax=ax, legend=False)
            ax.set_title(f"{y_col} by {x_col}")
            st.pyplot(fig)
    except Exception:
        pass

# ============================================================
# 1️⃣1️⃣ Streamlit UI Setup
# ============================================================
st.set_page_config(page_title="Smart E-Commerce Chat Analyst", layout="wide")
st.title("🤖 Smart E-Commerce Chat Analyst (Gemini + DuckDB + Web Knowledge)")
st.caption("Ask your e-commerce database or general business questions — now web-aware!")

# Sidebar Controls
with st.sidebar:
    st.header("🧭 Controls")
    if st.button("🧽 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
    if st.button("🧹 Clear Query History"):
        clear_query_history()
    if st.button("🧠 Clear Memory Context"):
        st.session_state.chat_history = []
        st.sidebar.success("🧠 Memory context cleared.")
        st.rerun()

    st.markdown("---")
    st.subheader("🕓 Query History")
    history = load_query_history()
    if not history.empty:
        st.dataframe(history.sort_values(by="Time", ascending=False)[["Time", "Question"]])
    else:
        st.info("No query history yet.")

# ============================================================
# 1️⃣2️⃣ Display Chat History
# ============================================================
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["df"] is not None:
            st.dataframe(msg["df"])
            plot_from_df(msg["df"])
            csv_data = msg["df"].to_csv(index=False).encode("utf-8")
            st.download_button(
                "💾 Download CSV",
                csv_data,
                "results.csv",
                "text/csv",
                key=f"dl_{hash(msg['content'])}"
            )

# ============================================================
# 1️⃣3️⃣ Handle User Input (Enhanced with External Knowledge)
# ============================================================
if user_input := st.chat_input("💬 Ask a question (business, data, or general e-commerce)..."):
    add_chat("user", user_input)
    with st.chat_message("user"):
        st.markdown(user_input)

    # 🌐 Step 1: Check for global or external trend queries first
    external_response = external_trend_response(user_input)
    if external_response:
        with st.chat_message("assistant"):
            st.markdown(external_response)
        add_chat("assistant", external_response)

    # 💡 Step 2: Smart tool responses (translate, define, location)
    elif any(k in user_input.lower() for k in ["translate", "define", "location"]):
        response_text = smart_tool_response(user_input)
        with st.chat_message("assistant"):
            st.markdown(response_text)
        add_chat("assistant", response_text)

    # 🧠 Step 3: SQL-based analytical queries
    else:
        # Build conversational context
        context_messages = [
            f"{m['role'].capitalize()}: {m['content']}"
            for m in st.session_state.chat_history[-MEMORY_WINDOW:]
        ]
        context = "\n".join(context_messages)
        sql_query = generate_sql(user_input, context)

        with st.chat_message("assistant"):
            st.code(sql_query, language="sql")
            df = execute_query(sql_query)

            if isinstance(df, str):  # SQL Error handling
                st.error(df)
                add_chat("assistant", df)

                # 🌍 Web fallback (optional insight)
                web_info = fetch_web_answer(user_input)
                if web_info:
                    st.info("🌐 Web Insight:")
                    st.markdown(web_info)
                    add_chat("assistant", web_info)

            elif df is not None and len(df) > 0:
                explanation = explain_query(sql_query)
                st.success("✅ Query executed successfully!")
                st.dataframe(df)
                st.markdown(f"**🧾 Explanation:** {explanation}")
                plot_from_df(df)

                add_chat("assistant", explanation, df=df)
                log_query_history(user_input, sql_query, explanation)

            else:
                st.warning("No data returned for this query.")
                web_info = fetch_web_answer(user_input)
                if web_info:
                    st.info("🌐 Web Insight:")
                    st.markdown(web_info)
                    add_chat("assistant", web_info)

























