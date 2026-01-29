import streamlit as st
import google.generativeai as genai

st.set_page_config(page_title="Aether: Diagnostic", page_icon="🕵️")
st.title("🕵️ Aether: Modul Detectiv")

# --- VERIFICARE ---
try:
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
        genai.configure(api_key=api_key)
        st.success("✅ Cheia API a fost acceptată de sistem.")
        
        st.markdown("### 📋 Ce modele vede Google pentru contul tău?")
        st.write("Sistemul caută lista de modele disponibile...")
        
        # Întrebăm Google ce modele avem
        gasit_ceva = False
        modele_disponibile = []
        
        try:
            for m in genai.list_models():
                # Căutăm doar modelele care pot genera text
                if 'generateContent' in m.supported_generation_methods:
                    st.code(m.name) # Afișăm numele exact
                    modele_disponibile.append(m.name)
                    gasit_ceva = True
            
            if not gasit_ceva:
                st.error("❌ Google spune că nu ai acces la niciun model! Verifică dacă ai activat 'Generative Language API' în consola Google Cloud sau fă o cheie nouă.")
            else:
                st.success(f"✅ Am găsit {len(modele_disponibile)} modele!")
                st.info("Copiază unul dintre numele de mai sus (de exemplu 'models/gemini-1.5-flash') și spune-mi care apare în listă.")

        except Exception as e:
            st.error(f"Eroare la citirea listei: {e}")

    else:
        st.error("⚠️ Cheia API lipsește din Secrets!")

except Exception as e:
    st.error(f"Eroare critică: {e}")





