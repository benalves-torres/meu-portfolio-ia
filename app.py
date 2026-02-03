import streamlit as st
from groq import Groq

# Configuração da Página (Minimalismo)
st.set_page_config(page_title="Product Portfolio Builder", layout="centered")

# CSS para garantir o visual limpo (Fundo branco, texto escuro)
st.markdown("""
    <style>
    .stApp { background-color: white; color: #1E1E1E; }
    [data-testid="stSidebar"] { background-color: #F8F9FA; }
    </style>
    """, unsafe_allow_html=True)

# Inicialização do Cliente Groq
# Certifique-se de configurar sua chave de API nas Secrets do Streamlit ou ambiente
client = Groq(api_key="SUA_CHAVE_AQUI")

# --- ESTADO DA SESSÃO ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pilar_index" not in st.session_state:
    st.session_state.pilar_index = 0
if "respostas" not in st.session_state:
    st.session_state.respostas = {}

pilares = ["Visão", "Impacto", "Conexão", "Tech", "Processos"]

# --- BARRA LATERAL ---
with st.sidebar:
    st.title("Configurações")
    nivel_alvo = st.selectbox(
        "Nível Desejado",
        ["Junior", "Pleno", "Senior", "Staff PM", "GPM"]
    )
    if st.button("Resetar Entrevista"):
        st.session_state.messages = []
        st.session_state.pilar_index = 0
        st.session_state.respostas = {}
        st.rerun()

st.title("Portfolio Interviewer")
st.caption(f"Focando no nível: **{nivel_alvo}**")

# --- LÓGICA DE ENTREVISTA ---

# Mensagem inicial do assistente
if not st.session_state.messages:
    boas_vindas = f"Olá! Vamos construir seu portfólio para o nível **{nivel_alvo}**. Começaremos pelo pilar: **{pilares[0]}**. Me conte sobre um projeto onde você definiu a direção do produto."
    st.session_state.messages.append({"role": "assistant", "content": boas_vindas})

# Exibir histórico do chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Entrada do Usuário
if prompt := st.chat_input("Sua resposta..."):
    # Adiciona resposta do usuário
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Salva a resposta no pilar atual
    atual = pilares[st.session_state.pilar_index]
    st.session_state.respostas[atual] = prompt
    st.session_state.pilar_index += 1

    # Próximo passo
    if st.session_state.pilar_index < len(pilares):
        proximo = pilares[st.session_state.pilar_index]
        pergunta_proximo = f"Ótimo. Agora sobre **{proximo}**, o que você pode compartilhar?"
        st.session_state.messages.append({"role": "assistant", "content": pergunta_proximo})
        st.rerun()
    else:
        # GERAR PORTFÓLIO FINAL
        with st.spinner("Analisando sua experiência e gerando portfólio..."):
            
            contexto_usuario = "\n".join([f"{k}: {v}" for k, v in st.session_state.respostas.items()])
            
            prompt_final = f"""
            Com base nas respostas abaixo de um Product Manager que almeja o nível {nivel_alvo}, 
            crie um 'Portfólio de Produto' profissional em Markdown.
            Use bullet points de alto impacto (formato Situação, Ação, Resultado).
            No final, adicione uma seção chamada 'Sugestão de Senioridade' avaliando se as respostas condizem com o nível {nivel_alvo}.
            
            Respostas:
            {contexto_usuario}
            """

            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "user", "content": prompt_final}],
                temperature=0.7,
            )
            
            portfolio_gerado = completion.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": "Entrevista concluída! Veja seu portfólio abaixo."})
            
            st.divider()
            st.header("✨ Portfólio Gerado")
            st.markdown(portfolio_gerado)
