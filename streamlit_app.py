import streamlit as st
import sqlite3
import pandas as pd
import json
from datetime import datetime

# Configuração da página - Tema Dark/Light e Layout Wide
st.set_page_config(
    page_title="Momentum - Dashboard Pro", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- LÓGICA DO BANCO DE DADOS ---
DB_PATH = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, name TEXT, streak INTEGER)')
    cursor.execute('CREATE TABLE IF NOT EXISTS routine (id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, time TEXT, task TEXT, desc TEXT, icon TEXT, completed BOOLEAN DEFAULT 0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, name TEXT, series TEXT, muscle_group TEXT, completed BOOLEAN DEFAULT 0)')
    cursor.execute('CREATE TABLE IF NOT EXISTS goals (id INTEGER PRIMARY KEY AUTOINCREMENT, quarter TEXT, title TEXT, description TEXT, icon TEXT, progress INTEGER DEFAULT 0, active BOOLEAN DEFAULT 0)')

    cursor.execute('SELECT * FROM profile WHERE id = 1')
    if not cursor.fetchone():
        cursor.execute('INSERT INTO profile (id, name, streak) VALUES (1, "Emerson", 12)')
        
        # Dados da Rotina (Subset para exemplo, já populado anteriormente)
        routine_data = {
            "Seg": [
                ("07:30", "Acordar", "Café e preparação", "sunny"),
                ("09:00", "Trabalho", "Foco Total", "work"),
                ("12:00", "Marmita", "Almoço saudável", "restaurant"),
                ("16:30", "Treino PUSH", "Academia - 1h20", "fitness_center"),
                ("19:00", "Jantar", "Refeição pós-treino", "dinner_dining"),
                ("22:30", "Banho", "Relaxar e dormir", "shower")
            ],
            "Ter": [
                ("07:30", "Acordar", "Café e preparação", "sunny"),
                ("09:00", "Trabalho", "Foco Total", "work"),
                ("16:30", "Treino PULL", "Academia", "fitness_center"),
                ("20:00", "Faculdade", "Aulas e exercícios", "school")
            ],
            "Qua": [
                ("07:30", "Acordar", "Café e preparação", "sunny"),
                ("16:30", "Treino LEG", "Academia", "fitness_center"),
                ("19:30", "Jantar", "Refeição equilibrada", "dinner_dining"),
                ("20:00", "Inglês", "1h de foco", "translate")
            ],
            "Qui": [
                ("17:00", "Terapia", "Prioridade Semanal", "psychology"),
                ("18:30", "Treino PUSH", "Pós-Terapia", "fitness_center"),
                ("22:30", "Banho", "Relaxar", "shower")
            ],
            "Sex": [
                ("09:00", "Trabalho", "Foco Total", "work"),
                ("16:30", "Treino PULL", "Último da semana", "fitness_center"),
                ("21:00", "Tempo Esposa", "Série / Lazer", "favorite")
            ],
            "Sáb": [
                ("11:00", "Capoeira", "Prioridade Treino", "sports_martial_arts"),
                ("17:00", "Lazer Esposa", "Tempo de Qualidade", "restaurant")
            ],
            "Dom": [
                ("09:30", "Manhã Esposa", "Café fora e relaxar", "bakery_dining"),
                ("17:00", "Prep. Semana", "Agenda e Marmitas", "inventory_2")
            ]
        }
        for day, tasks in routine_data.items():
            for task in tasks:
                cursor.execute('INSERT INTO routine (day, time, task, desc, icon) VALUES (?, ?, ?, ?, ?)', (day, task[0], task[1], task[2], task[3]))

        workouts = [
            ('Push', 'Supino Reto', '4 x 10', 'Peito'),
            ('Push', 'Supino Inclinado', '3 x 12', 'Peito'),
            ('Push', 'Desenvolvimento Militar', '4 x 10', 'Ombro'),
            ('Push', 'Elevação Lateral', '4 x 15', 'Ombro'),
            ('Push', 'Tríceps Corda', '3 x 12', 'Tríceps'),
            ('Pull', 'Puxada Aberta', '4 x 12', 'Costas'),
            ('Pull', 'Remada Curvada', '3 x 10', 'Costas'),
            ('Leg', 'Agachamento', '4 x 10', 'Pernas'),
            ('Capoeira', 'Ginga e Esquivas', '30 min', 'Geral')
        ]
        for w in workouts:
            cursor.execute('INSERT INTO workouts (category, name, series, muscle_group) VALUES (?, ?, ?, ?)', w)

        goals = [
            ('1º Trimestre', 'Ferramentas Google', 'Looker, Sheets e Apps Script', 'analytics', 45, 1),
            ('1º Trimestre', 'Inglês Técnico', 'Conversação e leitura contínua', 'language', 30, 1),
            ('2º Trimestre', 'A definir', 'Planejamento pendente', 'edit', 0, 0),
            ('3º Trimestre', 'A definir', 'Planejamento pendente', 'edit', 0, 0),
            ('4º Trimestre', 'A definir', 'Planejamento pendente', 'edit', 0, 0)
        ]
        for g in goals:
            cursor.execute('INSERT INTO goals (quarter, title, description, icon, progress, active) VALUES (?, ?, ?, ?, ?, ?)', g)

    conn.commit()
    conn.close()

