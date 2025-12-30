import streamlit as st
import pandas as pd
import numpy as np

# Configurare pagină
st.set_page_config(page_title="Loto Analyzer Pro", page_icon="📊", layout="wide")

# Stiluri CSS - Corectate pentru vizibilitate maximă
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    /* Scris negru pe galben deschis pentru anomalii - mult mai vizibil */
    .anomaly-card { 
        border: 2px solid #ff4b4b; 
        padding: 15px; 
        border-radius: 10px; 
        background-color: #fff3cd; 
        color: #000000; 
        margin-bottom: 15px; 
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

if 'runde' not in st.session_state: st.session_state.runde = []
if 'variante' not in st.session_state: st.session_state.variante = []

# --- MOTOR DETECȚIE ANOMALII ---
def detecteaza_anomalia(numere):
    if not numere: return []
    numere_s = sorted(numere)
    alerte = []
    # 1. Consecutivitate
    cons = sum(1 for i in range(len(numere_s)-1) if numere_s[i+1] - numere_s[i] == 1)
    if cons >= 2: alerte.append(f"Consecutive: {cons+1}")
    # 2. Suma (Raportată la media ta de 31/număr)
    suma = sum(numere)
    if suma < 60 or suma > 200: alerte.append(f"Suma: {suma}")
    # 3. Paritate
    pare = sum(1 for n in numere if n % 2 == 0)
    if pare == len(numere) or pare == 0: alerte.append("Paritate 4/0")
    # 4. Terminații
    ultimele = set(n % 10 for n in numere)
    if len(ultimele) == 1: alerte.append("Terminatie identica")
    return alerte

# --- SIDEBAR: GESTIONARE DATE ȘI DOWNLOAD ---
with st.sidebar:
    st.header("📥 Import Date")
    r_input = st.text_area("Introdu Runde", height=100)
    if st.button("Adaugă Runde", type="primary", use_container_width=True):
        for l in r_input.strip().split('\n'):
            try:
                n = [int(x.strip()) for x in l.replace(',', ' ').split() if x.strip()]
                if n: st.session_state.runde.append(n)
            except: pass
        st.rerun()

    v_input = st.text_area("Introdu Variante (ID, 1 2 3 4)", height=150)
    if st.button("Adaugă Variante", type="primary", use_container_width=True):
        for l in v_input.strip().split('\n'):
            try:
                parti = l.split(',', 1)
                id_v, nums = parti[0].strip(), [int(x) for x in parti[1].replace(',', ' ').split()]
                st.session_state.variante.append({'id': id_v, 'numere': nums})
            except: pass
        st.rerun()
    
    if st.button("Resetare Totală", use_container_width=True):
        st.session_state.runde = []; st.session_state.variante = []; st.rerun()

    # --- LOGICA DOWNLOAD FILTRATĂ ---
    if st.session_state.runde and st.session_state.variante:
        st.divider()
        st.header("💾 Export Curat")
        
        v_ids = [v['id'] for v in st.session_state.variante]
        v_nums = [v['numere'] for v in st.session_state.variante]
        r_sets = [set(r) for r in st.session_state.runde]
        v_sets = [set(v) for v in v_nums]
        matrice = np.array([[len(vs.intersection(rs)) for rs in r_sets] for vs in v_sets])
        
        linii_export = []
        for i in range(len(v_ids)):
            # 1. Verificăm dacă e Anomalie
            este_anomalie = len(detecteaza_anomalia(v_nums[i])) > 0
            
            # 2. Verificăm performanța
            max_h = np.max(matrice[i])
            c2 = np.sum(matrice[i] == 2)
            is_buna_sau_medie = (max_h >= 3) or (c2 > (len(r_sets) * 0.15))
            
            # Exportăm DOAR dacă are scor și NU este anomalie
            if is_buna_sau_medie and not este_anomalie:
                nums_str = " ".join(map(str, v_nums[i]))
                linii_export.append(f"{v_ids[i]}, {nums_str}")
        
        if linii_export:
            st.download_button(
                label="📥 Descarcă Bune & Fără Anomalii",
                data="\n".join(linii_export),
                file_name="selectie_finala.txt",
                mime="text/plain",
                use_container_width=True
            )
            st.success(f"Filtrate: {len(linii_export)} variante curate.")
        else:
            st.warning("Nicio variantă nu a trecut filtrul de siguranță.")

# --- AFIȘARE PRINCIPALĂ ---
if st.session_state.runde and st.session_state.variante:
    st.subheader("🚨 Detector Anomalii (Vizibilitate sporită)")
    anom_cols = st.columns(4)
    anom_count = 0
    for i, (vid, vnum) in enumerate(zip([v['id'] for v in st.session_state.variante], [v['numere'] for v in st.session_state.variante])):
        alerte = detecteaza_anomalia(vnum)
        if alerte:
            with anom_cols[anom_count % 4]:
                st.markdown(f"""<div class='anomaly-card'>
                    ID: {vid}<br>
                    <span style='font-size: 13px;'>{', '.join(alerte)}</span>
                </div>""", unsafe_allow_html=True)
                anom_count += 1
    
    st.divider()
    st.subheader("📊 Monitorizare Performanță")
    
    c0_counts = np.sum(matrice == 0, axis=1)
    sort_idx = np.argsort(-c0_counts)
    
    grid = st.columns(3)
    for idx, i in enumerate(sort_idx):
        res = matrice[i]
        c = {j: np.sum(res == j) for j in range(5)}
        max_val = np.max(res)
        
        # Culori carduri performanță
        if max_val >= 3: color, status = "#28a745", "BUNĂ"
        elif c[2] > (len(r_sets) * 0.15): color, status = "#ffc107", "MEDIE"
        else: color, status = "#dc3545", "SLABĂ"
        
        with grid[idx % 3]:
            with st.container(border=True):
                st.markdown(f"**ID: {v_ids[i]}** | <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
                st.progress((c[2] + c[3] + c[4]) / len(r_sets))
                st.caption(f"Record: {max_val}/4 | 0/4: {c[0]} ori")
