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

# 2. Configuração Visual com Paleta Terracota Sóbria
st.set_page_config(page_title="Portfolio AI", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');
    
    /* Variáveis de Cor Terracota */
    :root {
        --terracota-dark: #7E3524;
        --terracota-main: #C96E57;
        --terracota-light: #F2D8D0;
        --bg-sidebar: #2C2C2C; /* Escuro para contraste total */
    }

    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #FFFFFF; 
    }

    /* Sidebar com alto contraste */
    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar);
        color: white;
    }
    
    /* Ajuste de labels e inputs na sidebar para leitura */
    [data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] label {
        color: #F9FAFB !important;
        font-weight: 500;
    }

    /* Estilização dos Inputs */
    .stTextInput input, .stSelectbox div {
        background-color: #3D3D3D !important;
        color: white !important;
        border: 1px solid #555555 !important;
        border-radius: 8px !important;
    }

    /* Botão Principal em Terracota */
    .stButton>button {
        background-color: var(--terracota-main);
        color: white;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        height: 3em;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: var(--terracota-dark);
        border: none;
        color: white;
    }

    /* Chat Bubbles */
    [data-testid="stChatMessage"] {
        background-color: #F9F9F9;
        border-radius: 15px;
        border: 1px solid #F0F0F0;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. Inicialização Groq
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("Erro: API Key não encontrada.")

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

# --- SIDEBAR REFORMULADA ---
with st.sidebar:
    st.markdown("<h2 style='color: white;'>🎯 Portfolio AI</h2>", unsafe_allow_html=True)
    
    # Removido e-mail, mantido apenas Nome conforme solicitado
    nome = st.text_input("Nome")
    
    nivel_atual = st.selectbox("Senioridade Atual", ["APM", "PM I", "PM II", "PM III", "Senior PM", "GPM"])
    nivel_alvo = st.selectbox("Senioridade Target", ["PM II", "Senior PM", "GPM", "Staff PM"])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("🚀 Iniciar Entrevista"):
        if nome:
            st.session_state.onboarding = True
            st.session_state.messages = []
            st.session_state.pilar_index = 0
            st.rerun()
        else:
            st.error("Por favor, insira seu nome.")

# --- FLUXO DE CONVERSA ---
if not st.session_state.onboarding:
    st.markdown(f"""
        <div style='text-align: center; padding-top: 100px;'>
            <h1 style='color: #7E3524;'>Construa um Portfólio de Elite</h1>
            <p style='color: #666;'>Preencha seus dados ao lado para começar sua entrevista com nossa IA.</p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.write(f"### Olá, {nome}! 👋")

    # Início Ativo
    if not st.session_state.messages:
        msg_inicial = f"Tudo pronto para começarmos seu portfólio para **{nivel_alvo}**. \n\nVamos falar sobre **{pilares[0]}**: Me conte sobre um projeto onde você influenciou a estratégia do seu time."
        st.session_state.messages.append({"role": "assistant", "content": msg_inicial})

    # Mostrar Chat
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Processamento de Respostas (Lógica mantida)
    if prompt := st.chat_input("Descreva sua experiência..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.spinner("Analisando..."):
            pilar_atual = pilares[st.session_state.pilar_index]
            check_prompt = f"Analise se esta resposta para {pilar_atual} é adequada para um {nivel_alvo}: {prompt}"
            
            # Aqui entraria a chamada da API (simplificada para o exemplo)
            response = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=[{"role": "system", "content": check_prompt + " Se for boa, chame o próximo pilar."}]
            )
            
            ai_msg = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_msg})
            
            if "próximo" in ai_msg.lower():
                st.session_state.respostas_completas.append(f"{pilar_atual}: {prompt}")
                st.session_state.pilar_index += 1
            
            st.rerun()
