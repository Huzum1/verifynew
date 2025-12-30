import streamlit as st
import pandas as pd
import numpy as np

# Configurare pagină
st.set_page_config(page_title="Analiză Loterie - Variante Reci", page_icon="🎰", layout="wide")

st.title("🎰 Analiză Variante: Calde vs Reci")
st.markdown("""
    **Logica de selecție:**
    * **Variante Calde:** Cele care ating pragul de **3/4** sau **4/4** (potențial ridicat).
    * **Variante Reci (Slabe):** Cele care rămân blocate în **0/4, 1/4** sau **2/4** (fără progres).
""")
st.divider()

# Inițializare Session State
if 'runde' not in st.session_state: st.session_state.runde = []
if 'variante' not in st.session_state: st.session_state.variante = []

# --- ZONA INPUT ---
col1, col2 = st.columns(2)
with col1:
    st.header("📋 Panou Runde")
    text_runde = st.text_area("Introdu rundele (ex: 1,2,3,4)", height=150, key="in_r")
    c_r1, c_r2 = st.columns(2)
    if c_r1.button("Adaugă Runde", type="primary", use_container_width=True, key="btn_add_runde"):
        if text_runde.strip():
            for l in text_runde.strip().split('\n'):
                try:
                    n = [int(x.strip()) for x in l.split(',') if x.strip()]
                    if n: st.session_state.runde.append(n)
                except: pass
            st.rerun()
    if c_r2.button("Șterge tot", use_container_width=True, key="btn_del_runde"):
        st.session_state.runde = []; st.rerun()

with col2:
    st.header("🎲 Panou Variante")
    text_variante = st.text_area("Introdu variantele (ex: ID, 1 2 3 4)", height=150, key="in_v")
    c_v1, c_v2 = st.columns(2)
    if c_v1.button("Adaugă Variante", type="primary", use_container_width=True, key="btn_add_var"):
        if text_variante.strip():
            for l in text_variante.strip().split('\n'):
                try:
                    p = l.split(',', 1)
                    if len(p) == 2:
                        st.session_state.variante.append({'id': p[0].strip(), 'numere': [int(x.strip()) for x in p[1].strip().split()]})
                except: pass
            st.rerun()
    if c_v2.button("Șterge tot", use_container_width=True, key="btn_del_var"):
        st.session_state.variante = []; st.rerun()

# --- CALCUL ȘI FILTRARE ---
if st.session_state.runde and st.session_state.variante:
    st.divider()
    
    # Vectorizare NumPy (Viteză ridicată)
    v_sets = [set(v['numere']) for v in st.session_state.variante]
    r_sets = [set(r) for r in st.session_state.runde]
    v_ids = [v['id'] for v in st.session_state.variante]
    
    # Matricea de bază
    matrice = np.array([[len(vs.intersection(rs)) for rs in r_sets] for vs in v_sets])
    
    max_hits = np.max(matrice, axis=1)
    count_0 = np.sum(matrice == 0, axis=1)
    count_1 = np.sum(matrice == 1, axis=1)
    count_2 = np.sum(matrice == 2, axis=1)
    count_3 = np.sum(matrice == 3, axis=1)
    count_4 = np.sum(matrice == 4, axis=1)

    col_A, col_B = st.columns(2)

    with col_A:
        st.subheader("🟢 Variante cu Potențial (Calde)")
        with st.container(height=500):
            idx_calde = np.where(max_hits >= 3)[0]
            if len(idx_calde) > 0:
                for i in idx_calde:
                    st.success(f"ID {v_ids[i]} | Record: {max_hits[i]}/4 | (3/4: {count_3[i]} ori, 4/4: {count_4[i]} ori)")
            else:
                st.write("Nicio variantă nu a atins pragul de 3/4.")

    with col_B:
        st.subheader("🔴 Variante Slabe (Reci)")
        with st.container(height=500):
            idx_reci = np.where(max_hits < 3)[0]
            if len(idx_reci) > 0:
                # Sortăm: cele mai multe de 0/4 primele
                sorted_reci = idx_reci[np.argsort(-count_0[idx_reci])] 
                for i in sorted_reci:
                    st.markdown(f"""
                    <div style="border: 1px solid #ff4b4b; padding: 10px; border-radius: 5px; margin-bottom: 5px;">
                        <b style="color: #ff4b4b;">ID {v_ids[i]}</b><br>
                        <small>Record: {max_hits[i]}/4 | 0/4: <b>{count_0[i]}</b> ori | 1/4: {count_1[i]} ori | 2/4: {count_2[i]} ori</small>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.write("Toate variantele au atins măcar o dată 3/4.")

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Variante", len(v_ids))
    m2.metric("Variante Calde", len(idx_calde))
    m3.metric("Variante Reci", len(idx_reci))
else:
    st.info("Aștept introducerea datelor pentru analiză...")
