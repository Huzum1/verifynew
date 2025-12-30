import streamlit as st
import pandas as pd
import numpy as np

# Configurare pagină
st.set_page_config(
    page_title="Verificare Loterie Pro",
    page_icon="🎰",
    layout="wide"
)

st.title("🎰 Verificare Variante Loterie - Optimizat")
st.divider()

# Inițializare session state
if 'runde' not in st.session_state:
    st.session_state.runde = []
if 'variante' not in st.session_state:
    st.session_state.variante = []

# --- LOGICA DE CALCUL OPTIMIZATĂ (INGINERIE) ---
def calcul_performanta_vectorizat(runde_list, variante_list):
    if not runde_list or not variante_list:
        return None, None

    # Transformăm în matrici NumPy pentru viteză fulger (vectorizare)
    # Presupunem că variantele au lungime fixă (ex: 4 numere)
    # Dacă lungimile variază, folosim o abordare optimizată de seturi pre-calculate
    
    ids = [v['id'] for v in variante_list]
    var_sets = [set(v['numere']) for v in variante_list]
    run_sets = [set(r) for r in runde_list]
    
    # Matricea de rezultate: Linii = Variante, Coloane = Runde
    # Stocăm numărul de potriviri pentru fiecare variantă în fiecare rundă
    rezultate = np.zeros((len(var_sets), len(run_sets)), dtype=int)
    
    for r_idx, r_set in enumerate(run_sets):
        for v_idx, v_set in enumerate(var_sets):
            rezultate[v_idx, r_idx] = len(v_set.intersection(r_set))
            
    return ids, rezultate

# --- INTERFAȚĂ ---
col1, col2 = st.columns(2)

with col1:
    st.header("📋 Runde")
    text_runde = st.text_area("Format: 1,6,7,9,44,77", height=150, key="input_runde_bulk")
    
    c1, c2 = st.columns(2)
    if c1.button("Adaugă Runde", type="primary", use_container_width=True):
        if text_runde.strip():
            linii = text_runde.strip().split('\n')
            runde_noi = [[int(n.strip()) for n in l.split(',') if n.strip()] for l in linii if l.strip()]
            st.session_state.runde.extend(runde_noi)
            st.rerun()
    if c2.button("Șterge Runde", use_container_width=True):
        st.session_state.runde = []
        st.rerun()

with col2:
    st.header("🎲 Variante")
    text_variante = st.text_area("Format: ID, 1 2 3 4", height=150, key="input_variante_bulk")
    
    c3, c4 = st.columns(2)
    if c3.button("Adaugă Variante", type="primary", use_container_width=True):
        if text_variante.strip():
            linii = text_variante.strip().split('\n')
            for linie in linii:
                parti = linie.split(',', 1)
                if len(parti) == 2:
                    st.session_state.variante.append({
                        'id': parti[0].strip(),
                        'numere': [int(n.strip()) for n in parti[1].strip().split()]
                    })
            st.rerun()
    if c4.button("Șterge Variante", use_container_width=True):
        st.session_state.variante = []
        st.rerun()

# --- PROCESARE ȘI REZULTATE ---
if st.session_state.runde and st.session_state.variante:
    st.divider()
    
    with st.spinner("Calculăm rezultatele..."):
        ids, matrice_rezultate = calcul_performanta_vectorizat(st.session_state.runde, st.session_state.variante)
    
    # 1. Determinăm care sunt variante BUNE (au cel puțin un 3 sau 4)
    # Presupunem pragul de 3/4 conform cerinței tale
    max_per_varianta = np.max(matrice_rezultate, axis=1)
    
    variante_bune_indices = np.where(max_per_varianta >= 3)[0]
    variante_slabe_indices = np.where(max_per_varianta < 3)[0]

    # --- AFIȘARE REZULTATE ---
    col_rez1, col_rez2 = st.columns(2)

    with col_rez1:
        st.subheader("✅ Variante Bune (minim 3/4)")
        with st.container(height=400):
            for idx in variante_bune_indices:
                v_id = ids[idx]
                best_score = max_per_varianta[idx]
                st.markdown(f"**[ID {v_id}]** - Cel mai bun scor: `{best_score}/4` :green[✔]")

    with col_rez2:
        st.subheader("❌ Variante Slabe (max 2/4)")
        with st.container(height=400):
            for idx in variante_slabe_indices:
                v_id = ids[idx]
                # Calculăm de câte ori a scos 0, 1 sau 2
                frecvente = pd.Series(matrice_rezultate[idx]).value_counts().to_dict()
                info = f"0/4: {frecvente.get(0,0)} ori | 1/4: {frecvente.get(1,0)} ori | 2/4: {frecvente.get(2,0)} ori"
                st.markdown(f"<span style='color: #ff4b4b;'>**ID {v_id}**</span> - {info}", unsafe_allow_html=True)

    # --- STATISTICI GENERALE ---
    st.divider()
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Runde", len(st.session_state.runde))
    s2.metric("Total Variante", len(st.session_state.variante))
    s3.metric("Variante Bune", len(variante_bune_indices), delta_color="normal")
    s4.metric("Variante Slabe", len(variante_slabe_indices), delta_color="inverse")

else:
    st.info("Introdu datele pentru a porni analiza.")

# Instrucțiuni pentru GitHub
with st.expander("🚀 Instrucțiuni Deploy GitHub"):
    st.code("""
# 1. Creează un fișier numit requirements.txt și pune:
streamlit
pandas
numpy
    """, language="text")
