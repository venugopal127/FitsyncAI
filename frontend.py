import streamlit as st
import requests  # For backend API requests to fetch LLM responses
import pymongo
from pymongo import MongoClient
import datetime

# MongoDB setup
def get_mongo_client():
    try:
        client = MongoClient('mongodb://localhost:27017/')  # Connect to the local MongoDB instance
        db = client['Fitness']  # Database: Fitness
        collection = db['plan']  # Collection: plan
        return collection
    except Exception as e:
        st.error(f"Error connecting to MongoDB: {e}")
        return None

# Function to store response in MongoDB
def store_response_in_mongo(response, user_data):
    collection = get_mongo_client()
    
    # If MongoDB connection failed, return early
    if collection is None:
        return
    
    try:
        # Creating the document to store
        document = {
            "user_data": user_data,
            "fitness_plan": response,
            "timestamp": datetime.datetime.now()  # Add timestamp for when the document was created
        }
        
        # Insert the document into the MongoDB collection
        collection.insert_one(document)
        st.success("Response successfully saved to MongoDB!")
        print(f"Document inserted: {document}")  # Debugging line to check document inserted
    except Exception as e:
        st.error(f"Error inserting data into MongoDB: {e}")
        print(f"Error inserting data into MongoDB: {e}")  # Debugging line for error

# Function to send data to backend and get LLM response
def send_to_backend(user_data):
    backend_url = "http://127.0.0.1:5000/generate_fitness_plan"  # Replace with your backend URL
    try:
        response = requests.post(backend_url, json=user_data)
        
        if response.status_code == 200:
            print(f"Backend response: {response.json()}")  # Debugging line to check the response from backend
            return response.json()  # Assuming response is in JSON format
        else:
            st.error(f"Failed to get a response from LLM. Status Code: {response.status_code}")
            print(f"Failed to get a response. Status Code: {response.status_code}")  # Debugging line
            return None
    except Exception as e:
        st.error(f"Error while sending data to the backend: {e}")
        print(f"Error while sending data to the backend: {e}")  # Debugging line
        return None

st.set_page_config(page_title="FitSync AI", layout="wide")

# Custom CSS for sticky navbar, smooth scrolling, and section styling
st.markdown(
    """
    <style>
        html, body, .main, [data-testid="stAppViewContainer"] {
        background-color: #e9dbf0 !important;
    }
        .navbar {
            position: -webkit-sticky;
            position: sticky;
            top: 0;
            background-color: #e2d0ea;
            padding: 10px;
            text-align: center;
            box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
            z-index: 1000;
        }
        #bmi {
            background-image: url('bmi-bc.jpg');
            background-size: cover;
            background-position: center;
        }
        #workout {
            background-image: url('background.jpg');
            background-size: cover;
            background-position: center;
        }
        #diet {
            background-image: url('diet.jpg');
            background-size: cover;
            background-position: center;
        }
        .navbar a {
            margin: 0 15px;
            text-decoration: none;
            font-size: 18px;
            color: #7119a0;
            font-weight: bold;
            cursor: pointer;
        }
        .navbar a:hover {
            color: #35044f;
        }
        html { scroll-behavior: smooth; }
        .content-container {
            display: flex;
            align-items: center;
        }
        .text-content {
            flex: 1;
            text-align: left;
            padding-right: 20px;
            font-size: 20px;
            color: #6e6075;
        }
        .image-content img {
            width: 300px;
            border-radius: 10px;
            }
        .textarea {
            width: 50%;
            height: 50px;
        }
        div.stButton > button {
        background-color: #b07fc8; 
        color: black;
    }
    </style>
    <div class='navbar'>
        <a href='#introduction'>Introduction</a>
        <a href='#bmi'>BMI Calculations</a>
        <a href='#workout'>Workout Plans</a>
    </div>
    """,
    unsafe_allow_html=True
)

def show_user_profile():
    # Initialize session state variables if not already initialized
    if 'age' not in st.session_state:
        st.session_state.age = 25
    if 'gender' not in st.session_state:
        st.session_state.gender = "Male"
    if 'fitness_level' not in st.session_state:
        st.session_state.fitness_level = "Intermediate"
    if 'weight' not in st.session_state:
        st.session_state.weight = 75.0
    if 'height' not in st.session_state:
        st.session_state.height = 175.0
    if 'goal' not in st.session_state:
        st.session_state.goal = "Six Pack (Abs)"
    
    st.markdown("<div id='user_data' class='section'>", unsafe_allow_html=True)
    st.markdown("<h2>User Profile</h2>", unsafe_allow_html=True)
    
    # Collect user data
    st.session_state.age = st.number_input("Enter your age", min_value=1, max_value=120, step=1, value=st.session_state.age, key="age_input")
    st.session_state.gender = st.selectbox("Select your gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(st.session_state.gender), key="gender_select")
    st.session_state.fitness_level = st.selectbox("Select your fitness level", ["Beginner", "Intermediate", "Advanced"], index=["Beginner", "Intermediate", "Advanced"].index(st.session_state.fitness_level), key="fitness_level_select")
    st.session_state.weight = st.number_input("Enter your weight (kg)", min_value=1.0, format="%.2f", value=st.session_state.weight, key="weight_input")
    st.session_state.height = st.number_input("Enter your height (cm)", min_value=50.0, format="%.1f", value=st.session_state.height, key="height_input")
    st.session_state.goal = st.text_input("Your Fitness Goal", st.session_state.goal, key="goal_input")
    
    st.markdown("### Workout History")
    if 'workouts' not in st.session_state:
        st.session_state.workouts = []
    
    # Select exercise type
    exercise_options = ["Squat", "Bench Press", "Deadlift", "Pull-up", "Push-up", "Lunges", "Plank"]
    exercise = st.selectbox("Select an Exercise", exercise_options, key="exercise_select")
    
    # Input for exercise duration
    duration = st.number_input("Enter Duration (min)", min_value=1, value=30, key="duration_input")
    
    # Input for exercise intensity
    intensity = st.selectbox("Select Intensity", ["Low", "Medium", "High"], index=1, key="intensity_select")
    
    # Button to add the workout
    if st.button("Add Workout", key="add_workout_button"):
        workout = {
            "exercise": exercise,
            "duration": duration,
            "intensity": intensity
        }
        st.session_state.workouts.append(workout)
    
    # Display added workouts
    if st.session_state.workouts:
        st.write("### Added Workouts:")
        for workout in st.session_state.workouts:
            st.write(f"**Exercise:** {workout['exercise']} | **Duration:** {workout['duration']} min | **Intensity:** {workout['intensity']}")
    
    st.markdown("</div>", unsafe_allow_html=True)

def show_features():
    st.markdown("<div id='introduction' class='section'>", unsafe_allow_html=True)
    st.markdown("<h2>Introduction</h2>", unsafe_allow_html=True)
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""<div class='text-content'>
            FitSync AI is your smart fitness companion that adapts to your lifestyle, helping you achieve your health goals efficiently.
            Leveraging cutting-edge artificial intelligence, our platform offers real-time fitness tracking, adaptive workout plans, and 
            personalized diet recommendations. Whether you are looking to lose weight, build muscle, or simply maintain a balanced lifestyle, 
            FitSync AI ensures you stay on the right path. Let's embark on a journey to a healthier you!
        </div>""", unsafe_allow_html=True)
    with col2:
        st.image("nextbc.jpg", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

def show_bmi_calculations():
    st.markdown("<div id='bmi' class='section'>", unsafe_allow_html=True)
    st.markdown("<h2>BMI Calculations</h2>", unsafe_allow_html=True)
    
    age = st.number_input("Enter your age", min_value=1, max_value=120, step=1, key="bmi_age_input")
    gender = st.selectbox("Select your gender", ["Male", "Female", "Other"], key="bmi_gender_select")
    weight = st.number_input("Enter your weight (kg)", min_value=1.0, format="%.2f", key="bmi_weight_input")
    
    # Separate inputs for feet and inches
    height_ft = st.number_input("Enter your height (feet)", min_value=1, max_value=8, step=1, value=5, key="height_ft_input")
    height_in = st.number_input("Enter additional inches", min_value=0, max_value=11, step=1, value=7, key="height_in_input")

    # Convert height to cm
    height_in_inches = height_ft * 12 + height_in
    height_cm = height_in_inches * 2.54  # Convert inches to cm

    # BMI calculation
    if weight > 0 and height_cm > 0:
        bmi = weight / (height_cm / 100) ** 2
        st.write(f"BMI: {bmi:.2f}")
    st.markdown("</div>", unsafe_allow_html=True)

def show_workout_plans():
    st.markdown("<div id='workout' class='section'>", unsafe_allow_html=True)
    st.markdown("<h2>Workout Plans</h2>", unsafe_allow_html=True)
    st.markdown("### Tailored to your needs")
    st.markdown("</div>", unsafe_allow_html=True)

def show_diet_plan():
    st.markdown("<div id='diet' class='section'>", unsafe_allow_html=True)
    st.markdown("<h2>Diet Plan</h2>", unsafe_allow_html=True)
    st.markdown("### Nutrition is key to success")
    st.markdown("</div>", unsafe_allow_html=True)

def display_llm_response():
    st.markdown("<div id='llm_response' class='section'>", unsafe_allow_html=True)
    st.markdown("<h2>Response from AI</h2>", unsafe_allow_html=True)
    
    if st.button("Get AI Response"):
        # Assuming we collect user data
        user_data = {
            "age": st.session_state.age,
            "gender": st.session_state.gender,
            "fitness_level": st.session_state.fitness_level,
            "weight": st.session_state.weight,
            "height": st.session_state.height,
            "goal": st.session_state.goal
        }
        response = send_to_backend(user_data)
        
        if response:
            # Assuming response is the full fitness plan text
            full_response = response.get("fitness_plan", "")
            
            # Store response in MongoDB
            store_response_in_mongo(full_response, user_data)
            
            # Split the full response by Roman numerals (e.g., I., II., III., IV., V.)
            sections = full_response.split("\n\n")  # Assuming each section is separated by an empty line
            
            for section in sections:
                if section.startswith("I."):
                    st.markdown("## I. Workout Routine (3 days/week)")
                elif section.startswith("II."):
                    st.markdown("## II. Recovery Strategies")
                elif section.startswith("III."):
                    st.markdown("## III. Nutrition and Diet")
                elif section.startswith("IV."):
                    st.markdown("## IV. Motivation and Progress Tracking")
                elif section.startswith("V."):
                    st.markdown("## V. Important Considerations")
                
                # Display the section content
                st.markdown(section)
    
    st.markdown("</div>", unsafe_allow_html=True)


# Display sections
show_features()
show_bmi_calculations()
show_workout_plans()
show_diet_plan()
show_user_profile()
display_llm_response()
