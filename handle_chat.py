import streamlit as st
from llm import client

def handle_core_chat():
    with st.spinner("Responding..."):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                max_tokens=300,
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"⚠️ API Error: {e}"
    return answer



def summarize_dataframe(df):
    summary = []
    for col in df.columns:
        dtype = df[col].dtype
        missing = df[col].isna().sum()
        unique = df[col].nunique()
        summary.append(f"{col} ({dtype}) — {missing} missing, {unique} unique")
    return "\n".join(summary)


def handle_csv_chat(df, query):
    try:
        q = query.lower()

        if "basic stats" in q or "describe" in q:
            st.write(df.describe())
            return "Basic stats for numeric columns shown above."

        elif "missing" in q:
            missing = df.isna().sum().sort_values(ascending=False)
            st.write(missing)
            return f"The column '{missing.index[0]}' has the most missing values."

        elif "histogram" in q:
            import matplotlib.pyplot as plt
            numeric_cols = df.select_dtypes(include="number").columns
            if len(numeric_cols) == 0:
                return "No numeric columns found to plot."
            col = numeric_cols[0] 
            fig, ax = plt.subplots()
            df[col].hist(ax=ax)
            st.pyplot(fig)
            return f"Histogram of column '{col}'."

        else:
            df_summary = summarize_dataframe(df)
            context = f"Here is a summary of the dataset:\n{df_summary}\n\nQuestion: {query}"
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are an assistant base on data, you give the answer to user"},
                          {"role": "user", "content": context}],
                max_tokens=400,
            )
            return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Error analyzing CSV: {e}"
