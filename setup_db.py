import os
from pathlib import Path

# Create instance directory if it doesn't exist
instance_dir = Path('instance')
instance_dir.mkdir(exist_ok=True)
print(f"Created directory: {instance_dir}") 