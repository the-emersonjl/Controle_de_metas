import streamlit as st
import sqlite3
import pandas as pd
import json
from datetime import datetime

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Momentum - Dashboard de Evolução", 
    layout="wide", 
    initial_sidebar_state="collapsed"
)

# --- LÓGICA DO BANCO DE DADOS ---
DB_PATH = 'database.db'

def get_db_connection():
    """Cria uma conexão com o banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Inicializa o banco de dados e cria as tabelas se não existirem."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de perfil do usuário
    cursor.execute('CREATE TABLE IF NOT EXISTS profile (id INTEGER PRIMARY KEY, name TEXT, streak INTEGER)')
    
    # Tabela de rotina diária
    cursor.execute('CREATE TABLE IF NOT EXISTS routine (id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, time TEXT, task TEXT, desc TEXT, icon TEXT, completed BOOLEAN DEFAULT 0)')
    
    # Tabela de treinos (divisões)
    cursor.execute('CREATE TABLE IF NOT EXISTS workouts (id INTEGER PRIMARY KEY AUTOINCREMENT, category TEXT, name TEXT, series TEXT, muscle_group TEXT, completed BOOLEAN DEFAULT 0)')
    
    # Tabela de metas trimestrais
    cursor.execute('CREATE TABLE IF NOT EXISTS goals (id INTEGER PRIMARY KEY AUTOINCREMENT, quarter TEXT, title TEXT, description TEXT, icon TEXT, progress INTEGER DEFAULT 0, active BOOLEAN DEFAULT 0)')

    # Verifica se o perfil já existe, se não, cria o perfil inicial (Emerson)
    cursor.execute('SELECT * FROM profile WHERE id = 1')
    if not cursor.fetchone():
        cursor.execute('INSERT INTO profile (id, name, streak) VALUES (1, "Emerson", 12)')
        
        # Dados iniciais da rotina completa
        routine_data = {
            "Seg": [
                ("07:30", "Acordar", "Café e preparação", "sunny"),
                ("08:20", "Deslocamento", "Podcast ou música", "commute"),
                ("09:00", "Trabalho", "Foco Total", "work"),
                ("12:00", "Marmita", "Almoço saudável", "restaurant"),
                ("16:00", "Saída → Academia", "Direto do trabalho", "directions_run"),
                ("16:30", "Treino PUSH", "Academia - 1h20", "fitness_center"),
                ("18:10", "Estudos Dados", "API / Ferramentas", "database"),
                ("19:00", "Jantar", "Refeição pós-treino", "dinner_dining"),
                ("20:00", "Faculdade", "Aulas e exercícios", "school"),
                ("22:30", "Banho", "Relaxar e dormir", "shower")
            ],
            "Ter": [
                ("07:30", "Acordar", "Café e preparação", "sunny"),
                ("09:00", "Trabalho", "Foco Total", "work"),
                ("12:00", "Marmita", "Almoço saudável", "restaurant"),
                ("16:30", "Treino PULL", "Academia", "fitness_center"),
                ("18:10", "Inglês", "Familiarização Contínua", "translate"),
                ("19:30", "Jantar", "Refeição leve", "dinner_dining"),
                ("20:00", "Faculdade", "Aulas e exercícios", "school"),
                ("22:30", "Banho", "Relaxar", "shower")
            ],
            "Qua": [
                ("07:30", "Acordar", "Café e preparação", "sunny"),
                ("09:00", "Trabalho", "Foco Total", "work"),
                ("12:00", "Marmita", "Almoço saudável", "restaurant"),
                ("16:30", "Treino LEG", "Academia", "fitness_center"),
                ("18:10", "Estudos Dados", "Comunicação / DS", "analytics"),
                ("19:30", "Jantar", "Refeição equilibrada", "dinner_dining"),
                ("20:00", "Inglês", "1h de foco", "translate"),
                ("21:00", "Faculdade", "Revisão rápida", "school"),
                ("22:30", "Banho", "Higiene noturna", "shower")
            ],
            "Qui": [
                ("07:30", "Acordar", "Café e preparação", "sunny"),
                ("09:00", "Trabalho", "Foco Total", "work"),
                ("12:00", "Marmita", "Almoço saudável", "restaurant"),
                ("17:00", "Terapia", "Prioridade Semanal", "psychology"),
                ("18:30", "Treino PUSH", "Pós-Terapia", "fitness_center"),
                ("20:00", "Jantar", "Refeição rápida", "dinner_dining"),
                ("21:00", "Inglês", "Sessão noturna", "translate"),
                ("22:30", "Banho", "Relaxar", "shower")
            ],
            "Sex": [
                ("07:30", "Acordar", "Café e preparação", "sunny"),
                ("09:00", "Trabalho", "Foco Total", "work"),
                ("12:00", "Marmita", "Almoço saudável", "restaurant"),
                ("16:30", "Treino PULL", "Último da semana", "fitness_center"),
                ("18:10", "Estudos Dados", "Projetos", "database"),
                ("19:30", "Jantar", "Refeição livre", "dinner_dining"),
                ("21:00", "Tempo Esposa", "Série / Lazer", "favorite"),
                ("22:30", "Banho", "Higiene noturna", "shower")
            ],
            "Sáb": [
                ("09:00", "Acordar", "Café tranquilo", "sunny"),
                ("11:00", "Capoeira", "Prioridade Treino", "sports_martial_arts"),
                ("13:00", "Almoço", "Família", "restaurant"),
                ("14:00", "Faculdade", "Tarefas e revisão", "school"),
                ("16:00", "Inglês", "Prática livre", "translate"),
                ("17:00", "Lazer Esposa", "Tempo de Qualidade", "restaurant"),
                ("20:00", "Jantar Especial", "Fora ou delivery", "dinner_dining"),
                ("22:30", "Banho", "Relaxar", "shower")
            ],
            "Dom": [
                ("09:30", "Manhã Esposa", "Café fora e relaxar", "bakery_dining"),
                ("13:00", "Almoço", "Família", "restaurant"),
                ("15:00", "Inglês", "Ritmo tranquilo", "translate"),
                ("17:00", "Prep. Semana", "Agenda e Marmitas", "inventory_2"),
                ("19:00", "Jantar", "Refeição leve", "dinner_dining"),
                ("21:00", "Organização", "Limpeza rápida", "clean_hands"),
                ("22:30", "Banho", "Preparar para Seg", "shower")
            ]
        }
        for day, tasks in routine_data.items():
            for task in tasks:
                cursor.execute('INSERT INTO routine (day, time, task, desc, icon) VALUES (?, ?, ?, ?, ?)', (day, task[0], task[1], task[2], task[3]))

        # Dados iniciais de exercícios por categoria
        workouts = [
            ('Push', 'Supino Reto', '4 x 10', 'Peito'),
            ('Push', 'Supino Inclinado', '3 x 12', 'Peito'),
            ('Push', 'Crucifixo Máquina', '3 x 15', 'Peito'),
            ('Push', 'Desenvolvimento Militar', '4 x 10', 'Ombro'),
            ('Push', 'Elevação Lateral', '4 x 15', 'Ombro'),
            ('Push', 'Tríceps Corda', '3 x 12', 'Tríceps'),
            ('Push', 'Tríceps Testa', '3 x 10', 'Tríceps'),
            ('Pull', 'Puxada Aberta', '4 x 12', 'Costas'),
            ('Pull', 'Remada Curvada', '3 x 10', 'Costas'),
            ('Leg', 'Agachamento', '4 x 10', 'Pernas'),
            ('Capoeira', 'Ginga e Esquivas', '30 min', 'Geral')
        ]
        for w in workouts:
            cursor.execute('INSERT INTO workouts (category, name, series, muscle_group) VALUES (?, ?, ?, ?)', w)

        # Dados iniciais de metas
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

# --- INTERFACE DO STREAMLIT ---
init_db()

# CSS Customizado para manter a estética premium original
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lexend:wght@400;600;700;900&display=swap');
        
        /* Estilo base e cores */
        .main { background-color: #faf8ff; }
        .stButton>button { border-radius: 12px; transition: all 0.2s; }
        .card { background-color: white; padding: 20px; border-radius: 24px; border: 1px solid #eaedff; margin-bottom: 20px; box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05); }
        .font-lexend { font-family: 'Lexend', sans-serif; }
        .text-primary { color: #003ec7; }
        .text-outline { color: #737688; }
        
        /* Simulação de barras de progresso e ícones */
        .progress-bar-bg { background-color: #eaedff; height: 10px; border-radius: 5px; width: 100%; margin-top: 5px; }
        .progress-bar-fill { background-color: #003ec7; height: 10px; border-radius: 5px; }
        .material-symbols-outlined { font-family: 'Material Symbols Outlined'; }
    </style>
""", unsafe_allow_html=True)

