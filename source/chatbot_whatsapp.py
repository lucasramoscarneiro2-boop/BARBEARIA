import time
import psycopg2
from psycopg2.extras import RealDictCursor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from datetime import datetime
import streamlit as st

# ==========================
# Conexão com Supabase (PostgreSQL)
# ==========================
cfg = st.secrets["postgres"]

def get_conn():
    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        database=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
        sslmode=cfg.get("sslmode", "require")
    )

# ==========================
# Configuração Selenium
# ==========================
options = webdriver.ChromeOptions()
options.add_argument("--user-data-dir=C:\\whatsapp_session")  # mantém sessão logada
options.add_argument("--start-maximized")

driver = webdriver.Chrome(options=options)
driver.get("https://web.whatsapp.com")

print("📱 Aguarde o login no WhatsApp Web...")
while True:
    try:
        driver.find_element(By.XPATH, "//canvas[@aria-label='Imagem do código QR']")
        time.sleep(2)
    except:
        print("✅ Login detectado com sucesso!")
        break
    time.sleep(2)

# ==========================
# Função para enviar mensagens
# ==========================
def enviar_mensagem(numero, msg):
    """Envia mensagem via WhatsApp Web"""
    try:
        numero_formatado = numero.replace(" ", "").replace("-", "")
        if not numero_formatado.startswith("55"):
            numero_formatado = "55" + numero_formatado

        link = f"https://web.whatsapp.com/send?phone={numero_formatado}&text={msg}"
        driver.get(link)
        print(f"➡️ Enviando mensagem para {numero_formatado} ...")

        wait = WebDriverWait(driver, 120)
        message_box = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='textbox']")))

        # Aguarda botão de envio
        botao = None
        for seletor in [
            "//button[@aria-label='Enviar']",
            "//span[@data-icon='send']",
            "//div[@aria-label='Enviar mensagem']"
        ]:
            try:
                botao = wait.until(EC.element_to_be_clickable((By.XPATH, seletor)))
                if botao:
                    break
            except:
                continue

        # Envia mensagem
        if botao:
            botao.click()
            print("✅ Mensagem enviada (via botão).")
        else:
            message_box.send_keys(Keys.RETURN)
            print("✅ Mensagem enviada (via ENTER).")

        time.sleep(3)
        return True

    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)
        return False

# ==========================
# Loop principal
# ==========================
print("\n🚀 Robô iniciado — monitorando novos agendamentos no Supabase...\n")

while True:
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Busca agendamentos sem mensagem enviada
        cur.execute("""
            SELECT id, nome, telefone, data, hora, servico
            FROM agendamentos
            WHERE (mensagem_enviada IS DISTINCT FROM TRUE)
              AND (bloqueado IS DISTINCT FROM TRUE)
            ORDER BY criado_em ASC
        """)
        agendamentos = cur.fetchall()

        for ag in agendamentos:
            data_br = ag["data"]
            hora = ag["hora"]
            msg = (
                f"💈 Olá, {ag['nome']}!%0A"
                f"Seu horário na *Barbearia Cardoso* está confirmado para "
                f"{data_br} às {hora}.%0A"
                f"✂️ Serviço: {ag['servico']}%0A%0AAté logo! 💇‍♂️"
            )

            enviado = enviar_mensagem(ag["telefone"], msg)

            if enviado:
                cur.execute(
                    "UPDATE agendamentos SET mensagem_enviada = TRUE WHERE id = %s",
                    (ag["id"],)
                )
                conn.commit()

        cur.close()
        conn.close()

    except psycopg2.OperationalError:
        print("⚠️ Conexão perdida com o Supabase — tentando reconectar em 10s...")
        time.sleep(10)
        continue

    except Exception as e:
        print("⚠️ Erro geral:", e)

    # Aguarda antes de verificar novamente
    time.sleep(30)
