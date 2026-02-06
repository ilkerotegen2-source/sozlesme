import streamlit as st
import json
import os

# --- VERİTABANI DOSYASI ---
DB_FILE = "contract_database.json"

def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_db(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Sözleşme Takip Sistemi", layout="wide")

if 'db' not in st.session_state:
    st.session_state.db = load_db()

# --- SIDEBAR (YÖNETİM PANELİ) ---
with st.sidebar:
    st.header("🛠️ Yönetim Paneli")
    
    # 1. YENİ SÖZLEŞME EKLE
    with st.expander("➕ Yeni Sözleşme Tanımla", expanded=True):
        new_name = st.text_input("Sözleşme Adı")
        if st.button("Sözleşmeyi Kaydet"):
            if new_name and new_name not in st.session_state.db:
                st.session_state.db[new_name] = {"stages": [], "completed_tasks": []}
                save_db(st.session_state.db)
                st.success(f"{new_name} oluşturuldu!")
                st.rerun()

    st.divider()

    # 2. SÖZLEŞME SEÇ
    all_contracts = list(st.session_state.db.keys())
    selected_contract = st.selectbox("Düzenlenecek Sözleşme", options=all_contracts if all_contracts else ["Sözleşme Yok"])

    # 3. SEÇİLİ SÖZLEŞMEYE AŞAMA EKLE
    if selected_contract != "Sözleşme Yok":
        st.divider()
        st.subheader(f"⚙️ {selected_contract} Ayarları")
        with st.expander("📏 Yeni Aşama/Görev Ekle"):
            stage_name = st.text_input("Aşama Başlığı (Örn: Taslak)")
            tasks_text = st.text_area("Görevler (Her satıra bir tane)")
            if st.button("Aşamayı Ekle"):
                if stage_name and tasks_text:
                    new_stage = {
                        "name": stage_name,
                        "tasks": [t.strip() for t in tasks_text.split("\n") if t.strip()]
                    }
                    st.session_state.db[selected_contract]["stages"].append(new_stage)
                    save_db(st.session_state.db)
                    st.rerun()
        
        if st.button("🗑️ Sözleşmeyi Tamamen Sil"):
            del st.session_state.db[selected_contract]
            save_db(st.session_state.db)
            st.rerun()

# --- ANA EKRAN (TAKİP ALANI) ---
if selected_contract == "Sözleşme Yok":
    st.info("Sol taraftaki panelden bir sözleşme oluşturun ve aşamalarını ekleyin.")
else:
    st.title(f"📑 {selected_contract}")
    data = st.session_state.db[selected_contract]
    
    if not data["stages"]:
        st.warning("Bu sözleşme için henüz bir aşama eklenmemiş. Sol panelden ekleme yapın.")
    else:
        # İlerleme Hesaplama
        total_tasks = sum(len(s["tasks"]) for s in data["stages"])
        done_tasks = len(data["completed_tasks"])
        progress = done_tasks / total_tasks if total_tasks > 0 else 0
        st.progress(progress)
        st.write(f"Toplam İlerleme: %{int(progress*100)}")

        # AŞAMALARI GÖSTER (SIRALI KİLİT SİSTEMİ)
        for i, stage in enumerate(data["stages"]):
            # Önceki aşamadaki tüm görevler bitti mi kontrol et
            prev_stage_done = True
            if i > 0:
                prev_stage = data["stages"][i-1]
                prev_stage_done = all(t in data["completed_tasks"] for t in prev_stage["tasks"])

            if not prev_stage_done:
                st.lockup_msg = st.warning(f"🔒 '{data['stages'][i-1]['name']}' aşaması tamamlanmadan bu alan açılmaz.")
                break # Diğer aşamaları gösterme

            with st.expander(f"Aşama {i+1}: {stage['name']}", expanded=True):
                for task in stage["tasks"]:
                    is_done = task in data["completed_tasks"]
                    
                    # Checkbox
                    if st.checkbox(task, value=is_done, key=f"{selected_contract}_{i}_{task}"):
                        if task not in data["completed_tasks"]:
                            data["completed_tasks"].append(task)
                            save_db(st.session_state.db)
                            st.rerun()
                    else:
                        if task in data["completed_tasks"]:
                            data["completed_tasks"].remove(task)
                            save_db(st.session_state.db)
                            st.rerun()
