import streamlit as st
import pandas as pd
import random
import json
import time
from datetime import date, datetime, timedelta

st.set_page_config(page_title="MedPrep Scheduler 💉", layout="wide")

# --- LOGIN ---
st.markdown("## 🔒 Welcome to Pritee's Study Scheduler 💖")

with st.form("login_form"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")

# --- CREDENTIAL CHECK ---
if not submit:
    st.stop()

if username != "priteekanase" or password != "hazelnuit":
    st.error("Oops! Wrong username or password 😢")
    st.stop()

# --- CUTE LOADING SCREEN ---
with st.spinner("✨ Warming up your study magic, Pritee... ✨"):
    time.sleep(2)

st.success("Welcome back, Pritee! 🎀 Let's ace this day!")
st.balloons()


# --- CONFIG ---
TOTAL_DAYS = 156  # approx 6 months, assuming 6 study days/week
PROGRESS_FILE = "progress.csv"

# --- INITIAL MODULE DATA ---
default_modules = {
    "Anatomy": (6, 84),
    "Biochemistry": (0, 53),
    "Phisiology": (2, 62),
    "Pharmacology": (1, 75),
    "Microbiology": (0, 84),
    "Pathology": (1, 79),
    "Community Medicine": (0, 100),
    "Forensic Medicine": (0, 44),
    "Opthalmology": (0, 52),
    "ENT": (0, 65),
    "Anaestheasia": (0, 28),
    "Dermatology": (4, 26),
    "Psychiatry": (7, 22),
    "Radiology": (4, 42),
    "Medicine": (60, 202),
    "Surgery": (32, 84),
    "Orthopaedics": (8, 25),
    "Paeediatrics": (28, 55),
    "OBGYN": (28, 111)
}

# --- LOAD OR INIT CSV ---
def load_progress():
    try:
        df = pd.read_csv(PROGRESS_FILE, index_col=0)
    except FileNotFoundError:
        df = pd.DataFrame([
            {"Module": m, "Watched": w, "Total": t}
            for m, (w, t) in default_modules.items()
        ])
        df.set_index("Module", inplace=True)
        df.to_csv(PROGRESS_FILE)
    df["Watched"] = df["Watched"].fillna(0).astype(int)
    df["Total"] = df["Total"].fillna(0).astype(int)
    return df

df = load_progress()

# --- CALCULATE DAILY PLAN ---
df["Remaining"] = df["Total"] - df["Watched"]
total_remaining = df["Remaining"].sum()
videos_per_day = max(total_remaining // TOTAL_DAYS, 1)

# Weighted allocation
df["Weight"] = df["Remaining"] / total_remaining
df["Today"] = (df["Weight"] * videos_per_day).round().astype(int)

# --- TITLE ---
st.title("📚 Med Exam Study Scheduler")
st.subheader("Custom Daily Plan — Just for You 💖")

# --- TODAY'S PLAN ---
st.markdown(f"### 📅 Study Plan for Today ({date.today()})")
for module, row in df.iterrows():
    if row["Today"] > 0:
        st.write(f"**{module}** — Watch **{row['Today']}** videos")

# --- PROGRESS TRACKING ---
st.markdown("### 📈 Update Your Progress")
edited_df = df.copy()
for module, row in df.iterrows():
    total = int(row["Total"]) if not pd.isna(row["Total"]) else 0
    watched = int(row["Watched"]) if not pd.isna(row["Watched"]) else 0
    new_val = st.slider(f"{module}", 0, total, watched)
    edited_df.at[module, "Watched"] = new_val

# --- SAVE PROGRESS ---
if st.button("💾 Save Progress"):
    edited_df_to_save = edited_df.drop(columns=["Remaining", "Weight", "Today"]).reset_index()
    edited_df_to_save.to_csv(PROGRESS_FILE, index=False)
    st.success("Progress saved!")

# --- FUNNY MOTIVATION ---
quotes = [
    "You’re doing med-iculously well! 🩺",
    "Keep calm and trust your neurons. 🧠",
    "Another day, another diagnosis! 🦠",
    "Brains > Boredom. You got this! 💪",
    "You deserve a caffeine IV drip ☕💉",
]
st.markdown("### 😄 Daily Dose of Motivation")
st.info(random.choice(quotes))

# --- PROGRESS BARS ---
st.markdown("### 📊 Module Progress")
for module, row in df.iterrows():
    percent = int((row["Watched"] / row["Total"]) * 100) if row["Total"] > 0 else 0
    st.progress(percent, text=f"{module} ({percent}%)")

# --- STREAK TRACKING ---
st.markdown("### 🔥 Your Study Streak")

STREAK_FILE = "streak.json"

def load_streak():
    try:
        with open(STREAK_FILE, "r") as f:
            return json.load(f)
    except:
        return {"last_date": "", "current": 0, "best": 0}

def save_streak(streak_data):
    with open(STREAK_FILE, "w") as f:
        json.dump(streak_data, f)

today_str = date.today().isoformat()
streak = load_streak()

# Check if a new day has passed
last_date = streak["last_date"]
if last_date != today_str:
    if last_date and (date.fromisoformat(today_str) - date.fromisoformat(last_date)).days == 1:
        streak["current"] += 1
    else:
        streak["current"] = 1
    streak["best"] = max(streak["best"], streak["current"])
    streak["last_date"] = today_str
    save_streak(streak)

# Show current and best streak
st.success(f"🔥 Current Streak: {streak['current']} days")
st.info(f"🏅 Best Streak: {streak['best']} days")

# 🎉 Confetti if hitting 7-day or 14, 21... etc
if streak["current"] in [7, 14, 21, 30, 50, 100]:
    st.balloons()
    st.success("🎉 Woohoo! You hit a streak milestone!")

# --- DAILY STUDY CALENDAR ---
st.markdown("### 📅 6-Month Study Calendar")

calendar = []
current_day = date.today()

daily_plan = []

# Recalculate daily targets
df["Remaining"] = df["Total"] - df["Watched"]
total_remaining = df["Remaining"].sum()
videos_per_day = max(total_remaining // TOTAL_DAYS, 1)
df["Weight"] = df["Remaining"] / total_remaining
df["Daily"] = (df["Weight"] * videos_per_day).round().astype(int)

for day in range(TOTAL_DAYS):
    day_plan = {
        "Date": (current_day + timedelta(days=day)).isoformat(),
        "Plan": {}
    }
    for module, row in df.iterrows():
        if row["Watched"] >= row["Total"]:
            day_plan["Plan"][module] = "✅"
        elif row["Daily"] > 0:
            day_plan["Plan"][module] = f"{int(row['Daily'])} videos"
    daily_plan.append(day_plan)

# Show the next 7 days
st.markdown("#### 🗓️ This Week's Plan")
for i in range(7):
    entry = daily_plan[i]
    st.write(f"**{entry['Date']}**")
    for mod, task in entry["Plan"].items():
        st.markdown(f"- {mod}: **{task}**")
