import streamlit as st
import pandas as pd
import numpy as np

# Configurare pagină
st.set_page_config(page_title="Loto Analyzer Pro - Anomalii & Performanță", page_icon="📊", layout="wide")

# Stiluri CSS pentru interfață
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    .anomaly-card { border: 2px solid #ff4b4b; padding: 15px; border-radius: 10px; background-color: #fff1f1; margin-bottom: 15px; }
    .variant-card { border: 1px solid #e6e9ef; padding: 15px; border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

if 'runde' not in st.session_state: st.session_state.runde = []
if 'variante' not in st.session_state: st.session_state.variante = []

# --- MOTORUL DE DETECȚIE ANOMALII ---
def detecteaza_anomalia(numere):
    if not numere: return []
    numere_s = sorted(numere)
    alerte = []
    
    # 1. Consecutivitate (ex: 1, 2, 3)
    cons = sum(1 for i in range(len(numere_s)-1) if numere_s[i+1] - numere_s[i] == 1)
    if cons >= 2: alerte.append(f"⚠️ {cons+1} numere consecutive")
    
    # 2. Suma extremă (Bazat pe media de 31/număr a rundelor tale)
    suma = sum(numere)
    if suma < 60 or suma > 200: alerte.append(f"⚠️ Sumă atipică ({suma})")
    
    # 3. Paritate extremă (Toate Pare / Toate Impare)
    pare = sum(1 for n in numere if n % 2 == 0)
    if pare == len(numere) or pare == 0: alerte.append("⚠️ Dezechilibru Paritate (4/0)")
    
    # 4. Terminații identice (ex: 4, 14, 24, 34)
    ultimele_cifre = set(n % 10 for n in numere)
    if len(ultimele_cifre) == 1: alerte.append("⚠️ Toate cu aceeași terminație")
    
    return alerte

# --- SIDEBAR: GESTIONARE DATE ---
with st.sidebar:
    st.header("📥 Import Date")
    r_input = st.text_area("Introdu Runde (ex: 4,8,49...)", height=150, help="Fiecare rundă pe un rând nou")
    if st.button("Adaugă Runde", type="primary", use_container_width=True, key="add_r"):
        for l in r_input.strip().split('\n'):
            try:
                n = [int(x.strip()) for x in l.replace(',', ' ').split() if x.strip()]
                if n: st.session_state.runde.append(n)
            except: pass
        st.rerun()

    v_input = st.text_area("Introdu Variante (ex: ID1, 1 2 3 4)", height=150, help="ID urmat de virgulă și numere")
    if st.button("Adaugă Variante", type="primary", use_container_width=True, key="add_v"):
        for l in v_input.strip().split('\n'):
            try:
                parti = l.split(',', 1)
                id_v, nums = parti[0].strip(), [int(x) for x in parti[1].replace(',', ' ').split()]
                st.session_state.variante.append({'id': id_v, 'numere': nums})
            except: pass
        st.rerun()
    
    if st.button("Resetare Totală", use_container_width=True, key="reset"):
        st.session_state.runde = []; st.session_state.variante = []; st.rerun()

# --- ANALIZĂ ȘI AFIȘARE ---
if st.session_state.runde and st.session_state.variante:
    # Pregătire date (Vectorizare)
    v_ids = [v['id'] for v in st.session_state.variante]
    v_nums = [v['numere'] for v in st.session_state.variante]
    r_sets = [set(r) for r in st.session_state.runde]
    v_sets = [set(v) for v in v_nums]
    
    matrice = np.array([[len(vs.intersection(rs)) for rs in r_sets] for vs in v_sets])
    nr_runde = len(st.session_state.runde)

    # 1. SECȚIUNEA DE ANOMALII
    st.subheader("🚨 Detector Anomalii (Șanse minime de succes)")
    anom_cols = st.columns(4)
    anom_count = 0
    for i, (vid, vnum) in enumerate(zip(v_ids, v_nums)):
        alerte = detecteaza_anomalia(vnum)
        if alerte:
            with anom_cols[anom_count % 4]:
                st.markdown(f"""<div class='anomaly-card'>
                    <b>ID {vid}</b><br>
                    <small>{', '.join(alerte)}</small><br>
                    <small>Numere: {vnum}</small>
                </div>""", unsafe_allow_html=True)
                anom_count += 1
    if anom_count == 0: st.info("Nu s-au detectat anomalii în variantele introduse.")

    st.divider()

    # 2. MONITORIZARE DETALIATĂ
    st.subheader("📊 Monitorizare Performanță (Sortate după eșec 0/4)")
    
    # Sortare: Cele mai "Reci" (cele mai multe 0/4) apar primele
    c0_counts = np.sum(matrice == 0, axis=1)
    sort_idx = np.argsort(-c0_counts)
    
    grid = st.columns(3)
    for idx, i in enumerate(sort_idx):
        res = matrice[i]
        c = {j: np.sum(res == j) for j in range(5)}
        max_h = np.max(res)
        
        # Logica Status & Culori
        if max_h >= 3: color, status = "#28a745", "BUNĂ (Top)"
        elif c[2] > (nr_runde * 0.15): color, status = "#ffc107", "MEDIE (Potențial)"
        else: color, status = "#dc3545", "SLABĂ (Rece)"
        
        progres = (c[2] + c[3] + c[4]) / nr_runde if nr_runde > 0 else 0
        
        with grid[idx % 3]:
            with st.container(border=True):
                st.markdown(f"**ID: {v_ids[i]}** | <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
                st.progress(progres)
                
                m_cols = st.columns(4)
                m_cols[0].metric("1/4", c[1])
                m_cols[1].metric("2/4", c[2])
                m_cols[2].metric("3/4", c[3])
                m_cols[3].metric("4/4", c[4])
                st.caption(f"Eșec total (0/4): **{c[0]} ori** | Record: **{max_h}/4**")

    # Statistici Finale
    st.divider()
    st.metric("Total Variante Analizate", len(v_ids))
else:
    st.info("Aștept datele... Introdu rundele și variantele în meniul lateral.")
