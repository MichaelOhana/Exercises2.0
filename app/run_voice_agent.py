from dotenv import load_dotenv
import os
from pathlib import Path
from voice_agent import VoiceAgent

# Get the absolute path to the .env file
env_path = Path(__file__).parent.parent / '.env'
print(f"📁 Looking for .env file at: {env_path}")
print(f"File exists: {env_path.exists()}")

# Load environment variables from .env file
load_dotenv(dotenv_path=env_path)

def main():
    # Get API keys from environment variables
    deepgram_key = os.getenv('DEEPGRAM_API_KEY')
    google_key = os.getenv('GOOGLE_API_KEY')
    
    print(f"📝 Environment variables:")
    print(f"DEEPGRAM_API_KEY: {deepgram_key[:10]}... (length: {len(deepgram_key) if deepgram_key else 0})")
    print(f"GOOGLE_API_KEY: {google_key[:10]}... (length: {len(google_key) if google_key else 0})")
    
    if not deepgram_key or not google_key:
        print("❌ Error: Please set DEEPGRAM_API_KEY and GOOGLE_API_KEY in your .env file")
        return
    
    print("🤖 Initializing voice agent...")
    
    # Create voice agent instance
    agent = VoiceAgent(
        deepgram_api_key=deepgram_key,
        google_api_key=google_key
    )
    
    print("🚀 Starting voice conversation...")
    
    # Start listening
    agent.start_listening()

if __name__ == "__main__":
    main() 