init_db()

# --- CUSTOM CSS (STYLE STITCH) ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lexend:wght@400;600;700;900&display=swap');
        
        :root {
            --primary: #003ec7;
            --primary-container: #0052ff;
            --surface: #faf8ff;
            --on-background: #131b2e;
            --outline: #737688;
        }

        .main { background-color: var(--surface); color: var(--on-background); font-family: 'Inter', sans-serif; }
        
        h1, h2, h3, .font-lexend { font-family: 'Lexend', sans-serif; }
        
        /* Bento Card Style */
        .bento-card {
            background: white;
            padding: 24px;
            border-radius: 28px;
            border: 1px solid #eaedff;
            box-shadow: 0 8px 30px rgba(0, 82, 255, 0.05);
            transition: transform 0.2s, box-shadow 0.2s;
            margin-bottom: 20px;
        }
        .bento-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 40px rgba(0, 82, 255, 0.08);
        }

        /* Hero Card with Image */
        .hero-card {
            position: relative;
            height: 240px;
            border-radius: 28px;
            overflow: hidden;
            color: white;
            display: flex;
            flex-col;
            justify-content: flex-end;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        .hero-bg {
            position: absolute;
            inset: 0;
            background-size: cover;
            background-position: center;
            z-index: 0;
        }
        .hero-overlay {
            position: absolute;
            inset: 0;
            background: linear-gradient(180deg, rgba(0,0,0,0) 0%, rgba(0,0,0,0.7) 100%);
            z-index: 1;
        }
        .hero-content { position: relative; z-index: 2; }

        /* Stats Badge */
        .stat-badge {
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            padding: 4px 12px;
            border-radius: 100px;
            font-size: 10px;
            font-weight: 700;
            text-transform: uppercase;
            border: 1px solid rgba(255,255,255,0.3);
            margin-bottom: 8px;
            display: inline-block;
        }

        /* Custom Progress Bar */
        .custom-progress-bg { background: rgba(255,255,255,0.2); height: 6px; border-radius: 100px; width: 100%; margin-top: 12px; }
        .custom-progress-fill { background: white; height: 6px; border-radius: 100px; box-shadow: 0 0 15px rgba(255,255,255,0.5); }

        /* Navigation Simulation */
        .nav-item {
            padding: 12px;
            border-radius: 16px;
            text-align: center;
            cursor: pointer;
            transition: background 0.2s;
            color: #737688;
        }
        .nav-item.active { background: #eef0ff; color: #003ec7; font-weight: 700; }

        /* FAB */
        .fab {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 56px;
            height: 56px;
            background: #003ec7;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 8px 25px rgba(0,62,199,0.4);
            z-index: 1000;
            cursor: pointer;
        }
        
        .material-symbols-outlined { font-family: 'Material Symbols Outlined'; }
    </style>
""", unsafe_allow_html=True)

# --- DB HELPERS ---
def query_db(query, args=(), one=False):
    conn = get_db_connection()
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    conn = get_db_connection()
    conn.execute(query, args)
    conn.commit()
    conn.close()

# --- STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"

# --- TOP APP BAR ---
col_logo, col_space, col_settings = st.columns([1, 4, 1])
with col_logo:
    st.markdown("<div style='display:flex; align-items:center; gap:12px; padding:10px 0;'><div style='width:40px; height:40px; border-radius:50%; background: #003ec7; display:flex; align-items:center; justify-content:center; color:white; font-weight:900;'>M</div><span style='font-family:Lexend; font-weight:900; color:#003ec7; font-size:20px;'>Momentum</span></div>", unsafe_allow_html=True)
with col_settings:
    st.markdown("<div style='display:flex; justify-content:flex-end; padding:10px 0;'><span class='material-symbols-outlined' style='color:#737688; cursor:pointer;'>settings</span></div>", unsafe_allow_html=True)

# --- NAVIGATION BAR (TOP-STYLE FOR STREAMLIT) ---
tabs = ["Dashboard", "Rotina", "Metas", "Treino", "Histórico"]
cols = st.columns(len(tabs))
for i, tab in enumerate(tabs):
    if cols[i].button(tab, use_container_width=True, type="primary" if st.session_state.page == tab else "secondary"):
        st.session_state.page = tab
        st.rerun()

# --- DATA LOAD ---
profile = query_db('SELECT * FROM profile WHERE id = 1', one=True)

# --- PAGE CONTENT ---
if st.session_state.page == "Dashboard":
    # Greeting
    st.markdown(f"<h1 style='font-size: 32px; margin-top: 20px;'>Welcome back, {profile['name']}.</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#737688; margin-bottom: 32px;'>You're on a {profile['streak']}-day winning streak. Keep the momentum!</p>", unsafe_allow_html=True)

    # Bento Grid
    row1_col1, row1_col2 = st.columns([2, 1])
    
    with row1_col1:
        # Weekly Evolution Hero
        st.markdown(f"""
            <div class="bento-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:24px;">
                    <div>
                        <h2 style="font-size: 24px; margin:0;">Weekly Progress</h2>
                        <p style="font-size:12px; color:#737688; text-transform:uppercase; font-weight:700;">Overall Evolution Index</p>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:32px; font-weight:900; color:#003ec7;">+18%</span>
                        <p style="font-size:12px; color:#005b28; font-weight:700; text-transform:uppercase;">vs Last Week</p>
                    </div>
                </div>
                <div style="height:150px; display:flex; align-items:flex-end; gap:12px;">
                    <div style="flex:1; background:#eaedff; height:40%; border-radius:12px 12px 0 0;"></div>
                    <div style="flex:1; background:#eaedff; height:65%; border-radius:12px 12px 0 0;"></div>
                    <div style="flex:1; background:#eaedff; height:50%; border-radius:12px 12px 0 0;"></div>
                    <div style="flex:1; background:#003ec7; height:90%; border-radius:12px 12px 0 0; box-shadow:0 8px 20px rgba(0,62,199,0.2);"></div>
                    <div style="flex:1; background:#eaedff; height:75%; border-radius:12px 12px 0 0;"></div>
                    <div style="flex:1; background:#eaedff; height:40%; border-radius:12px 12px 0 0;"></div>
                    <div style="flex:1; background:#eaedff; height:30%; border-radius:12px 12px 0 0;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with row1_col2:
        # Quick Stats Cards
        st.markdown(f"""
            <div class="bento-card" style="display:flex; align-items:center; gap:20px;">
                <div style="width:56px; height:56px; background:#fe6b001a; border-radius:16px; display:flex; align-items:center; justify-content:center; color:#fe6b00;">
                    <span class="material-symbols-outlined" style="font-size:32px;">schedule</span>
                </div>
                <div>
                    <p style="font-size:12px; color:#737688; font-weight:700; text-transform:uppercase; margin:0;">Deep Work</p>
                    <h3 style="margin:0; font-size:24px;">6.5 <span style="font-size:16px; font-weight:400; color:#737688;">hrs</span></h3>
                </div>
            </div>
            <div class="bento-card" style="display:flex; align-items:center; gap:20px;">
                <div style="width:56px; height:56px; background:#005b281a; border-radius:16px; display:flex; align-items:center; justify-content:center; color:#005b28;">
                    <span class="material-symbols-outlined" style="font-size:32px;">local_fire_department</span>
                </div>
                <div>
                    <p style="font-size:12px; color:#737688; font-weight:700; text-transform:uppercase; margin:0;">Burned</p>
                    <h3 style="margin:0; font-size:24px;">1,240 <span style="font-size:16px; font-weight:400; color:#737688;">kcal</span></h3>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # Hero Row 2
    row2_col1, row2_col2 = st.columns(2)
    
    with row2_col1:
        # Professional Goal Hero
        st.markdown(f"""
            <div class="hero-card">
                <div class="hero-bg" style="background-image: url('https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=800&q=80');"></div>
                <div class="hero-overlay"></div>
                <div class="hero-content">
                    <span class="stat-badge">Professional</span>
                    <h3 style="margin:0; font-size:24px;">System Architecture Mastery</h3>
                    <p style="font-size:14px; opacity:0.8; margin-top:4px;">Capítulo 4: Comunicação Microservices</p>
                    <div style="display:flex; align-items:center; gap:12px; margin-top:16px;">
                        <div class="custom-progress-bg"><div class="custom-progress-fill" style="width:75%;"></div></div>
                        <span style="font-size:14px; font-weight:700;">75%</span>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with row2_col2:
        # Workout Hero
        st.markdown(f"""
            <div class="hero-card" style="background:#fe6b00;">
                <div class="hero-bg" style="background-image: url('https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=800&q=80');"></div>
                <div class="hero-overlay" style="background: linear-gradient(180deg, rgba(254,107,0,0) 0%, rgba(254,107,0,0.8) 100%);"></div>
                <div class="hero-content">
                    <span class="stat-badge">Workout</span>
                    <h3 style="margin:0; font-size:24px;">High-Intensity Training</h3>
                    <p style="font-size:14px; opacity:0.8; margin-top:4px;">Hoje: 45 min explosivos</p>
                    <button style="width:100%; background:white; color:#fe6b00; border:none; padding:10px; border-radius:12px; font-weight:700; margin-top:20px; cursor:pointer;">Começar Sessão</button>
                </div>
            </div>
        """, unsafe_allow_html=True)

elif st.session_state.page == "Rotina":
    st.markdown("<h2 style='margin-top:20px;'>Rotina Estruturada</h2>", unsafe_allow_html=True)
    days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    sel_day = st.select_slider("Selecione o Dia", options=days)
    
    tasks = query_db('SELECT * FROM routine WHERE day = ?', (sel_day,))
    for t in tasks:
        col_icon, col_txt, col_btn = st.columns([0.5, 4, 1])
        with col_icon:
            st.markdown(f"<div style='height:100%; display:flex; align-items:center; justify-content:center;'><span class='material-symbols-outlined' style='font-size:24px; color:{'#005b28' if t['completed'] else '#737688'};'>{t['icon']}</span></div>", unsafe_allow_html=True)
        with col_txt:
            st.markdown(f"""
                <div style='padding: 10px 0; opacity: {0.5 if t['completed'] else 1}'>
                    <span style='color:#003ec7; font-weight:900; font-size:12px;'>{t['time']}</span>
                    <p style='font-weight:700; margin:0; {'text-decoration: line-through;' if t['completed'] else ''}'>{t['task']}</p>
                    <p style='font-size:12px; color:#737688;'>{t['desc']}</p>
                </div>
            """, unsafe_allow_html=True)
        with col_btn:
            if st.button("✓" if not t['completed'] else "↺", key=f"t_{t['id']}"):
                execute_db('UPDATE routine SET completed = ? WHERE id = ?', (1 if not t['completed'] else 0, t['id']))
                st.rerun()
        st.divider()

elif st.session_state.page == "Metas":
    st.markdown("<h2 style='margin-top:20px;'>Planejamento Estratégico</h2>", unsafe_allow_html=True)
    goals = query_db('SELECT * FROM goals')
    for g in goals:
        with st.container():
            st.markdown(f"""
                <div class="bento-card">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-size:10px; font-weight:700; color:#003ec7; text-transform:uppercase;">{g['quarter']}</span>
                            <h3 style="margin:0;">{g['title']}</h3>
                            <p style="font-size:12px; color:#737688;">{g['description']}</p>
                        </div>
                        <div style="text-align:right;">
                            <span style="font-size:20px; font-weight:900; color:#003ec7;">{g['progress']}%</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            # Edit via sidebar or expansion
            with st.expander("Editar Meta"):
                new_p = st.slider("Progresso", 0, 100, int(g['progress']), key=f"p_{g['id']}")
                new_t = st.text_input("Título", g['title'], key=f"nt_{g['id']}")
                if st.button("Salvar", key=f"s_{g['id']}"):
                    execute_db('UPDATE goals SET progress = ?, title = ? WHERE id = ?', (new_p, new_t, g['id']))
                    st.rerun()

elif st.session_state.page == "Treino":
    st.markdown("<h2 style='margin-top:20px;'>Foco do Dia</h2>", unsafe_allow_html=True)
    cat = st.radio("Divisão", ["Push", "Pull", "Leg", "Capoeira"], horizontal=True)
    exercises = query_db('SELECT * FROM workouts WHERE category = ?', (cat,))
    for ex in exercises:
        st.markdown(f"""
            <div class="bento-card" style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <h4 style="margin:0;">{ex['name']}</h4>
                    <p style="font-size:12px; color:#737688;">{ex['series']} • {ex['muscle_group']}</p>
                </div>
                <span class="material-symbols-outlined" style="color:#eaedff; font-size:32px;">check_circle</span>
            </div>
        """, unsafe_allow_html=True)
    st.button("Finalizar Treino", type="primary", use_container_width=True)

# FAB Simulation
st.markdown("<div class='fab'><span class='material-symbols-outlined'>add</span></div>", unsafe_allow_html=True)
