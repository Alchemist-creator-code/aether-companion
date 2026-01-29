import streamlit as st
import google.generativeai as genai
import edge_tts
import asyncio
import io

# --- CONFIGURARE ---
st.set_page_config(page_title="Aether: Companion", page_icon="🤗", layout="centered")

# --- CONECTARE AI ---
def gaseste_model_activ():
    if "GOOGLE_API_KEY" not in st.secrets:
        st.error("⚠️ Cheia API lipsește din Secrets!")
        st.stop()
        
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
    
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return genai.GenerativeModel(m.name)
    except:
        pass
    
    st.error("❌ Eroare la conectarea cu Google AI.")
    st.stop()

# Inițializăm AI-ul
try:
    model = gaseste_model_activ()
except:
    st.stop()

# --- FUNCȚIE VOCE NOUĂ (MICROSOFT NEURAL) ---
async def genereaza_audio_neural(text):
    # Curățăm textul de steluțe și diez-uri
    text_curat = text.replace("*", "").replace("#", "")
    
    # Folosim vocea 'Alina' (Neurală) - sună foarte uman
    # Există și 'ro-RO-EmilNeural' pentru voce de bărbat
    comunicare = edge_tts.Communicate(text_curat, "ro-RO-AlinaNeural")
    
    # Salvăm în memorie temporară
    mp3_fp = io.BytesIO()
    async for chunk in comunicare.stream():
        if chunk["type"] == "audio":
            mp3_fp.write(chunk["data"])
            
    mp3_fp.seek(0)
    return mp3_fp

def vorbeste(text):
    try:
        # Rulăm funcția asincronă într-un mod compatibil cu Streamlit
        audio_buffer = asyncio.run(genereaza_audio_neural(text))
        st.audio(audio_buffer, format='audio/mp3', autoplay=True)
    except Exception as e:
        st.warning(f"Eroare voce: {e}")

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
                    # Instruim AI-ul să nu folosească liste cu puncte ca să nu sune sacadat
                    prompt_ai = f"Ești un companion empatic. Răspunde cursiv, în fraze, fără liste și fără simboluri. Întrebare: {prompt}"
                    msg_ai = model.generate_content(prompt_ai)
                    st.write(msg_ai.text)
                    vorbeste(msg_ai.text)
                    st.session_state.messages.append({"role": "assistant", "content": msg_ai.text})
                except Exception as e:
                    st.error(f"Eroare: {e}")

