import pg8000.native
import streamlit as st
import pandas as pd

def get_conn():
    creds = st.secrets["postgres"]
    conn = pg8000.native.Connection(
        user=creds["user"],
        password=creds["password"],
        host=creds["host"],
        port=int(creds.get("port", 5432)),
        database=creds["database"],
        ssl=True
    )
    return conn

def listar_agendamentos_por_data(data_str: str):
    conn = get_conn()
    rows = conn.run(
        "SELECT nome, telefone, data, hora, servico, valor FROM agendamentos WHERE data = :data",
        data=data_str
    )
    colunas = ["nome", "telefone", "data", "hora", "servico", "valor"]
    df = pd.DataFrame(rows, columns=colunas)
    conn.close()
    return df.to_dict(orient="records")

def inserir_agendamento(nome, telefone, data, hora, servico, valor):
    conn = get_conn()
    conn.run("""
        INSERT INTO agendamentos (nome, telefone, data, hora, servico, valor)
        VALUES (:nome, :telefone, :data, :hora, :servico, :valor)
    """, nome=nome, telefone=telefone, data=data, hora=hora, servico=servico, valor=valor)
    conn.close()

def bloquear_horario(data, hora, motivo):
    conn = get_conn()
    conn.run("""
        INSERT INTO agendamentos (data, hora, servico, bloqueado)
        VALUES (:data, :hora, :motivo, true)
    """, data=data, hora=hora, motivo=motivo)
    conn.close()

def cancelar_agendamento(id_agendamento):
    conn = get_conn()
    conn.run("DELETE FROM agendamentos WHERE id = :id", id=id_agendamento)
    conn.close()

def autenticar(usuario, senha):
    conn = get_conn()
    res = conn.run("SELECT 1 FROM usuarios WHERE usuario = :u AND senha = :s", u=usuario, s=senha)
    conn.close()
    return len(res) > 0