# Funções auxiliares para manipulação do banco de dados
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

# Barra lateral para navegação
with st.sidebar:
    st.title("Momentum")
    page = st.radio("Navegação", ["Início", "Rotina", "Metas", "Treino", "Log"])

# Carrega perfil do usuário
profile = query_db('SELECT * FROM profile WHERE id = 1', one=True)

if page == "Início":
    st.markdown(f"<h1 class='font-lexend' style='font-size: 2.5rem; margin-bottom: 0;'>Olá, {profile['name']}.</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='text-outline'>Você está em uma sequência de {profile['streak']} dias. Mantenha o foco!</p>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Gráfico semanal simulado com HTML/CSS
        st.markdown("<div class='card'><h2 class='font-lexend'>Evolução Semanal</h2><p class='text-outline' style='font-size: 0.8rem;'>Índice de Consistência</p><div style='height: 150px; display: flex; align-items: flex-end; gap: 10px;'><div style='flex:1; background:#eaedff; height:40%; border-radius:8px 8px 0 0;'></div><div style='flex:1; background:#eaedff; height:65%; border-radius:8px 8px 0 0;'></div><div style='flex:1; background:#003ec7; height:90%; border-radius:8px 8px 0 0;'></div><div style='flex:1; background:#eaedff; height:55%; border-radius:8px 8px 0 0;'></div><div style='flex:1; background:#eaedff; height:80%; border-radius:8px 8px 0 0;'></div><div style='flex:1; background:#eaedff; height:30%; border-radius:8px 8px 0 0;'></div><div style='flex:1; background:#eaedff; height:20%; border-radius:8px 8px 0 0;'></div></div></div>", unsafe_allow_html=True)
        
    with col2:
        # Cards de estatísticas rápidas
        st.markdown("<div class='card' style='display: flex; align-items: center; gap: 15px;'><div style='background: #fff7ed; padding: 10px; border-radius: 12px; color: #fe6b00;'><span class='material-symbols-outlined' style='font-size: 2rem;'>terminal</span></div><div><p class='text-outline' style='font-size: 0.7rem; font-weight: bold; margin:0;'>ESTUDOS HOJE</p><h3 class='font-lexend' style='margin:0;'>1.5 hrs</h3></div></div>", unsafe_allow_html=True)
        st.markdown("<div class='card' style='display: flex; align-items: center; gap: 15px;'><div style='background: #f0fdf4; padding: 10px; border-radius: 12px; color: #005b28;'><span class='material-symbols-outlined' style='font-size: 2rem;'>fitness_center</span></div><div><p class='text-outline' style='font-size: 0.7rem; font-weight: bold; margin:0;'>TREINO</p><h3 class='font-lexend' style='margin:0;'>Push Day</h3></div></div>", unsafe_allow_html=True)

elif page == "Rotina":
    st.markdown("<h2 class='font-lexend'>Rotina Estruturada</h2>", unsafe_allow_html=True)
    
    days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    selected_day = st.select_slider("Selecione o Dia", options=days)
    
    # Busca tarefas do dia selecionado
    tasks = query_db('SELECT * FROM routine WHERE day = ?', (selected_day,))
    
    for task in tasks:
        col_t, col_b = st.columns([4, 1])
        with col_t:
            st.markdown(f"""
                <div class='card' style='margin-bottom: 10px; opacity: {0.5 if task['completed'] else 1}; border-left: 5px solid {"#005b28" if task['completed'] else "#003ec7"}'>
                    <div style='display: flex; justify-content: space-between;'>
                        <div>
                            <span class='text-primary' style='font-weight: bold; font-size: 0.8rem;'>{task['time']}</span>
                            <p class='font-lexend' style='margin: 0; font-size: 1rem; {"text-decoration: line-through;" if task['completed'] else ""}'>{task['task']}</p>
                            <p class='text-outline' style='font-size: 0.7rem;'>{task['desc']}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with col_b:
            # Botão para alternar status da tarefa
            if st.button("✓" if not task['completed'] else "↺", key=f"btn_{task['id']}"):
                execute_db('UPDATE routine SET completed = ? WHERE id = ?', (1 if not task['completed'] else 0, task['id']))
                st.rerun()

elif page == "Metas":
    st.markdown("<h2 class='font-lexend'>Metas Trimestrais</h2>", unsafe_allow_html=True)
    
    goals = query_db('SELECT * FROM goals')
    quarters = sorted(list(set([g['quarter'] for g in goals])))
    
    for q in quarters:
        q_goals = [g for g in goals if g['quarter'] == q]
        avg_prog = sum([g['progress'] for g in q_goals]) // len(q_goals)
        
        # Expander por trimestre
        with st.expander(f"{q} - Progresso Geral: {avg_prog}%", expanded=(q == '1º Trimestre')):
            for g in q_goals:
                st.markdown(f"**{g['title']}**")
                st.markdown(f"<p class='text-outline' style='font-size: 0.8rem;'>{g['description']}</p>", unsafe_allow_html=True)
                
                # Sliders para atualizar progresso em tempo real
                new_prog = st.slider("Progresso (%)", 0, 100, int(g['progress']), key=f"goal_{g['id']}")
                if new_prog != g['progress']:
                    execute_db('UPDATE goals SET progress = ? WHERE id = ?', (new_prog, g['id']))
                    st.rerun()
                
                # Campos de edição de texto
                new_title = st.text_input("Editar Título", g['title'], key=f"title_{g['id']}")
                new_desc = st.text_input("Editar Descrição", g['description'], key=f"desc_{g['id']}")
                if new_title != g['title'] or new_desc != g['description']:
                    execute_db('UPDATE goals SET title = ?, description = ? WHERE id = ?', (new_title, new_desc, g['id']))
                    st.rerun()
                st.divider()

elif page == "Treino":
    st.markdown("<h2 class='font-lexend'>Treino</h2>", unsafe_allow_html=True)
    cat = st.selectbox("Selecione a Divisão", ["Push", "Pull", "Leg", "Capoeira"])
    
    # Busca exercícios da categoria selecionada
    exercises = query_db('SELECT * FROM workouts WHERE category = ?', (cat,))
    
    for ex in exercises:
        st.markdown(f"""
            <div class='card'>
                <div style='display: flex; justify-content: space-between; align-items: center;'>
                    <div>
                        <p class='font-lexend' style='margin: 0;'>{ex['name']}</p>
                        <p class='text-outline' style='font-size: 0.8rem;'>{ex['series']} • {ex['muscle_group']}</p>
                    </div>
                    <span class='material-symbols-outlined' style='color: #eaedff;'>check_circle</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    if st.button("FINALIZAR TREINO", type="primary", use_container_width=True):
        st.success(f"Treino {cat} finalizado com sucesso, Emerson! Ótimo trabalho.")

elif page == "Log":
    st.markdown("<h2 class='font-lexend'>Log de Progresso</h2>", unsafe_allow_html=True)
    # Calendário interativo nativo do Streamlit
    st.date_input("Consultar Histórico")
    st.info("Aqui você verá a retrospectiva da sua evolução conforme preenche os dados diários.")

