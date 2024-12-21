import os
from dotenv import load_dotenv
from pathlib import Path

# Get the absolute path to the root directory
root_dir = Path(__file__).resolve().parent.parent

# Load environment variables from the root .env file
env_path = os.path.join(root_dir, '.env')
load_dotenv(env_path)

# Debug prints
print("\nEnvironment Variable Loading Debug:")
print(f"Loading from: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        env_content = f.read()
        print("First few chars of .env content:", env_content[:50])
        # Check if the correct key exists in the file
        if 'OPENAI_API_KEY=sk-proj-' in env_content:
            print("Found correct API key format in .env file")
        else:
            print("WARNING: Correct API key format not found in .env file")

# Clear any existing OpenAI API key from environment
if 'OPENAI_API_KEY' in os.environ:
    del os.environ['OPENAI_API_KEY']
if 'OPENAPI_API_KEY' in os.environ:
    del os.environ['OPENAPI_API_KEY']

# Load the key fresh from .env
load_dotenv(env_path, override=True)

# Get and verify the API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
print(f"Final OpenAI API key being used: {OPENAI_API_KEY[:10]}...")

if not OPENAI_API_KEY or not OPENAI_API_KEY.startswith('sk-proj-'):
    raise ValueError(
        "Invalid OpenAI API key format. Please ensure your .env file contains the correct key starting with 'sk-proj-'"
    )

# Flask Configuration
SECRET_KEY = os.getenv('SECRET_KEY')

# Database Configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///users.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Other API Keys
ELEVEN_LABS_API_KEY = os.getenv('ELEVEN_LABS_API_KEY')
GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET') 