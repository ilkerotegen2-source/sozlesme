import streamlit as st
import json
import os

# --- DOSYA YOLLARI ---
SABLON_FILE = "sozlesme_sablonu.json"
VERI_FILE = "sozlesme_kayitlari.json"

# --- VERİ FONKSİYONLARI ---
def load_json(file_path, default_value):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default_value

def save_json(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# --- ŞABLON BAŞLATMA ---
# Eğer hiç şablon yoksa varsayılan 3 adımı oluşturur
varsayilan_asama = [
    {"name": "1. Taslak Hazırlama", "tasks": ["Müşteri bilgilerini gir", "Kapsamı belirle"]},
    {"name": "2. Hukuki İnceleme", "tasks": ["Risk analizi yap", "Avukat onayı al"]},
    {"name": "3. İmza Süreci", "tasks": ["E-imza gönder", "Arşivle"]}
]

sablon = load_json(SABLON_FILE, varsayilan_asama)
kayitlar = load_json(VERI_FILE, {})

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Dinamik Sözleşme Yönetimi", layout="wide")

# --- SIDEBAR: ŞABLON VE SÖZLEŞME YÖNETİMİ ---
with st.sidebar:
    st.header("⚙️ Şablonu Düzenle")
    st.info("Burada yapacağınız değişiklikler tüm yeni sözleşmeleri etkiler.")
    
    with st.expander("➕ Yeni Aşama/Görev Ekle"):
        yeni_asama_adi = st.text_input("Aşama Adı")
        yeni_gorevler = st.text_area("Görevler (Her satıra bir tane)").split('\n')
        
        if st.button("Şablona Kaydet"):
            temiz_gorevler = [t.strip() for t in yeni_gorevler if t.strip()]
            if yeni_asama_adi and temiz_gorevler:
                sablon.append({"name": yeni_asama_adi, "tasks": temiz_gorevler})
                save_json(SABLON_FILE, sablon)
                st.success("Şablon güncellendi!")
                st.rerun()

    if st.button("♻️ Şablonu Sıfırla (Varsayılana Dön)"):
        save_json(SABLON_FILE, varsayilan_asama)
        st.rerun()

    st.divider()
    st.header("📄 Sözleşmeler")
    yeni_sozlesme_adi = st.text_input("Yeni Sözleşme Başlat")
    if st.button("Sözleşme Oluştur"):
        if yeni_sozlesme_adi and yeni_sozlesme_adi not in kayitlar:
            # Yeni sözleşmeyi O ANKİ ŞABLON ile oluşturur
            kayitlar[yeni_sozlesme_adi] = {
                "asama_durumu": 0,
                "tamamlanan_gorevler": [],
                "mevcut_sablon": sablon # O anki şablon kopyalanır
            }
            save_json(VERI_FILE, kayitlar)
            st.rerun()

    secilen_is = st.selectbox("Takip Edilecek Sözleşme", options=list(kayitlar.keys()) if kayitlar else ["Yok"])

# --- ANA EKRAN ---
if secilen_is != "Yok":
    st.title(f"📋 {secilen_is}")
    data = kayitlar[secilen_is]
    aktif_sablon = data["mevcut_sablon"]
    
    # İlerleme Çubuğu
    toplam_gorev = sum(len(a["tasks"]) for a in aktif_sablon)
    yapilan_gorev = len(data["tamamlanan_gorevler"])
    st.progress(yapilan_gorev / toplam_gorev if toplam_gorev > 0 else 0)

    # SIRALI AKIŞ MANTIĞI
    for idx, asama in enumerate(aktif_sablon):
        # Kilit mekanizması: Önceki aşama bitmeden sonraki görünmez
        if idx > 0:
            onceki_asama_gorevleri = aktif_sablon[idx-1]["tasks"]
            if not all(g in data["tamamlanan_gorevler"] for g in onceki_asama_gorevleri):
                st.warning(f"🔒 '{aktif_sablon[idx-1]['name']}' tamamlanmadan bu aşama açılmaz.")
                break

        with st.expander(f"🔹 {asama['name']}", expanded=True):
            for gorev in asama["tasks"]:
                gorev_key = f"{secilen_is}_{idx}_{gorev}"
                is_checked = gorev in data["tamamlanan_gorevler"]
                
                if st.checkbox(gorev, value=is_checked, key=gorev_key):
                    if gorev not in data["tamamlanan_gorevler"]:
                        data["tamamlanan_gorevler"].append(gorev)
                        save_json(VERI_FILE, kayitlar)
                        st.rerun()
                else:
                    if gorev in data["tamamlanan_gorevler"]:
                        data["tamamlanan_gorevler"].remove(gorev)
                        save_json(VERI_FILE, kayitlar)
                        st.rerun()

else:
    st.info("Lütfen sol panelden bir sözleşme oluşturun.")
