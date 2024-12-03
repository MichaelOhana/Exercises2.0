from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import openai
import os
import json
import requests
import base64
from dotenv import load_dotenv
import uuid  # Add this import at the top
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from oauthlib.oauth2 import WebApplicationClient
from models import db, User

load_dotenv()  # Add this near the top of your file

GOOGLE_CLIENT_ID='407009912770-86uea0qh9uvr4gn3umcpflvjfpc8ad0d.apps.googleusercontent.com'

GOOGLE_CLIENT_SECRET='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'

app = Flask(__name__)
app.secret_key = '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'  # Replace with your own secret key
# Toggle this flag to switch between testing mode (mock data) and real API calls
TESTING = True
openai.api_key = os.getenv('OPENAI_API_KEY')  # Ensure your API key is set in the environment variable
ELEVEN_LABS_API_KEY= "sk_509f9a9e1b44d057e5927dfa612289b6a67dcf6207508744"
ELEVEN_LABS_API_KEY = os.getenv('ELEVEN_LABS_API_KEY')  # Remove the hardcoded key
VOICE_ID = "21m00Tcm4TlvDq8ikWAM"  # Rachel voice

# Google OAuth 2.0 credentials
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OAuth 2.0 client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Add these new routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('register'))
        
        user = User(email=email, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/login/google')
def google_login():
    # Find out what URL to hit for Google login
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)

@app.route('/login/google/callback')
def google_callback():
    # Get authorization code Google sent back
    code = request.args.get("code")
    
    # Find out what URL to hit to get tokens
    google_provider_cfg = requests.get(GOOGLE_DISCOVERY_URL).json()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Get tokens
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Get user info from Google
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    if userinfo_response.json().get("email_verified"):
        google_id = userinfo_response.json()["sub"]
        email = userinfo_response.json()["email"]
        name = userinfo_response.json()["given_name"]

        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                email=email,
                name=name,
                google_id=google_id
            )
            db.session.add(user)
            db.session.commit()

        login_user(user)
        return redirect(url_for('index'))
    else:
        flash("Google authentication failed")
        return redirect(url_for('login'))

# Add @login_required decorator to routes that need authentication
@app.route('/', methods=['GET', 'POST'])
@login_required
def show_quiz():
    if request.method == 'POST':
        youtube_url = request.form.get('youtube_url')
        try:
            video_id = get_video_id(youtube_url)
            print(f"Extracted video ID: {video_id}")  # Debugging
            
            transcript = get_transcript(video_id)
            if transcript:
                print(f"Transcript length: {len(transcript)}")  # Debugging
                exercises = generate_exercises_from_transcript(transcript)
                if exercises:
                    return render_template('quiz.html', 
                                        video_id=video_id,
                                        exercises=exercises['exercises'])
                else:
                    return "Failed to generate exercises. Please try again."
            else:
                return "Transcript not available for this video. Please try a different video."
        except ValueError as e:
            return str(e)
        except Exception as e:
            print(f"Error: {str(e)}")  # Debugging
            return f"An error occurred: {str(e)}"
    return render_template('index.html')

@app.route('/quiz', methods=['POST'])
def handle_quiz_submission():
    try:
        # Capture quiz responses
        level = request.form.get('level')
        reason = request.form.get('reason')
        interest = request.form.get('interest')

        # Prepare the OpenAI prompt based on quiz responses
        prompt = f"""
        You are an educational content creator. Based on the following user profile, generate a complete lesson script:
        
        - Professional field: Law
        - Vocabulary Level: {level}
        - Learning Reason: {reason}
        - Vocabulary Interest: {interest}
        
        Create a detailed and engaging lesson script that introduces the topic, teaches vocabulary, and includes a practice activity.
        """

        # Request to OpenAI API
        functions = [
            {
                "name": "generate_lesson_script",
                "description": "Create a complete lesson script in one string.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lesson_script": {
                            "type": "string",
                            "description": "A detailed and engaging lesson script."
                        }
                    },
                    "required": ["lesson_script"],
                    "additionalProperties": False  # Proper placement of additionalProperties
                }
            }
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4-mini",
            messages=[
                {"role": "system", "content": "Generate educational exercise questions."},
                {"role": "user", "content": prompt}
            ],
            functions=functions,
            function_call={"name": "generate_lesson_script"}
        )

        # Extract the generated lesson script
        lesson_script = response['choices'][0]['message']['function_call']['arguments']['lesson_script']

        # Return or render the lesson script
        return render_template('lesson.html', lesson_script=lesson_script)

    except Exception as e:
        print(f"Error generating lesson script: {e}")
        return jsonify({"error": str(e)})


# Function that either calls the mock function or the real API function
def generate_exercises_from_transcript(transcript):
    if TESTING:
        return mock_generate_exercises_from_transcript(transcript)
    else:
        return real_generate_exercises_from_transcript(transcript)

# Helper function to get YouTube video ID from URL
def get_video_id(url):
    import re
    # Handle different YouTube URL formats
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard and shortened URLs
        r'(?:embed\/)([0-9A-Za-z_-]{11})',   # Embed URLs
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})'  # Shortened URLs
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    raise ValueError('Invalid YouTube URL')

