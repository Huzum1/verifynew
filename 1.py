import streamlit as st
import pandas as pd
import numpy as np

# Configurare pagină
st.set_page_config(page_title="Loto Big Data - Top 250", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    .anomaly-card { border: 2px solid #ff4b4b; padding: 10px; border-radius: 8px; background-color: #fff3cd; color: #000; margin-bottom: 10px; font-size: 12px;}
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
    if cons >= 2: alerte.append("Consecutive")
    suma = sum(numere)
    if suma < 60 or suma > 200: alerte.append(f"Suma:{suma}")
    pare = sum(1 for n in numere if n % 2 == 0)
    if pare == len(numere) or pare == 0: alerte.append("Paritate")
    ultimele = set(n % 10 for n in numere)
    if len(ultimele) == 1: alerte.append("Terminatie")
    return alerte

# --- SIDEBAR: IMPORT, RESET ȘI DOWNLOAD ---
with st.sidebar:
    st.header("📥 Gestiune Date")
    
    # Import Runde
    r_input = st.text_area("Introdu Runde (până la 13.000)", height=150)
    if st.button("Procesează Runde", type="primary", use_container_width=True):
        lines = r_input.strip().split('\n')
        st.session_state.runde = [[int(x) for x in l.replace(',', ' ').split()] for l in lines if l.strip()]
        st.rerun()

    # Import Variante
    v_input = st.text_area("Introdu Variante (ID, 1 2 3 4)", height=150)
    if st.button("Procesează Variante", type="primary", use_container_width=True):
        lines = v_input.strip().split('\n')
        new_vars = []
        for l in lines:
            if ',' in l:
                parti = l.split(',', 1)
                new_vars.append({'id': parti[0].strip(), 'numere': [int(x) for x in parti[1].replace(',', ' ').split()]})
        st.session_state.variante = new_vars
        st.rerun()
    
    st.divider()
    
    # BUTON RESETARE (Restaurat)
    if st.button("🗑️ Resetare Totală", use_container_width=True):
        st.session_state.runde = []
        st.session_state.variante = []
        st.rerun()

    st.divider()
    
    # --- LOGICA DOWNLOAD TOP 250 ---
    if st.session_state.runde and st.session_state.variante:
        st.header("💾 Export Top 250")
        
        v_ids = [v['id'] for v in st.session_state.variante]
        v_nums = [v['numere'] for v in st.session_state.variante]
        r_sets = [set(r) for r in st.session_state.runde]
        v_sets = [set(v) for v in v_nums]
        
        # Calcul intersecții NumPy
        matrice = np.array([[len(vs.intersection(rs)) for rs in r_sets] for vs in v_sets])
        
        # Scor ponderat pentru clasament
        scoruri = (np.sum(matrice == 2, axis=1) * 1 + 
                   np.sum(matrice == 3, axis=1) * 8 + 
                   np.sum(matrice == 4, axis=1) * 50)
        
        export_data = []
        for i in range(len(v_ids)):
            # Filtru: Excludem anomaliile
            if not detecteaza_anomalia(v_nums[i]):
                export_data.append({
                    'id': v_ids[i],
                    'numere': " ".join(map(str, v_nums[i])),
                    'scor': scoruri[i]
                })
        
        # Sortează și păstrează TOP 250
        df_export = pd.DataFrame(export_data).sort_values(by='scor', ascending=False).head(250)
        
        if not df_export.empty:
            txt_output = "\n".join([f"{row['id']}, {row['numere']}" for _, row in df_export.iterrows()])
            st.download_button(f"📥 Descarcă Top {len(df_export)} Variante", txt_output, "top_250_curate.txt", use_container_width=True)
            st.success(f"Gata! Top {len(df_export)} selectate.")

# --- AFIȘARE REZULTATE ---
if st.session_state.runde and st.session_state.variante:
    st.info(f"Sistemul a analizat {len(st.session_state.runde)} runde și {len(st.session_state.variante)} variante.")
    
    # Vizualizare Anomalii
    with st.expander("🚨 Detectate ca Anomalii (Excluse din Top)"):
        cols = st.columns(5)
        a_idx = 0
        for v in st.session_state.variante:
            alerte = detecteaza_anomalia(v['numere'])
            if alerte:
                with cols[a_idx % 5]:
                    st.markdown(f"<div class='anomaly-card'>ID: {v['id']}<br>{', '.join(alerte)}</div>", unsafe_allow_html=True)
                a_idx += 1

    st.divider()
    st.subheader("📊 Exemplu Performanță (Primele 30 sortate după eșec)")
    
    grid = st.columns(3)
    c0_counts = np.sum(matrice == 0, axis=1)
    view_idx = np.argsort(-c0_counts)[:30]
    
    for idx, i in enumerate(view_idx):
        res = matrice[i]
        c = {j: np.sum(res == j) for j in range(5)}
        with grid[idx % 3]:
            with st.container(border=True):
                st.write(f"**ID: {v_ids[i]}**")
                st.caption(f"2/4: {c[2]} | 3/4: {c[3]} | 4/4: {c[4]}")
                st.progress((c[2]+c[3]+c[4])/len(st.session_state.runde))
else:
    st.warning("Te rog să încarci datele din meniul lateral.")
