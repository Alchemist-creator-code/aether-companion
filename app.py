import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import io

# --- CONFIGURARE ---
try:
    # 1. Luăm cheia din secretele Streamlit
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    else:
        st.error("⚠️ Cheia API lipsește din Secrets! Mergi la Settings -> Secrets pe Streamlit.")
        st.stop()

    # 2. Conectăm Google
    genai.configure(api_key=api_key)

    # 3. AICI ERA PROBLEMA: Folosim numele simplu, FĂRĂ "models/" în față
    model = genai.GenerativeModel("gemini-1.5-flash")

except Exception as e:
    st.error(f"Eroare critică la configurare: {e}")
    try:
        tts = gTTS(text=text, lang='ro')
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        # Autoplay activat
        st.audio(audio_buffer, format='audio/mp3', autoplay=True)
    except:
        pass

# ... (Restul codului tău rămâne la fel de aici în jos) ...
st.set_page_config(page_title="Aether: Companion", page_icon="🤗", layout="centered")

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

# --- MENIU LATERAL ---
mod = st.sidebar.radio("Alege Modul:", ["📖 Povestitor (Pentru Copii)", "👴 Companion (Pentru Seniori)"])

# === MODUL 1: POVESTITOR ===
if mod == "📖 Povestitor (Pentru Copii)":
    st.title("📖 Aether Povestitorul")
    st.image("https://cdn-icons-png.flaticon.com/512/3408/3408627.png", width=150)
    st.info("Spune-mi despre ce vrei să fie povestea de azi?")
    
    tema = st.text_input("Exemplu: Un ursuleț care vrea să zboare pe lună...")
    lungime = st.slider("Cât de lungă să fie?", 100, 1000, 300)
    
    if st.button("Creează Povestea ✨"):
        with st.spinner("Scriu povestea..."):
            prompt = f"Scrie o poveste pentru copii despre: {tema}. Să aibă aproximativ {lungime} cuvinte. Să fie educativă și caldă. Limba Română."
            res = model.generate_content(prompt)
            st.markdown(f"### Povestea Ta:\n\n{res.text}")
            vorbeste(res.text)

# === MODUL 2: COMPANION SENIORI ===
elif mod == "👴 Companion (Pentru Seniori)":
    st.title("👴 Aether Companion")
    st.image("https://cdn-icons-png.flaticon.com/512/2639/2639260.png", width=150)
    st.info("Sunt aici să stăm de vorbă. Spune-mi ce ai pe suflet sau ce amintiri îți trec prin gând.")
    
    # Istoric simplu în sesiune
    if "istoric" not in st.session_state:
        st.session_state.istoric = []

    # Afișare chat
    for mesaj in st.session_state.istoric:
        with st.chat_message(mesaj["rol"]):
            st.write(mesaj["text"])

    intrebare = st.chat_input("Scrie aici...")
    
    if intrebare:
        # Afișăm ce a scris utilizatorul
        with st.chat_message("user"):
            st.write(intrebare)
        st.session_state.istoric.append({"rol": "user", "text": intrebare})
        
        # AI Răspunde
        with st.chat_message("assistant"):
            with st.spinner("Mă gândesc..."):
                prompt = f"Ești un companion calm, respectuos și empatic pentru o persoană în vârstă. Răspunde cu blândețe, pune întrebări despre trecut, fii un bun ascultător. Discuția: {intrebare}"
                res = model.generate_content(prompt)
                st.write(res.text)
                vorbeste(res.text)

        st.session_state.istoric.append({"rol": "assistant", "text": res.text})




