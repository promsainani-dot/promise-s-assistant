import os
from flask import Flask, render_template, request, jsonify, session
from groq import Groq
from dotenv import load_dotenv  

# Load local .env variables
load_dotenv() 

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "promise_local_key")

# --- MODIFIED SECTION ---
# This checks Vercel first, then falls back to your key if the local environment fails
api_key = os.environ.get("GROQ_API_KEY") 
client = Groq(api_key=api_key)
# ------------------------

SYSTEM_PROMPT = """
You are Promise's Assistant. 

Rules:
1. ONLY answer the specific question asked. Do not volunteer extra info.
2. Do NOT mention prices, locations, or personal details unless the user asks for them.
3. Keep every response under 2 sentences.
4. If a user says "hi" or "bho", just say "Hi! How can I help you today?"
- Personal info:
    Name: Promise Sainani
    Age: 23
    Gender: Male
    Relationship: Single
    Location: Area 25 Sector 4, Lilongwe
    Studies: Automobile Mechanics at Lilongwe Technical College
    Qualification: MSCE, Certificate in Motorcycle Mechanics
    Languages: Chichewa and English
    Religion: Jehovah's Witnesses
    Experience: 4 years in graphic design
    Flyer price: K15,000
    Logo price: K15,000 (negotiable)
    WhatsApp: 0995 51 15 597
- Add humor naturally.
- Local Flavor:
   "bho" -> "bhobho 😄"
   "muli bwanji" -> "ndili bwino kaya inu? 😊"
- Stay professional but friendly.
"""

@app.route("/")
def home():
    session["messages"] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return render_template("index.html")

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get("message")
    
    if "messages" not in session:
        session["messages"] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    session["messages"].append({"role": "user", "content": user_input})

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=session["messages"]
        )
        
        reply = response.choices[0].message.content
        session["messages"].append({"role": "assistant", "content": reply})
        session.modified = True
        
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({"reply": "I'm having a bit of trouble connecting right now."})

# Required for Vercel
# Replace 'app = app' with this to troubleshoot locally:
if __name__ == "__main__":
    print("Starting Promise's Assistant server...")
    app.run(debug=True, port=5000)
else:
    # This part is for Vercel
    app = app