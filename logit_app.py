"""
=============================================================================
PROJECT NAME: Logit - Multi-User Smart Goal Tracking & Analytics System
DEVELOPED FOR: Class 12 Computer Science/IP Project Submission
DESCRIPTION: 
    A full-stack desktop/web application built with Python (Frontend using Streamlit) 
    and SQLite (Backend database). Features multi-account switching, age-adaptive 
    dynamic UI (Child vs Adult themes), glassmorphic visual effects, charts, 
    bulletproof dropdown/form validations, and comprehensive financial analytics.
=============================================================================
"""

import streamlit as st
import sqlite3
import pandas as pd

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & INITIAL SETUP
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Logit - Goal Tracker System",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# 2. DATABASE MANAGEMENT MODULE (SQLITE BACKEND)
# -----------------------------------------------------------------------------
# Establishing persistent database connection with check_same_thread=False for Streamlit safety
conn = sqlite3.connect("logit.db", check_same_thread=False)
cur = conn.cursor()

def initialize_database():
    """
    Creates relational SQLite tables for users and their respective financial goals 
    if they do not already exist. Demonstrates robust backend database structuring.
    """
    # Users table to handle multi-account profiles
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        age INTEGER NOT NULL
    )
    """)

    # Goals table linked via Foreign Key to users table (Relational Database Design)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS goals(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        goal_name TEXT NOT NULL,
        target_amount REAL NOT NULL,
        current_amount REAL DEFAULT 0.0,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)
    conn.commit()

# Initialize tables on load
initialize_database()

# -----------------------------------------------------------------------------
# 3. SESSION STATE MANAGEMENT
# -----------------------------------------------------------------------------
# Initialize session variables to track user state, navigation, and form safety flags
if "current_user_id" not in st.session_state:
    st.session_state.current_user_id = None
if "current_user_name" not in st.session_state:
    st.session_state.current_user_name = None
if "current_user_age" not in st.session_state:
    st.session_state.current_user_age = None
if "form_reset_counter" not in st.session_state:
    st.session_state.form_reset_counter = 0

# Fetch all registered users for account switching functionality
all_users = cur.execute("SELECT id, name, age FROM users").fetchall()

# -----------------------------------------------------------------------------
# 4. AGE-ADAPTIVE DYNAMIC UI & GLASSMORPHIC STYLING MODULE
# -----------------------------------------------------------------------------
# Determine if the active user is a child (Age < 13) to dynamically shift themes
is_kid = False
if st.session_state.current_user_id and st.session_state.current_user_age < 13:
    is_kid = True

if is_kid:
    # Playful, Colorful Kid Theme with Floating Star & Magical Badge Animation Effects
    theme_css = """
    <style>
    .stApp {
        background: linear-gradient(rgba(255, 240, 245, 0.88), rgba(240, 248, 255, 0.88)), 
                    url('https://images.unsplash.com/photo-1513151233558-d860c5398176?q=80&w=1920&auto=format&fit=crop') no-repeat center center fixed;
        background-size: cover;
        font-family: 'Comic Sans MS', cursive, sans-serif;
    }
    h1, h2, h3 {
        color: #FF4B4B !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    /* Glassmorphism Card Effect for Kids */
    .glass-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        border-radius: 20px;
        padding: 20px;
        border: 2px solid #FFD93D;
        box-shadow: 0 8px 32px 0 rgba(255, 107, 107, 0.2);
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(45deg, #FF6B6B, #FFD93D);
        color: white;
        border-radius: 25px;
        font-weight: bold;
        border: none;
        box-shadow: 0px 4px 15px rgba(255, 107, 107, 0.4);
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.08);
        box-shadow: 0px 6px 20px rgba(255, 107, 107, 0.6);
    }
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 240, 245, 0.95);
        border-right: 2px dashed #FF6B6B;
    }
    </style>
    """
else:
    # Sleek, Professional Adult Theme with Neon Glow & Modern Glass Cards
    theme_css = """
    <style>
    .stApp {
        background: linear-gradient(rgba(15, 23, 42, 0.92), rgba(15, 23, 42, 0.92)), 
                    url('https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1920&auto=format&fit=crop') no-repeat center center fixed;
        background-size: cover;
        color: #F8FAFC;
    }
    h1, h2, h3 {
        color: #38BDF8 !important;
        text-shadow: 0 0 12px rgba(56, 189, 248, 0.4);
    }
    /* Sleek Glassmorphism Card Effect for Professionals */
    .glass-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(16px);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(56, 189, 248, 0.2);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 20px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #0ea5e9, #6366f1);
        color: white;
        border-radius: 12px;
        font-weight: 600;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.4);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(99, 102, 241, 0.6);
    }
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.95);
        border-right: 1px solid rgba(56, 189, 248, 0.2);
    }
    </style>
    """

st.markdown(theme_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. SIDEBAR: ACCOUNT SWITCHING & PROFILE MANAGEMENT
# -----------------------------------------------------------------------------
st.sidebar.title("👥 Logit Account Manager")

if all_users:
    user_options = {u[1]: (u[0], u[2]) for u in all_users}
    selected_username = st.sidebar.selectbox("Switch Active Account", ["-- Select Account --"] + list(user_options.keys()))
    
    if selected_username != "-- Select Account --":
        u_id, u_age = user_options[selected_username]
        if st.session_state.current_user_id != u_id:
            st.session_state.current_user_id = u_id
            st.session_state.current_user_name = selected_username
            st.session_state.current_user_age = u_age
            st.rerun()

st.sidebar.markdown("---")
with st.sidebar.expander("➕ Register New User"):
    with st.form("new_user_form"):
        new_u_name = st.text_input("Full Name")
        new_u_age = st.number_input("Age", min_value=1, max_value=120, value=20)
        create_u_btn = st.form_submit_button("Create Account 🚀")
        
        if create_u_btn:
            if new_u_name.strip() == "":
                st.error("Name cannot be empty!")
            else:
                try:
                    cur.execute("INSERT INTO users (name, age) VALUES (?, ?)", (new_u_name, new_u_age))
                    conn.commit()
                    st.success(f"User '{new_u_name}' registered successfully!")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("Account name already exists in database!")

# -----------------------------------------------------------------------------
# 6. WELCOME & ONBOARDING SCREEN (WHEN NO ACCOUNT IS ACTIVE)
# -----------------------------------------------------------------------------
if not st.session_state.current_user_id:
    st.markdown("""
    <div class='glass-card' style='text-align: center;'>
        <h1>📈 Welcome to Logit</h1>
        <p style='font-size: 18px;'>The Advanced Multi-User Financial Goal Tracker & Analytics System.</p>
        <hr style='border-color: rgba(255,255,255,0.1);'>
        <p><b>Please select an existing account from the sidebar or create a new one to begin your tracking journey!</b></p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# -----------------------------------------------------------------------------
