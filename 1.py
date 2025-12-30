import streamlit as st
import pandas as pd
import numpy as np

# Configurare pagină
st.set_page_config(page_title="Analiză Loterie - Scor", page_icon="🎰", layout="wide")

st.title("🎰 Clasament Performanță Variante")
st.caption("Analiză bazată pe scorul acumulat în toate rundele")
st.divider()

if 'runde' not in st.session_state: st.session_state.runde = []
if 'variante' not in st.session_state: st.session_state.variante = []

# --- ZONA INPUT ---
col1, col2 = st.columns(2)
with col1:
    st.header("📋 Runde")
    text_runde = st.text_area("Format: 1,6,7,9", height=150, key="in_r")
    c1, c2 = st.columns(2)
    if c1.button("Adaugă Runde", type="primary", use_container_width=True):
        if text_runde.strip():
            for l in text_runde.strip().split('\n'):
                try:
                    n = [int(x.strip()) for x in l.split(',') if x.strip()]
                    if n: st.session_state.runde.append(n)
                except: pass
            st.rerun()
    if c2.button("Șterge", use_container_width=True, key="del_r"):
        st.session_state.runde = []; st.rerun()

with col2:
    st.header("🎲 Variante")
    text_variante = st.text_area("Format: ID, 1 2 3 4", height=150, key="in_v")
    c3, c4 = st.columns(2)
    if c3.button("Adaugă Variante", type="primary", use_container_width=True):
        if text_variante.strip():
            for l in text_variante.strip().split('\n'):
                try:
                    p = l.split(',', 1)
                    if len(p) == 2:
                        st.session_state.variante.append({'id': p[0].strip(), 'numere': [int(x.strip()) for x in p[1].strip().split()]})
                except: pass
            st.rerun()
    if c4.button("Șterge", use_container_width=True, key="del_v"):
        st.session_state.variante = []; st.rerun()

# --- ANALIZĂ ȘI CLASAMENT ---
if st.session_state.runde and st.session_state.variante:
    st.divider()
    
    # 1. Calcul rapid (Vectorizat)
    var_sets = [set(v['numere']) for v in st.session_state.variante]
    run_sets = [set(r) for r in st.session_state.runde]
    ids = [v['id'] for v in st.session_state.variante]
    
    # Matricea de potriviri
    matrice = np.array([[len(v_s.intersection(r_s)) for r_s in run_sets] for v_s in var_sets])
    
    # 2. Calculăm SCORUL MEDIU per variantă (Suma punctelor / Număr runde)
    # Acesta este cel mai corect indicator de "slăbiciune" sau "putere"
    scoruri_medii = np.mean(matrice, axis=1)
    
    # Creăm un DataFrame pentru sortare ușoară
    df_rezultate = pd.DataFrame({
        'ID': ids,
        'Scor Mediu': scoruri_medii,
        'Maxim': np.max(matrice, axis=1)
    }).sort_values(by='Scor Mediu', ascending=False)

    # 3. Afișare în coloane
    col_bune, col_slabe = st.columns(2)

    with col_bune:
        st.subheader("🟢 Top Variante Puternice")
        with st.container(height=500):
            top_bune = df_rezultate.head(50) # Primele 50 cele mai bune
            for _, row in top_bune.iterrows():
                st.write(f"✅ **ID {row['ID']}** | Scor Mediu: `{row['Scor Mediu']:.2f}` | Record: `{row['Maxim']}/4`")

    with col_slabe:
        st.subheader("🔴 Top Variante Slabe")
        with st.container(height=500):
            # Sortăm invers pentru cele mai slabe
            top_slabe = df_rezultate.sort_values(by='Scor Mediu', ascending=True).head(50)
            for _, row in top_slabe.iterrows():
                st.markdown(f"<span style='color: #ff4b4b;'>❌ **ID {row['ID']}**</span> | Scor Mediu: `{row['Scor Mediu']:.2f}` | Record: `{row['Maxim']}/4`", unsafe_allow_html=True)

    # Statistici finale
    st.divider()
    st.metric("Total Variante Analizate", len(ids))
else:
    st.info("Introdu datele pentru a genera clasamentul de performanță.")
