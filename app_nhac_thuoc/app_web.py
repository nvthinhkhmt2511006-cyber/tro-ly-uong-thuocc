import streamlit as st
from pydantic import BaseModel
from google import genai
from google.genai import types
from PIL import Image

class ThongTinThuoc(BaseModel):
    ten_thuoc: str 
    lieu_luong: str 
    cac_buoi_uong: list[str] 
    gio_uong_goi_y: list[str] 
    ghi_chu: str 

class ToaThuocSmart(BaseModel):
    danh_sach_thuoc: list[ThongTinThuoc]
    so_ngay_uong: int 

def doc_toa_thuoc_bang_ai(file_anh):
    # TRUYỀN TRỰC TIẾP MÃ AQ... CỦA BẠN VÀO ĐÂY:
    client = genai.Client(api_key="AQ.Ab8RN6KrJBCd6hbU3X2aaUVU-V0ornZdDX6QI5H374IZBJwpxQ") 
    
    image = Image.open(file_anh)
    loi_dan = """
    Hãy đọc toa thuốc trong ảnh.
    Trích xuất tên thuốc, liều dùng, số ngày uống.
    Đổi các buổi (Sáng, Trưa, Chiều, Tối) thành giờ cụ thể (08:00, 12:00, 16:00, 20:00).
    """

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[image, loi_dan],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ToaThuocSmart,
            temperature=0.1 
        ),
    )
    return ToaThuocSmart.model_validate_json(response.text)

st.set_page_config(page_title="Trợ Lý Nhắc Thuốc", page_icon="💊")
st.title("💊 Trợ Lý Đọc Toa Thuốc Thông Minh")

file_tai_len = st.file_uploader("Tải ảnh toa thuốc...", type=["jpg", "jpeg", "png"])

if file_tai_len is not None:
    st.image(file_tai_len, caption="Ảnh đã tải lên", use_container_width=True)
    
    if st.button("🤖 Phân tích toa thuốc"):
        with st.spinner("Gemini đang đọc đơn thuốc..."):
            try:
                du_lieu = doc_toa_thuoc_bang_ai(file_tai_len)
                if du_lieu:
                    st.success(f"✅ Đơn thuốc dùng trong {du_lieu.so_ngay_uong} ngày")
                    for thuoc in du_lieu.danh_sach_thuoc:
                        with st.expander(f"💊 {thuoc.ten_thuoc}"):
                            st.write(f"**Liều dùng:** {thuoc.lieu_luong}")
                            st.write(f"**Giờ uống:** {', '.join(thuoc.gio_uong_goi_y)}")
                            if thuoc.ghi_chu: st.info(f"Ghi chú: {thuoc.ghi_chu}")
            except Exception as e:
                st.error(f"Lỗi: {e}")