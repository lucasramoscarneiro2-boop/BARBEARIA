import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from pathlib import Path
from db_supabase import inserir_agendamento, listar_agendamentos_por_data

# ==========================
# CONFIGURAÇÃO GERAL
# ==========================
st.set_page_config(page_title="Agendamento Barbearia", layout="centered", page_icon="💈")

# Caminho base das imagens
BASE_DIR = Path(__file__).resolve().parents[1]
IMG_DIR = BASE_DIR / "imagens"

# ==========================
# ESTILOS
# ==========================
st.markdown("""
<style>
body, .stApp {
    background-color: #f5f6fa;
    font-family: 'Poppins', sans-serif;
    color: #222;
}

/* Cabeçalhos */
h1, h2, h3, h4 {
    text-align: center;
    color: #111;
}
h1 { font-size: 1.8rem !important; margin-bottom: 0.8rem; }
h2, h3 { font-size: 1.4rem !important; }

/* Botões */
.stButton>button {
    width: 100%;
    border-radius: 12px;
    background: linear-gradient(90deg, #007bff, #00b4d8);
    color: white !important;
    font-weight: 600;
    padding: 0.7rem 0;
    border: none;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    background: linear-gradient(90deg, #0056b3, #0096c7);
    transform: scale(1.02);
}

/* Cards de serviços */
.servico-card {
    background: white;
    border-radius: 16px;
    padding: 1rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    text-align: center;
    transition: all 0.25s ease;
}
.servico-card:hover {
    transform: scale(1.03);
    box-shadow: 0 4px 16px rgba(0,123,255,0.2);
}

/* Mobile */
@media (max-width: 768px) {
    .block-container { padding: 0.5rem 1rem !important; }
    h1 { font-size: 1.5rem !important; }
    h4 { font-size: 1rem !important; }
    .stButton>button { font-size: 1rem !important; padding: 0.6rem; }
}
</style>
""", unsafe_allow_html=True)

# ==========================
# CABEÇALHO
# ==========================
st.title("💈 Barbearia Cardoso 💈")
st.markdown("<p style='text-align:center; color:#333;'>Agende seu horário rapidamente no seu celular!</p>", unsafe_allow_html=True)

# ==========================
# FUNÇÃO DE HORÁRIOS
# ==========================
def horarios_disponiveis(data_str):
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
    ("Corte e barba.png", "Corte e barba", 85),
    ("Corte na 0 e Barba.png", "Corte na 0 e barba", 65),
    ("Cera nariz.png", "Cera quente e corta", 60),
    ("Alisamento.png", "Alisamento e corte", 70),
    ("Sombrancelha.png", "Sobrancelha", 15),
    ("Pezinho.png", "Pezinho e acabamento", 15),
    ("Kings Day.png", "King’s Day (Corte + Barba + Cera quente)", 95),
    ("Corte barba alisamento e sombrancelha.png", "Corte, Barba, Alisamento e Sobrancelha", 110),
]

col1, col2 = st.columns(2)

for i, (img_name, nome, valor) in enumerate(servicos):
    selecionado = "servico" in st.session_state and st.session_state["servico"] == nome
    border = "#007bff" if selecionado else "#ccc"
    sombra = "0 0 20px rgba(0,123,255,0.6)" if selecionado else "0 2px 10px rgba(0,0,0,0.1)"

    with (col1 if i % 2 == 0 else col2):
        st.markdown(
            f"""
            <div id="card_{i}"
                 style="cursor:pointer; border:3px solid {border};
                        border-radius:18px; padding:1rem; margin-bottom:1.2rem;
                        background:rgba(255,255,255,0.97); box-shadow:{sombra};
                        text-align:center; transition:all .25s ease;"
                 onclick="window.parent.postMessage({{'servico':'{nome}','valor':{valor}}}, '*')">
                <img src="imagens/{img_name}"
                     alt="{nome}" style="width:100%; border-radius:14px;
                     box-shadow:0 4px 12px rgba(0,0,0,0.15);" />
                <h4 style="margin-top:0.6rem; color:#111;">{nome}</h4>
                <p style="margin:0; font-weight:600; color:#007bff;">R$ {valor:.2f}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# Captura clique no card
components.html(
    """
    <script>
    window.addEventListener('message', (event) => {
        if (event.data.servico) {
            const params = new URLSearchParams();
            params.set("servico", event.data.servico);
            params.set("valor", event.data.valor);
            window.parent.location.search = params.toString();
        }
    });
    </script>
    """,
    height=0,
)

# Detecta clique e faz scroll
params = st.experimental_get_query_params()
if "servico" in params:
    st.session_state["servico"] = params["servico"][0]
    st.session_state["valor"] = float(params["valor"][0])
    st.session_state["scroll_to_form"] = True
    st.rerun()

# ==========================
# 2️⃣ Formulário do cliente
# ==========================
st.markdown("<div id='form-anchor'></div>", unsafe_allow_html=True)

if "servico" not in st.session_state:
    st.warning("👈 Escolha um serviço antes de continuar.")
    st.stop()

st.success(f"Serviço selecionado: {st.session_state['servico']} (R$ {st.session_state['valor']},00)")

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
    hora = st.selectbox("Escolha o horário", disponiveis, key="hora_select")
    if st.button("✅ Confirmar agendamento", type="primary"):
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