# 7. MAIN NAVIGATION MENU (ADAPTIVE BASED ON AGE)
# -----------------------------------------------------------------------------
if is_kid:
    st.sidebar.title(f"🌈 Hi, {st.session_state.current_user_name}! 🦄")
    st.sidebar.info("✨ Welcome to your Magical Piggy Bank!")
    menu = st.sidebar.selectbox(
        "✨ Magical Menu",
        ["Create Goal", "Add Savings", "View Goals", "Delete Goal", "Smart Analytics"]
    )
else:
    st.sidebar.title(f"👤 Active: {st.session_state.current_user_name}")
    st.sidebar.caption(f"Age: {st.session_state.current_user_age} | Mode: Professional")
    menu = st.sidebar.selectbox(
        "Navigation Menu",
        ["Create Goal", "Add Savings", "View Goals", "Delete Goal", "Smart Analytics"]
    )

# -----------------------------------------------------------------------------
# MODULE 1: CREATE GOAL (WITH INPUT VALIDATION)
# -----------------------------------------------------------------------------
if menu == "Create Goal":
    if is_kid:
        st.markdown("<h2>🎨 Create a New Magical Dream Goal!</h2>", unsafe_allow_html=True)
        st.write("What awesome toy or treat are you saving up for?")
    else:
        st.markdown("<h2>🎯 Create Financial Goal</h2>", unsafe_allow_html=True)
        st.write(f"Setting target milestones for account: **{st.session_state.current_user_name}**.")

    with st.form("create_goal_form"):
        goal_name_input = st.text_input("Goal Name (e.g., Lego Set, New Laptop, Emergency Fund)")
        target_amount_input = st.number_input("Target Amount (₹)", min_value=1.0, value=1000.0, step=100.0)
        create_goal_btn = st.form_submit_button("Create Goal 🚀")

        if create_goal_btn:
            if goal_name_input.strip() == "":
                st.error("⚠️ Goal name cannot be empty!")
            else:
                cur.execute(
                    "INSERT INTO goals (user_id, goal_name, target_amount, current_amount) VALUES (?, ?, ?, 0.0)",
                    (st.session_state.current_user_id, goal_name_input.strip(), target_amount_input)
                )
                conn.commit()
                if is_kid:
                    st.success(f"🎉 Woohoo! Magical goal '{goal_name_input}' created successfully!")
                    st.balloons()
                else:
                    st.success("Goal successfully added to the database!")

