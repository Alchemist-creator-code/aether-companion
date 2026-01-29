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
        
        # SCHIMBARE MAJORĂ: Folosim "gemini-pro".
        # Acest model este compatibil cu toate versiunile de server.
        model = genai.GenerativeModel("gemini-pro")
    else:
        st.error("⚠️ Lipsește cheia din Secrets!")
        st.stop()
except Exception as e:
    st.error(f"Eroare conectare: {e}")
    st.stop()

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

mod = st.radio("Alege modul:", ["📖 Povestitor (Copii)", "👴 Companion (Seniori)"])

if mod == "📖 Povestitor (Copii)":
    st.image("https://cdn-icons-png.flaticon.com/512/3408/3408627.png", width=100)
    tema = st.text_input("Despre ce să fie povestea?")
    
    if st.button("✨ Scrie Povestea"):
        if not tema:
            st.warning("Scrie o idee întâi!")
        else:
            with st.spinner("Scriu..."):
                try:
                    res = model.generate_content(f"Scrie o poveste scurtă pt copii despre {tema}, română.")
                    st.markdown(res.text)
                    vorbeste(res.text)
                except Exception as e:
                    st.error(f"Eroare: {e}")

elif mod == "👴 Companion (Seniori)":
    st.image("https://cdn-icons-png.flaticon.com/512/2639/2639260.png", width=100)
    st.write("Te ascult.")

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
            with st.spinner("..."):
                try:
                    msg_ai = model.generate_content(f"Ești un companion empatic. Răspunde scurt la: {prompt}")
                    st.write(msg_ai.text)
                    vorbeste(msg_ai.text)
                    st.session_state.messages.append({"role": "assistant", "content": msg_ai.text})
                except Exception as e:
                    st.error(f"Eroare: {e}")


