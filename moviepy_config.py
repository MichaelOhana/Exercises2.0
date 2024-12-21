import os

# Set ImageMagick binary path
IMAGEMAGICK_BINARY = 'C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe'

# Set it as an environment variable
os.environ['IMAGEMAGICK_BINARY'] = IMAGEMAGICK_BINARY

# Set other MoviePy configurations if needed
os.environ['MOVIEPY_EDITOR_QUIET'] = '1'  # Reduce output verbosity 