# -----------------------------------------------------------------------------
# MODULE 2: ADD SAVINGS (WITH STABLE SESSION STATE DROPDOWN SELECTION)
# -----------------------------------------------------------------------------
elif menu == "Add Savings":
    if is_kid:
        st.markdown("<h2>🪙 Add Coins to Your Piggy Bank</h2>", unsafe_allow_html=True)
        st.write("Feed your goals with your savings and earn badges!")
    else:
        st.markdown("<h2>💰 Add Savings Contribution</h2>", unsafe_allow_html=True)
        st.write("Allocate funds toward your active financial goals.")

    # Fetch active user's goals from database
    user_goals = cur.execute("SELECT id, goal_name, target_amount, current_amount FROM goals WHERE user_id = ?", (st.session_state.current_user_id,)).fetchall()

    if user_goals:
        # Create dictionary map for secure dropdown handling
        goal_options_map = {f"{g[1]} (Saved: ₹{g[3]:,.0f} / Target: ₹{g[2]:,.0f})": g[0] for g in user_goals}
        
        selected_goal_label = st.selectbox("Select Target Goal", list(goal_options_map.keys()))
        selected_goal_id = goal_options_map[selected_goal_label]

        savings_amount = st.number_input("Amount to Add (₹)", min_value=1.0, value=500.0, step=50.0)

        if st.button("Confirm & Add Savings ✨"):
            # Update database safely using the mapped goal ID
            cur.execute(
                "UPDATE goals SET current_amount = current_amount + ? WHERE id = ? AND user_id = ?",
                (savings_amount, selected_goal_id, st.session_state.current_user_id)
            )
            conn.commit()
            
            if is_kid:
                st.balloons()
                st.success(f"🌟 Awesome job, {st.session_state.current_user_name}! Added ₹{savings_amount:,.0f} to your treasure! 🦄")
            else:
                st.success("Savings contribution successfully recorded in database!")
    else:
        st.warning("⚠️ No active goals found for this account. Please create a goal first.")

