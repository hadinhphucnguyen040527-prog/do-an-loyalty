import streamlit as st
import pandas as pd
from datetime import datetime
from collections import deque

# ==========================================
# CÀI ĐẶT GIAO DIỆN & MÀU NỀN
# ==========================================
st.set_page_config(page_title="Loyalty App", layout="wide")

# Hàm chèn CSS tùy chỉnh
def add_bg_and_style():
    st.markdown(
        """
        <style>
        /* Đổi màu nền toàn bộ trang web (Gradient nhạt sang trọng) */
        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* Chỉnh màu tiêu đề chính */
        h1 {
            color: #2c3e50;
            text-align: center;
            font-family: 'Arial Black', sans-serif;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }

        /* Làm nổi bật các Tab */
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #ffffff;
            border-radius: 10px 10px 0 0;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            box-shadow: 0px -2px 5px rgba(0,0,0,0.05);
        }
        
        /* Khung chứa nội dung (Card) */
        .css-1r6slb0, .css-18e3th9 {
            background-color: rgba(255, 255, 255, 0.8);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        /* Màu nút bấm */
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 10px 24px;
            transition: all 0.3s;
        }
        .stButton>button:hover {
            background-color: #45a049;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            transform: scale(1.02);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# Gọi hàm áp dụng CSS
add_bg_and_style()

# ==========================================
# PHẦN 1: CORE LOGIC (Giữ nguyên cấu trúc thuật toán)
# ==========================================
class LoyaltySystem:
    def __init__(self):
        self.tai_khoan_kh = {}
        self.ty_le_hoan = {"AN_UONG": 0.05, "MUA_SAM": 0.02, "GIAI_TRI": 0.03, "KHAC": 0.01}
        self.hang_doi_doi_qua = deque() # Queue
        self.ngan_xep_undo = []         # Stack
        self.so_luong_khach = 0

    def them_khach_hang(self, ten_kh):
        self.so_luong_khach += 1
        ma_kh = f"KH{self.so_luong_khach:02d}"
        self.tai_khoan_kh[ma_kh] = {
            "ten": ten_kh, "tong_diem": 0.0, "tong_tien_hoan": 0.0,
            "hang_thanh_vien": "Đồng", "lich_su_gd": []
        }
        return ma_kh

    def xep_hang_thanh_vien(self, ma_kh):
        tk = self.tai_khoan_kh[ma_kh]
        diem = tk["tong_diem"]
        if diem >= 10000: tk["hang_thanh_vien"] = "Kim Cương"
        elif diem >= 5000: tk["hang_thanh_vien"] = "Vàng"
        elif diem >= 1000: tk["hang_thanh_vien"] = "Bạc"
        else: tk["hang_thanh_vien"] = "Đồng"

    def ghi_nhan_giao_dich(self, ma_kh, ma_gd, so_tien, danh_muc):
        if ma_kh not in self.tai_khoan_kh: return False, "Không tìm thấy mã khách hàng!"
        
        ty_le = self.ty_le_hoan.get(danh_muc, 0.01)
        tien_hoan = so_tien * ty_le
        diem_thuong = so_tien / 10000 
        tk = self.tai_khoan_kh[ma_kh]
        
        self.ngan_xep_undo.append({
            "ma_kh": ma_kh, "ma_gd": ma_gd,
            "diem_truoc_gd": tk["tong_diem"],
            "tien_hoan_truoc_gd": tk["tong_tien_hoan"],
            "hang_truoc_gd": tk["hang_thanh_vien"]
        })
        
        giao_dich = {
            "ma_gd": ma_gd, "ngay": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "so_tien": so_tien, "danh_muc": danh_muc,
            "diem_nhan": diem_thuong, "tien_hoan": tien_hoan
        }
        tk["lich_su_gd"].append(giao_dich)
        tk["tong_diem"] += diem_thuong
        tk["tong_tien_hoan"] += tien_hoan
        self.xep_hang_thanh_vien(ma_kh)
        return True, f"Thành công! +{diem_thuong:,.0f} điểm | Hoàn +{tien_hoan:,.0f}đ"

    def hoan_tac_giao_dich(self):
        if not self.ngan_xep_undo: return False, "Stack trống: Không có GD nào để hoàn tác."
        trang_thai = self.ngan_xep_undo.pop()
        ma_kh = trang_thai["ma_kh"]
        tk = self.tai_khoan_kh[ma_kh]
        tk["tong_diem"] = trang_thai["diem_truoc_gd"]
        tk["tong_tien_hoan"] = trang_thai["tien_hoan_truoc_gd"]
        tk["hang_thanh_vien"] = trang_thai["hang_truoc_gd"]
        if tk["lich_su_gd"]: tk["lich_su_gd"].pop()
        self.tai_khoan_kh[ma_kh] = tk
        return True, f"Đã hoàn tác GD {trang_thai['ma_gd']} của khách {ma_kh}."

    def sap_xep_giao_dich(self, ma_kh):
        if ma_kh not in self.tai_khoan_kh: return []
        def quick_sort(arr, key):
            if len(arr) <= 1: return arr
            pivot = arr[len(arr) // 2]
            left = [x for x in arr if x[key] < pivot[key]]
            middle = [x for x in arr if x[key] == pivot[key]]
            right = [x for x in arr if x[key] > pivot[key]]
            return quick_sort(left, key) + middle + quick_sort(right, key)
        
        ds = self.tai_khoan_kh[ma_kh]["lich_su_gd"]
        ds_sap_xep = quick_sort(ds, "tien_hoan")
        return ds_sap_xep[::-1]

    def tao_yeu_cau_doi_qua(self, ma_kh, so_diem_can, phan_thuong):
        tk = self.tai_khoan_kh.get(ma_kh)
        if tk and tk["tong_diem"] >= so_diem_can:
            tk["tong_diem"] -= so_diem_can
            self.hang_doi_doi_qua.append({
                "ma_kh": ma_kh, "phan_thuong": phan_thuong,
                "thoi_gian": datetime.now().strftime("%H:%M:%S")
            })
            return True, f"Đã đưa yêu cầu đổi '{phan_thuong}' vào Hàng đợi Queue."
        return False, "Lỗi: Khách hàng không tồn tại hoặc không đủ điểm!"

    def xu_ly_doi_qua(self):
        if not self.hang_doi_doi_qua: return False, "Hàng đợi Queue đang trống."
        yeu_cau = self.hang_doi_doi_qua.popleft()
        return True, f"Đã xuất quà '{yeu_cau['phan_thuong']}' cho {yeu_cau['ma_kh']} (Lúc {yeu_cau['thoi_gian']})."

# ==========================================
# KHỞI TẠO DỮ LIỆU & GIAO DIỆN
# ==========================================
if 'ht' not in st.session_state:
    st.session_state.ht = LoyaltySystem()
    st.session_state.ht.them_khach_hang("Hà Đình Phúc Nguyên")
    st.session_state.ht.ghi_nhan_giao_dich("KH01", "GD001", 500000, "AN_UONG")

ht = st.session_state.ht

st.title("🛍️ HỆ THỐNG QUẢN LÝ TÍCH ĐIỂM & HOÀN TIỀN")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs(["👥 Tổng quan & Khách hàng", "💸 Giao dịch & Sắp xếp", "🎁 Đổi quà (Queue)", "↩️ Hoàn tác (Stack)"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Tạo tài khoản mới")
        ten_kh = st.text_input("Nhập tên khách hàng:")
        if st.button("Tạo tài khoản"):
            if ten_kh:
                ma_moi = ht.them_khach_hang(ten_kh)
                st.success(f"Tạo thành công! Mã khách hàng: **{ma_moi}**")
            else:
                st.error("Vui lòng nhập tên!")
    with col2:
        st.subheader("Danh sách Khách hàng")
        if ht.tai_khoan_kh:
            df_kh = pd.DataFrame.from_dict(ht.tai_khoan_kh, orient='index')
            st.dataframe(df_kh.drop(columns=['lich_su_gd']), use_container_width=True)
        else:
            st.info("Hệ thống chưa có dữ liệu.")

with tab2:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader("Nhập giao dịch")
        ma_kh_gd = st.text_input("Mã KH:", value="KH01")
        ma_gd = st.text_input("Mã GD:", value="GD002")
        so_tien = st.number_input("Số tiền (VNĐ):", min_value=0, step=10000)
        danh_muc = st.selectbox("Danh mục:", ["AN_UONG", "MUA_SAM", "GIAI_TRI", "KHAC"])
        if st.button("Ghi nhận giao dịch"):
            thanh_cong, msg = ht.ghi_nhan_giao_dich(ma_kh_gd, ma_gd, so_tien, danh_muc)
            if thanh_cong: st.success(msg)
            else: st.error(msg)
    with col2:
        st.subheader("Lịch sử Giao dịch (Quick Sort)")
        ma_kh_ls = st.text_input("Nhập Mã KH để xem:", value="KH01")
        if st.button("Lọc và Sắp xếp (Tiền hoàn giảm dần)"):
            ds_gd = ht.sap_xep_giao_dich(ma_kh_ls)
            if ds_gd:
                st.table(pd.DataFrame(ds_gd))
            else:
                st.warning("Không có dữ liệu hoặc sai mã KH.")

with tab3:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Xếp hàng đổi quà")
        ma_kh_qua = st.text_input("Mã KH đổi quà:")
        qua = st.text_input("Tên phần thưởng:")
        diem_can = st.number_input("Số điểm cần trừ:", min_value=1, step=50)
        if st.button("Đăng ký đổi quà"):
            tc, msg = ht.tao_yeu_cau_doi_qua(ma_kh_qua, diem_can, qua)
            if tc: st.success(msg)
            else: st.error(msg)
    with col2:
        st.subheader("Xử lý Hàng đợi (FIFO)")
        if len(ht.hang_doi_doi_qua) > 0:
            st.info(f"Đang có {len(ht.hang_doi_doi_qua)} người xếp hàng.")
            st.write(list(ht.hang_doi_doi_qua))
        else:
            st.write("Hàng đợi trống.")
        if st.button("Phát quà (Popleft)"):
            tc, msg = ht.xu_ly_doi_qua()
            if tc: st.success(msg)
            else: st.warning(msg)

with tab4:
    st.subheader("Hoàn tác Giao dịch (LIFO)")
    st.write(f"Hiện có **{len(ht.ngan_xep_undo)}** trạng thái lưu trong Stack.")
    if st.button("Hoàn tác (Undo) Giao dịch gần nhất"):
        tc, msg = ht.hoan_tac_giao_dich()
        if tc: st.success(msg)
        else: st.warning(msg)
