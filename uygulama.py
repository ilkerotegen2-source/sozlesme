import streamlit as st
import json
import os

# --- DOSYA YOLLARI ---
SABLON_FILE = "master_sablon_v2.json"
VERI_FILE = "sozlesme_arsivi_v2.json"

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

# --- PROGRAM BAŞLATMA ---
st.set_page_config(page_title="Master Sözleşme Editörü", layout="wide")

if 'master_sablon' not in st.session_state:
    varsayilan = [
        {"name": "1. Taslak", "tasks": ["Bilgileri topla", "Metni yaz"]},
        {"name": "2. Hukuk", "tasks": ["Risk analizi", "Onay al"]},
        {"name": "3. İmza", "tasks": ["İmzalat", "Arşivle"]}
    ]
    st.session_state.master_sablon = load_json(SABLON_FILE, varsayilan)

if 'kayitlar' not in st.session_state:
    st.session_state.kayitlar = load_json(VERI_FILE, {})

# --- SIDEBAR: ŞABLON EDİTÖRÜ ---
with st.sidebar:
    st.header("🛠️ Şablon Editörü")
    st.caption("Buradaki değişiklikler kodun geneline işlenir.")

    # ŞABLON DÜZENLEME ALANI
    with st.expander("📝 Mevcut Aşamaları Düzenle/Sırala"):
        yeni_sablon_duzeni = []
        for i, stage in enumerate(st.session_state.master_sablon):
            st.markdown(f"**Aşama {i+1}**")
            new_n = st.text_input(f"Aşama Adı", value=stage['name'], key=f"edit_n_{i}")
            new_t = st.text_area(f"Görevler (Satır satır)", value="\n".join(stage['tasks']), key=f"edit_t_{i}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"⬆️ Yukarı", key=f"up_{i}") and i > 0:
                    st.session_state.master_sablon[i], st.session_state.master_sablon[i-1] = st.session_state.master_sablon[i-1], st.session_state.master_sablon[i]
                    save_json(SABLON_FILE, st.session_state.master_sablon)
                    st.rerun()
            with col2:
                if st.button(f"🗑️ Sil", key=f"del_{i}"):
                    st.session_state.master_sablon.pop(i)
                    save_json(SABLON_FILE, st.session_state.master_sablon)
                    st.rerun()
            
            yeni_sablon_duzeni.append({"name": new_n, "tasks": [x.strip() for x in new_t.split("\n") if x.strip()]})
            st.divider()
        
        if st.button("✅ Tüm Değişiklikleri Şablona Kaydet"):
            st.session_state.master_sablon = yeni_sablon_duzeni
            save_json(SABLON_FILE, st.session_state.master_sablon)
            st.success("Ana şablon güncellendi!")
            st.rerun()

    with st.expander("➕ Araya/Sona Yeni Aşama Ekle"):
        insert_pos = st.number_input("Kaçıncı sıraya eklensin?", min_value=1, max_value=len(st.session_state.master_sablon)+1, value=len(st.session_state.master_sablon)+1)
        ins_name = st.text_input("Yeni Aşama Başlığı")
        ins_tasks = st.text_area("Yeni Görevler")
        
        if st.button("Aşamayı Yerleştir"):
            if ins_name:
                new_entry = {"name": ins_name, "tasks": [x.strip() for x in ins_tasks.split("\n") if x.strip()]}
                st.session_state.master_sablon.insert(int(insert_pos)-1, new_entry)
                save_json(SABLON_FILE, st.session_state.master_sablon)
                st.rerun()

    st.divider()
    st.header("📄 Yeni Sözleşme")
    yeni_soz_adi = st.text_input("Sözleşme/Müşteri Adı")
    if st.button("Sözleşmeyi Başlat"):
        if yeni_soz_adi and yeni_soz_adi not in st.session_state.kayitlar:
            st.session_state.kayitlar[yeni_soz_adi] = {
                "sozlesme_sablone": list(st.session_state.master_sablon),
                "completed": []
            }
            save_json(VERI_FILE, st.session_state.kayitlar)
            st.rerun()

    secilen = st.selectbox("İş Seçin", options=list(st.session_state.kayitlar.keys()) if st.session_state.kayitlar else ["Boş"])

# --- ANA EKRAN ---
if secilen != "Boş":
    st.title(f"🔍 {secilen}")
    current_contract = st.session_state.kayitlar[secilen]
    steps = current_contract["sozlesme_sablone"]
    
    # Progress
    total_g = sum(len(x["tasks"]) for x in steps)
    done_g = len(current_contract["completed"])
    st.progress(done_g / total_g if total_g > 0 else 0)

    # AKIŞ (SEQUENTIAL LOGIC)
    for idx, asama in enumerate(steps):
        # Kilit mekanizması
        if idx > 0:
            onceki_gorevler = steps[idx-1]["tasks"]
            if not all(t in current_contract["completed"] for t in onceki_gorevler):
                st.warning(f"🔒 Önceki aşama ({steps[idx-1]['name']}) tamamlanmadan bu aşama açılmaz.")
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
