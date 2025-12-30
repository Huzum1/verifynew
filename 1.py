import streamlit as st
import pandas as pd
import numpy as np

# Configurare pagină
st.set_page_config(page_title="Loto Analyzer Pro - Top 500", page_icon="📊", layout="wide")

# Stiluri CSS
st.markdown("""
    <style>
    .stProgress > div > div > div > div { background-color: #4CAF50; }
    .anomaly-card { 
        border: 2px solid #ff4b4b; 
        padding: 10px; 
        border-radius: 8px; 
        background-color: #fff3cd; 
        color: #000000; 
        margin-bottom: 10px; 
        font-weight: bold;
        font-size: 12px;
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
    cons = sum(1 for i in range(len(numere_s)-1) if numere_s[i+1] - numere_s[i] == 1)
    if cons >= 2: alerte.append(f"Consecutive")
    suma = sum(numere)
    if suma < 60 or suma > 200: alerte.append(f"Suma")
    pare = sum(1 for n in numere if n % 2 == 0)
    if pare == len(numere) or pare == 0: alerte.append("Paritate")
    ultimele = set(n % 10 for n in numere)
    if len(ultimele) == 1: alerte.append("Terminatie")
    return alerte

# --- SIDEBAR: DATE ȘI DOWNLOAD TOP 500 ---
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

    # --- LOGICA DOWNLOAD TOP 500 ---
    if st.session_state.runde and st.session_state.variante:
        st.divider()
        st.header("💾 Export Top 500")
        
        v_ids = [v['id'] for v in st.session_state.variante]
        v_nums = [v['numere'] for v in st.session_state.variante]
        r_sets = [set(r) for r in st.session_state.runde]
        v_sets = [set(v) for v in v_nums]
        matrice = np.array([[len(vs.intersection(rs)) for rs in r_sets] for v_sets])
        
        # Clasament: Calculăm un scor de performanță (3p pentru 4/4, 2p pentru 3/4, 1p pentru 2/4)
        scoruri = np.sum(matrice == 2, axis=1) * 1 + np.sum(matrice == 3, axis=1) * 5 + np.sum(matrice == 4, axis=1) * 20
        
        date_export = []
        for i in range(len(v_ids)):
            # Sărim peste anomalii
            if len(detecteaza_anomalia(v_nums[i])) == 0:
                date_export.append({
                    'id': v_ids[i],
                    'numere': " ".join(map(str, v_nums[i])),
                    'scor': scoruri[i]
                })
        
        # Sortează după scor (descrescător) și ia primele 500
        df_export = pd.DataFrame(date_export).sort_values(by='scor', ascending=False).head(500)
        
        if not df_export.empty:
            linii_txt = [f"{row['id']}, {row['numere']}" for _, row in df_export.iterrows()]
            st.download_button(
                label=f"📥 Descarcă Top {len(linii_txt)} Variante",
                data="\n".join(linii_txt),
                file_name="top_500_curate.txt",
                mime="text/plain",
                use_container_width=True
            )
            st.caption(f"S-au ales cele mai bune {len(linii_txt)} variante non-anormale.")

# --- AFIȘARE ---
if st.session_state.runde and st.session_state.variante:
    st.subheader("🚨 Anomalii Detectate")
    anom_cols = st.columns(5)
    anom_count = 0
    for i, (vid, vnum) in enumerate(zip([v['id'] for v in st.session_state.variante], [v['numere'] for v in st.session_state.variante])):
        alerte = detecteaza_anomalia(vnum)
        if alerte:
            with anom_cols[anom_count % 5]:
                st.markdown(f"<div class='anomaly-card'>ID: {vid}<br>{', '.join(alerte)}</div>", unsafe_allow_html=True)
                anom_count += 1
    
    st.divider()
    st.subheader("📊 Top Performanță (Vizualizare)")
    
    # Afișăm în interfață sortat după cele mai slabe (cum ai cerut anterior pentru monitorizare)
    c0_counts = np.sum(matrice == 0, axis=1)
    sort_idx = np.argsort(-c0_counts)
    
    grid = st.columns(3)
    for idx, i in enumerate(sort_idx[:100]): # Limităm afișarea la 100 carduri ca să nu blocheze browserul
        res = matrice[i]
        c = {j: np.sum(res == j) for j in range(5)}
        max_val = np.max(res)
        
        color = "#28a745" if max_val >= 3 else "#ffc107" if c[2] > (len(r_sets)*0.1) else "#dc3545"
        
        with grid[idx % 3]:
            with st.container(border=True):
                st.markdown(f"**ID: {v_ids[i]}**")
                st.progress((c[2] + c[3] + c[4]) / len(r_sets))
                st.caption(f"Record: {max_val}/4 | 0/4: {c[0]} ori")
