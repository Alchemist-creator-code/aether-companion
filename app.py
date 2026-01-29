import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# --- CONFIGURARE ---
st.set_page_config(page_title="Aether: Companion", page_icon="🤗", layout="centered")

try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        
        # FOLOSIM NUMELE SIMPLU ȘI CORECT
        model = genai.GenerativeModel("gemini-1.5-flash")
    else:
        st.error("⚠️ Cheia API lipsește din Secrets!")
        st.stop()
except Exception as e:
    st.error(f"Eroare la conectare: {e}")

# --- FUNCȚIE VOCE ---
def vorbeste(text):
    try:
        tts = gTTS(text=text, lang='ro')
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        st.audio(audio_buffer, format='audio/mp3', autoplay=True)
    except:
        pass

# --- INTERFAȚA ---
st.title("🤗 Aether Companion")

# Meniu simplificat
mod = st.radio("Ce facem azi?", ["📖 Povestitor", "👴 Discuție"])

if mod == "📖 Povestitor":
    tema = st.text_input("Despre ce să fie povestea?")
    if st.button("Spune Povestea"):
        if not tema:
            st.warning("Scrie o temă întâi!")
        else:
            with st.spinner("Scriu povestea..."):
                try:
                    res = model.generate_content(f"Scrie o poveste scurtă pt copii despre {tema}, limba română.")
                    st.write(res.text)
                    vorbeste(res.text)
                except Exception as e:
                    st.error(f"Eroare AI: {e}")

elif mod == "👴 Discuție":
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    if prompt := st.chat_input("Scrie aici..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Mă gândesc..."):
                try:
                    msg_ai = model.generate_content(f"Ești un companion empatic. Răspunde la: {prompt}")
                    st.write(msg_ai.text)
                    vorbeste(msg_ai.text)
                    st.session_state.messages.append({"role": "assistant", "content": msg_ai.text})
                except Exception as e:
                    st.error(f"Eroare AI: {e}")





