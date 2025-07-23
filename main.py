import sys
from gtts import gTTS
from pydub import AudioSegment
from TTS.api import TTS
import re
import os
import json
 
# ===== CONFIG =====
STORY_TEXT = """
Leo sat by his window, a soft <b>yawn</b> escaping his lips [sound:yawn.mp3] as the sky painted the sunrise [sound:sunrise.mp3].
"""
OUTPUT_FILE = "story_with_sounds.mp3"
SOUNDS_FOLDER = "Sounds"
# ==================
 
def find_sound_file(sounds_folder, filename):
    # Enhanced: Try original, 'ing', and verb forms (V1, V2, V3) dynamically
    import os
    filename_lower = filename.lower().strip()
    base, ext = os.path.splitext(filename_lower)
    base = base.strip()
    # Dynamically try common verb forms
    # Try base, base+'ing', base+'ed', base+'s', and handle plural 's' (e.g., "tree" -> "trees")
    verb_forms = [base, base + "ing", base + "ed", base + "s"]
    # If the word ends with 'y', try replacing 'y' with 'ies' (e.g., "story" -> "stories")
    if base.endswith("y") and len(base) > 1:
        verb_forms.append(base[:-1] + "ies")
    # If the word ends with 's', try removing 's' for singular (e.g., "trees" -> "tree")
    if base.endswith("s") and len(base) > 1:
        verb_forms.append(base[:-1])
    # Also try removing trailing 'e' for 'ing' (e.g., "make" -> "making")
    if base.endswith("e") and len(base) > 1:
        verb_forms.append(base[:-1] + "ing")
    # Remove duplicates while preserving order
    seen = set()
    verb_forms = [x for x in verb_forms if not (x in seen or seen.add(x))]
    possible_exts = ['.mp3', '.ogg'] if ext in ['.mp3', '.ogg'] else ['.mp3', '.ogg']
    for form in verb_forms:
        for try_ext in possible_exts:
            target = form + try_ext
            for root, _, files in os.walk(sounds_folder):
                for f in files:
                    # Debug print for each file checked
                    # print(f"Checking: {os.path.join(root, f)} against target: {target}")
                    if f.lower() == target:
                        print(f"[DEBUG] Found sound file: {os.path.join(root, f)} for target: {target}")
                        return os.path.join(root, f)
    print(f"[DEBUG] No sound file found for '{filename}'. Tried forms: {verb_forms} with extensions: {possible_exts}")
    return None

def text_to_speech_with_sounds(
    input_text,
    sounds_folder='Sounds',
    output_file='output.mp3',
    sample_voice_path=None
):
    import re
    from pydub import AudioSegment
    import os

    tts_kwargs = {}
    if sample_voice_path:
        # Use YourTTS for voice cloning when a sample is provided.
        # print("Initializing YourTTS model for voice cloning...")
        tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=False, gpu=False)

        if not os.path.exists(sample_voice_path):
            print(f"[ERROR] Sample voice file not found: {sample_voice_path}")
            print("Aborting audio generation.")
            return

        # print(f"Using voice cloning with sample: {sample_voice_path}")
        tts_kwargs = {"speaker_wav": sample_voice_path, "language": "en"}
    else:
        # Use a high-quality female narrator voice suitable for kids.
        # print("Initializing narrator voice model (LJSpeech VITS)...")
        tts = TTS(model_name="tts_models/en/ljspeech/vits", progress_bar=False, gpu=False)
        # No extra kwargs needed for this single-speaker model.

    audio_segments = []

    def synthesize_text(text_to_synth):
        """Synthesizes text and returns True on success, False on failure."""
        # Remove <b> and </b> tags
        text_to_synth = re.sub(r'<\/?b>', '', text_to_synth)
        text_to_synth = text_to_synth.strip()
        if not text_to_synth:
            return True
        try:
            tts.tts_to_file(text=text_to_synth, file_path='temp_tts.wav', **tts_kwargs)
            audio_segments.append(AudioSegment.from_file('temp_tts.wav'))
            os.remove('temp_tts.wav')
            return True
        except TypeError as e:
            error_message = "\n[ERROR] Failed to generate speech."
            if sample_voice_path:
                error_message += f" Using the sample voice '{sample_voice_path}'."
                error_message += "\n   > This usually means the audio file is incompatible or corrupted."
                error_message += "\n   > Please try using a different sample file (a clear WAV file, 5-10 seconds long, is recommended)."
            else:
                error_message += f"\n   > An internal error occurred: {e}"
            print(error_message)
            return False
        except Exception as e:
            # print(f"\n[ERROR] An unexpected error occurred during speech generation: {e}")
            return False

    def find_and_add_sound(filename):
        """Finds a sound file and adds it to the audio segments."""
        sound_file = find_sound_file(sounds_folder, filename.strip())
        if sound_file:
            try:
                # Use from_file to support both mp3 and ogg
                audio_segments.append(AudioSegment.from_file(sound_file))
            except Exception as e:
                print(f"Warning: Could not load sound file {sound_file}: {e}")
        else:
            print(f"Warning: Sound file {filename.strip()} not found in {sounds_folder} or its subfolders.")

    # Split input into text and sound tags
    pattern = re.compile(r'\[(?:Sound|sound|SOUND):\s*(.*?)\]', re.IGNORECASE)
    segments = pattern.split(input_text)

    for i, segment in enumerate(segments):
        if i % 2 == 0:
            # Text segment
            text = segment.strip()
            if text:
                synthesize_text(text)
        else:
            # Sound segment
            find_and_add_sound(segment)

    if audio_segments:
        final_audio = audio_segments[0]
        for seg in audio_segments[1:]:
            final_audio += seg
        # Save output to user's Downloads folder
        from pathlib import Path
        downloads_folder = str(Path.home() / "Downloads")
        os.makedirs(downloads_folder, exist_ok=True)
        output_path = os.path.join(downloads_folder, output_file)
        final_audio.export(output_path, format='mp3')
        print(f"Generated {output_path}")
    else:
        print("No audio generated.")
 
def run_agent(story_text=None, output_file=None, sample_voice_path=None):
    """
    Runs the AI agent to generate audio from story text with sound effects.
    """
    if story_text is None:
        story_text = STORY_TEXT
    if output_file is None:
        output_file = OUTPUT_FILE
    print(f"Generating audio for agent input...")
    text_to_speech_with_sounds(
        input_text=story_text,
        output_file=output_file,
        sample_voice_path=sample_voice_path
    )

# --- Main execution block ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Agent: Generate audio story with sound effects.")
    parser.add_argument('--story', type=str, help='Story text to synthesize')
    parser.add_argument('--output', type=str, help='Output MP3 file name')
    parser.add_argument('--sample_voice', type=str, help='Path to sample voice file for cloning')

    args = parser.parse_args()

    if args.story or args.output or args.sample_voice:
        run_agent(
            story_text=args.story if args.story else STORY_TEXT,
            output_file=args.output if args.output else OUTPUT_FILE,
            sample_voice_path=args.sample_voice
        )
    else:
        print(f"Generating audio for STORY_TEXT...")
        text_to_speech_with_sounds(
            input_text=STORY_TEXT,
            output_file=OUTPUT_FILE
        )