# Helper function to get transcript from YouTube video
def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ' '.join([entry['text'] for entry in transcript_list])
        print(transcript)
        return transcript
    except Exception as e:
        print(f"Error retrieving transcript: {e}")
        return None

@app.route('/youtube_url', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        youtube_url = request.form['youtube_url']
        try:
            video_id = get_video_id(youtube_url)
            session['video_id'] = video_id  # Store video ID for embedding
            transcript = get_transcript(video_id)
            if transcript:
                exercises = generate_exercises_from_transcript(transcript)
                if exercises:
                    return redirect(url_for('questions'))
                else:
                    return "Failed to generate exercises."
            else:
                return "Transcript not available."
        except ValueError as e:
            return str(e)
    return render_template('index.html')

@app.route('/questions')
def questions():
    exercises = session.get('exercises')
    current_exercise = session.get('current_exercise', 0)

    if exercises and current_exercise < len(exercises):
        exercise = exercises[current_exercise]
        question_served = session.get('question_served')
        if question_served is None:
            # Serve fill-in-the-blank question
            session['question_served'] = 'fill_in_the_blank'
            return render_template('fill_in_the_blank.html')
        elif question_served == 'fill_in_the_blank':
            # Serve multiple-choice question
            session['question_served'] = 'multiple_choice'
            return render_template('multiple_choice.html')
        elif question_served == 'multiple_choice':
            # Serve true/false question
            session['question_served'] = 'true_false'
            return render_template('true_false.html')
        else:
            # Move to next exercise
            session['question_served'] = None
            session['current_exercise'] += 1
            return redirect(url_for('questions'))
    else:
        return "No more exercises."

@app.route('/get-fill-in-the-blank')
def get_fill_in_the_blank():
    exercises = session.get('exercises')
    current_exercise = session.get('current_exercise', 0)

    if exercises and current_exercise < len(exercises):
        exercise = exercises[current_exercise]
        if "fill_in_the_blank" in exercise:
            return jsonify({
                "word": exercise["word"],
                "fill_in_the_blank": exercise["fill_in_the_blank"]
            })
    return jsonify({"error": "No fill-in-the-blank question available"}), 404

@app.route('/get-multiple-choice')
def get_multiple_choice():
    exercises = session.get('exercises')
    current_exercise = session.get('current_exercise', 0)

    if exercises and current_exercise < len(exercises):
        exercise = exercises[current_exercise]
        if "multiple_choice" in exercise:
            return jsonify({
                "multiple_choice": exercise["multiple_choice"]
            })
    return jsonify({"error": "No multiple-choice question available"}), 404

@app.route('/get-true-false')
def get_true_false():
    exercises = session.get('exercises')
    current_exercise = session.get('current_exercise', 0)

    if exercises and current_exercise < len(exercises):
        exercise = exercises[current_exercise]
        if "true_false" in exercise:
            return jsonify({
                "true_false": exercise["true_false"]
            })
    return jsonify({"error": "No true/false question available"}), 404

@app.route('/questionnaire')
def questionnaire():
    return render_template('questionnaire.html')

# Add this after your other constants
SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'scripts')
os.makedirs(SCRIPTS_DIR, exist_ok=True)

def save_script_data(script_data):
    """Save script data to a file and return the script ID"""
    script_id = str(uuid.uuid4())
    filepath = os.path.join(SCRIPTS_DIR, f"{script_id}.json")
    
    with open(filepath, 'w') as f:
        json.dump(script_data, f)
    
    return script_id

def get_script_data(script_id):
    """Retrieve script data from file"""
    filepath = os.path.join(SCRIPTS_DIR, f"{script_id}.json")
    
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            return json.load(f)
    return None

