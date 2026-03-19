import streamlit as st
import asyncio
import edge_tts
from io import BytesIO

# --- STREAMLIT UI SETUP ---
st.set_page_config(page_title="ISOC Voice Reader Pro", page_icon="🔊", layout="centered")

# --- FUNCTIONS ---
async def text_to_speech_ai(text, voice, level):
    """สร้างเสียงอ่านพร้อมปรับความเร็วตามระดับ -5 ถึง 5"""
    # แปลงระดับ 1-5 เป็นเปอร์เซ็นต์ (เช่น ระดับ 1 = +10%, ระดับ -2 = -20%)
    speed_percent = level * 10
    rate_str = f"{speed_percent:+d}%"
    
    communicate = edge_tts.Communicate(text, voice, rate=rate_str)
    audio_data = BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data.write(chunk["data"])
    audio_data.seek(0)
    return audio_data

# --- MAIN UI ---
st.title("🔊 ISOC Voice Reader")
st.caption("เวอร์ชันปรับปรุง: ควบคุมระดับความเร็ว -5 ถึง 5")

# --- ส่วนการตั้งค่า (ออกแบบมาเพื่อหน้าจอมือถือ) ---
with st.container():
    col_v, col_s = st.columns([1, 1])
    
    with col_v:
        # เลือกเสียง 2 เสียงตามที่กำหนด
        voice_map = {
            "👨 นิวัฒน์ (ชาย)": "th-TH-NiwatNeural",
            "👩 เปรมวดี (หญิง)": "th-TH-PremwadeeNeural"
        }
        selected_voice_label = st.selectbox("เลือกเสียง", options=list(voice_map.keys()))
        selected_voice_id = voice_map[selected_voice_label]

    with col_s:
        # ปรับความเร็วเป็นระดับ -5 ถึง 5
        speed_level = st.select_slider(
            "ระดับความเร็ว",
            options=list(range(-5, 6)),
            value=0,
            help="0 คือปกติ, + คือเร็วขึ้น, - คือช้าลง"
        )

# แสดงสถานะความเร็วปัจจุบันแบบเข้าใจง่าย
speed_text = "ปกติ" if speed_level == 0 else f"{'เร็ว' if speed_level > 0 else 'ช้า'} ระดับ {abs(speed_level)}"
st.info(f"📢 กำลังจะอ่านด้วยเสียง: {selected_voice_label} | ความเร็ว: {speed_text}")

# --- ส่วนรับข้อมูล ---
text_input = st.text_area("✍️ วางข้อความภาษาไทย", height=250, placeholder="ใส่ข้อความที่ต้องการให้อ่านที่นี่...")

# --- ปุ่มดำเนินการ ---
col_run, col_clr = st.columns(2)

with col_run:
    generate_btn = st.button("🔊 เริ่มอ่านเสียง", type="primary", use_container_width=True)

with col_clr:
    if st.button("🧹 ล้างหน้าจอ", use_container_width=True):
        st.rerun()

# --- PROCESSING ---
if generate_btn:
    if not text_input.strip():
        st.warning("⚠️ กรุณาใส่ข้อความก่อนครับ")
    else:
        with st.spinner(f"🤖 AI กำลังประมวลผลด้วยความเร็วระดับ {speed_level}..."):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                audio_file = loop.run_until_complete(
                    text_to_speech_ai(text_input, selected_voice_id, speed_level)
                )
                
                st.success("✅ สร้างเสียงสำเร็จ!")
                st.audio(audio_file, format="audio/mp3")
                
                st.download_button(
                    label="📥 ดาวน์โหลดไฟล์ MP3",
                    data=audio_file,
                    file_name=f"isoc_speed_{speed_level}.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"❌ พบปัญหาทางเทคนิค: {str(e)}")

# --- FOOTER ---
st.markdown("---")
st.caption("พัฒนาโดย พ.อ.นริศ เกิดบาง ผอ.สขผ.สบข.กอ.รมน.")