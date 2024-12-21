import os

# Create all required directories
directories = [
    'app/static/test_videos',
    'app/static/video_assets/backgrounds',
    'app/static/video_assets/animations',
    'app/static/video_assets/icons',
    'app/static/video_assets/templates',
    'app/static/video_assets/cache',
    'output_videos'
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    print(f"Created directory: {directory}") 