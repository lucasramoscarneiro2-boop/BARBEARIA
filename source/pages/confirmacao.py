import streamlit as st

st.set_page_config(page_title="Confirmação - Barbearia Cardoso", layout="centered", page_icon="💈")

st.markdown("""
<style>
body, .stApp {
    background-color: #0b1a3a;
    font-family: 'Poppins', sans-serif;
    color: #fff !important;
    text-align: center;
}
.container {
    margin-top: 3rem;
    padding: 2rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #1b263b, #14213d);
    box-shadow: 0 0 25px rgba(0,0,0,0.5);
}
h1 {
    color: #00b4d8;
    margin-bottom: 1rem;
    font-size: 2rem;
}
h2 {
    color: #ffffff;
    margin-bottom: 1.2rem;
}
p {
    color: #dcdcdc;
    font-size: 1.1rem;
    line-height: 1.6;
}
.detalhes {
    background-color: rgba(0, 180, 216, 0.1);
    border: 1px solid #00b4d8;
    padding: 1rem;
    border-radius: 12px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

st.balloons()

st.markdown("<div class='container'>", unsafe_allow_html=True)
st.markdown("<h1>✅ Agendamento Confirmado!</h1>", unsafe_allow_html=True)
st.markdown("<p>Seu horário foi reservado com sucesso 💈</p>", unsafe_allow_html=True)

if "cliente" in st.session_state:
    nome = st.session_state.get("cliente", "")
    servico = st.session_state.get("servico", "")
    data = st.session_state.get("data", "")
    hora = st.session_state.get("hora", "")
    valor = st.session_state.get("valor", "")

    st.markdown(f"""
    <div class='detalhes'>
        <h2>Resumo do seu agendamento</h2>
        <p><strong>👤 Cliente:</strong> {nome}</p>
        <p><strong>💇‍♂️ Serviço:</strong> {servico}</p>
        <p><strong>🗓 Data:</strong> {data}</p>
        <p><strong>⏰ Horário:</strong> {hora}</p>
        <p><strong>💰 Valor:</strong> R$ {valor},00</p>
    </div>
    <p>Agradecemos por escolher a <strong>Barbearia Cardoso</strong>.<br>
    Estamos prontos para te atender com excelência e estilo!</p>
    """, unsafe_allow_html=True)

else:
    st.error("Nenhum agendamento encontrado.")

if st.button("⬅️ Voltar para o início"):
    st.switch_page("agendamento.py")

st.markdown("</div>", unsafe_allow_html=True)
