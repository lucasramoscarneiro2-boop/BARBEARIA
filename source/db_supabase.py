from supabase import create_client
import streamlit as st
import pandas as pd

def get_client():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

def listar_agendamentos_por_data(data_str):
    client = get_client()
    res = client.table("agendamentos").select("*").eq("data", data_str).execute()
    return res.data or []

def inserir_agendamento(nome, telefone, data, hora, servico, valor):
    client = get_client()
    client.table("agendamentos").insert({
        "nome": nome,
        "telefone": telefone,
        "data": data,
        "hora": hora,
        "servico": servico,
        "valor": valor
    }).execute()

def bloquear_horario(data, hora, motivo):
    client = get_client()
    client.table("agendamentos").insert({
        "data": data,
        "hora": hora,
        "servico": motivo,
        "bloqueado": True
    }).execute()

def cancelar_agendamento(id_agendamento):
    client = get_client()
    client.table("agendamentos").delete().eq("id", id_agendamento).execute()

def autenticar(usuario, senha):
    client = get_client()
    res = client.table("usuarios").select("*").eq("usuario", usuario).eq("senha", senha).execute()
    return len(res.data) > 0
