import streamlit as st
import pandas as pd
import numpy as np

# Configurare pagină
st.set_page_config(page_title="Monitorizare Avansată & Anomalii", page_icon="📊", layout="wide")

st.title("📊 Monitorizare Detaliată & Detecție Anomalii")
st.divider()

if 'runde' not in st.session_state: st.session_state.runde = []
if 'variante' not in st.session_state: st.session_state.variante = []

# --- FUNCȚIE INGINEREASCĂ: DETECȚIE ANOMALII ---
def analizeaza_anomalia(numere):
    if not numere: return None
    numere_sortate = sorted(numere)
    # Diferența dintre cel mai mare și cel mai mic (Dispersia)
    dispersie = numere_sortate[-1] - numere_sortate[0]
    # Verificare numere consecutive (ex: 1, 2, 3)
    consecutive = sum(1 for i in range(len(numere_sortate)-1) if numere_sortate[i+1] - numere_sortate[i] == 1)
    
    alerte = []
    if consecutive >= 2: alerte.append(f"⚠️ {consecutive+1} numere consecutive")
    if dispersie < 10: alerte.append("⚠️ Dispersie prea mică (grupate)")
    
    return alerte

# --- SIDEBAR PENTRU DATE ---
with st.sidebar:
    st.header("⚙️ Configurare")
    text_r = st.text_area("Runde (1,2,3,4)", height=150, key="side_r")
    if st.button("Adaugă Runde", use_container_width=True, type="primary"):
        for l in text_r.strip().split('\n'):
            try:
                n = [int(x.strip()) for x in l.split(',') if x.strip()]
                if n: st.session_state.runde.append(n)
            except: pass
        st.rerun()
        
    text_v = st.text_area("Variante (ID1, 1 2 3 4)", height=150, key="side_v")
    if st.button("Adaugă Variante", use_container_width=True, type="primary"):
        for l in text_v.strip().split('\n'):
            try:
                p = l.split(',', 1)
                if len(p) == 2:
                    st.session_state.variante.append({
                        'id': p[0].strip(), 
                        'numere': [int(x.strip()) for x in p[1].strip().split()]
                    })
            except: pass
        st.rerun()
    
    if st.button("Resetare Totală", use_container_width=True):
        st.session_state.runde = []; st.session_state.variante = []; st.rerun()

# --- ANALIZĂ ȘI AFIȘARE ---
if st.session_state.runde and st.session_state.variante:
    v_ids = [v['id'] for v in st.session_state.variante]
    v_nums = [v['numere'] for v in st.session_state.variante]
    v_sets = [set(v) for v in v_nums]
    r_sets = [set(r) for r in st.session_state.runde]
    
    matrice = np.array([[len(vs.intersection(rs)) for rs in r_sets] for vs in v_sets])
    nr_runde = len(st.session_state.runde)

    # SECȚIUNEA 1: DETECTORUL DE ANOMALII (Top-ul paginii)
    st.subheader("🚨 Anomalii Detectate (Variante cu șanse minime)")
    anomalii_cols = st.columns(4)
    found_anomaly = False
    
    for i, (v_id, nums) in enumerate(zip(v_ids, v_nums)):
        alerte = analizeaza_anomalia(nums)
        if alerte:
            found_anomaly = True
            with anomalii_cols[i % 4]:
                st.error(f"**ID: {v_id}**\n\n{', '.join(alerte)}\n\nNumere: `{nums}`")
    
    if not found_anomaly:
        st.success("Nu s-au detectat anomalii structurale în variantele introduse.")

    st.divider()

    # SECȚIUNEA 2: MONITORIZARE DETALIATĂ
    st.subheader("📊 Monitorizare Performanță & Progres")
    cols = st.columns(3)
    
    for i, v_id in enumerate(v_ids):
        res = matrice[i]
        stats = {j: np.sum(res == j) for j in range(5)}
        max_h = np.max(res)
        
        # Logica de culori
        if max_h >= 3:
            color, status = "#28a745", "BUNĂ (Top)"
        elif stats[2] > (nr_runde * 0.15):
            color, status = "#ffc107", "MEDIE (Potențial)"
        else:
            color, status = "#dc3545", "SLABĂ (Rece)"
            
        progres = (stats[2] + stats[3] + stats[4]) / nr_runde if nr_runde > 0 else 0
        
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### ID: {v_id} <span style='font-size:12px; color:{color}'>[{status}]</span>", unsafe_allow_html=True)
                st.progress(progres)
                
                m_cols = st.columns(4)
                m_cols[0].metric("1/4", stats[1])
                m_cols[1].metric("2/4", stats[2])
                m_cols[2].metric("3/4", stats[3])
                m_cols[3].metric("4/4", stats[4])
                st.caption(f"Eșec total (0/4): {stats[0]} ori")
else:
    st.info("Introdu datele în meniul lateral pentru a porni monitorizarea.")
