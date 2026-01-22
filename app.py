import streamlit as st
from huggingface_hub import InferenceClient

# --- UI CONFIGURATION ---
st.set_page_config(page_title="OpenStudentFit", page_icon="🥗", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f6; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: HUGGING FACE SETUP ---
with st.sidebar:
    st.title("🛡️ API Settings")
    hf_token = st.text_input("Enter Hugging Face Token", type="password", help="Get your free token at hf.co/settings/tokens")
    model_choice = st.selectbox("Select Open Source Model", [
        "mistralai/Mistral-7B-Instruct-v0.3",
        "meta-llama/Llama-3.2-3B-Instruct",
        "HuggingFaceH4/zephyr-7b-beta"
    ])
    st.info("The Inference API is free but has rate limits.")

# --- APP HEADER ---
st.title("🥗 OpenStudentFit AI")
st.markdown("### Budget-Friendly & Cultural AI Health Planner")

# --- STEP 1: CALCULATIONS ---
def calculate_tdee(weight, height, age, gender, activity):
    # Mifflin-St Jeor Equation
    s = 5 if gender == "Male" else -161
    bmr = (10 * weight) + (6.25 * height) - (5 * age) + s
    multipliers = {"Sedentary": 1.2, "Lightly Active": 1.375, "Moderately Active": 1.55, "Very Active": 1.725}
    return round(bmr * multipliers[activity])

# --- STEP 2: USER INPUTS ---
col1, col2 = st.columns(2)
with col1:
    age = st.number_input("Age", 18, 100, 20)
    gender = st.selectbox("Gender", ["Male", "Female"])
    weight = st.number_input("Weight (kg)", 40, 200, 70)
    height = st.number_input("Height (cm)", 120, 230, 175)

with col2:
    activity = st.selectbox("Activity Level", ["Sedentary", "Lightly Active", "Moderately Active", "Very Active"])
    budget = st.select_slider("Budget", options=["Student/Low", "Moderate", "High"])
    culture = st.text_input("Cuisine (e.g., Nigerian, Indian, Vegan)", "Global")
    equipment = st.text_input("Equipment (e.g., No gym, Dumbbells)", "No gym")

# --- STEP 3: GENERATE PLAN ---
if st.button("Generate My Open-Source Plan"):
    if not hf_token:
        st.warning("⚠️ Please provide a Hugging Face Access Token in the sidebar.")
    else:
        # 1. Calculate Target
        tdee = calculate_tdee(weight, height, age, gender, activity)
        
        # 2. Initialize Hugging Face Client
        client = InferenceClient(model=model_choice, token=hf_token)
        
        # 3. Build Prompt
        prompt = f"""<s>[INST] You are a budget-conscious student health coach. 
        Create a 1-day plan for a student with:
        - Calorie Goal: {tdee} kcal
        - Budget: {budget}
        - Cultural Preference: {culture}
        - Equipment: {equipment}

        Structure your response as follows:
        ### 🍽️ Budget {culture} Meal Plan
        (List Breakfast, Lunch, and Dinner with cheap ingredients)
        
        ### 🏃 Workout ({equipment})
        (List 4-5 exercises)
        
        ### 💡 Student Hack
        (One tip for dorm life)
        [/INST]"""

        with st.spinner(f"Requesting {model_choice}..."):
            try:
                # Call the Inference API
                response = client.text_generation(
                    prompt, 
                    max_new_tokens=800, 
                    temperature=0.7,
                    return_full_text=False
                )
                
                st.success(f"Plan Generated for {tdee} Calories!")
                st.markdown("---")
                st.markdown(response)
                
            except Exception as e:
                st.error(f"Error: {e}. The model might be loading. Try again in 30 seconds.")

