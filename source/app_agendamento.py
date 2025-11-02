import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from pathlib import Path
from db_supabase import inserir_agendamento, listar_agendamentos_por_data

# ==========================
# CONFIGURAÇÃO GERAL
# ==========================
st.set_page_config(page_title="Agendamento Barbearia", layout="centered", page_icon="💈")

# Caminhos robustos
REPO_ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = REPO_ROOT / "imagens"

# --- Scroll helper (funciona no Streamlit Cloud e mobile) ---
def scroll_to_anchor(anchor_id: str = "form-anchor"):
    components.html(
        f"""
        <script>
        function go() {{
          const el = window.parent.document.querySelector("#{anchor_id}");
          if (el) {{
            el.scrollIntoView({{behavior: 'smooth', block: 'start'}});
          }} else {{
            setTimeout(go, 120);
          }}
        }}
        setTimeout(go, 80);
        </script>
        """,
        height=0,
    )

# Se veio de um clique de serviço, aciona scroll no início
if st.session_state.get("scroll_to_form"):
    scroll_to_anchor("form-anchor")
    st.session_state["scroll_to_form"] = False

# ==========================
# CSS E TÍTULOS
# ==========================
st.markdown("""
<style>
body, .stApp { background-color: #f5f6fa; font-family: 'Poppins', sans-serif; color: #222; }
h1, h2, h3, h4 { text-align: center; color: #111; }
h1 { font-size: 1.8rem !important; margin-bottom: 0.8rem; }
h2, h3 { font-size: 1.4rem !important; }

.stButton>button {
  width: 100%; border-radius: 12px;
  background: linear-gradient(90deg, #007bff, #00b4d8);
  color: white !important; font-weight: 600;
  padding: 0.7rem 0; border: none; transition: all .3s ease;
}
.stButton>button:hover {
  background: linear-gradient(90deg, #0056b3, #0096c7);
  transform: scale(1.02);
}

.servico-card {
  background: #fff; border-radius: 16px; padding: 1rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 2px 10px rgba(0,0,0,.05);
  text-align: center;
}
.servico-img {
  border-radius: 15px; width: 100%; height: auto;
  box-shadow: 0 4px 12px rgba(0,0,0,.1);
}
.servico-nome { margin-top: .5rem; font-size: 1.1rem; font-weight: 600; color: #222; }
.servico-preco { color: #007bff; font-size: 1rem; margin-bottom: .5rem; }

@media (max-width: 768px) {
  .block-container { padding: .5rem 1rem !important; }
  h1 { font-size: 1.4rem !important; }
  .stButton>button { font-size: 1rem !important; padding: .6rem; }
}

/* === Campos de texto personalizados === */
input, textarea, select {
  color: #000 !important;
  font-weight: 500 !important;
}
::placeholder {
  color: #444 !important;
  opacity: 1 !important;
}
input, textarea {
  background-color: #fff !important;
  border: 1.5px solid #ccc !important;
  border-radius: 10px !important;
  padding: 0.6rem 0.8rem !important;
}
input:focus, textarea:focus {
  border-color: #007bff !important;
  outline: none !important;
  box-shadow: 0 0 6px rgba(0,123,255,0.3);
}
</style>
""", unsafe_allow_html=True)

# ==========================
# CABEÇALHO
# ==========================
st.title("💈 Barbearia Cardoso 💈")
st.markdown("<p style='text-align:center;'>Agende seu horário rapidamente no seu celular!</p>", unsafe_allow_html=True)

# ==========================
# FUNÇÕES
# ==========================
def horarios_disponiveis(data_str: str):
    agendamentos = listar_agendamentos_por_data(data_str)
    ocupados = {a.get("hora") for a in agendamentos if not a.get("bloqueado")}
    bloqueados = {a.get("hora") for a in agendamentos if a.get("bloqueado")}
    todos = [f"{h:02d}:00" for h in range(9, 19)]
    return [h for h in todos if h not in ocupados and h not in bloqueados]

def safe_image(path: Path):
    if path.exists():
        st.image(str(path), use_column_width=True)
    else:
        st.image("https://via.placeholder.com/600x400?text=Imagem+indispon%C3%ADvel", use_column_width=True)

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
    with (col1 if i % 2 == 0 else col2):
        st.markdown('<div class="servico-card">', unsafe_allow_html=True)
        safe_image(IMAGES_DIR / img_name)
        st.markdown(f'<div class="servico-nome">{nome}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="servico-preco">R$ {valor},00</div>', unsafe_allow_html=True)

        if st.button(f"Selecionar {nome}", key=f"btn_{nome}"):
            st.session_state["servico"] = nome
            st.session_state["valor"] = valor
            st.session_state["scroll_to_form"] = True
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ==========================
# 2️⃣ Dados do cliente (âncora + scroll)
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
