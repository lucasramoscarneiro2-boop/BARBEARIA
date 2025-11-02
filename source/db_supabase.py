import psycopg2
import psycopg2.extras
import streamlit as st
import pandas as pd

# ==========================================
# 🔗 CONEXÃO COM O BANCO (SUPABASE POSTGRES)
# ==========================================
def get_conn():
    """Retorna uma conexão segura ao banco Postgres (usando .streamlit/secrets.toml)."""
    creds = st.secrets["postgres"]
    conn = psycopg2.connect(
        host=creds["host"],
        port=creds["port"],
        database=creds["database"],
        user=creds["user"],
        password=creds["password"],
        sslmode=creds.get("sslmode", "require")
    )
    return conn


# ==========================================
# 📅 LISTAR AGENDAMENTOS POR DATA
# ==========================================
def listar_agendamentos_por_data(data_str: str):
    """Retorna todos os agendamentos (incluindo bloqueados) de uma data específica."""
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("""
        SELECT 
            nome, telefone, data, hora, servico, valor, 
            COALESCE(bloqueado, false) AS bloqueado
        FROM agendamentos
        WHERE data = %s
        ORDER BY hora;
    """, (data_str,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=["nome", "telefone", "data", "hora", "servico", "valor", "bloqueado"]).to_dict(orient="records")


# ==========================================
# ✂️ INSERIR NOVO AGENDAMENTO
# ==========================================
def inserir_agendamento(nome, telefone, data, hora, servico, valor):
    """Insere um novo agendamento normal."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO agendamentos (nome, telefone, data, hora, servico, valor, bloqueado)
        VALUES (%s, %s, %s, %s, %s, %s, false);
    """, (nome, telefone, data, hora, servico, valor))
    conn.commit()
    cur.close()
    conn.close()


# ==========================================
# 🚫 BLOQUEAR HORÁRIO
# ==========================================
def bloquear_horario(data, hora, motivo):
    """Cria um agendamento marcado como bloqueado (sem cliente)."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO agendamentos (data, hora, servico, bloqueado)
        VALUES (%s, %s, %s, true);
    """, (data, hora, motivo))
    conn.commit()
    cur.close()
    conn.close()


# ==========================================
# ❌ CANCELAR AGENDAMENTO OU BLOQUEIO
# ==========================================
def cancelar_agendamento(data_str: str, hora: str):
    """
    Cancela (remove) um agendamento existente com base na data e hora.
    Assim, o horário volta a ficar disponível automaticamente.
    """
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM agendamentos WHERE data = %s AND hora = %s;",
            (data_str, hora)
        )
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception as e:
        print("Erro ao cancelar agendamento:", e)
        return False


# ==========================================
# 🔐 AUTENTICAÇÃO DO BARBEIRO
# ==========================================
def autenticar(usuario: str, senha: str):
    """Verifica se usuário e senha correspondem a um login válido."""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM usuarios WHERE usuario = %s AND senha = %s;",
        (usuario, senha)
    )
    ok = cur.fetchone()
    cur.close()
    conn.close()
    return ok is not None
