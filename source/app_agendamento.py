import streamlit as st
from datetime import datetime
from db_supabase import inserir_agendamento, listar_agendamentos_por_data

# ==========================
# CONFIGURAÇÃO GERAL
# ==========================
st.set_page_config(page_title="Agendamento Barbearia", layout="centered", page_icon="💈")

# CSS customizado para aparência mobile
st.markdown("""
<style>
    body, html {
        margin: 0;
        padding: 0;
    }
    [data-testid="stAppViewContainer"] {
        background-color: #f8f9fa;
        padding-top: 1rem;
    }
    h1 {
        text-align: center;
        font-size: 1.8rem !important;
    }
    h4 {
        font-size: 1.1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #1e88e5 !important;
        color: white !important;
        font-weight: 600;
        padding: 0.6rem 0;
        margin-top: 5px;
    }
    .stButton>button:hover {
        background-color: #1565c0 !important;
    }
    img {
        border-radius: 12px;
    }
    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
        }
        h1 {
            font-size: 1.5rem !important;
        }
        h4, p {
            text-align: center;
        }
    }
</style>
""", unsafe_allow_html=True)

st.title("💈 Barbearia Cardoso 💈")
st.markdown("<p style='text-align:center;'>Agende seu horário rapidamente no seu celular!</p>", unsafe_allow_html=True)

# ==========================
# FUNÇÕES
# ==========================
def horarios_disponiveis(data_str):
    """Retorna horários livres baseados no Supabase"""
    agendamentos = listar_agendamentos_por_data(data_str)
    ocupados = {a["hora"] for a in agendamentos if not a.get("bloqueado")}
    bloqueados = {a["hora"] for a in agendamentos if a.get("bloqueado")}
    todos = [f"{h:02d}:00" for h in range(9, 19)]
    return [h for h in todos if h not in ocupados and h not in bloqueados]

# ==========================
# 1️⃣ Escolha do serviço
# ==========================
st.subheader("✂️ Escolha o serviço desejado")

servicos = [
    ("Corte Masculino.png", "Corte masculino", 40),
    ("Barba.png", "Barba", 35),
    ("Barbo terapia.png", "Barboterapia com toalha quente", 45),
    ("Corte e Barba.png", "Corte e barba", 85),
    ("Corte na 0 e Barba.png", "Corte na 0 e barba", 65),
    ("Cera Quente e Corte.png", "Cera quente e corte", 60),
    ("Alisamento.png", "Alisamento e corte", 70),
    ("Sobrancelha.png", "Sobrancelha", 15),
    ("Pezinho.png", "Pezinho e acabamento", 15),
    ("Kings Day.png", "King’s Day (Corte + Barba + Cera quente)", 95),
    ("Corte Barba Alisamento Sobrancelha.png", "Corte, Barba, Alisamento e Sobrancelha", 110),
]

cols = st.columns(2)
for i, (img, nome, valor) in enumerate(servicos):
    with cols[i % 2]:
        st.image(f"imagens/{img}", use_column_width=True)
        st.markdown(f"<h4 style='text-align:center;'>{nome}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'>R$ {valor},00</p>", unsafe_allow_html=True)
        if st.button(f"Selecionar {nome}", key=nome):
            st.session_state["servico"] = nome
            st.session_state["valor"] = valor
    if i % 2 == 1:
        st.markdown("---")

if "servico" not in st.session_state:
    st.warning("👈 Escolha um serviço antes de continuar.")
    st.stop()

st.success(f"Serviço selecionado: {st.session_state['servico']} (R$ {st.session_state['valor']},00)")

# ==========================
# 2️⃣ Dados do cliente
# ==========================
st.divider()
st.subheader("📋 Informe seus dados")

nome = st.text_input("Seu nome completo")
telefone = st.text_input("Seu WhatsApp (ex: 11 99999-9999)")
data = st.date_input("Escolha o dia")
data_str = data.strftime("%d/%m/%Y")
disponiveis = horarios_disponiveis(data_str)

if not disponiveis:
    st.info("⏰ Nenhum horário disponível neste dia.")
else:
    hora = st.selectbox("Escolha o horário", disponiveis)
    if st.button("✅ Confirmar agendamento"):
        if not nome or not telefone:
            st.warning("Preencha todos os campos.")
        else:
            inserir_agendamento(
                nome,
                telefone,
                data_str,
                hora,
                st.session_state["servico"],
                st.session_state["valor"]
            )
            st.success(f"✅ Agendamento confirmado para {data_str} às {hora}!")
            st.balloons()
