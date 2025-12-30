import streamlit as st
import pandas as pd
import numpy as np

# Configurare pagină
st.set_page_config(page_title="Loto Analyzer Pro - Export", page_icon="📊", layout="wide")

# Stiluri CSS
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    .anomaly-card { border: 2px solid #ff4b4b; padding: 15px; border-radius: 10px; background-color: #fff1f1; margin-bottom: 15px; }
    .variant-card { border: 1px solid #e6e9ef; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

if 'runde' not in st.session_state: st.session_state.runde = []
if 'variante' not in st.session_state: st.session_state.variante = []

# --- MOTOR DETECȚIE ANOMALII ---
def detecteaza_anomalia(numere):
    if not numere: return []
    numere_s = sorted(numere)
    alerte = []
    cons = sum(1 for i in range(len(numere_s)-1) if numere_s[i+1] - numere_s[i] == 1)
    if cons >= 2: alerte.append(f"⚠️ {cons+1} numere consecutive")
    suma = sum(numere)
    if suma < 60 or suma > 200: alerte.append(f"⚠️ Sumă atipică ({suma})")
    pare = sum(1 for n in numere if n % 2 == 0)
    if pare == len(numere) or pare == 0: alerte.append("⚠️ Dezechilibru Paritate (4/0)")
    ultimele_cifre = set(n % 10 for n in numere)
    if len(ultimele_cifre) == 1: alerte.append("⚠️ Aceeași terminație")
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

    # --- FUNCȚIE DOWNLOAD ---
    if st.session_state.runde and st.session_state.variante:
        st.divider()
        st.header("💾 Export Date")
        
        # Calculăm categoriile pentru export
        v_ids = [v['id'] for v in st.session_state.variante]
        v_nums = [v['numere'] for v in st.session_state.variante]
        r_sets = [set(r) for r in st.session_state.runde]
        v_sets = [set(v) for v in v_nums]
        matrice = np.array([[len(vs.intersection(rs)) for rs in r_sets] for vs in v_sets])
        
        max_h = np.max(matrice, axis=1)
        nr_runde = len(r_sets)
        
        # Filtrăm Bune + Medii
        linii_export = []
        for i in range(len(v_ids)):
            c2 = np.sum(matrice[i] == 2)
            is_buna = max_h[i] >= 3
            is_medie = c2 > (nr_runde * 0.15)
            
            if is_buna or is_medie:
                nums_str = " ".join(map(str, v_nums[i]))
                linii_export.append(f"{v_ids[i]}, {nums_str}")
        
        if linii_export:
            content = "\n".join(linii_export)
            st.download_button(
                label="📥 Descarcă Bune & Medii (.txt)",
                data=content,
                file_name="variante_filtrate.txt",
                mime="text/plain",
                use_container_width=True
            )
            st.caption(f"Pregătite pentru download: {len(linii_export)} variante.")

# --- AFIȘARE PRINCIPALĂ ---
if st.session_state.runde and st.session_state.variante:
    st.subheader("🚨 Detector Anomalii")
    anom_cols = st.columns(4)
    anom_count = 0
    for i, (vid, vnum) in enumerate(zip([v['id'] for v in st.session_state.variante], [v['numere'] for v in st.session_state.variante])):
        alerte = detecteaza_anomalia(vnum)
        if alerte:
            with anom_cols[anom_count % 4]:
                st.markdown(f"<div class='anomaly-card'><b>ID {vid}</b><br><small>{', '.join(alerte)}</small></div>", unsafe_allow_html=True)
                anom_count += 1
    
    st.divider()
    st.subheader("📊 Monitorizare Performanță")
    
    # Recalculăm pentru afișare (după sortare eșec)
    v_ids = [v['id'] for v in st.session_state.variante]
    c0_counts = np.sum(matrice == 0, axis=1)
    sort_idx = np.argsort(-c0_counts)
    
    grid = st.columns(3)
    for idx, i in enumerate(sort_idx):
        res = matrice[i]
        c = {j: np.sum(res == j) for j in range(5)}
        max_val = np.max(res)
        
        if max_val >= 3: color, status = "#28a745", "BUNĂ"
        elif c[2] > (len(r_sets) * 0.15): color, status = "#ffc107", "MEDIE"
        else: color, status = "#dc3545", "SLABĂ"
        
        progres = (c[2] + c[3] + c[4]) / len(r_sets)
        
        with grid[idx % 3]:
            with st.container(border=True):
                st.markdown(f"**ID: {v_ids[i]}** | <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
                st.progress(progres)
                st.caption(f"Record: {max_val}/4 | 0/4: {c[0]} ori")
else:
    st.info("Introdu datele în meniul lateral.")
