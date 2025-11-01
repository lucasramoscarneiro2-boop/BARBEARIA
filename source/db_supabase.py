import psycopg2
import psycopg2.extras
import streamlit as st

def get_conn():
    cfg = st.secrets["postgres"]
    return psycopg2.connect(
        host=cfg["host"],
        port=cfg["port"],
        database=cfg["database"],
        user=cfg["user"],
        password=cfg["password"],
        sslmode=cfg.get("sslmode", "require")
    )

def listar_agendamentos_por_data(data_str):
    conn = get_conn()
    with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
        cur.execute("SELECT * FROM agendamentos WHERE data = %s ORDER BY hora", (data_str,))
        rows = cur.fetchall()
    conn.close()
    return rows

def inserir_agendamento(nome, telefone, data, hora, servico, valor):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO agendamentos (nome, telefone, data, hora, servico, valor)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (nome, telefone, data, hora, servico, valor))
        conn.commit()
    conn.close()

def bloquear_horario(data, hora, motivo):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO agendamentos (data, hora, servico, bloqueado)
            VALUES (%s, %s, %s, true)
        """, (data, hora, motivo))
        conn.commit()
    conn.close()

def cancelar_agendamento(id_agendamento):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM agendamentos WHERE id = %s", (id_agendamento,))
        conn.commit()
    conn.close()

def autenticar(usuario, senha):
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM usuarios WHERE usuario = %s AND senha = %s", (usuario, senha))
        ok = cur.fetchone()
    conn.close()
    return ok is not None
