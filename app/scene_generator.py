from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import whisper
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
import tempfile
import os
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ImageClip
import soundfile as sf
import librosa
import uuid

from .video_assets import AssetManager
from .media_sources import MediaFetcher

@dataclass
class SceneConfig:
    duration: float
    text_content: Dict[str, str]
    background_query: str
    animation_queries: List[str]
    audio_text: str
    font_size: int = 48
    text_color: str = 'white'
    text_positions: Dict[str, Tuple[str, str]] = None  # (horizontal, vertical) alignment

class SceneGenerator:
    def __init__(self, output_dir: str = "static/generated_videos"):
        self.asset_manager = AssetManager()
        self.media_fetcher = MediaFetcher()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_scene_audio(self, text: str, output_path: Path) -> Dict:
        """Generate audio using Google Text-to-Speech"""
        try:
            from gtts import gTTS
            
            # Create audio using gTTS
            tts = gTTS(text=text, lang='en')
            tts.save(str(output_path))
            
            # Get audio duration using moviepy
            audio_clip = AudioFileClip(str(output_path))
            duration = audio_clip.duration
            audio_clip.close()
            
            return {
                'duration': duration,
                'path': output_path
            }
        except Exception as e:
            print(f"Error generating audio: {e}")
            return None

    def generate_word_scene(self, word: str, phonetic: str, definition: str) -> Path:
        """Generate a scene showing the word, its pronunciation, and definition"""
        config = SceneConfig(
            duration=5.0,
            text_content={
                'word': word,
                'phonetic': f"/{phonetic}/",
                'definition': definition
            },
            background_query="clean professional background",
            animation_queries=[],
            audio_text=f"The word {word}, pronounced as {phonetic}, means {definition}",
            text_positions={
                'word': ('center', 'top'),
                'phonetic': ('center', 'center'),
                'definition': ('center', 'bottom')
            }
        )
        
        return self._generate_scene(config, 'word')

    def _create_text_overlay(self, 
                           text: str, 
                           size: Tuple[int, int], 
                           position: Tuple[str, str],
                           font_size: int = 48,
                           color: str = 'white',
                           duration: float = None) -> TextClip:
        """Create a text overlay with the specified properties"""
        text_clip = TextClip(
            text,
            fontsize=font_size,
            color=color,
            size=size,
            method='label'
        )
        
        if duration:
            text_clip = text_clip.set_duration(duration)
            
        # Position the text
        w, h = size
        x_align, y_align = position
        
        if x_align == 'center':
            x_pos = w//2 - text_clip.w//2
        elif x_align == 'left':
            x_pos = 20
        else:  # right
            x_pos = w - text_clip.w - 20
            
        if y_align == 'center':
            y_pos = h//2 - text_clip.h//2
        elif y_align == 'top':
            y_pos = 20
        else:  # bottom
            y_pos = h - text_clip.h - 20
            
        return text_clip.set_position((x_pos, y_pos))

    def _generate_scene(self, config: SceneConfig, scene_type: str) -> Path:
        """Generate a scene based on configuration"""
        try:
            # Get background
            backgrounds = self.media_fetcher.search_images(config.background_query, 1)
            if not backgrounds:
                raise ValueError(f"No background found for query: {config.background_query}")
                
            background_path = self.media_fetcher.download_media(
                backgrounds[0]['download_url'],
                f"{scene_type}_background_{backgrounds[0]['id']}.jpg"
            )
            
            # Generate audio
            audio_path = Path(tempfile.mktemp(suffix='.wav'))
            audio_info = self.generate_scene_audio(config.audio_text, audio_path)
            
            if not audio_info:
                raise ValueError("Failed to generate audio")
            
            # Create scene
            output_path = self._compose_scene(
                background_path,
                config.text_content,
                audio_path,
                config.duration,
                config.text_positions,
                config.font_size,
                config.text_color
            )
            
            return output_path
            
        except Exception as e:
            print(f"Error generating scene: {e}")
            return None

    def _compose_scene(self, 
                      background_path: Path,
                      text_content: Dict[str, str],
                      audio_path: Path,
                      duration: float,
                      text_positions: Dict[str, Tuple[str, str]],
                      font_size: int,
                      text_color: str) -> Path:
        """Compose a scene with background, text, and audio"""
        try:
            # Create background clip
            background = ImageClip(str(background_path))
            bg_clip = background.set_duration(duration)
            
            # Create text overlays
            text_clips = []
            for text_type, text in text_content.items():
                position = text_positions.get(text_type, ('center', 'center'))
                text_clip = self._create_text_overlay(
                    text,
                    background.size,
                    position,
                    font_size,
                    text_color,
                    duration
                )
                text_clips.append(text_clip)
            
            # Combine background and text
            video = CompositeVideoClip([bg_clip] + text_clips)
            
            # Add audio
            audio = AudioFileClip(str(audio_path))
            video = video.set_audio(audio)
            
            # Write output file
            output_path = self.output_dir / f"{uuid.uuid4()}.mp4"
            video.write_videofile(
                str(output_path),
                fps=24,
                codec='libx264',
                audio_codec='aac'
            )
            
            return output_path
            
        except Exception as e:
            print(f"Error composing scene: {e}")
            return None

    def generate_intro_scene(self, word: str, field: str) -> Path:
        """Generate the introduction scene (5-10 seconds)"""
        config = SceneConfig(
            duration=8.0,
            text_content={
                'title': f"Understanding the Word: {word}",
                'subtitle': f"Your {field} Vocabulary Series",
                'subtext': "Learn pronunciation, meaning, and examples"
            },
            background_query=f"{field} professional background",
            animation_queries=[],
            audio_text=f"Welcome to your {field} vocabulary series. Today, we'll learn about the word '{word}'",
            text_positions={
                'title': ('center', 'top'),
                'subtitle': ('center', 'center'),
                'subtext': ('center', 'bottom')
            }
        )
        return self._generate_scene(config, 'intro')

    def generate_breakdown_scene(self, word: str, phonetic: str) -> Path:
        """Generate the word breakdown scene (10-15 seconds)"""
        # Split word into syllables (simplified version)
        syllables = word.lower().replace('-', ' ').split()
        syllable_text = '-'.join(syllables)
        
        config = SceneConfig(
            duration=12.0,
            text_content={
                'word': word,
                'syllables': syllable_text,
                'phonetic': f"/{phonetic}/",
            },
            background_query="clean educational background",
            animation_queries=["syllable highlight animation"],
            audio_text=f"The word '{word}' is pronounced as {phonetic}. Let's break it down: {', '.join(syllables)}",
            text_positions={
                'word': ('center', 'top'),
                'syllables': ('center', 'center'),
                'phonetic': ('center', 'bottom')
            }
        )
        return self._generate_scene(config, 'breakdown')

    def generate_definition_scene(self, word: str, definition: str, context: str) -> Path:
        """Generate the definition and explanation scene (15-20 seconds)"""
        config = SceneConfig(
            duration=18.0,
            text_content={
                'word': word,
                'definition': definition,
                'context': f"Common in: {context}"
            },
            background_query=f"{context} setting",
            animation_queries=[],
            audio_text=f"{word} means {definition}. It is commonly used in {context}.",
            text_positions={
                'word': ('center', 'top'),
                'definition': ('center', 'center'),
                'context': ('center', 'bottom')
            }
        )
        return self._generate_scene(config, 'definition')

    def generate_examples_scene(self, word: str, examples: List[str]) -> Path:
        """Generate the example sentences scene (20-25 seconds)"""
        formatted_examples = '\n'.join([f"• {example}" for example in examples])
        
        config = SceneConfig(
            duration=22.0,
            text_content={
                'title': "Example Sentences",
                'examples': formatted_examples
            },
            background_query=f"professional presentation background",
            animation_queries=[],
            audio_text=f"Here are some example sentences using '{word}'. {'. '.join(examples)}",
            text_positions={
                'title': ('center', 'top'),
                'examples': ('left', 'center')
            }
        )
        return self._generate_scene(config, 'examples')

    def generate_context_scene(self, word: str, dialogue: List[Dict[str, str]]) -> Path:
        """Generate the contextual usage scene (25-30 seconds)"""
        dialogue_text = '\n'.join([f"{speaker}: {line}" for speaker, line in dialogue])
        
        config = SceneConfig(
            duration=28.0,
            text_content={
                'title': "Contextual Usage",
                'dialogue': dialogue_text
            },
            background_query="professional conversation setting",
            animation_queries=[],
            audio_text=' '.join([line for _, line in dialogue]),
            text_positions={
                'title': ('center', 'top'),
                'dialogue': ('center', 'center')
            }
        )
        return self._generate_scene(config, 'context')

    def generate_summary_scene(self, word: str, summary_points: Dict[str, str]) -> Path:
        """Generate the visual summary scene (10-15 seconds)"""
        summary_text = '\n'.join([f"• {key}: {value}" for key, value in summary_points.items()])
        
        config = SceneConfig(
            duration=12.0,
            text_content={
                'title': "Summary",
                'summary': summary_text
            },
            background_query="clean professional background",
            animation_queries=[],
            audio_text=f"Let's summarize what we learned about '{word}'. {'. '.join([f'{key} is {value}' for key, value in summary_points.items()])}",
            text_positions={
                'title': ('center', 'top'),
                'summary': ('left', 'center')
            }
        )
        return self._generate_scene(config, 'summary')