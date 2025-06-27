import streamlit as st
import pandas as pd
import random
import json
import os
import time
from datetime import date, timedelta, datetime
import matplotlib.pyplot as plt

# --- CONFIG ---
TOTAL_DAYS = 156  # 6 months (approx 6 study days/week)
PROGRESS_FILE = "progress.csv"
STREAK_FILE = "streak.json"
USERNAME = "priteekanase"
PASSWORD = "hazelnuit"

# --- UI CONFIG ---
st.set_page_config(page_title="MedPrep for Pritee 💖", layout="wide")

# --- LOADING SCREEN ---
st.image("https://images.unsplash.com/photo-1519682337058-a94d519337bc", caption="Loading... Studying never looked this good 📚")
st.markdown("<h3 style='text-align: center;'>Booting up your personalized MedPrep dashboard...✨</h3>", unsafe_allow_html=True)
time.sleep(2)

# --- AUTH ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.markdown("## 🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login = st.button("Login")

if not login or username != USERNAME or password != PASSWORD:
    st.warning("Please login to continue.")
    st.stop()

# --- DEFAULT MODULE DATA ---
default_modules = {
    "Anatomy": (6, 84), "Biochemistry": (0, 53), "Phisiology": (2, 62),
    "Pharmacology": (1, 75), "Microbiology": (0, 84), "Pathology": (1, 79),
    "Community Medicine": (0, 100), "Forensic Medicine": (0, 44), "Opthalmology": (0, 52),
    "ENT": (0, 65), "Anaestheasia": (0, 28), "Dermatology": (4, 26), "Psychiatry": (7, 22),
    "Radiology": (4, 42), "Medicine": (60, 202), "Surgery": (32, 84),
    "Orthopaedics": (8, 25), "Paeediatrics": (28, 55), "OBGYN": (28, 111)
}

# --- LOAD PROGRESS ---
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        return pd.read_csv(PROGRESS_FILE)
    else:
        df = pd.DataFrame([{"Module": m, "Watched": w, "Total": t} for m, (w, t) in default_modules.items()])
        df.to_csv(PROGRESS_FILE, index=False)
        return df

# --- LOAD STREAK ---
def load_streak():
    if os.path.exists(STREAK_FILE):
        with open(STREAK_FILE, 'r') as f:
            return json.load(f)
    else:
        return {"last_date": None, "streak": 0}

def save_streak(streak_data):
    with open(STREAK_FILE, 'w') as f:
        json.dump(streak_data, f)

# --- CALCULATE PLAN ---
df = load_progress()
df["Remaining"] = df["Total"] - df["Watched"]
total_remaining = df["Remaining"].sum()
videos_per_day = total_remaining // TOTAL_DAYS if TOTAL_DAYS else 1
df["Weight"] = df["Remaining"] / total_remaining
df["Today"] = (df["Weight"] * videos_per_day).round().astype(int)

# --- STREAK CHECK ---
streak_data = load_streak()
last_date = streak_data.get("last_date")
streak = streak_data.get("streak", 0)

if last_date != str(date.today()) and df["Today"].sum() == 0:
    streak += 1
    streak_data = {"last_date": str(date.today()), "streak": streak}
    save_streak(streak_data)
    st.balloons()

# --- TABS ---
st.title("📚 Med Exam Scheduler for Dr. Pritee 💖")
with st.sidebar:
    st.success(f"🔥 Current Streak: {streak} days")
    st.metric("Remaining Videos", int(df["Remaining"].sum()))
    st.markdown(f"🗓️ Today: {date.today().isoformat()}")

# Tabs
plan_tab, update_tab, chart_tab, calendar_tab, mood_tab = st.tabs([
    "📅 Daily Plan", "✅ Update Progress", "📈 Progress Graph", "🗓️ Calendar", "💌 Motivation"])

# --- DAILY PLAN TAB ---
with plan_tab:
    st.header("🎯 What to Watch Today")
    for _, row in df.iterrows():
        if row["Today"] > 0:
            st.markdown(f"✅ **{row['Module']}** — Watch **{row['Today']}** videos")

# --- UPDATE PROGRESS TAB ---
with update_tab:
    st.header("📈 Update Your Progress")
    edited_df = df.copy()
    for i, row in df.iterrows():
        new_val = st.slider(f"{row['Module']}", 0, row["Total"], int(row["Watched"]))
        edited_df.at[i, "Watched"] = new_val
    if st.button("💾 Save Progress"):
        edited_df.drop(columns=["Remaining", "Weight", "Today"]).to_csv(PROGRESS_FILE, index=False)
        st.success("Progress saved!")

# --- PROGRESS GRAPH TAB ---
with chart_tab:
    st.header("📊 Ideal vs Actual Trajectory")
    watched_total = df["Watched"].sum()
if videos_per_day > 0:
    days_passed = watched_total // videos_per_day
else:
    days_passed = 0

start_day = datetime.today() - timedelta(days=days_passed)

    dates = [start_day + timedelta(days=i) for i in range(TOTAL_DAYS)]
    ideal = [total_remaining - (i * videos_per_day) for i in range(TOTAL_DAYS)]
    actual = [max(total_remaining - df["Watched"].sum(), 0)] + [None]*(TOTAL_DAYS-1)
    
    plt.figure(figsize=(10, 4))
    plt.plot(dates, ideal, label="Ideal Trajectory")
    plt.axhline(y=total_remaining - df["Watched"].sum(), color='r', linestyle='--', label="Current Position")
    plt.xlabel("Date")
    plt.ylabel("Remaining Videos")
    plt.title("Progress Tracker")
    plt.legend()
    st.pyplot(plt)

# --- CALENDAR TAB ---
with calendar_tab:
    st.header("🗓️ Your Study Calendar")
    current_day = date.today()
    calendar_data = []
    for day in range(TOTAL_DAYS):
        videos = int(videos_per_day)
        status = "✅" if (day < streak) else "🔲"
        calendar_data.append({"Date": (current_day + timedelta(days=day)).isoformat(), "Videos": videos, "Status": status})
    cal_df = pd.DataFrame(calendar_data)
    st.dataframe(cal_df)

# --- MOTIVATION TAB ---
with mood_tab:
    st.header("💖 Your Daily Dose")
    quotes = [
        "You’re doing med-iculously well! 🩺",
        "Keep calm and trust your neurons. 🧠",
        "Another day, another diagnosis! 🦠",
        "Brains > Boredom. You got this! 💪",
        "You deserve a caffeine IV drip ☕️💉",
    ]
    st.success(random.choice(quotes))
    st.image("https://media.giphy.com/media/xT0xeJpnrWC4XWblEk/giphy.gif", caption="You're amazing, Pritee!")

