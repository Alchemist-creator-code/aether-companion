import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="Aether: Companion", page_icon="🤗", layout="centered")

# --- CONECTARE AI CU FALLBACK (Siguranță Maximă) ---
def conecteaza_ai():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("⚠️ Cheia API lipsește din Secrets!")
        st.stop()
    
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    
    # Lista de modele pe care le încercăm (în ordinea preferinței tale)
    lista_modele = [
        "models/gemini-2.5-pro",    # Cel găsit de tine
        "models/gemini-1.5-flash",  # Varianta rapidă standard
        "models/gemini-pro",        # Varianta clasică (backup)
        "gemini-pro"                # Varianta fără prefix
    ]
    
    for nume_model in lista_modele:
        try:
            model = genai.GenerativeModel(nume_model)
            # Facem un test invizibil să vedem dacă merge
            model.generate_content("test")
            return model
        except Exception:
            continue # Dacă dă eroare, trecem la următorul din listă
            
    st.error("❌ Niciun model nu a răspuns. Verifică cheia API.")
    st.stop()

# Inițializăm modelul care funcționează
model = conecteaza_ai()

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

# Meniu
mod = st.radio("Alege modul:", ["📖 Povestitor (Copii)", "👴 Companion (Seniori)"])

if mod == "📖 Povestitor (Copii)":
    st.image("https://cdn-icons-png.flaticon.com/512/3408/3408627.png", width=100)
    tema = st.text_input("Despre ce să fie povestea? (ex: un dragon politicos)")
    
    if st.button("✨ Scrie Povestea"):
        if not tema:
            st.warning("Scrie o idee întâi!")
        else:
            with st.spinner("Aether scrie povestea..."):
                try:
                    prompt = f"Scrie o poveste scurtă, educativă și caldă pentru copii despre: {tema}. Limba Română."
                    res = model.generate_content(prompt)
                    st.markdown(res.text)
                    vorbeste(res.text)
                except Exception as e:
                    st.error(f"Eroare: {e}")

elif mod == "👴 Companion (Seniori)":
    st.image("https://cdn-icons-png.flaticon.com/512/2639/2639260.png", width=100)
    st.write("Sunt aici să te ascult. Spune-mi ce ai pe suflet.")

    # Memoria discuției
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Afișăm istoricul
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Câmpul de chat
    if prompt := st.chat_input("Scrie mesajul tău aici..."):
        # 1. Afișăm mesajul tău
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # 2. AI răspunde
        with st.chat_message("assistant"):
            with st.spinner("Mă gândesc..."):
                try:
                    prompt_ai = f"Ești un companion empatic, calm și respectuos pentru vârstnici. Răspunde scurt și cald la: {prompt}"
                    msg_ai = model.generate_content(prompt_ai)
                    st.write(msg_ai.text)
                    vorbeste(msg_ai.text)
                    st.session_state.messages.append({"role": "assistant", "content": msg_ai.text})
                except Exception as e:
                    st.error(f"Eroare: {e}")




