from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import openai

app = Flask(__name__)
app.secret_key = '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'  # Required for session handling

# Toggle this flag to switch between testing mode (mock data) and real API calls
TESTING = False
openai.api_key = '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'  # Replace with your OpenAI API key if testing is False

@app.route('/get-fill-in-the-blank', methods=['GET'])
def get_fill_in_the_blank():
    exercises = session.get('exercises')
    current_exercise = session.get('current_exercise', 0)

    if exercises and current_exercise < len(exercises):
        exercise = exercises[current_exercise]
        if "fill_in_the_blank" in exercise:
            # Return the fill-in-the-blank question as JSON
            return jsonify({
                "word": exercise["word"],
                "fill_in_the_blank": exercise["fill_in_the_blank"]
            })
    return jsonify({"error": "No fill-in-the-blank question available"}), 404

# Mock function to simulate API response for testing purposes
def mock_generate_exercises_from_transcript(transcript):
    return [
        {
            "word": "Photosynthesis",
            "fill_in_the_blank": "Plants perform ______ to convert sunlight into energy.",
            "multiple_choice": {
                "question": "What process do plants use to make food?",
                "options": ["Photosynthesis", "Digestion", "Fermentation", "Respiration"]
            },
            "true_false": "Photosynthesis is a process used by animals to make food."
        },
        {
            "word": "Mitochondria",
            "fill_in_the_blank": "The ______ is known as the powerhouse of the cell.",
            "multiple_choice": {
                "question": "What is the powerhouse of the cell?",
                "options": ["Nucleus", "Chloroplast", "Mitochondria", "Ribosome"]
            },
            "true_false": "The mitochondria produces energy for the cell."
        }
    ]

# Real API call function (used only when TESTING is False)
def real_generate_exercises_from_transcript(transcript):
    prompt = f"""
    You are an educational content generator. The following is a transcript from a video that teaches specific keywords. For each keyword in the video, generate three types of exercise questions:
    1. A fill-in-the-blank sentence using the word.
    2. A multiple-choice question with the correct answer as the word and three incorrect options.
    3. A true-or-false statement using the word.

    The transcript is:
    {transcript}
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "Generate educational exercise questions in a structured format."},
            {"role": "user", "content": prompt}
        ],
        response_format={
            "type": "json_schema",  # Specify the response format type
            "json_schema": {        # Define the expected JSON schema
                "name": "generate_exercises",  # Provide a unique name for the schema
                "type": "object",
                "properties": {
                    "exercises": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "word": {"type": "string"},
                                "fill_in_the_blank": {"type": "string"},
                                "multiple_choice": {
                                    "type": "object",
                                    "properties": {
                                        "question": {"type": "string"},
                                        "options": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    },
                                    "required": ["question", "options"]
                                },
                                "true_false": {"type": "string"}
                            },
                            "required": ["word", "fill_in_the_blank", "multiple_choice", "true_false"]
                        }
                    }
                },
                "required": ["exercises"],
                "additionalProperties": False
            }
        }
    )

    print("API response:", response)

    try:
        exercises = response['choices'][0]['message']['parsed']
        session['exercises'] = exercises['exercises']
        session['current_exercise'] = 0
        return exercises['exercises']
    except (KeyError, TypeError) as e:
        print(f"Error parsing exercises: {e}")
        return None

# Function that either calls the mock function or the real API function
def generate_exercises_from_transcript(transcript):
    if TESTING:
        exercises = mock_generate_exercises_from_transcript(transcript)
        print("Mock exercises loaded:", exercises)  # Add this line
        session['exercises'] = exercises
        session['current_exercise'] = 0
        return exercises
    else:
        return real_generate_exercises_from_transcript(transcript)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        youtube_url = request.form['youtube_url']
        try:
            video_id = get_video_id(youtube_url)
            session['video_id'] = video_id  # Store video ID for embedding
            transcript = get_transcript(video_id)
            print(transcript)
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
    video_id = session.get('video_id')

    print("Current exercises in session:", exercises)  # Add this line
    print("Current exercise index:", current_exercise)  # And this line

    if exercises and current_exercise < len(exercises):
        exercise = exercises[current_exercise]
        question_type = determine_question_type(exercise)

        if question_type == 'fill_in_the_blank':
            return render_template('fill_in_the_blank.html', exercise=exercise, video_id=video_id)
        elif question_type == 'multiple_choice':
            return render_template('multiple_choice.html', exercise=exercise, video_id=video_id)
        elif question_type == 'true_false':
            return render_template('true_false.html', exercise=exercise, video_id=video_id)
    else:
        return "No more exercises."

@app.route('/next-question', methods=['GET'])
def next_question():
    session['current_exercise'] += 1
    exercises = session.get('exercises')
    current_exercise = session.get('current_exercise', 0)

    if exercises and current_exercise < len(exercises):
        exercise = exercises[current_exercise]
        if "fill_in_the_blank" in exercise:
            return jsonify({
                "word": exercise["word"],
                "fill_in_the_blank": exercise["fill_in_the_blank"]
            })
        elif "multiple_choice" in exercise:
            return jsonify({
                "question": exercise["multiple_choice"]["question"],
                "options": exercise["multiple_choice"]["options"],
                "type": "multiple_choice"
            })
        elif "true_false" in exercise:
            return jsonify({
                "statement": exercise["true_false"],
                "type": "true_false"
            })
    return jsonify({"error": "No more questions available"}), 404

def determine_question_type(exercise):
    if "fill_in_the_blank" in exercise:
        return "fill_in_the_blank"
    elif "multiple_choice" in exercise:
        return "multiple_choice"
    elif "true_false" in exercise:
        return "true_false"
    return None

# Helper function to get YouTube video ID from URL
def get_video_id(url):
    import re
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError('Invalid YouTube URL')

# Helper function to get transcript from YouTube video
def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ' '.join([entry['text'] for entry in transcript_list])
        return transcript
    except Exception as e:
        print(f"Error retrieving transcript: {e}")
        return None

if __name__ == '__main__':
    app.run(debug=True)
