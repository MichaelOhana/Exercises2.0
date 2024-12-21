from flask import Flask, request, render_template, redirect, url_for, session, jsonify, flash
import openai
import os
import json
import requests
import base64
import uuid
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from oauthlib.oauth2 import WebApplicationClient
from .models import db, User
from oauthlib.oauth2.rfc6749.errors import InsecureTransportError
from flask import Blueprint
from .config import *  # Import all config variables

# Create blueprint
main_bp = Blueprint('main', __name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = SECRET_KEY  # Use from config

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

# Toggle this flag to switch between testing mode (mock data) and real API calls
TESTING = True

# Other API configurations
ELEVEN_LABS_API_KEY = os.getenv('ELEVEN_LABS_API_KEY')
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

# Move these routes to use main_bp instead of app
@main_bp.route('/')
@login_required
def index():
    return redirect(url_for('main.default_course'))

@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get('next')
            # Make sure the next_page is a relative URL
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('main.default_course')
            return redirect(next_page)
        
        flash('Invalid email or password')
    return render_template('login.html')

@main_bp.route('/register', methods=['GET', 'POST'])
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
        return redirect(url_for('main.default_course'))
    return render_template('register.html')

@main_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main_bp.route('/login/google')
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

@main_bp.route('/login/google/callback')
def google_callback():
    try:
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
            name = userinfo_response.json().get("given_name", email)

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
            return redirect(url_for('main.default_course'))
        else:
            flash("Google authentication failed - Email not verified")
            return redirect(url_for('login'))
            
    except Exception as e:
        print(f"Error in Google callback: {str(e)}")
        flash(f"Failed to log in with Google: {str(e)}")
        return redirect(url_for('login'))

# Move the YouTube URL functionality to a different route
@app.route('/youtube-exercises', methods=['GET', 'POST'])
@login_required
def youtube_exercises():
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
def youtube_url_handler():
    if request.method == 'POST':
        youtube_url = request.form['youtube_url']
        try:
            video_id = get_video_id(youtube_url)
            session['video_id'] = video_id  # Store video ID for embedding
            transcript = get_transcript(video_id)
            if transcript:
                exercises = generate_exercises_from_transcript(transcript)
                if exercises:
                    return redirect(url_for('main.questions'))
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

@main_bp.route('/questionnaire')
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

@main_bp.route('/submit-questionnaire', methods=['POST'])
def submit_questionnaire():
    answers = request.json
    
    try:
        print("Received answers:", answers)
        script = generate_vocabulary_script(answers)
        if script:
            script_id = save_script_data(script)
            session['script_id'] = script_id
            # Make sure we're using the correct URL for word assessment
            redirect_url = url_for('main.word_assessment')
            print(f"Redirecting to: {redirect_url}")  # Debug print
            return jsonify({
                'status': 'success', 
                'redirect': redirect_url
            })
        else:
            print("Failed to generate script - script is None")
            return jsonify({'status': 'error', 'message': 'Failed to generate script - no content returned'}), 500
    except Exception as e:
        import traceback
        print(f"Error generating script: {str(e)}")
        print("Full traceback:")
        print(traceback.format_exc())
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
    print(f"Debug - Using OpenAI API key in generate_vocabulary_script: {openai.api_key[:10]}...")
    
    # Get the vocabulary type and any follow-up answer
    vocab_type = answers.get('job_area', 'general')  # Changed from vocabulary_type to job_area
    follow_up_id = f"{vocab_type}_role"  # Changed to match your questionnaire structure
    follow_up_answer = answers.get(follow_up_id, '')
    
    # Construct the specialized field string
    specialized_field = ''
    if vocab_type == 'business' and follow_up_answer:
        specialized_field = f"Business ({follow_up_answer})"
    elif vocab_type == 'technology' and follow_up_answer:
        specialized_field = f"Technology ({follow_up_answer})"
    else:
        specialized_field = vocab_type

    # Construct the prompt based on user's answers
    prompt = f"""
    Create a vocabulary learning script for a student with the following profile:
    - Native Language: {answers.get('native_language', 'Not specified')}
    - Target Language: {answers.get('target_language', 'English')}
    - Current Level: {answers.get('current_level', 'intermediate')}
    - Main Struggles: {', '.join(answers.get('struggles', []))}
    - Professional Field: {specialized_field}
    - Confidence Goals: {', '.join(answers.get('confidence_situations', []))}
    - Learning Preferences: {', '.join(answers.get('learning_preferences', []))}
    - Specific Topics: {answers.get('specific_topics', 'Not specified')}
    
    Generate a script teaching 5 relevant vocabulary words that would be most useful for this student's profile.
    The words should be appropriate for their level and aligned with their learning goals.
    
    Important: Since the student works in {specialized_field}, please ensure the vocabulary words are specifically relevant to this field.
    """
    print("Generated prompt:", prompt)

    # Define the JSON schema for structured output
    json_schema = {
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

    try:
        # Force the API key from config
        from .config import OPENAI_API_KEY
        openai.api_key = OPENAI_API_KEY
        
        print("Making OpenAI API call with key:", openai.api_key[:10], "...")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a vocabulary teaching expert. Return your response as a JSON object."
                },
                {
                    "role": "user",
                    "content": f"Generate a JSON response for the following request:\n{prompt}"
                }
            ],
            response_format={"type": "json_object"},
            functions=[{
                "name": "generate_vocabulary_lesson",
                "parameters": json_schema
            }]
        )
        print("OpenAI API response received:", response.choices[0].message)

        # Parse the response
        if response.choices[0].message.function_call:
            function_response = json.loads(
                response.choices[0].message.function_call.arguments
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

@main_bp.route('/generating-course')
def generating_course():
    script_id = session.get('script_id')
    if not script_id:
        return redirect(url_for('main.questionnaire'))
    
    script = get_script_data(script_id)
    if not script:
        return redirect(url_for('main.questionnaire'))
    
    return render_template('generating_course.html', script=script)

@main_bp.route('/course/<course_id>')
def course_page(course_id):
    # Updated course data with welcome section
    course_structure = {
        'title': 'Your Personalized Language Course',
        'units': [
            {
                'id': 1,
                'title': 'Getting Started',
                'expanded': True,  # This unit starts expanded
                'content': [
                    {
                        'id': 1, 
                        'type': 'welcome', 
                        'title': 'Welcome to Your Course', 
                        'active': True  # This makes it selected by default
                    },
                    {
                        'id': 2, 
                        'type': 'lesson', 
                        'title': 'First Lesson'
                    }
                ]
            }
        ]
    }
    return render_template('course.html', course=course_structure)

@main_bp.route('/course')
def default_course():
    return redirect(url_for('main.course_page', course_id='default'))

@app.route('/api/content/<content_type>/<int:content_id>')
def get_content(content_type, content_id):
    if content_type == 'welcome':
        # Get the user's assessment results from session
        assessment = session.get('word_assessment', {})
        known_words = assessment.get('known_words', [])
        unknown_words = assessment.get('unknown_words', [])
        
        content = {
            'title': 'Welcome to Your Personalized Course',
            'introduction': '''
                <div class="welcome-content">
                    <h2>Your Learning Journey Begins!</h2>
                    <p>Based on your assessment, we've created a personalized learning path for you.</p>
                    
                    <div class="assessment-summary">
                        <h3>Your Vocabulary Assessment Results:</h3>
                        <ul>
                            <li>Words you know well: {}</li>
                            <li>Words to learn: {}</li>
                        </ul>
                    </div>
                    
                    <p>We'll focus on strengthening your vocabulary in these areas while introducing new concepts 
                    that match your learning goals.</p>
                    
                    <div class="next-steps">
                        <h3>What's Next?</h3>
                        <p>Click the "Next" button to begin your first lesson!</p>
                    </div>
                </div>
            '''.format(len(known_words), len(unknown_words))
        }
        return jsonify(content)
    
    # ... rest of your existing content types ...

@main_bp.route('/word-assessment')
def word_assessment():
    print("Accessing word assessment route")  # Debug print
    script_id = session.get('script_id')
    print(f"Script ID from session: {script_id}")  # Debug print
    
    if not script_id:
        print("No script ID found, redirecting to questionnaire")  # Debug print
        return redirect(url_for('main.questionnaire'))
    
    script = get_script_data(script_id)
    if not script:
        print("No script data found, redirecting to questionnaire")  # Debug print
        return redirect(url_for('main.questionnaire'))
    
    # Transform script data into the format expected by the template
    vocabulary = {
        'words': [
            {
                'word': word['word'],
                'definition': word['definition'],
                'example': word['example_sentence'],
                'usage_tip': word['usage_tip'],
                'difficulty': 3,  # You could calculate this based on word complexity
                'native_translation': ''  # You could add translation if needed
            }
            for word in script['words']
        ]
    }
    print(f"Rendering word assessment with vocabulary: {vocabulary}")  # Debug print
    
    return render_template('word_assessment.html', vocabulary=vocabulary)

@main_bp.route('/submit-assessment', methods=['POST'])
def submit_assessment():
    data = request.json
    word = data.get('word')
    is_known = data.get('known')
    
    # Initialize the assessment data structure if it doesn't exist
    if 'word_assessment' not in session:
        session['word_assessment'] = {
            'known_words': [],
            'unknown_words': []
        }
    
    # Add the word to the appropriate list
    if is_known:
        session['word_assessment']['known_words'].append(word)
    else:
        session['word_assessment']['unknown_words'].append(word)
    
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables
    app.run(debug=True)
