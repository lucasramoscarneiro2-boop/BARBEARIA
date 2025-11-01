import pg8000
import streamlit as st
import pandas as pd
import ssl

def get_conn():
    """Cria conexão com o Supabase Postgres (usando Pooler)."""
    creds = st.secrets["postgres"]

    # Cria contexto SSL (necessário no Streamlit Cloud)
    ssl_context = ssl.create_default_context()

    conn = pg8000.connect(
        host=creds["host"],
        port=int(creds.get("port", 5432)),
        database=creds["database"],
        user=creds["user"],
        password=creds["password"],
        ssl_context=ssl_context,   # ✅ Corrigido (antes estava True)
    )
    return conn


def listar_agendamentos_por_data(data_str: str):
    """Lista todos os agendamentos de uma data específica."""
    conn = get_conn()
    cursor = conn.cursor()
    query = """
        SELECT id, nome, telefone, data, hora, servico, valor, bloqueado
        FROM agendamentos
        WHERE data = %s
        ORDER BY hora;
    """
    cursor.execute(query, (data_str,))
    rows = cursor.fetchall()
    colunas = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(rows, columns=colunas)
    cursor.close()
    conn.close()
    return df.to_dict(orient="records")


def inserir_agendamento(nome, telefone, data, hora, servico, valor):
    """Insere um novo agendamento no Supabase."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO agendamentos (nome, telefone, data, hora, servico, valor, bloqueado)
            VALUES (%s, %s, %s, %s, %s, %s, false)
        """, (nome, telefone, data, hora, servico, valor))
        conn.commit()
    conn.close()


def bloquear_horario(data, hora, motivo):
    """Bloqueia um horário específico (impede novos agendamentos)."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO agendamentos (data, hora, servico, bloqueado)
            VALUES (%s, %s, %s, true)
        """, (data, hora, motivo))
        conn.commit()
    conn.close()


def cancelar_agendamento(id_agendamento):
    """Cancela (remove) um agendamento existente."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM agendamentos WHERE id = %s;", (id_agendamento,))
        conn.commit()
    conn.close()


def autenticar(usuario, senha):
    """Valida login de barbeiro (tabela usuarios)."""
    conn = get_conn()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT 1 FROM usuarios
            WHERE usuario = %s AND senha = %s;
        """, (usuario, senha))
        ok = cur.fetchone()
    conn.close()
    return ok is not None
