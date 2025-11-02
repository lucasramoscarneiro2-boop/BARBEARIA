import streamlit as st
from datetime import date, timedelta
import streamlit.components.v1 as components
from streamlit_calendar import calendar
from time import time
import hashlib
from db_supabase import (
    listar_agendamentos_por_data,
    cancelar_agendamento,
    bloquear_horario,
    autenticar
)

# ==========================
# CONFIG GERAL
# ==========================
st.set_page_config(page_title="Agenda do Barbeiro", layout="centered", page_icon="💈")

st.markdown("""
<style>
body, .stApp {
    background-color: #111;
    color: white;
    font-family: 'Segoe UI', sans-serif;
}
.agenda-container {
    border-radius: 15px;
    background-color: #1a1a1a;
    padding: 20px;
    box-shadow: 0 0 15px rgba(255,255,255,0.1);
}
.agenda-hora { font-weight:bold;width:80px;color:#00bfff;display:inline-block; }
.agenda-bloco { border-bottom:1px solid #333;padding:10px 0; }
.ocupado {
    background-color:#222;border-left:5px solid #00bfff;border-radius:10px;
    padding:10px;margin-left:10px;
}
.bloqueado {
    background-color:#400;border-left:5px solid #ff3333;border-radius:10px;
    padding:10px;margin-left:10px;
}
.livre { color:gray;margin-left:10px; }
.toast {
    position:fixed;bottom:30px;right:30px;background:linear-gradient(90deg,#0044cc,#ff0000,#ffffff);
    background-size:300% 300%;color:#fff;padding:18px 28px;border-radius:12px;
    box-shadow:0 4px 20px rgba(0,0,0,0.4);font-weight:bold;z-index:9999;
    animation:glow 3s ease-in-out infinite, fadein 0.5s, fadeout 0.5s 4s;
}
@keyframes glow {0%{background-position:0% 50%;}50%{background-position:100% 50%;}100%{background-position:0% 50%;}}
@keyframes fadein { from {opacity:0;bottom:10px;} to {opacity:1;bottom:30px;} }
@keyframes fadeout { from {opacity:1;bottom:30px;} to {opacity:0;bottom:10px;} }
</style>
""", unsafe_allow_html=True)

st.title("💇‍♂️ Agenda do Barbeiro")
st.markdown("Gerencie seus horários — veja agendamentos, bloqueie ou libere horários")

# ==========================
# LOGIN COM TOKEN PERSISTENTE
# ==========================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "token" not in st.session_state:
    st.session_state.token = None

# se já há token na URL, reaplica
params = st.experimental_get_query_params()
if "token" in params and not st.session_state.autenticado:
    st.session_state.autenticado = True
    st.session_state.token = params["token"][0]
    st.session_state.usuario = params.get("usuario", [""])[0]

if not st.session_state.autenticado:
    st.subheader("🔐 Login do barbeiro")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if autenticar(usuario, senha):
            token = hashlib.sha256(f"{usuario}{time()}".encode()).hexdigest()
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.session_state.token = token
            st.experimental_set_query_params(usuario=usuario, token=token)
            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos.")
    st.stop()

# ==========================
# AUTO REFRESH SUAVE
# ==========================
REFRESH_INTERVAL = 60
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time()
if time() - st.session_state.last_refresh > REFRESH_INTERVAL:
    st.session_state.last_refresh = time()
    st.experimental_rerun()

colA, colB, colC = st.columns([1,1,1])
with colB:
    if st.button("🔄 Atualizar agora"):
        st.experimental_rerun()

# ==========================
# CALENDÁRIO SEMANAL
# ==========================
st.divider()
st.subheader("📆 Visualização semanal da agenda")

hoje = date.today()
inicio_semana = hoje - timedelta(days=hoje.weekday())
fim_semana = inicio_semana + timedelta(days=6)

