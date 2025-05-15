import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Smart Budgeting App", layout="wide")
st.title("💸 Interactive Smart Budgeting App")

# --- Sidebar Inputs ---
st.sidebar.header("Set Your Monthly Budget & Goals")

monthly_income = st.sidebar.number_input("Monthly Net Income (€)", min_value=0.0, step=50.0, value=1500.0, format="%.2f")
saving_goal = st.sidebar.number_input("Savings Goal (€)", min_value=0.0, step=50.0, value=200.0, format="%.2f")

st.sidebar.markdown("### Category Budgets")
expense_categories = ["🏠 Housing", "📺 Utilities", "🚗 Transportation", "🍜 Groceries", "🎉 Entertainment", "📦 Other"]

category_budgets = {}
for cat in expense_categories:
    category_budgets[cat] = st.sidebar.number_input(f"{cat} Budget (€)", min_value=0.0, step=10.0, value=100.0, format="%.2f")

# --- Session State ---
if "expenses" not in st.session_state:
    st.session_state.expenses = []

# --- Add Expenses by Category ---
st.subheader("➕ Add Expenses by Category")

for cat in expense_categories:
    with st.form(f"form_{cat}"):
        cols = st.columns([4, 1])
        with cols[0]:
            amount_input = st.text_input(f"Enter expense for {cat}", key=f"amount_{cat}")
        with cols[1]:
            add_clicked = st.form_submit_button("Add")
        if add_clicked:
            try:
                amount = float(amount_input.replace(",", "."))
                st.session_state.expenses.append({"Category": cat, "Amount": amount})
                st.success(f"Added €{amount:.2f} to {cat}")
            except ValueError:
                st.error("Please enter a valid number")

# --- Display All Expenses ---
st.markdown("### 🧾 All Expenses")

if st.session_state.expenses:
    updated_expenses = []
    for idx, expense in enumerate(st.session_state.expenses):
        col1, col2, col3 = st.columns([3, 2, 1])
        col1.write(f"{expense['Category']}")
        new_amount = col2.text_input("Amount", value=f"{expense['Amount']:.2f}", key=f"edit_{idx}")
        if col3.button("🗑️", key=f"delete_{idx}"):
            st.session_state.expenses.pop(idx)
            st.rerun()
        else:
            try:
                updated_amount = float(new_amount.replace(",", "."))
                updated_expenses.append({"Category": expense["Category"], "Amount": updated_amount})
            except ValueError:
                updated_expenses.append(expense)
    st.session_state.expenses = updated_expenses

# --- Final Calculation ---
st.markdown("---")
if st.button("🧮 Calculate Budget Overview") and st.session_state.expenses:
    st.markdown("## 📊 Budget Summary")

    expenses_df = pd.DataFrame(st.session_state.expenses)
    total_spent = expenses_df["Amount"].sum()
    savings = monthly_income - total_spent

    col1, col2, col3 = st.columns(3)
    col1.metric("💵 Monthly Income", f"€{monthly_income:.2f}")
    col2.metric("📟 Total Expenses", f"€{total_spent:.2f}")
    col3.metric("💰 Estimated Savings", f"€{savings:.2f}")

    if savings < 0:
        st.error("⚠️ You're spending more than you earn!")
    elif savings >= saving_goal:
        st.success("✅ You've met your savings goal!")
    else:
        st.warning(f"📉 You're €{saving_goal - savings:.2f} away from reaching your savings goal.")

    # Pie Chart
    st.markdown("### 📊 Spending by Category")
    pie_chart = px.pie(expenses_df, names="Category", values="Amount", hole=0.4)
    st.plotly_chart(pie_chart, use_container_width=True)

    # Budget Comparison
    st.markdown("### 📈 Budget Comparison by Category")
    spent_per_cat = expenses_df.groupby("Category")["Amount"].sum().reset_index()
    spent_per_cat["Budget"] = spent_per_cat["Category"].map(category_budgets)
    spent_per_cat["Remaining"] = spent_per_cat["Budget"] - spent_per_cat["Amount"]

    bar_chart = px.bar(spent_per_cat, x="Category", y=["Amount", "Budget"], barmode="group",
                       title="Expenses vs. Budget", labels={"value": "€", "variable": "Type"})
    st.plotly_chart(bar_chart, use_container_width=True)

    # Remaining budget summary
    st.markdown("### 📃 Category Budget Remaining")
    for _, row in spent_per_cat.iterrows():
        category = row["Category"]
        remaining = row["Remaining"]
        if remaining < 0:
            st.error(f"❌ Over budget in {category} by €{abs(remaining):.2f}")
        else:
            st.success(f"✅ You can still spend €{remaining:.2f} in {category}")

    # --- Full Analysis Table ---
    st.markdown("### 🧾 Full Expense Breakdown")

    analysis_df = spent_per_cat.copy()
    analysis_df.rename(columns={"Amount": "Actual Spent", "Budget": "Budgeted", "Remaining": "Remaining Budget"}, inplace=True)
    analysis_df["% of Budget Used"] = (analysis_df["Actual Spent"] / analysis_df["Budgeted"]) * 100
    analysis_df["% of Budget Used"] = analysis_df["% of Budget Used"].apply(lambda x: f"{x:.1f}%")

    for col in ["Budgeted", "Actual Spent", "Remaining Budget"]:
        analysis_df[col] = analysis_df[col].apply(lambda x: f"€{x:.2f}")

    analysis_df = analysis_df[["Category", "Budgeted", "Actual Spent", "Remaining Budget", "% of Budget Used"]]
    st.dataframe(analysis_df, use_container_width=True) 
    
