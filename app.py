import streamlit as st
import speech_recognition as sr
import requests
from gtts import gTTS
import tempfile
import os
from audio_recorder_streamlit import audio_recorder

st.set_page_config(page_title="Voice Translator", layout="centered")
st.title("🗣️ Voice Translator")

# Supported languages
languages = {
    "English": {"code": "en-US", "tts": "en"},
    "Tamil": {"code": "ta-IN", "tts": "ta"},
    "Hindi": {"code": "hi-IN", "tts": "hi"},
    "Telugu": {"code": "te-IN", "tts": "te"},
    "Kannada": {"code": "kn-IN", "tts": "kn"},
    "Malayalam": {"code": "ml-IN", "tts": "ml"},
    "Bengali": {"code": "bn-IN", "tts": "bn"},
    "Odia": {"code": "or-IN", "tts": "or"},
}

# Initialize session state
if 'recognized_text' not in st.session_state:
    st.session_state.recognized_text = ""
if 'translated_text' not in st.session_state:
    st.session_state.translated_text = ""

# Language selection
col1, col2 = st.columns(2)
with col1:
    source_lang = st.selectbox("Translate from", list(languages.keys()), index=0)
with col2:
    target_lang = st.selectbox("Translate to", list(languages.keys()), index=1)

st.write("---")

# Input methods
tab1, tab2, tab3 = st.tabs(["📝 Text Input", "🎤 Record Audio", "📁 Upload Audio"])

with tab1:
    st.write("**Type your text here:**")
    text_input = st.text_area("Enter text", height=150, value=st.session_state.recognized_text)

with tab2:
    st.write("**Record your voice:**")
    st.info("Click the microphone button below to start recording")
    
    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="microphone",
        icon_size="2x"
    )
    
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
        with st.spinner("Converting speech to text..."):
            recognizer = sr.Recognizer()
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(audio_bytes)
                audio_path = temp_audio.name
            
            try:
                with sr.AudioFile(audio_path) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = recognizer.record(source)
                
                recognized_text = recognizer.recognize_google(
                    audio_data, 
                    language=languages[source_lang]["code"]
                )
                
                st.session_state.recognized_text = recognized_text
                st.success(f"Recognized: {recognized_text}")
                
            except sr.UnknownValueError:
                st.error("Could not understand the audio. Please try again.")
            except sr.RequestError as e:
                st.error(f"Speech recognition error: {e}")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                try:
                    os.remove(audio_path)
                except:
                    pass

with tab3:
    st.write("**Upload an audio file:**")
    uploaded_file = st.file_uploader("Choose a .wav file", type=["wav"])
    
    if uploaded_file is not None:
        st.audio(uploaded_file, format="audio/wav")
        
        with st.spinner("Converting uploaded audio to text..."):
            recognizer = sr.Recognizer()

            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(uploaded_file.read())
                audio_path = temp_audio.name

            try:
                with sr.AudioFile(audio_path) as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio_data = recognizer.record(source)
                
                recognized_text = recognizer.recognize_google(
                    audio_data, 
                    language=languages[source_lang]["code"]
                )
                
                st.session_state.recognized_text = recognized_text
                st.success(f"Recognized: {recognized_text}")
                
            except sr.UnknownValueError:
                st.error("Could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"Speech recognition error: {e}")
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                try:
                    os.remove(audio_path)
                except:
                    pass

# Show current input text
if st.session_state.recognized_text:
    st.write("**Current Text:**")
    st.info(st.session_state.recognized_text)

# Action buttons
col1, col2 = st.columns([1, 3])

with col1:
    if st.button("Clear"):
        st.session_state.recognized_text = ""
        st.session_state.translated_text = ""
        st.rerun()

# Translation function
def translate(text, source, target):
    system_prompt = f"You are a professional translator. Translate the following {source} sentence into {target}. No explanation."

    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.2,
        "max_tokens": 256
    }

    headers = {
        "Authorization": "Bearer 315ed353decb44419d9b1b552f5daf0a4c06979fb7444249b7f41fb28ec964fd",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.together.xyz/v1/chat/completions", json=payload, headers=headers)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        return f"Error: {response.status_code}"

# Translate button
with col2:
    final_input_text = st.session_state.recognized_text if st.session_state.recognized_text else text_input.strip()
    
    if st.button("🌍 Translate", type="primary"):
        if not final_input_text:
            st.warning("Please enter text, record audio, or upload an audio file.")
        elif source_lang == target_lang:
            st.info("Source and target languages are the same.")
        else:
            with st.spinner("Translating..."):
                translated = translate(final_input_text, source_lang, target_lang)
                st.session_state.translated_text = translated
                
                st.success("Translation completed!")
                
                # Show results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Original ({source_lang}):**")
                    st.write(final_input_text)
                
                with col2:
                    st.write(f"**Translation ({target_lang}):**")
                    st.write(translated)

# Audio playback
if st.session_state.translated_text:
    st.write("---")
    st.write("### 🔊 Audio Playback")
    
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Original Audio:**")
        try:
            with st.spinner("Generating audio..."):
                tts_orig = gTTS(final_input_text, lang=languages[source_lang]["tts"], slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts_orig.save(fp.name)
                    with open(fp.name, 'rb') as audio_file:
                        audio_bytes_orig = audio_file.read()
                    st.audio(audio_bytes_orig, format="audio/mp3")
        except Exception as e:
            st.error(f"Could not generate original audio: {e}")

    with col2:
        st.write("**Translated Audio:**")
        try:
            with st.spinner("Generating audio..."):
                tts_trans = gTTS(st.session_state.translated_text, lang=languages[target_lang]["tts"], slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts_trans.save(fp.name)
                    with open(fp.name, 'rb') as audio_file:
                        audio_bytes_trans = audio_file.read()
                    st.audio(audio_bytes_trans, format="audio/mp3")
        except Exception as e:
            st.error(f"Could not generate translated audio: {e}")

# Help section
with st.expander("📋 How to Use"):
    st.write("""
    **Three ways to input text:**
    
    1. **Text Input**: Type directly in the text area
    2. **Record Audio**: Click the microphone to record your voice
    3. **Upload Audio**: Upload a .wav audio file
    
    **Steps:**
    1. Select source and target languages
    2. Input your text using any of the three methods
    3. Click "Translate" 
    4. Listen to the audio playback
    
    **Tips:**
    - Speak clearly for better recognition
    - Ensure microphone permissions are enabled
    - Use .wav format for uploaded files
    """)

st.write("---")
st.caption("Voice Translator - Simple and Easy to Use")
