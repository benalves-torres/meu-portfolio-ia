import streamlit as st
from groq import Groq

# 1. BASE DE CONHECIMENTO (Sua Planilha traduzida para a IA)
MATRIZ_CONHECIMENTO = """
VOCÊ É UM CPO AVALIADOR. USE ESTA MATRIZ PARA A ENTREVISTA:

PILAR: VISÃO (Estratégica e Sistêmica)
- Objetivo: Conectar produto ao negócio e entender o ecossistema.
- Palavras de Ouro: North Star Metric, Alinhamento de OKRs, Trade-off, Visão de Futuro.
- Red Flags: "Fiz porque pediram", foco apenas na tarefa (output) sem saber o porquê.

PILAR: IMPACTO (Discovery e Business Mindset)
- Objetivo: Mitigar riscos e mover alavancas financeiras (LTV, CAC, Churn).
- Palavras de Ouro: Teste de Hipótese, Discovery Contínuo, ROI, Unidades Econômicas.
- Red Flags: Não medir resultados, pular o Discovery, "achismo".

PILAR: CONEXÃO (Stakeholders e Liderança)
- Objetivo: Influência, negociação e colaboração cross-functional.
- Palavras de Ouro: Matriz de Stakeholders, Negociação Win-Win, Storytelling, Gestão de Expectativas.
- Red Flags: Conflitos não resolvidos, falta de comunicação com engenharia.

PILAR: TECH & PROCESS (Delivery e Agilidade)
- Objetivo: Qualidade da entrega e viabilidade técnica.
- Palavras de Ouro: Débito Técnico, Escalabilidade, API-First, Lead Time, Ciclo de Entrega.

NÍVEIS DE MATURIDADE (DREYFUS):
1. Novato: Segue regras, precisa de supervisão.
2. Intermediário: Entende processos, mas foca no operacional.
3. Competente: Independente, entende contexto e métricas.
4. Proficiente (Sênior): Reconhece padrões, antecipa problemas, foca em estratégia.
5. Especialista (GPM/Head): Visão holística, molda a cultura e estratégia organizacional.
"""

# 2. Configuração Visual
st.set_page_config(page_title="Portfolio Builder AI", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #F8F9FA; border-right: 1px solid #E5E7EB; }
    .stButton>button { background-color: #111827; color: white; border-radius: 8px; border: none; }
    .stChatInput { border-radius: 12px !important; }
    </style>
    """, unsafe_allow_html=True)

# 3. Inicialização Groq
# Certifique-se de ter GROQ_API_KEY nos Secrets do Streamlit
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Erro: API Key não encontrada. Configure nos Secrets do Streamlit.")

# --- ESTADO DA SESSÃO ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pilar_index" not in st.session_state:
    st.session_state.pilar_index = 0
if "respostas_completas" not in st.session_state:
    st.session_state.respostas_completas = []
if "onboarding" not in st.session_state:
    st.session_state.onboarding = False

pilares = ["Visão", "Impacto", "Conexão", "Tech & Processos"]

# --- SIDEBAR (ONBOARDING) ---
with st.sidebar:
    st.title("🎯 Portfolio AI")
    st.write("Baseado na Matriz de Produto iFood")
    
    nome = st.text_input("Nome")
    email = st.text_input("E-mail")
    nivel_atual = st.selectbox("Senioridade Atual", ["APM", "PM I", "PM II", "PM III", "Senior PM", "GPM"])
    nivel_alvo = st.selectbox("Senioridade Target", ["PM II", "Senior PM", "GPM", "Staff PM"])
    
    if st.button("🚀 Iniciar Entrevista"):
        if nome and email:
            st.session_state.onboarding = True
            st.session_state.messages = []
            st.session_state.pilar_index = 0
            st.rerun()

# --- FLUXO DE CONVERSA ---
if not st.session_state.onboarding:
    st.write("# Comece sua jornada")
    st.info("Preencha os dados na barra lateral para gerar um portfólio de alto impacto.")
else:
    # Mensagem de Boas-vindas
    if not st.session_state.messages:
        msg_inicial = f"Olá {nome}! Sou seu avaliador. Vamos estruturar seu portfólio para **{nivel_alvo}**. \n\nComeçaremos por **{pilares[0]}**. Me fale sobre um projeto onde você influenciou a estratégia ou os OKRs do seu time."
        st.session_state.messages.append({"role": "assistant", "content": msg_inicial})

    # Mostrar Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input do Usuário
    if prompt := st.chat_input("Descreva sua experiência..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Lógica da IA para avaliar e perguntar o próximo pilar
        with st.spinner("Analisando senioridade..."):
            pilar_atual = pilares[st.session_state.pilar_index]
            
            # Chamada para a IA decidir se aprofunda ou segue
            check_prompt = f"""
            {MATRIZ_CONHECIMENTO}
            Candidato: {nome} (Alvo: {nivel_alvo})
            Pilar atual: {pilar_atual}
            Resposta do candidato: {prompt}
            
            Tarefa: 
            1. Se a resposta for rasa para um {nivel_alvo}, peça um detalhe específico (Ex: métricas, técnica de discovery).
            2. Se a resposta demonstrar maturidade, valide o ponto positivo citando um conceito da matriz e chame o próximo pilar: {pilares[st.session_state.pilar_index+1] if st.session_state.pilar_index < 3 else 'Conclusão'}.
            """
            
            response = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "system", "content": check_prompt}]
            )
            
            ai_msg = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_msg})
            
            # Se a IA deu o OK para seguir (lógica simples de incremento)
            if "próximo pilar" in ai_msg.lower() or "vamos para" in ai_msg.lower():
                st.session_state.respostas_completas.append(f"{pilar_atual}: {prompt}")
                st.session_state.pilar_index += 1
            
            st.rerun()

    # Se terminar os pilares
    if st.session_state.pilar_index >= len(pilares):
        st.success("Entrevista Finalizada!")
        if st.button("✨ Gerar Portfólio Final"):
            # Prompt Final de Geração de Portfólio
            prompt_portfolio = f"""
            {MATRIZ_CONHECIMENTO}
            Crie um portfólio para {nome}, que quer ser {nivel_alvo}.
            Use as respostas abaixo para criar bullets em formato STAR (Situação, Tarefa, Ação, Resultado).
            Enfatize as 'Palavras de Ouro' que o candidato usou.
            
            Respostas: {st.session_state.respostas_completas}
            """
            
            res = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "system", "content": prompt_portfolio}]
            )
            
            final_portfolio = res.choices[0].message.content
            st.markdown("---")
            st.header("Seu Portfólio de Produto")
            st.markdown(final_portfolio)
            st.download_button("Baixar Portfólio", final_portfolio)
