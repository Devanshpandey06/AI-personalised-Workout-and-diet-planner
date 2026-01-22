import streamlit as st
from openai import OpenAI

# --- UI CONFIGURATION ---
st.set_page_config(page_title="StudentFit AI", page_icon="🎓", layout="centered")

# Custom CSS for a clean look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #FF4B4B; color: white; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: API SETUP ---
with st.sidebar:
    st.title("Settings")
    api_key = st.text_input("Enter OpenAI API Key", type="password")
    st.info("Your key is used only for this session.")

# --- APP HEADER ---
st.title("🎓 StudentFit AI")
st.subheader("Personalized Health for Student Budgets & Lifestyles")

# --- STEP 1: PHYSICAL STATS ---
with st.expander("Step 1: Physical Profile", expanded=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        age = st.number_input("Age", 18, 100, 20)
        gender = st.selectbox("Gender", ["Male", "Female"])
    with col2:
        weight = st.number_input("Weight (kg)", 40, 200, 70)
        height = st.number_input("Height (cm)", 120, 230, 175)
    with col3:
        activity = st.selectbox("Activity Level", [
            "Sedentary", "Lightly Active", "Moderately Active", "Very Active"
        ])

# --- STEP 2: STUDENT CONSTRAINTS ---
with st.expander("Step 2: Student Constraints", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        budget = st.select_slider("Daily Food Budget", options=["Tight (Ramen/Eggs)", "Moderate (Groceries)", "Flexible"])
        culture = st.text_input("Cultural Diet (e.g., Indian Veg, Mediterranean, Halal)", "General")
    with c2:
        equipment = st.multiselect("Available Equipment", ["None (Bodyweight)", "Dumbbells", "Resistance Bands", "Full Gym"])
        allergies = st.text_input("Allergies/Dislikes", "None")

# --- CALCULATION LOGIC ---
def calculate_tdee(weight, height, age, gender, activity):
    # Mifflin-St Jeor Equation
    if gender == "Male":
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5
    else:
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161
    
    multipliers = {"Sedentary": 1.2, "Lightly Active": 1.375, "Moderately Active": 1.55, "Very Active": 1.725}
    return round(bmr * multipliers[activity])

# --- GENERATION LOGIC ---
if st.button("Generate My Personalized Plan"):
    if not api_key:
        st.error("Please enter your OpenAI API Key in the sidebar.")
    else:
        client = OpenAI(api_key=api_key)
        tdee = calculate_tdee(weight, height, age, gender, activity)
        
        with st.spinner("Analyzing constraints and optimizing your plan..."):
            prompt = f"""
            System: You are a high-performance fitness coach and nutritionist specialized in student life.
            User Profile:
            - Daily Calorie Target (TDEE): {tdee} kcal
            - Budget: {budget}
            - Culture/Cuisine: {culture}
            - Equipment: {equipment}
            - Allergies: {allergies}
            
            Task: Provide a 1-day sample plan.
            1. DIET: Must be budget-friendly for a student. Focus on {culture} staples. Include local/cheap protein sources.
            2. WORKOUT: A 30-minute routine using only {equipment}. 
            3. STUDENT TIP: One tip on how to meal prep in a dorm or stay healthy during exams.
            
            Format the response with clear headings and bullet points.
            """

            try:
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.success("Your Plan is Ready!")
                st.markdown("---")
                st.markdown(f"### 🔥 Estimated Daily Burn: {tdee} Calories")
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"An error occurred: {e}")


