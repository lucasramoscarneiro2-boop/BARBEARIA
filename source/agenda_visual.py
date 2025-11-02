import streamlit as st
from datetime import date
import streamlit.components.v1 as components
from db_supabase import (
    listar_agendamentos_por_data,
    cancelar_agendamento,
    bloquear_horario,
    autenticar
)
from streamlit_autorefresh import st_autorefresh

# ==========================
# CONFIGURAÇÃO GERAL
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
.agenda-hora {
    font-weight: bold;
    width: 80px;
    color: #00bfff;
}
.agenda-bloco {
    border-bottom: 1px solid #333;
    padding: 10px 0;
}
.ocupado {
    background-color: #222;
    border-left: 5px solid #00bfff;
    border-radius: 10px;
    padding: 10px;
    margin-left: 10px;
}
.bloqueado {
    background-color: #400;
    border-left: 5px solid #ff3333;
    border-radius: 10px;
    padding: 10px;
    margin-left: 10px;
}
.livre {
    color: gray;
    margin-left: 10px;
}

/* ===== Toast notification com animação pulsante ===== */
.toast {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background: linear-gradient(90deg, #0044cc, #ff0000, #ffffff);
    background-size: 300% 300%;
    color: #fff;
    padding: 18px 28px;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
    font-weight: bold;
    z-index: 9999;
    animation: glow 3s ease-in-out infinite, fadein 0.5s, fadeout 0.5s 4s;
}
@keyframes glow {
  0% {background-position: 0% 50%;}
  50% {background-position: 100% 50%;}
  100% {background-position: 0% 50%;}
}
@keyframes fadein { from {opacity: 0; bottom: 10px;} to {opacity: 1; bottom: 30px;} }
@keyframes fadeout { from {opacity: 1; bottom: 30px;} to {opacity: 0; bottom: 10px;} }

</style>
""", unsafe_allow_html=True)

st.title("💇‍♂️ Agenda do Barbeiro")
st.markdown("Gerencie seus horários — veja agendamentos, bloqueie ou libere horários")

# ==========================
# LOGIN PERSISTENTE (sem query params)
# ==========================
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "senha" not in st.session_state:
    st.session_state.senha = ""
if "ultimo_total" not in st.session_state:
    st.session_state.ultimo_total = 0

if not st.session_state.autenticado:
    st.subheader("🔐 Login do barbeiro")
    usuario = st.text_input("Usuário", value=st.session_state.usuario)
    senha = st.text_input("Senha", type="password", value=st.session_state.senha)

    if st.button("Entrar"):
        if autenticar(usuario, senha):
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.session_state.senha = senha
            st.success("✅ Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("❌ Usuário ou senha incorretos.")
    st.stop()

# ==========================
# AUTOATUALIZAÇÃO SEGURA
# ==========================
REFRESH_INTERVAL = 60  # segundos
st_autorefresh(interval=REFRESH_INTERVAL * 1000, key="auto_refresh_key")

# ==========================
# FILTRO DE DATA E AGENDAMENTOS
# ==========================
data_filtro = st.date_input("📅 Escolha o dia", value=date.today())
data_str = data_filtro.strftime("%d/%m/%Y")

agendamentos = listar_agendamentos_por_data(data_str)
total_atual = len(agendamentos)

# Detecta novos agendamentos
novos_agendamentos = total_atual > st.session_state["ultimo_total"]
st.session_state["ultimo_total"] = total_atual

# 🔔 Toast visual + som ao receber novo agendamento
if novos_agendamentos:
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
    motivo = st.text_input("Motivo (opcional)", placeholder="Ex: Almoço, folga, manutenção...")

if st.button("Bloquear horário"):
    ocupado = any(a["hora"] == hora_bloqueio for a in agendamentos)
    if ocupado:
        st.error("⚠️ Este horário já está agendado ou bloqueado.")
    else:
        bloquear_horario(data_str, hora_bloqueio, motivo or "Bloqueado")
        st.success(f"🚫 Horário {hora_bloqueio} bloqueado com sucesso!")
        st.rerun()

# ==========================
# AGENDA VISUAL
# ==========================
st.divider()
st.markdown(f"### 🗓️ Agenda de {data_str}")
st.markdown("<div class='agenda-container'>", unsafe_allow_html=True)

horarios = [f"{h:02d}:00" for h in range(9, 20)]

for hora in horarios:
    st.markdown("<div class='agenda-bloco'>", unsafe_allow_html=True)
    st.markdown(f"<span class='agenda-hora'>{hora}</span>", unsafe_allow_html=True)

    agendamento = next((a for a in agendamentos if a["hora"] == hora), None)

    if agendamento:
        if agendamento.get("bloqueado"):
            st.markdown(
                f"""
                <div class='bloqueado'>
                    🛑 <strong>Horário bloqueado</strong><br>
                    {agendamento.get("servico", "")}
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"🔓 Desbloquear {hora}", key=f"unblock_{hora}"):
                cancelar_agendamento(agendamento["id"])
                st.success(f"✅ Horário {hora} foi liberado.")
                st.rerun()
        else:
            st.markdown(
                f"""
                <div class='ocupado'>
                    <strong>{agendamento['nome']}</strong><br>
                    ✂️ {agendamento['servico']} — 💰 R$ {agendamento['valor']},00<br>
                    📞 {agendamento['telefone']}
                </div>
                """,
                unsafe_allow_html=True
            )
            if st.button(f"❌ Cancelar {agendamento['nome']} - {hora}", key=f"cancel_{hora}"):
                cancelar_agendamento(agendamento["id"])
                st.warning(f"🚫 Agendamento de {agendamento['nome']} às {hora} foi cancelado.")
                st.rerun()
    else:
        st.markdown("<span class='livre'>🕓 Horário livre</span>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<br><p style='text-align:center; color:gray;'>💈 Barbearia Cardoso 💈 — Agenda online com alertas animados e som automático</p>", unsafe_allow_html=True)
