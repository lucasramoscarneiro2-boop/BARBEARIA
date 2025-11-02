import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime
from pathlib import Path
import base64
from db_supabase import inserir_agendamento, listar_agendamentos_por_data

# ==========================
# CONFIGURAÇÃO GERAL
# ==========================
st.set_page_config(page_title="Agendamento Barbearia", layout="centered", page_icon="💈")

# Caminho base das imagens (mantendo estrutura atual)
REPO_ROOT = Path(__file__).resolve().parents[1]
IMAGES_DIR = REPO_ROOT / "imagens"

# ==========================
# FUNÇÕES
# ==========================
def horarios_disponiveis(data_str: str):
    agendamentos = listar_agendamentos_por_data(data_str)
    ocupados = {a.get("hora") for a in agendamentos if not a.get("bloqueado")}
    bloqueados = {a.get("hora") for a in agendamentos if a.get("bloqueado")}
    todos = [f"{h:02d}:00" for h in range(9, 19)]
    return [h for h in todos if h not in ocupados and h not in bloqueados]

def image_to_base64(path: Path):
    """Converte imagem local em base64 para exibir inline no HTML."""
    if not path.exists():
        return "https://via.placeholder.com/600x400?text=Imagem+indispon%C3%ADvel"
    try:
        with open(path, "rb") as img_file:
            b64 = base64.b64encode(img_file.read()).decode()
            ext = path.suffix.replace(".", "")
            return f"data:image/{ext};base64,{b64}"
    except Exception:
        return "https://via.placeholder.com/600x400?text=Erro+ao+carregar"

def scroll_to_anchor(anchor_id: str = "form-anchor"):
    components.html(
        f"""
        <script>
        function go() {{
          const el = window.parent.document.querySelector("#{anchor_id}");
          if (el) el.scrollIntoView({{behavior:'smooth', block:'start'}});
          else setTimeout(go,120);
        }}
        setTimeout(go,80);
        </script>
        """,
        height=0,
    )

if st.session_state.get("scroll_to_form"):
    scroll_to_anchor("form-anchor")
    st.session_state["scroll_to_form"] = False

# ==========================
# CSS
# ==========================
st.markdown("""
<style>
body, .stApp {
  background-color: #f5f6fa;
  font-family: 'Poppins', sans-serif;
  color: #222;
}
h1, h2, h3, h4 { text-align: center; color: #111; }
h1 { font-size: 1.8rem !important; margin-bottom: 0.8rem; }

.servico-card {
  background: #fff;
  border-radius: 18px;
  padding: 1rem;
  margin-bottom: 1.3rem;
  text-align: center;
  box-shadow: 0 3px 10px rgba(0,0,0,.08);
  transition: all 0.25s ease;
  cursor: pointer;
  border: 2px solid transparent;
}
.servico-card:hover {
  transform: scale(1.03);
  border-color: #007bff;
}
.servico-img {
  border-radius: 14px;
  width: 100%;
  height: auto;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0,0,0,.12);
}
.servico-nome {
  margin-top: .6rem;
  font-weight: 600;
  color: #111;
}
.servico-preco {
  color: #007bff;
  font-weight: 500;
}
@media (max-width: 768px) {
  .block-container { padding: .5rem 1rem !important; }
  h1 { font-size: 1.4rem !important; }
}
</style>
""", unsafe_allow_html=True)

# ==========================
# CABEÇALHO
# ==========================
st.title("💈 Barbearia Cardoso 💈")
st.markdown("<p style='text-align:center;'>Agende seu horário rapidamente no seu celular!</p>", unsafe_allow_html=True)

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
        img_base64 = image_to_base64(IMAGES_DIR / img_name)
        html = f"""
        <div class="servico-card" onclick="window.parent.postMessage({{'servico':'{nome}','valor':{valor}}}, '*')">
            <img class="servico-img" src="{img_base64}" alt="{nome}">
            <div class="servico-nome">{nome}</div>
            <div class="servico-preco">R$ {valor},00</div>
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)

components.html("""
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
""", height=0)

params = st.experimental_get_query_params()
if "servico" in params:
    st.session_state["servico"] = params["servico"][0]
    st.session_state["valor"] = float(params["valor"][0])
    st.session_state["scroll_to_form"] = True
    st.rerun()

# ==========================
# 2️⃣ Dados do cliente
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
                nome, telefone, data_str, hora,
                st.session_state["servico"],
                st.session_state["valor"]
            )
            st.success(f"✅ Agendamento confirmado para {data_str} às {hora}!")
            st.balloons()
