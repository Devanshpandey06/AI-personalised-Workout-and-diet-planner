import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

os.environ["HUGGINGFACEHUB_API_TOKEN"] = "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"

workout_model = ChatHuggingFace(model_id="meta-llama/Llama-2-7b-chat-hf")

diet_model = ChatHuggingFace(model_id="meta-llama/Llama-2-7b-chat-hf")

# bmi and calorie calculations
def calculate_bmi(weight, height_cm):
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 2)

def calorie_needs(weight, height, age, goal):
    bmr = 10 * weight + 6.25 * height - 5 * age + 5
    if goal == "Fat Loss":
        return int(bmr * 1.2 - 400)
    elif goal == "Muscle Gain":
        return int(bmr * 1.2 + 300)
    return int(bmr * 1.2)
st.set_page_config(page_title="AI Fitness Planner", layout="centered")
st.title("🏋️ AI Personalized Workout & Diet Planner")

age = st.number_input("Age", 16, 40)
height = st.number_input("Height (cm)")
weight = st.number_input("Weight (kg)")
goal = st.selectbox("Goal", ["Fat Loss", "Muscle Gain", "Maintain"])
diet = st.selectbox("Diet Preference", ["Veg", "Non-Veg", "Eggitarian"])
equipment = st.selectbox("Equipment", ["None", "Dumbbells", "Gym"])
time = st.slider("Daily Workout Time (min)", 15, 60)
budget = st.slider("Daily Food Budget (₹)", 100, 500)

# template

workout_prompt = PromptTemplate(
    template="""
You are an expert fitness coach.
Create a weekly workout plan for a student.

Age: {age}
Goal: {goal}
Equipment: {equipment}
Daily workout time: {time} minutes

Requirements:
- Student-friendly
- Progressive
- Home-based if no equipment
- Clear exercises + reps
""",
input_variables=["age", "goal", "equipment", "time"]
)
# fill the placeholders
Workout_prompt = workout_prompt.invoke({
    "age":age,
    "goal":goal,
    "equipment":equipment,
    "time":time
})
calories = calorie_needs(weight, height, age, goal)
diet_prompt = PromptTemplate(
    template="""
You are a certified Indian nutritionist.

Create a daily meal plan:
Diet type: {diet}
Daily budget: ₹{budget}
Target calories: {calories}

Rules:
- Indian meals only
- Hostel-friendly
- High protein
- Affordable & practical
""",
input_variables=["diet", "budget", "calories"]
)
Diet_prompt = diet_prompt.invoke({
    "diet":diet,
    "budget":budget,
    "calories":calories
})




if st.button("Generate My Plan"):
    bmi = calculate_bmi(weight, height)
    st.subheader("📊 Your Stats")
    st.write(f"**BMI:** {bmi}")
    st.write(f"**Daily Calories Target:** {calories}")
    
    workout = workout_model.invoke("what is capital of india")
    
    diet_plan = diet_model.invoke(Diet_prompt)

    

    st.subheader("🏋️ Workout Plan")
    st.write(workout.content)

    st.subheader("🍛 Diet Plan")
    st.write(diet_plan.content)