@app.route('/submit-questionnaire', methods=['POST'])
def submit_questionnaire():
    answers = request.json
    
    try:
        script = generate_vocabulary_script(answers)
        if script:
            # Save script data to file instead of session
            script_id = save_script_data(script)
            # Store only the script ID in session
            session['script_id'] = script_id
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status': 'error', 'message': 'Failed to generate script'}), 500
    except Exception as e:
        print(f"Error generating script: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

AUDIO_DIR = os.path.join(os.path.dirname(__file__), 'static', 'audio')
os.makedirs(AUDIO_DIR, exist_ok=True)  # Create audio directory if it doesn't exist

def get_audio_filename(text, type_prefix):
    """Generate a unique filename for the audio based on the text content"""
    # Create a safe filename from the first few characters of the text
    safe_text = "".join(c for c in text[:30] if c.isalnum()).lower()
    return f"{type_prefix}_{safe_text}.mp3"

def generate_audio_with_timestamps(text, type_prefix='audio'):
    # Generate filename for this audio
    filename = get_audio_filename(text, type_prefix)
    filepath = os.path.join(AUDIO_DIR, filename)
    alignment_path = filepath.replace('.mp3', '_alignment.json')
    
    # Check if audio file already exists
    if os.path.exists(filepath) and os.path.exists(alignment_path):
        print(f"Using cached audio: {filename}")
        with open(filepath, 'rb') as f:
            audio_bytes = f.read()
        
        with open(alignment_path, 'r') as f:
            alignment = json.load(f)
        return audio_bytes, alignment
    
    # If in testing mode and file doesn't exist, return error
    if TESTING:
        print(f"Error: Testing mode - Cannot generate new audio. Missing file: {filename}")
        return None, None
    
    # If not in testing mode and file doesn't exist, generate new audio
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/with-timestamps"
    
    headers = {
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY
    }

    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            return None, None
            
        response_data = response.json()
        
        # Decode audio from base64
        audio_bytes = base64.b64decode(response_data["audio_base64"])
        alignment = response_data["alignment"]
        
        # Save audio file
        with open(filepath, 'wb') as f:
            f.write(audio_bytes)
        
        # Save alignment data
        with open(alignment_path, 'w') as f:
            json.dump(alignment, f)
        
        print(f"Generated and cached new audio: {filename}")
        return audio_bytes, alignment
        
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None, None

def generate_vocabulary_script(answers):
    # Get the vocabulary type and any follow-up answer
    vocab_type = answers.get('vocabulary_type', 'general')
    follow_up_id = f"{vocab_type}_followup"
    follow_up_answer = answers.get(follow_up_id, '')
    
    # Construct the specialized field string
    specialized_field = ''
    if vocab_type == 'business' and follow_up_answer:
        specialized_field = f"Business ({follow_up_answer})"
    elif vocab_type == 'academic' and follow_up_answer:
        specialized_field = f"Academic ({follow_up_answer})"
    elif vocab_type == 'industry' and follow_up_answer:
        specialized_field = f"Industry ({follow_up_answer})"
    else:
        specialized_field = vocab_type

    # Construct the prompt based on user's answers
    prompt = f"""
    Create a vocabulary learning script for a student with the following profile:
    - Proficiency Level: {answers.get('proficiency', 'intermediate')}
    - Main Challenge: {answers.get('struggle', 'vocabulary')}
    - Vocabulary Type: {specialized_field}
    - Learning Goal: {answers.get('main_goal', 'general improvement')}
    
    Generate a script teaching 5 relevant vocabulary words that would be most useful for this student's profile.
    The words should be appropriate for their level and aligned with their learning goals.
    
    Important: Since the student is interested in {specialized_field}, please ensure the vocabulary words are specifically relevant to this field.
    """
    print(prompt)

    # Define the function schema
    function_schema = {
        "name": "generate_vocabulary_lesson",
        "description": "Generate a structured vocabulary lesson script",
        "parameters": {
            "type": "object",
            "properties": {
                "words": {
                    "type": "array",
                    "minItems": 5,
                    "maxItems": 5,
                    "items": {
                        "type": "object",
                        "properties": {
                            "word": {
                                "type": "string",
                                "description": "The vocabulary word"
                            },
                            "definition": {
                                "type": "string",
                                "description": "The definition of the word"
                            },
                            "example_sentence": {
                                "type": "string",
                                "description": "An example sentence using the word in context"
                            },
                            "usage_tip": {
                                "type": "string",
                                "description": "A tip on how to use the word"
                            }
                        },
                        "required": ["word", "definition", "example_sentence", "usage_tip"]
                    }
                }
            },
            "required": ["words"]
        }
    }

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a vocabulary teaching expert."},
                {"role": "user", "content": prompt}
            ],
            functions=[function_schema],
            function_call={"name": "generate_vocabulary_lesson"}
        )

        if response.choices[0].message.get("function_call"):
            function_response = json.loads(
                response.choices[0].message["function_call"]["arguments"]
            )
            
            # Generate audio for each word and its content
            for word_item in function_response["words"]:
                # Generate audio for the word itself
                word_audio, word_alignment = generate_audio_with_timestamps(
                    word_item["word"], 
                    f"word_{word_item['word'].lower()}"
                )
                word_item["word_audio"] = base64.b64encode(word_audio).decode() if word_audio else None
                word_item["word_alignment"] = word_alignment

                # Generate audio for the full explanation
                full_text = f"{word_item['definition']}. For example: {word_item['example_sentence']}. {word_item['usage_tip']}"
                explanation_audio, explanation_alignment = generate_audio_with_timestamps(
                    full_text,
                    f"explanation_{word_item['word'].lower()}"
                )
                word_item["explanation_audio"] = base64.b64encode(explanation_audio).decode() if explanation_audio else None
                word_item["explanation_alignment"] = explanation_alignment

            return function_response
        else:
            print("No function call in response")
            return None

    except Exception as e:
        print(f"OpenAI API error: {e}")
        raise

@app.route('/generating-course')
def generating_course():
    script_id = session.get('script_id')
    if not script_id:
        return redirect(url_for('questionnaire'))
    
    script = get_script_data(script_id)
    if not script:
        return redirect(url_for('questionnaire'))
    
    return render_template('generating_course.html', script=script)

if __name__ == '__main__':
    app.run(debug=True)
