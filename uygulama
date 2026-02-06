import streamlit as st
import json
import os

# --- VERİTABANI AYARLARI ---
DB_FILE = "sozlesme_takip_db.json"

def veri_yukle():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def veri_kaydet(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- SAYFA YAPILANDIRMASI ---
st.set_page_config(page_title="Sözleşme Kontrol Paneli", layout="centered")

if 'db' not in st.session_state:
    st.session_state.db = veri_yukle()

# --- YAN PANEL (NAVİGASYON) ---
with st.sidebar:
    st.title("📂 Sözleşme Listesi")
    
    # Yeni Kontrol Listesi Oluşturma
    with st.expander("➕ Yeni Takip Başlat"):
        yeni_ad = st.text_input("Sözleşme/Proje Adı")
        if st.button("Listeyi Oluştur"):
            if yeni_ad and yeni_ad not in st.session_state.db:
                st.session_state.db[yeni_ad] = {
                    "asama_index": 0,
                    "tamamlananlar": []
                }
                veri_kaydet(st.session_state.db)
                st.rerun()

    st.divider()
    
    # Mevcut Sözleşmeler
    secilen_sozlesme = st.radio(
        "Takip Edilen Sözleşmeler:", 
        options=list(st.session_state.db.keys()) if st.session_state.db else ["Henüz liste yok"]
    )
    
    if st.button("🗑️ Seçili Listeyi Sil", type="secondary") and secilen_sozlesme != "Henüz liste yok":
        del st.session_state.db[secilen_sozlesme]
        veri_kaydet(st.session_state.db)
        st.rerun()

# --- ANA İÇERİK ---
# Sabit Akış Şablonu (Her sözleşme için aynı kurallar geçerli)
AKIS = [
    {"baslik": "1. Taslak Hazırlama", "isler": ["Taraf bilgilerini kontrol et", "Ödeme şartlarını ekle", "Fesih maddesini düzenle"]},
    {"baslik": "2. Hukuki İnceleme", "isler": ["Risk analizi yap", "Hukuk birimi onayı al", "Damga vergisi hesapla"]},
    {"baslik": "3. Onay ve İmza", "is har": ["Yönetim onayı", "Müşteriye gönderim", "Islak/E-imza kontrolü"]},
    {"baslik": "4. Arşivleme", "isler": ["Dijital kopyayı sakla", "Fiziki dosyayı rafa kaldır"]}
]

if secilen_sozlesme == "Henüz liste yok":
    st.info("Hoş geldiniz! Başlamak için sol panelden yeni bir sözleşme takibi oluşturun.")
else:
    st.header(f"📌 {secilen_sozlesme}")
    
    sozlesme_verisi = st.session_state.db[secilen_sozlesme]
    mevcut_asama_idx = sozlesme_verisi.get("asama_index", 0)
    
    # İlerleme Çubuğu
    toplam_asama = len(AKIS)
    ilerleme = mevcut_asama_idx / toplam_asama
    st.progress(ilerleme)
    st.write(f"Süreç Durumu: %{int(ilerleme * 100)}")

    st.divider()

    # Sıralı Gösterim Mantığı
    for idx, asama in enumerate(AKIS):
        # Sadece mevcut aşamayı veya geçilmiş aşamaları göster
        if idx <= mevcut_asama_idx:
            is_active = (idx == mevcut_asama_idx)
            with st.expander(f"{asama['baslik']}", expanded=is_active):
                st.markdown(f"**Yapılacaklar:**")
                
                tamamlanan_gorev_sayisi = 0
                for gorev in asama["isler"]:
                    unique_key = f"{secilen_sozlesme}_{idx}_{gorev}"
                    # Veritabanında kayıtlı mı kontrol et
                    is_checked = gorev in sozlesme_verisi["tamamlananlar"]
                    
                    check = st.checkbox(gorev, value=is_checked, key=unique_key)
                    
                    if check and gorev not in sozlesme_verisi["tamamlananlar"]:
                        sozlesme_verisi["tamamlananlar"].append(gorev)
                        veri_kaydet(st.session_state.db)
                    elif not check and gorev in sozlesme_verisi["tamamlananlar"]:
                        sozlesme_verisi["tamamlananlar"].remove(gorev)
                        veri_kaydet(st.session_state.db)
                    
                    if check: tamamlanan_gorev_sayisi += 1
                
                # Eğer o aşamadaki tüm görevler bittiyse ve son aşamada değilsek bir sonrakini aç
                if tamamlanan_gorev_sayisi == len(asama["isler"]) and idx == mevcut_asama_idx:
                    if mevcut_asama_idx < toplam_asama - 1:
                        sozlesme_verisi["asama_index"] += 1
                        veri_kaydet(st.session_state.db)
                        st.rerun()

    if mevcut_asama_idx == toplam_asama - 1 and len(sozlesme_verisi["tamamlananlar"]) == sum(len(a["isler"]) for a in AKIS):
        st.balloons()
        st.success("✅ Bu sözleşme için tüm süreçler tamamlandı!")
