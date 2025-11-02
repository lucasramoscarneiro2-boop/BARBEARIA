
import psycopg2
import streamlit as st
import pandas as pd

def get_conn():
    creds = st.secrets["postgres"]
    conn = psycopg2.connect(
        host=creds["host"],
        port=creds["port"],
        dbname=creds["database"],
        user=creds["user"],
        password=creds["password"],
        sslmode="require"
    )
    return conn


def listar_agendamentos_por_data(data_str: str):
    conn = get_conn()
    cursor = conn.cursor()
    query = """
        SELECT nome, telefone, data, hora, servico, valor, bloqueado
        FROM agendamentos
        WHERE data = %s;
    """
    cursor.execute(query, (data_str,))
    rows = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colunas)
    cursor.close()
    conn.close()
    return df.to_dict(orient="records")


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
