import streamlit as st
import pandas as pd
import datetime
import json
import os

st.set_page_config(page_title="Account-Ability", page_icon="💠", layout="centered")

# ---------------- FILES ----------------
DATA_FILE = "ai_memory.json"
LOG_FILE = "ai_log.txt"

def log_event(msg):
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.datetime.now()}] {msg}\n")

class AccountAbilityAI:

    def __init__(self):
        self.expenses = []
        self.memory = self.load_memory()

    def load_memory(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    return json.load(f)
            except:
                log_event("Memory load failed")
        return {"patterns": {}}

    def save_memory(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.memory, f)

    def add_expense(self, category, amount=None):
        try:
            entry = {"Category": category}

            if amount:
                try:
                    amount = float(amount)
                    entry["Amount"] = amount
                except:
                    return "Invalid amount format"

            self.expenses.append(entry)

            self.memory["patterns"][category] = self.memory["patterns"].get(category, 0) + 1
            self.save_memory()

            return f"Added: {category}"

        except:
            log_event("Add expense error")
            return "Error adding expense"

    def analyze(self, salary=None):
        try:
            advice = []

            if salary:
                salary = float(salary)

            df = pd.DataFrame(self.expenses)

            if df.empty:
                return "No expenses added yet."

            # No amounts case
            if "Amount" not in df.columns:
                common = sorted(
                    self.memory["patterns"],
                    key=self.memory["patterns"].get,
                    reverse=True
                )

                advice.append("📊 Based on your habits:")
                advice.append(f"Top categories: {', '.join(common[:3])}")
                advice.append("💡 Reduce frequent spending areas")

                return "\n".join(advice)

            total = df["Amount"].sum()
            balance = salary - total if salary else None

            if salary:
                if total > salary:
                    advice.append("🔴 Overspending detected")
                elif total > salary * 0.8:
                    advice.append("🟡 Spending is high")
                else:
                    advice.append("🟢 Budget is healthy")

            grouped = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
            top_category = grouped.index[0]

            advice.append(f"⚠️ Highest spending: {top_category}")

            df.to_excel("Account_Ability_Report.xlsx", index=False)

            if balance is not None:
                advice.append(f"💰 Balance: {round(balance, 2)}")

            return "\n".join(advice)

        except Exception as e:
            log_event(str(e))
            return "Analysis error"

# ---------------- INIT ----------------
if "ai" not in st.session_state:
    st.session_state.ai = AccountAbilityAI()

ai = st.session_state.ai

# ---------------- UI ----------------
st.title("💠 Account-Ability")
st.caption("Smart • Adaptive • Self-Learning Budget AI")

salary = st.text_input("💵 Monthly Salary (optional)")

st.markdown("---")

st.subheader("➕ Add Expense")

col1, col2 = st.columns(2)

with col1:
    category = st.text_input("Category")

with col2:
    amount = st.text_input("Amount (optional)")

colA, colB, colC = st.columns(3)

with colA:
    if st.button("➕ Add"):
        if category:
            st.success(ai.add_expense(category, amount if amount else None))
        else:
            st.warning("Enter category")

with colB:
    if st.button("📊 Analyze"):
        result = ai.analyze(salary if salary else None)
        st.info(result)

with colC:
    if st.button("🔄 Reset"):
        st.session_state.ai = AccountAbilityAI()
        st.success("Reset complete")

# ---------------- DISPLAY ----------------
if ai.expenses:
    st.markdown("---")
    st.subheader("📋 Expenses")

    df = pd.DataFrame(ai.expenses)
    st.dataframe(df, use_container_width=True)

    if "Amount" in df.columns:
        st.subheader("📊 Spending Overview")
        chart = df.groupby("Category")["Amount"].sum()
        st.bar_chart(chart)

st.markdown("---")
st.caption("⚙️ System Status: Learning & Adapting")