import streamlit as st
import requests

st.set_page_config(page_title="Multilingual Translator", layout="centered")
st.title("🌐 Translator")

languages = {
    "English": "English",
    "Tamil": "Tamil",
    "Telugu": "Telugu",
    "Hindi": "Hindi",
    "Kannada": "Kannada",
    "Malayalam": "Malayalam",
    "Odia": "Odia",
    "Bengali": "Bengali"
}


source_lang = st.selectbox("Translate from", list(languages.keys()), index=0)
target_lang = st.selectbox("Translate to", list(languages.keys()), index=1)

text_to_translate = st.text_area("Enter text here", height=150)

TOGETHER_API_KEY = "315ed353decb44419d9b1b552f5daf0a4c06979fb7444249b7f41fb28ec964fd"  
TOGETHER_API_URL = "https://api.together.xyz/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {TOGETHER_API_KEY}",
    "Content-Type": "application/json"
}

def translate(text, source, target):
    system_prompt = f"You are a professional translator. Translate the following {source} sentence into {target} only. Do not give any explanations or extra text."

    payload = {
        "model": "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",  
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        "temperature": 0.2,
        "max_tokens": 256
    }

    response = requests.post(TOGETHER_API_URL, headers=HEADERS, json=payload)

    if response.status_code == 200:
        try:
            return response.json()["choices"][0]["message"]["content"].strip()
        except:
            return "⚠️ Unexpected response format."
    else:
        return f"❌ Error: {response.status_code} - {response.text}"

if st.button("Translate"):
    if text_to_translate.strip() == "":
        st.warning("Please enter text to translate.")
    elif source_lang == target_lang:
        st.info("Source and target languages are the same.")
    else:
        with st.spinner("Translating..."):
            result = translate(text_to_translate, source_lang, target_lang)
        st.success("Translation:")
        st.write(result)
