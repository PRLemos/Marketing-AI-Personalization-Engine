import streamlit as st
from datetime import datetime
from openai import OpenAI
import pandas as pd
import os
import matplotlib.pyplot as plt

# =====================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================
st.set_page_config(
    page_title="Marketing AI Engine",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 Marketing AI Personalization Engine")
st.markdown("Segmentação Inteligente + IA Generativa + Análise de Engajamento")

# =====================================
# CARREGAR API KEY (Seguro)
# =====================================
def carregar_api_key():
    # 1️⃣ tenta pegar da variável de ambiente (Streamlit Cloud)
    api_key = os.getenv("OPENAI_API_KEY")

    # 2️⃣ se não existir, tenta pegar do arquivo local
    if not api_key:
        try:
            with open("api_key.txt", "r") as file:
                api_key = file.read().strip()
        except FileNotFoundError:
            return None

    return api_key

api_key = carregar_api_key()

# =====================================
# INPUTS EM COLUNAS
# =====================================
col1, col2 = st.columns(2)

with col1:
    nome = st.text_input("Nome do Cliente")

    perfil = st.selectbox(
        "Perfil do Cliente",
        [
            "Cliente Inativo",
            "Cliente Recorrente",
            "Cliente Caçador de Brindes",
            "Cliente Moderado"
        ]
    )

with col2:
    ultima_compra = st.date_input("Data da Última Compra")
    gosta_brindes = st.checkbox("Gosta de Brindes?")

# =====================================
# FUNÇÃO DE SCORE
# =====================================
def calcular_score(perfil, dias_sem_comprar):

    base_scores = {
        "Cliente Inativo": 30,
        "Cliente Moderado": 60,
        "Cliente Caçador de Brindes": 75,
        "Cliente Recorrente": 90
    }

    base = base_scores.get(perfil, 50)

    # penaliza até 30 pontos baseado nos dias sem compra
    penalidade = min(dias_sem_comprar, 30)

    score_final = base - penalidade

    return max(score_final, 0)

# =====================================
# FUNÇÃO DE GERAÇÃO DE MENSAGEM (IA)
# =====================================
def gerar_mensagem(nome, perfil, dias_sem_comprar, gosta_brindes):

    client = OpenAI(api_key=api_key)

    prompt = f"""
    Crie uma mensagem de marketing personalizada (máx 150 caracteres).
    
    Nome: {nome}
    Perfil: {perfil}
    Dias sem comprar: {dias_sem_comprar}
    Gosta de brindes: {gosta_brindes}
    
    Seja estratégico, persuasivo e profissional.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Você é especialista em marketing estratégico."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )

    return response.choices[0].message.content.strip()

# =====================================
# SESSION STATE PARA HISTÓRICO
# =====================================
if "historico" not in st.session_state:
    st.session_state.historico = []

# =====================================
# BOTÃO PRINCIPAL
# =====================================
if st.button("✨ Gerar Mensagem Personalizada"):

    if not api_key:
        st.error("API Key não encontrada. Adicione no api_key.txt ou nas Secrets.")
    elif not nome:
        st.warning("Digite o nome do cliente.")
    else:
        dias_sem_comprar = (datetime.now().date() - ultima_compra).days
        score = calcular_score(perfil, dias_sem_comprar)

        with st.spinner("Gerando mensagem com IA..."):
            mensagem = gerar_mensagem(
                nome,
                perfil,
                dias_sem_comprar,
                gosta_brindes
            )

        # Mostrar métricas
        m1, m2 = st.columns(2)
        m1.metric("📊 Dias sem compra", dias_sem_comprar)
        m2.metric("📈 Score de Engajamento", score)

        st.success("Mensagem gerada com sucesso!")
        st.info(mensagem)

        # Salvar no histórico
        st.session_state.historico.append({
            "Nome": nome,
            "Perfil": perfil,
            "Dias sem compra": dias_sem_comprar,
            "Score": score,
            "Mensagem": mensagem
        })

# =====================================
# HISTÓRICO + ANÁLISE + DOWNLOAD
# =====================================
if st.session_state.historico:

    st.markdown("---")
    st.markdown("## 🧠 Histórico de Mensagens")

    df_hist = pd.DataFrame(st.session_state.historico)

    st.dataframe(df_hist, use_container_width=True)

    # ===============================
    # 📊 ANÁLISE DE ENGAGEMENT
    # ===============================
    st.markdown("## 📊 Análise de Engajamento")

    media_score = df_hist["Score"].mean()
    st.metric("📈 Média Geral de Engajamento", round(media_score, 2))

    fig, ax = plt.subplots()
    ax.bar(df_hist["Nome"], df_hist["Score"])
    ax.set_xlabel("Cliente")
    ax.set_ylabel("Score de Engajamento")
    ax.set_title("Distribuição de Score por Cliente")

    st.pyplot(fig)

    # ===============================
    # 📥 DOWNLOAD EXCEL
    # ===============================
    excel_file = "historico_mensagens.xlsx"
    df_hist.to_excel(excel_file, index=False)

    with open(excel_file, "rb") as f:
        st.download_button(
            label="📥 Download Excel",
            data=f,
            file_name="historico_mensagens.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )