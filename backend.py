import google.generativeai as genai
import json
from flask import Flask, request, jsonify

# Configure your API key
genai.configure(api_key="AIzaSyClpb1wAURSNnYHPLMOnK6mcNA9lAIL0DM")

# Initialize Flask app
app = Flask(__name__)

# Load the model (Gemini model in your case)
model = genai.GenerativeModel("gemini-1.5-flash")

# Define route to handle POST request from frontend
@app.route('/generate_fitness_plan', methods=['POST'])
def generate_fitness_plan():
    try:
        # Get user data from the frontend request
        user_data = request.json  # This receives the user data as a JSON object from the frontend
        
        # Prepare the prompt based on the received user data
        prompt = f"""
        You are a top-tier personal trainer specializing in fitness and muscle development. Your task is to analyze the following fitness profile and create a highly personalized and detailed fitness plan for the user to achieve their goal of getting a six-pack (abs). The plan should include:
        1. A comprehensive workout routine, including the type of exercises, sets, reps, rest intervals, and any required adjustments based on the user's fitness level.
        2. Intensity recommendations based on current performance metrics and goals, such as increasing strength, endurance, and fat loss.
        3. Personalized recovery strategies, including sleep quality, rest days, and suggestions for minimizing soreness.
        4. Additional dietary and nutrition advice tailored to support muscle definition and fat reduction.
        5. Motivation and tips for consistency, staying positive, and tracking progress.
        6. Ensure the plan is sustainable, easy to follow, and structured to avoid injury and burnout.
        
        Here's the user profile:
        {json.dumps(user_data, indent=2)}

        Generate a complete plan with the following in mind:
        - Focus on the user’s goal of achieving a six-pack.
        - Take into account the user's current fitness level and workout history.
        - Provide a balanced approach to training and recovery.
        - Include clear and actionable steps for every part of the plan.
        """
        
        # Generate AI-based recommendations using Google Gemini model
        response = model.generate_content(prompt)
        
        # Return the AI-generated response as a JSON object
        return jsonify({"fitness_plan": response.text})
    
    except Exception as e:
        # Return an error if something goes wrong
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
