import psycopg2
import psycopg2.extras
import streamlit as st
import pandas as pd

def get_conn():
    creds = st.secrets["postgres"]
    conn = psycopg2.connect(
        host=creds["host"],
        port=creds["port"],
        database=creds["database"],
        user=creds["user"],
        password=creds["password"],
        sslmode=creds["sslmode"]
    )
    return conn


def listar_agendamentos_por_data(data_str):
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT nome, telefone, data, hora, servico, valor FROM agendamentos WHERE data = %s;", (data_str,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=["nome", "telefone", "data", "hora", "servico", "valor"]).to_dict(orient="records")


def inserir_agendamento(nome, telefone, data, hora, servico, valor):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO agendamentos (nome, telefone, data, hora, servico, valor)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (nome, telefone, data, hora, servico, valor))
    conn.commit()
    cur.close()
    conn.close()


def bloquear_horario(data, hora, motivo):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO agendamentos (data, hora, servico, bloqueado)
        VALUES (%s, %s, %s, true)
    """, (data, hora, motivo))
    conn.commit()
    cur.close()
    conn.close()


def cancelar_agendamento(id_agendamento):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM agendamentos WHERE id = %s", (id_agendamento,))
    conn.commit()
    cur.close()
    conn.close()


def autenticar(usuario, senha):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM usuarios WHERE usuario = %s AND senha = %s", (usuario, senha))
    ok = cur.fetchone()
    cur.close()
    conn.close()
    return ok is not None
