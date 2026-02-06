import streamlit as st
import json
import os

# --- DOSYA YOLLARI ---
SABLON_FILE = "master_sablon.json"
VERI_FILE = "sozlesme_arsivi.json"

# --- VERİ FONKSİYONLARI ---
def load_json(file_path, default_value):
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return default_value
    return default_value

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- PROGRAM BAŞLANGIÇ AYARLARI ---
st.set_page_config(page_title="Sözleşme Şablon Sistemi", layout="wide")

# Varsayılan Şablon (Eğer dosya yoksa ilk kez oluşturulur)
if 'master_sablon' not in st.session_state:
    varsayilan = [
        {"name": "1. Taslak", "tasks": ["Bilgileri topla"]},
        {"name": "2. Hukuk", "tasks": ["Onay al"]},
        {"name": "3. İmza", "tasks": ["İmzalat"]}
    ]
    st.session_state.master_sablon = load_json(SABLON_FILE, varsayilan)

if 'kayitlar' not in st.session_state:
    st.session_state.kayitlar = load_json(VERI_FILE, {})

# --- SIDEBAR (ŞABLON VE YÖNETİM) ---
with st.sidebar:
    st.header("⚙️ Şablon Yönetimi")
    st.info("Buradaki adımlar tüm yeni sözleşmelerin varsayılanı olur.")
    
    # ŞABLONU GÜNCELLEME ALANI
    with st.expander("📝 Ana Şablonu Düzenle"):
        # Mevcut şablonu düzenlemek veya silmek için
        for i, s_item in enumerate(st.session_state.master_sablon):
            st.text(f"{i+1}. {s_item['name']}")
        
        st.divider()
        st.subheader("Yeni Aşama Ekle")
        yeni_as_ad = st.text_input("Aşama Başlığı")
        yeni_as_grv = st.text_area("Görevler (Satır satır)").split('\n')
        
        if st.button("Şablona Kalıcı Ekle"):
            gorevler_listesi = [g.strip() for g in yeni_as_grv if g.strip()]
            if yeni_as_ad and gorevler_listesi:
                st.session_state.master_sablon.append({"name": yeni_as_ad, "tasks": gorevler_listesi})
                save_json(SABLON_FILE, st.session_state.master_sablon)
                st.success("Şablon güncellendi ve kaydedildi!")
                st.rerun()

    if st.button("🗑️ Şablonu Sıfırla"):
        if os.path.exists(SABLON_FILE): os.remove(SABLON_FILE)
        st.rerun()

    st.divider()
    st.header("📄 Sözleşme Başlat")
    yeni_soz_adi = st.text_input("İş/Müşteri Adı")
    if st.button("Yeni Takip Başlat"):
        if yeni_soz_adi and yeni_soz_adi not in st.session_state.kayitlar:
            # ÖNEMLİ: Yeni sözleşme oluştururken o anki güncel MASTER şablonu kopyalıyoruz
            st.session_state.kayitlar[yeni_soz_adi] = {
                "sozlesme_sablone": list(st.session_state.master_sablon), 
                "completed": []
            }
            save_json(VERI_FILE, st.session_state.kayitlar)
            st.success("Sözleşme başarıyla eklendi!")
            st.rerun()

    # Seçim Kutusu
    secilen = st.selectbox("İş Seçin", options=list(st.session_state.kayitlar.keys()) if st.session_state.kayitlar else ["Boş"])

# --- ANA EKRAN ---
if secilen != "Boş":
    st.title(f"🔍 {secilen}")
    current_contract = st.session_state.kayitlar[secilen]
    current_steps = current_contract["sozlesme_sablone"]
    
    # İlerleme
    total_g = sum(len(x["tasks"]) for x in current_steps)
    done_g = len(current_contract["completed"])
    st.progress(done_g / total_g if total_g > 0 else 0)

    # AKIŞ
    for idx, asama in enumerate(current_steps):
        # Kilit: Önceki aşama bitti mi?
        if idx > 0:
            onceki = current_steps[idx-1]["tasks"]
            if not all(t in current_contract["completed"] for t in onceki):
                st.warning(f"🔒 {current_steps[idx-1]['name']} aşamasını tamamlamadan burayı göremezsiniz.")
                break

        with st.expander(f"📌 {asama['name']}", expanded=True):
            for task in asama["tasks"]:
                cb_key = f"{secilen}_{idx}_{task}"
                is_checked = task in current_contract["completed"]
                
                if st.checkbox(task, value=is_checked, key=cb_key):
                    if task not in current_contract["completed"]:
                        current_contract["completed"].append(task)
                        save_json(VERI_FILE, st.session_state.kayitlar)
                        st.rerun()
                else:
                    if task in current_contract["completed"]:
                        current_contract["completed"].remove(task)
                        save_json(VERI_FILE, st.session_state.kayitlar)
                        st.rerun()
else:
    st.info("Sol taraftan 'Yeni Takip Başlat' butonuna basarak işlerinizi ekleyebilirsiniz.")
