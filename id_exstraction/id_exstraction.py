from flask import Flask, request, render_template, redirect, url_for, session
from youtube_transcript_api import YouTubeTranscriptApi
import openai

app = Flask(__name__)
app.secret_key = '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'  # Required for session handling

openai.api_key = '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'  # Replace with your OpenAI API key

# Function to get transcript from YouTube video
def get_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ' '.join([entry['text'] for entry in transcript_list])
        return transcript
    except Exception as e:
        print(f"Error retrieving transcript: {e}")
        return None

# Function to extract video ID from URL
def get_video_id(url):
    import re
    pattern = r'(?:v=|\/)([0-9A-Za-z_-]{11}).*'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError('Invalid YouTube URL')

# Function to generate exercises from transcript
def generate_exercises_from_transcript(transcript):
    prompt = f"""
    You are an educational content generator. The following is a transcript from a video that teaches specific keywords. For each keyword in the video, generate three types of exercise questions:
    1. A fill-in-the-blank sentence using the word.
    2. A multiple-choice question with the correct answer as the word and three incorrect options.
    3. A true-or-false statement using the word.

    The transcript is:
    {transcript}
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Generate educational exercise questions in a structured format."},
            {"role": "user", "content": prompt}
        ],
        functions=[{
            "name": "generate_exercises",
            "parameters": {
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
                                    }
                                },
                                "true_false": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }],
        function_call="auto"
    )

    # Debug print to inspect the actual API response structure
    print("API response:", response)

    try:
        # Check if the response has the expected function_call structure
        if response['choices'][0]['finish_reason'] == 'function_call':
            exercises_data = response['choices'][0]['message']['function_call']['arguments']
            exercises = exercises_data.get('exercises', [])
            session['exercises'] = exercises  # Store exercises in session for display in the questions route
            return exercises
        else:
            print("Unexpected API response format.")
            return None
    except (KeyError, TypeError) as e:
        print(f"Error parsing exercises: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
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
                    session['current_exercise'] = 0  # Track the current exercise
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

    if exercises and current_exercise < len(exercises):
        exercise = exercises[current_exercise]
        return render_template('questions.html', exercise=exercise, video_id=video_id)
    else:
        return "No more exercises."

@app.route('/next_exercise', methods=['POST'])
def next_exercise():
    session['current_exercise'] += 1
    return redirect(url_for('questions'))

if __name__ == '__main__':
    app.run(debug=True)