eventos = []
for i in range(7):
    data = (inicio_semana + timedelta(days=i)).strftime("%d/%m/%Y")
    for ag in listar_agendamentos_por_data(data):
        cor = "#1b9e77" if not ag.get("bloqueado") else "#d73027"
        eventos.append({
            "title": f"{ag['hora']} {ag['nome']} ({ag['servico']})",
            "start": f"2025-{data[3:5]}-{data[0:2]}",
            "color": cor,
        })

calendar_options = {
    "initialView": "dayGridWeek",
    "locale": "pt-br",
    "height": 650,
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,dayGridWeek,dayGridDay"
    },
}
calendar(events=eventos, options=calendar_options)

# ==========================
# FILTRO DE DATA DETALHADO
# ==========================
data_filtro = st.date_input("📅 Escolha o dia", value=date.today())
data_str = data_filtro.strftime("%d/%m/%Y")
agendamentos = listar_agendamentos_por_data(data_str)

if "ultimo_total" not in st.session_state:
    st.session_state.ultimo_total = 0

total_atual = len(agendamentos)
novos = total_atual > st.session_state.ultimo_total
st.session_state.ultimo_total = total_atual

if novos:
    components.html("""
    <div class="toast">💈 Novo agendamento recebido!</div>
    <script>
    const audio = new Audio("https://actions.google.com/sounds/v1/alarms/beep_short.ogg");
    audio.play();
    </script>
    """, height=0)

# ==========================
# BLOQUEAR HORÁRIO
# ==========================
st.divider()
st.subheader("🛑 Bloquear horário")

col1, col2 = st.columns(2)
with col1:
    hora_bloqueio = st.selectbox("Horário para bloquear", [f"{h:02d}:00" for h in range(9, 20)])
with col2:
    motivo = st.text_input("Motivo (opcional)", placeholder="Ex: Almoço, folga...")

if st.button("Bloquear horário"):
    if any(a["hora"] == hora_bloqueio for a in agendamentos):
        st.error("⚠️ Este horário já está agendado ou bloqueado.")
    else:
        bloquear_horario(data_str, hora_bloqueio, motivo or "Bloqueado")
        st.success(f"🚫 Horário {hora_bloqueio} bloqueado!")
        st.experimental_rerun()

# ==========================
# LISTA DETALHADA
# ==========================
st.divider()
st.markdown(f"### 🗓️ Agenda detalhada de {data_str}")
st.markdown("<div class='agenda-container'>", unsafe_allow_html=True)

for h in [f"{x:02d}:00" for x in range(9, 20)]:
    st.markdown("<div class='agenda-bloco'>", unsafe_allow_html=True)
    st.markdown(f"<span class='agenda-hora'>{h}</span>", unsafe_allow_html=True)
    ag = next((a for a in agendamentos if a["hora"] == h), None)
    if ag:
        if ag.get("bloqueado"):
            st.markdown(f"<div class='bloqueado'>🛑 <strong>Horário bloqueado</strong><br>{ag.get('servico','')}</div>", unsafe_allow_html=True)
            if st.button(f"🔓 Desbloquear {h}", key=f"u_{h}"):
                cancelar_agendamento(ag["id"])
                st.success(f"✅ Horário {h} liberado.")
                st.experimental_rerun()
        else:
            st.markdown(f"<div class='ocupado'><strong>{ag['nome']}</strong><br>✂️ {ag['servico']} — 💰 R$ {ag['valor']},00<br>📞 {ag['telefone']}</div>", unsafe_allow_html=True)
            if st.button(f"❌ Cancelar {ag['nome']} - {h}", key=f"c_{h}"):
                cancelar_agendamento(ag["id"])
                st.warning(f"🚫 Agendamento de {ag['nome']} às {h} cancelado.")
                st.experimental_rerun()
    else:
        st.markdown("<span class='livre'>🕓 Horário livre</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br><p style='text-align:center; color:gray;'>💈 Barbearia Cardoso 💈 — Agenda com login persistente, visual semanal e alertas</p>", unsafe_allow_html=True)