# -----------------------------------------------------------------------------
# MODULE 3: VIEW GOALS (WITH GLASS CARDS, PROGRESS BARS & REMAINING AMOUNTS)
# -----------------------------------------------------------------------------
elif menu == "View Goals":
    if is_kid:
        st.markdown("<h2>🏰 Your Treasure Map & Goals</h2>", unsafe_allow_html=True)
        st.write("Look how close you are to grabbing your magical rewards! ⭐")
    else:
        st.markdown(f"<h2>📊 Goals Dashboard - {st.session_state.current_user_name}</h2>", unsafe_allow_html=True)
        st.write("Real-time tracking of active targets, completed funds, and remaining amounts.")

    user_goals = cur.execute("SELECT goal_name, target_amount, current_amount FROM goals WHERE user_id = ?", (st.session_state.current_user_id,)).fetchall()

    if user_goals:
        for goal, target, current in user_goals:
            progress = min(current / target, 1.0)
            remaining = max(target - current, 0.0)
            
            # Render inside glassmorphism container
            st.markdown(f"""
            <div class='glass-card'>
                <h3>{'🌟 ' + goal if is_kid else '📌 ' + goal}</h3>
                <p><b>Target:</b> ₹{target:,.0f} &nbsp;|&nbsp; <b>Saved:</b> ₹{current:,.0f} &nbsp;|&nbsp; <b>Remaining:</b> ₹{remaining:,.0f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.progress(progress)
            st.write(f"**Completion Status:** {progress * 100:.1f}%")
            
            # Kid badges and celebration reward effects
            if is_kid and progress >= 1.0:
                st.markdown("👑 **BADGE UNLOCKED:** *Master Treasure Hunter!* 🎉")
            elif is_kid and progress >= 0.5:
                st.markdown("⭐ **BADGE UNLOCKED:** *Super Saver Star!* Keep going!")
                
            st.markdown("---")
    else:
        st.info("No goals recorded yet for this account.")

# -----------------------------------------------------------------------------
# MODULE 4: DELETE GOAL (WITH CONFIRMATION CHECKBOX & INPUT VALIDATION)
# -----------------------------------------------------------------------------
elif menu == "Delete Goal":
    if is_kid:
        st.markdown("<h2>🗑️ Remove a Goal</h2>", unsafe_allow_html=True)
        st.write("Finished with a goal or want to clear an old one? You can remove it securely here.")
    else:
        st.markdown("<h2>🗑️ Delete Goal</h2>", unsafe_allow_html=True)
        st.write("Permanently remove obsolete or completed goals from database storage.")

    user_goals = cur.execute("SELECT id, goal_name FROM goals WHERE user_id = ?", (st.session_state.current_user_id,)).fetchall()

    if user_goals:
        goal_delete_map = {g[1]: g[0] for g in user_goals}
        selected_goal_to_delete = st.selectbox("Select Goal to Delete", list(goal_delete_map.keys()))
        
        # Safety confirmation checkbox to prevent accidental deletions
        confirm_deletion = st.checkbox("I confirm that I want to permanently delete this goal.")

        if st.button("Delete Selected Goal ⚠️", type="primary"):
            if confirm_deletion:
                target_delete_id = goal_delete_map[selected_goal_to_delete]
                cur.execute("DELETE FROM goals WHERE id = ? AND user_id = ?", (target_delete_id, st.session_state.current_user_id))
                conn.commit()
                
                if is_kid:
                    st.success(f"Poof! Goal '{selected_goal_to_delete}' has vanished into thin air!")
                else:
                    st.success("Goal successfully deleted from database!")
                st.rerun()
            else:
                st.error("⚠️ Please check the confirmation box before deleting!")
    else:
        st.warning("No goals available for deletion.")

# -----------------------------------------------------------------------------
# MODULE 5: SMART ANALYTICS (CHARTS, METRICS & REMAINING CALCULATION)
# -----------------------------------------------------------------------------
elif menu == "Smart Analytics":
    if is_kid:
        st.markdown("<h2>📈 Milestone Progress Overview & Charts</h2>", unsafe_allow_html=True)
        st.write("Check out your awesome savings growth charts! 🚀")
    else:
        st.markdown("<h2>📈 Financial Analytics & Data Visualization</h2>", unsafe_allow_html=True)
        st.write("Comprehensive summary metrics and graphical distributions of your savings portfolio.")

    user_goals = cur.execute("SELECT goal_name, target_amount, current_amount FROM goals WHERE user_id = ?", (st.session_state.current_user_id,)).fetchall()

    if user_goals:
        # Calculate aggregate metrics
        total_target_val = sum([g[1] for g in user_goals])
        total_saved_val = sum([g[2] for g in user_goals])
        total_remaining_val = max(total_target_val - total_saved_val, 0.0)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Target Portfolio", f"₹{total_target_val:,.0f}")
        with col2:
            st.metric("Total Saved Amount", f"₹{total_saved_val:,.0f}")
        with col3:
            st.metric("Total Remaining Balance", f"₹{total_remaining_val:,.0f}")

        st.markdown("---")
        
        # Prepare Pandas DataFrame for graphical chart visualization
        df_analytics = pd.DataFrame(user_goals, columns=["Goal Name", "Target Amount", "Current Amount"])
        df_analytics["Remaining Amount"] = df_analytics["Target Amount"] - df_analytics["Current Amount"]
        
        st.subheader("📊 Goal-wise Target vs Savings Comparison")
        chart_data = df_analytics.set_index("GoalName" if "GoalName" in df_analytics.columns else "Goal Name")[["Target Amount", "Current Amount"]]
        st.bar_chart(chart_data)
        
        st.markdown("---")
        st.subheader("📋 Detailed Breakdown Table")
        st.dataframe(df_analytics, use_container_width=True)
        
    else:
        st.info("No analytics data available yet. Create goals and add savings to view visual charts.")
