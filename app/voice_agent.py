import asyncio
import json
import time
from typing import AsyncGenerator, Optional
import websockets
import google.generativeai as genai
import sounddevice as sd
import numpy as np
from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveTranscriptionEvents,
    LiveOptions,
    Microphone,
    SpeakWebSocketEvents,
    SpeakWSOptions,
)

class VoiceAgent:
    def __init__(
        self,
        deepgram_api_key: str,
        google_api_key: str,
        deepgram_aura_api_key: Optional[str] = None,
    ):
        # Initialize Deepgram for STT with keepalive
        self.dg_client = DeepgramClient(deepgram_api_key)
        
        # Initialize Gemini
        genai.configure(api_key=google_api_key)
        self.model = genai.GenerativeModel('gemini-1.5-pro')
        self.chat = self.model.start_chat(history=[])
        
        # Initialize Deepgram Aura for TTS
        self.aura_api_key = deepgram_aura_api_key or deepgram_api_key
        
        # Store final transcripts
        self.is_finals = []
        
        # Create event loop for async operations
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        # Audio playback settings
        self.sample_rate = 16000  # Changed to match STT sample rate
        self.audio_buffer = []

        # Latency tracking
        self.latency_stats = {
            "stt": [],
            "llm": [],
            "tts": [],
            "total": []
        }
        
        # Add interruption handling
        self.current_tts_task = None
        self.current_response_task = None
        self.is_speaking = False

    async def cancel_current_speech(self):
        """Cancel any ongoing TTS and response handling"""
        if self.current_tts_task and not self.current_tts_task.done():
            self.current_tts_task.cancel()
            try:
                await self.current_tts_task
            except asyncio.CancelledError:
                pass
        
        if self.current_response_task and not self.current_response_task.done():
            self.current_response_task.cancel()
            try:
                await self.current_response_task
            except asyncio.CancelledError:
                pass
        
        self.is_speaking = False

    def play_audio(self, audio_data):
        """Play audio using sounddevice"""
        try:
            print(f"🔊 Playing audio ({len(audio_data)} bytes)")
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Check if audio data is valid
            if audio_array.size == 0 or (audio_array.max() == 0 and audio_array.min() == 0):
                return
            
            # Normalize audio if needed
            if audio_array.max() > 0:
                audio_array = audio_array.astype(np.float32) / 32768.0
            
            # Play audio
            sd.play(audio_array, self.sample_rate)
            sd.wait()  # Wait until audio is finished playing
            print("🔊 Finished playing audio")
        except Exception as e:
            print(f"Error playing audio: {e}")

    async def handle_response(self, text: str):
        """Handle the response processing and TTS in a pipeline"""
        try:
            if self.is_speaking:
                await self.cancel_current_speech()
            
            self.is_speaking = True
            start_time = time.time()
            
            # Process text through LLM with streaming
            llm_start = time.time()
            try:
                sentence_count = 0
                async for sentence in self.process_text(text):
                    if not self.is_speaking:  # Check if we've been interrupted
                        break
                        
                    sentence_count += 1
                    print(f"🤖 Assistant (part {sentence_count}): {sentence}")
                    
                    # Start TTS for this sentence while getting next one
                    audio_data = None
                    async for chunk in self.text_to_speech(sentence):
                        if chunk:
                            audio_data = chunk
                            break
                    
                    if audio_data and self.is_speaking:
                        self.play_audio(audio_data)
                
                llm_time = time.time() - llm_start
                self.latency_stats["llm"].append(llm_time)
                print(f"🕒 LLM processing time: {llm_time:.2f}s")
                
            except asyncio.TimeoutError:
                print("⚠️ LLM timeout")
                if self.is_speaking:  # Only respond if not interrupted
                    response = "Could you repeat that?"
                    print(f"🤖 Assistant: {response}")
                    async for chunk in self.text_to_speech(response):
                        if chunk:
                            self.play_audio(chunk)
                            break
            
            tts_time = time.time() - start_time
            self.latency_stats["tts"].append(tts_time)
            print(f"🕒 TTS processing time: {tts_time:.2f}s")
            
            total_time = time.time() - start_time
            self.latency_stats["total"].append(total_time)
            print(f"🕒 Total processing time: {total_time:.2f}s")

        except asyncio.CancelledError:
            print("🛑 Response handling cancelled")
            raise
        except Exception as e:
            print(f"Error handling response: {e}")
        finally:
            self.is_speaking = False

    async def process_text(self, text: str) -> AsyncGenerator[str, None]:
        """Process text through Gemini 1.5 Flash with sentence splitting"""
        try:
            prompt = (
                f"You are a friendly conversation partner helping someone practice English. "
                f"Be natural and engaging, but keep the conversation flowing smoothly. "
                f"Focus on one topic or question at a time. "
                f"User says: {text}"
            )
            
            # Get the full response first
            response = await self.chat.send_message_async(prompt)
            response_text = response.text.strip()
            
            # Split into sentences and yield them one by one
            sentences = []
            current_sentence = []
            
            # Split on sentence endings while preserving punctuation
            for word in response_text.split():
                current_sentence.append(word)
                if any(word.endswith(end) for end in ['.', '!', '?']):
                    sentences.append(' '.join(current_sentence))
                    current_sentence = []
            
            # Add any remaining words as the last sentence
            if current_sentence:
                sentences.append(' '.join(current_sentence))
            
            # Yield sentences one by one
            for sentence in sentences:
                yield sentence.strip()
                
        except Exception as e:
            print(f"Error in text processing: {e}")
            yield "Could you repeat that?"

    async def text_to_speech(self, text: str) -> AsyncGenerator[bytes, None]:
        """Convert text to speech using Deepgram Aura WebSocket API"""
        try:
            # Create a websocket connection to Deepgram
            dg_client = DeepgramClient(self.aura_api_key)
            dg_connection = dg_client.speak.websocket.v("1")
            
            # Use events to control the flow
            audio_complete = asyncio.Event()
            audio_chunks = []
            
            def on_open(self, open, **kwargs):
                print(f"🎙️ TTS WebSocket opened: {open}")
            
            def on_binary_data(self, data, **kwargs):
                if len(data) > 0:  # Only collect non-empty chunks
                    audio_chunks.append(data)
            
            def on_error(self, error, **kwargs):
                print(f"🚨 TTS Error: {error}")
                audio_complete.set()
            
            def on_close(self, close, **kwargs):
                audio_complete.set()
            
            # Register event handlers
            dg_connection.on(SpeakWebSocketEvents.Open, on_open)
            dg_connection.on(SpeakWebSocketEvents.AudioData, on_binary_data)
            dg_connection.on(SpeakWebSocketEvents.Error, on_error)
            dg_connection.on(SpeakWebSocketEvents.Close, on_close)
            
            # Configure options
            options = SpeakWSOptions(
                model="aura-asteria-en",
                encoding="linear16",
                sample_rate=16000
            )
            
            # Start the connection
            if dg_connection.start(options) is False:
                print("❌ Failed to start TTS connection")
                return
            
            # Clean text
            text = str(text).strip()
            if len(text) > 2000:
                text = text[:1997] + "..."
            
            # Send text and wait for all audio
            dg_connection.send_text(text)
            dg_connection.flush()
            
            # Wait for audio completion
            try:
                await asyncio.wait_for(audio_complete.wait(), timeout=3.0)
            except asyncio.TimeoutError:
                print("⚠️ TTS timeout waiting for completion")
            finally:
                dg_connection.finish()
            
            # Return complete audio only if we have chunks
            if audio_chunks:
                complete_audio = b''.join(audio_chunks)
                if len(complete_audio) > 0:
                    yield complete_audio
            
        except Exception as e:
            print(f"Error in speech synthesis: {e}")
            yield b""

    def start_listening(self):
        """Start listening to microphone input"""
        try:
            # Create websocket connection
            dg_connection = self.dg_client.listen.websocket.v("1")
            
            # Store instance reference for callbacks
            agent = self
            
            def on_open(self, open, **kwargs):
                print("🎤 Connection Open")

            def on_message(self, result, **kwargs):
                sentence = result.channel.alternatives[0].transcript
                if len(sentence) == 0:
                    return
                
                if result.is_final:
                    print(f"🎤 Final: {sentence}")
                    agent.is_finals.append(sentence)
                    
                    if result.speech_final:
                        utterance = " ".join(agent.is_finals)
                        print(f"🎤 Complete utterance: {utterance}")
                        # Process through LLM and TTS using the event loop
                        future = asyncio.run_coroutine_threadsafe(
                            agent.handle_response(utterance), 
                            agent.loop
                        )
                        agent.is_finals = []
                else:
                    print(f"🎤 Interim: {sentence}")

            def on_error(self, error, **kwargs):
                print(f"🚨 Error: {error}")

            def on_close(self, close, **kwargs):
                print("🔌 Connection closed")

            def on_metadata(self, metadata, **kwargs):
                print(f"📝 Metadata: {metadata}")

            def on_speech_started(self, speech_started, **kwargs):
                print("🎙️ Speech Started")
                # Cancel any ongoing speech when new speech is detected
                if agent.is_speaking:
                    future = asyncio.run_coroutine_threadsafe(
                        agent.cancel_current_speech(),
                        agent.loop
                    )
                    future.result()  # Wait for cancellation to complete
            
            def on_utterance_end(self, utterance_end, **kwargs):
                print("🎙️ Utterance End")
                if len(agent.is_finals) > 0:
                    stt_time = time.time() - agent.speech_start_time
                    agent.latency_stats["stt"].append(stt_time)
                    print(f"🕒 STT processing time: {stt_time:.2f}s")
                    
                    utterance = " ".join(agent.is_finals)
                    print(f"🎤 Final utterance: {utterance}")
                    # Process through LLM and TTS using the event loop
                    agent.current_response_task = asyncio.run_coroutine_threadsafe(
                        agent.handle_response(utterance), 
                        agent.loop
                    )
                    agent.is_finals = []

            # Register event handlers
            dg_connection.on(LiveTranscriptionEvents.Open, on_open)
            dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
            dg_connection.on(LiveTranscriptionEvents.Error, on_error)
            dg_connection.on(LiveTranscriptionEvents.Close, on_close)
            dg_connection.on(LiveTranscriptionEvents.Metadata, on_metadata)
            dg_connection.on(LiveTranscriptionEvents.SpeechStarted, on_speech_started)
            dg_connection.on(LiveTranscriptionEvents.UtteranceEnd, on_utterance_end)

            # Configure live transcription options
            options = LiveOptions(
                model="nova-2",
                language="en-US",
                smart_format=True,
                encoding="linear16",
                channels=1,
                sample_rate=16000,
                interim_results=True,
                utterance_end_ms="1000",
                vad_events=True,
                endpointing=300
            )
            
            # Start the event loop in a separate thread
            def run_event_loop():
                asyncio.set_event_loop(self.loop)
                self.loop.run_forever()
            
            import threading
            loop_thread = threading.Thread(target=run_event_loop, daemon=True)
            loop_thread.start()

            # Start the connection with options
            if dg_connection.start(options) is False:
                print("❌ Failed to connect to Deepgram")
                return

            print("🎤 Connection to Deepgram established")
            print("\nPress Enter to stop recording...\n")

            # Open a microphone stream
            microphone = Microphone(dg_connection.send)
            
            # Start microphone
            self.speech_start_time = time.time()  # Track when we start listening
            microphone.start()
            
            # Wait for user to press Enter
            input("")
            
            # Clean up
            microphone.finish()
            dg_connection.finish()
            
            # Stop the event loop
            self.loop.call_soon_threadsafe(self.loop.stop)
            loop_thread.join()
            
            # Print average latencies
            print("\n📊 Latency Statistics:")
            for key, values in self.latency_stats.items():
                if values:
                    avg = sum(values) / len(values)
                    print(f"  {key.upper()}: {avg:.2f}s average over {len(values)} samples")
            
            print("✨ Finished")

        except Exception as e:
            print(f"Could not open socket: {e}")
            return