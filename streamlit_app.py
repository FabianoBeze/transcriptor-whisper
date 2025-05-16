import streamlit as st
import whisper
from docx import Document
import tempfile
import os
import subprocess

# ✅ Instalar ffmpeg en Streamlit Cloud
os.system("apt-get update && apt-get install -y ffmpeg")

st.set_page_config(page_title="Transcriptor de Audio", layout="centered")

st.title("📝 Transcriptor de Audio con Whisper")
st.write("Sube un archivo de audio (.mp3, .wav, .mp4, .dat, .unknown) y genera su transcripción en texto y Word.")

uploaded_file = st.file_uploader("📂 Sube tu archivo de audio", type=["mp3", "wav", "m4a", "mp4", "aac", "dat", "unknown"])

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    # Renombrar si es .dat o .unknown a .mp4 (para que ffmpeg lo acepte)
    if uploaded_file.name.endswith(".dat") or uploaded_file.name.endswith(".unknown"):
        new_path = tmp_path + ".mp4"
        os.rename(tmp_path, new_path)
        tmp_path = new_path

    st.info("🔄 Convirtiendo audio a WAV...")

    # Convertir a WAV usando ffmpeg
    wav_path = tmp_path.rsplit(".", 1)[0] + ".wav"
    conversion = subprocess.run(
        ["ffmpeg", "-y", "-i", tmp_path, "-ar", "16000", "-ac", "1", wav_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if not os.path.exists(wav_path):
        st.error("❌ Error al convertir el audio. Asegúrate de que el archivo contenga audio válido.")
        st.stop()

    st.info("🔄 Transcribiendo audio, espera un momento...")

    model = whisper.load_model("base")
    result = model.transcribe(wav_path, language="es")

    st.success("✅ Transcripción completa")
    st.subheader("📄 Texto transcrito:")
    st.write(result["text"])

    doc = Document()
    doc.add_heading("Transcripción de Audio", 0)
    doc.add_paragraph(result["text"])

    word_file = "transcripcion.docx"
    doc.save(word_file)

    with open(word_file, "rb") as f:
        st.download_button("📥 Descargar Word", f, file_name=word_file, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    os.remove(tmp_path)
    os.remove(wav_path)
    os.remove(word_file)
