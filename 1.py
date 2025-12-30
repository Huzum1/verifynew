import streamlit as st
import pandas as pd
import numpy as np

# Configurare pagină
st.set_page_config(page_title="Monitorizare Avansată Loterie", page_icon="📊", layout="wide")

st.title("📊 Monitorizare Detaliată Variante")
st.divider()

if 'runde' not in st.session_state: st.session_state.runde = []
if 'variante' not in st.session_state: st.session_state.variante = []

# --- INPUT DATE ---
with st.sidebar:
    st.header("⚙️ Configurare Date")
    
    # Input Runde
    text_r = st.text_area("Runde (ex: 1,2,3,4)", height=150, key="side_r")
    if st.button("Adaugă Runde", use_container_width=True, type="primary"):
        for l in text_r.strip().split('\n'):
            try:
                n = [int(x.strip()) for x in l.split(',') if x.strip()]
                if n: st.session_state.runde.append(n)
            except: pass
        st.rerun()
        
    # Input Variante
    text_v = st.text_area("Variante (ex: ID1, 1 2 3 4)", height=150, key="side_v")
    if st.button("Adaugă Variante", use_container_width=True, type="primary"):
        for l in text_v.strip().split('\n'):
            try:
                p = l.split(',', 1)
                if len(p) == 2:
                    st.session_state.variante.append({'id': p[0].strip(), 'numere': [int(x.strip()) for x in p[1].strip().split()]})
            except: pass
        st.rerun()
    
    if st.button("Șterge tot", use_container_width=True):
        st.session_state.runde = []
        st.session_state.variante = []
        st.rerun()

# --- CALCUL ȘI AFIȘARE INEDITĂ ---
if st.session_state.runde and st.session_state.variante:
    # Vectorizare pentru performanță
    v_ids = [v['id'] for v in st.session_state.variante]
    v_sets = [set(v['numere']) for v in st.session_state.variante]
    r_sets = [set(r) for r in st.session_state.runde]
    
    matrice = np.array([[len(vs.intersection(rs)) for rs in r_sets] for vs in v_sets])
    nr_runde = len(st.session_state.runde)

    st.subheader(f"Analiză pe {len(v_ids)} variante și {nr_runde} runde")
    
    # Grid de afișare (3 variante pe rând)
    cols = st.columns(3)
    
    for i, v_id in enumerate(v_ids):
        res = matrice[i]
        c0, c1, c2, c3, c4 = [np.sum(res == j) for j in range(5)]
        
        # Determinăm culoarea și statusul
        max_h = np.max(res)
        if max_h >= 3:
            color = "#28a745" # Verde
            status = "BUNĂ (Top)"
        elif c2 > (nr_runde * 0.2): # Dacă are peste 20% rezultate de 2/4
            color = "#ffc107" # Galben
            status = "MEDIE (Potențial)"
        else:
            color = "#dc3545" # Roșu
            status = "SLABĂ (Rece)"
            
        # Calculăm progresul (cât de des a ieșit minim 2/4)
        progres = (c2 + c3 + c4) / nr_runde if nr_runde > 0 else 0
        
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(f"### ID: {v_id}")
                st.markdown(f"**Status:** <span style='color:{color}'>{status}</span>", unsafe_allow_html=True)
                
                # Bară de progres pentru "Calitatea" variantei
                st.progress(progres)
                st.caption(f"Frecvență succes (minim 2/4): {progres*100:.1f}%")
                
                # Detalii distribuție
                stat_cols = st.columns(4)
                stat_cols[0].metric("1/4", c1)
                stat_cols[1].metric("2/4", c2)
                stat_cols[2].metric("3/4", c3)
                stat_cols[3].metric("4/4", c4)
                
                st.write(f"❌ **Total 0/4:** {c0} ori")
else:
    st.info("Folosește meniul din stânga pentru a introduce datele.")
