# app_fatores_essenciais_final.py
import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
import matplotlib.pyplot as plt

# --- PALETA DE CORES E CONFIGURAÇÃO DA PÁGINA ---
COLOR_PRIMARY = "#70D1C6"
COLOR_TEXT_DARK = "#333333"
COLOR_BACKGROUND = "#FFFFFF"

st.set_page_config(
    page_title="Inventário — Fatores Essenciais",
    layout="wide"
)

# --- CSS CUSTOMIZADO (Omitido para economizar espaço) ---
st.markdown(f"""
    <style>
        div[data-testid="stHeader"], div[data-testid="stDecoration"] {{
            visibility: hidden; height: 0%; position: fixed;
        }}
        #autoclick-div {
            display: none;
        }
        footer {{ visibility: hidden; height: 0%; }}
        /* Estilos gerais */
        .stApp {{ background-color: {COLOR_BACKGROUND}; color: {COLOR_TEXT_DARK}; }}
        h1, h2, h3 {{ color: {COLOR_TEXT_DARK}; }}
        /* Cabeçalho customizado */
        .stApp > header {{
            background-color: {COLOR_PRIMARY}; padding: 1rem;
            border-bottom: 5px solid {COLOR_TEXT_DARK};
        }}
        /* Card de container */
        div.st-emotion-cache-1r4qj8v {{
             background-color: #f0f2f6; border-left: 5px solid {COLOR_PRIMARY};
             border-radius: 5px; padding: 1.5rem; margin-top: 1rem;
             margin-bottom: 1.5rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        /* Inputs e Labels */
        div[data-testid="textInputRootElement"] > label,
        div[data-testid="stTextArea"] > label,
        div[data-testid="stRadioGroup"] > label {{
            color: {COLOR_TEXT_DARK}; font-weight: 600;
        }}
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        div[data-testid="stSelectbox"] > div,
        div[data-testid="stTextArea"] textarea {{
            border: 1px solid #cccccc;
            border-radius: 5px;
            background-color: #FFFFFF;
        }}
        /* Expanders */
        .streamlit-expanderHeader {{
            background-color: {COLOR_PRIMARY}; color: white; font-size: 1.2rem;
            font-weight: bold; border-radius: 8px; margin-top: 1rem;
            padding: 0.75rem 1rem; border: none; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }}
        .streamlit-expanderHeader:hover {{ background-color: {COLOR_TEXT_DARK}; }}
        .streamlit-expanderContent {{
            background-color: #f9f9f9; border-left: 3px solid {COLOR_PRIMARY}; padding: 1rem;
            border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; margin-bottom: 1rem;
        }}
        /* Botões de rádio (Likert) responsivos */
        div[data-testid="stRadio"] > div {{
            display: flex; flex-wrap: wrap; justify-content: flex-start;
        }}
        div[data-testid="stRadio"] label {{
            margin-right: 1.2rem; margin-bottom: 0.5rem; color: {COLOR_TEXT_DARK};
        }}
        /* Botão de Finalizar */
        .stButton button {{
            background-color: {COLOR_PRIMARY}; color: white; font-weight: bold;
            padding: 0.75rem 1.5rem; border-radius: 8px; border: none;
        }}
        .stButton button:hover {{
            background-color: {COLOR_TEXT_DARK}; color: white;
        }}
    </style>
""", unsafe_allow_html=True)
# --- CONEXÃO COM GOOGLE SHEETS (COM CACHE) ---
@st.cache_resource
def connect_to_gsheet():
    """Conecta ao Google Sheets e retorna o objeto da aba de respostas."""
    try:
        creds_dict = dict(st.secrets["google_credentials"])
        creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
        
        gc = gspread.service_account_from_dict(creds_dict)
        spreadsheet = gc.open("Respostas Formularios")
        
        return spreadsheet.worksheet("Fatores_Essenciais")
    except Exception as e:
        st.error(f"Erro ao conectar com o Google Sheets: {e}")
        return None

ws_respostas = connect_to_gsheet()

if ws_respostas is None:
    st.error("Não foi possível conectar à aba 'Fatores_Essenciais' da planilha. Verifique o nome e as permissões.")
    st.stop()


# --- CABEÇALHO DA APLICAÇÃO ---
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("logo_wedja.jpg", width=120)
    except FileNotFoundError:
        st.warning("Logo 'logo_wedja.jpg' não encontrada.")
with col2:
    st.markdown(f"""
    <div style="display: flex; align-items: center; height: 100%;">
        <h1 style='color: {COLOR_TEXT_DARK}; margin: 0; padding: 0;'>INVENTÁRIO — FATORES ESSENCIAIS</h1>
    </div>
    """, unsafe_allow_html=True)


# --- SEÇÃO DE IDENTIFICAÇÃO ---
with st.container(border=True):
    st.markdown("<h3 style='text-align: center;'>Identificação</h3>", unsafe_allow_html=True)
    
    col1_form, col2_form = st.columns(2)
    with col1_form:
        respondente = st.text_input("Respondente:", key="input_respondente")
        data = st.text_input("Data:", datetime.now().strftime('%d/%m/%Y'))
    with col2_form:
        organizacao_coletora = st.text_input("Organização Coletora:", "Instituto Wedja de Socionomia", disabled=True)


# --- INSTRUÇÕES ---
with st.expander("Ver Orientações aos Respondentes", expanded=True):
    st.info(
        """
        - **Escala Likert 1–5:** 1=Discordo totalmente • 2=Discordo • 3=Nem discordo nem concordo • 4=Concordo • 5=Concordo totalmente.
        - Itens marcados como **(R)** são inversos para análise (a pontuação será 6 − resposta).
        """
    )


# --- LÓGICA DO QUESTIONÁRIO (BACK-END) ---
@st.cache_data
def carregar_itens():
    data = [
        ('Recompensas e Benefícios', 'RE01', 'A política de recompensas e benefícios é justa e clara.', 'NÃO'),
        ('Recompensas e Benefícios', 'RE02', 'A remuneração é compatível com as responsabilidades do cargo.', 'NÃO'),
        ('Saúde e Segurança', 'SE01', 'As condições de trabalho garantem minha saúde e segurança.', 'NÃO'),
        ('Saúde e Segurança', 'SE02', 'A empresa investe em prevenção de acidentes e treinamentos de segurança.', 'NÃO'),
        ('Reconhecimento e Valorização', 'RC01', 'Meu esforço e resultados são reconhecidos com frequência.', 'NÃO'),
        ('Reconhecimento e Valorização', 'RC02', 'Sinto que minhas contribuições são valorizadas pela liderança.', 'NÃO'),
        ('Equilíbrio e Qualidade de Vida', 'EQ01', 'Equilibro bem minhas responsabilidades pessoais e profissionais.', 'NÃO'),
        ('Equilíbrio e Qualidade de Vida', 'EQ02', 'A carga horária e o ritmo de trabalho permitem qualidade de vida.', 'NÃO'),
        ('Fatores de Risco (Reversos)', 'EX01', 'Sacrifico frequentemente minha vida pessoal por excesso de trabalho.', 'SIM'),
        ('Fatores de Risco (Reversos)', 'EX02', 'O reconhecimento acontece raramente ou de forma desigual.', 'SIM'),
    ]
    df = pd.DataFrame(data, columns=["Bloco", "ID", "Item", "Reverso"])
    return df

# --- INICIALIZAÇÃO E FORMULÁRIO DINÂMICO ---
df_itens = carregar_itens()
if 'respostas' not in st.session_state:
    st.session_state.respostas = {}

st.subheader("Questionário")
blocos = df_itens["Bloco"].unique().tolist()
def registrar_resposta(item_id, key):
    st.session_state.respostas[item_id] = st.session_state[key]

for bloco in blocos:
    df_bloco = df_itens[df_itens["Bloco"] == bloco]
    
    prefixo_bloco = df_bloco['ID'].iloc[0][:2] if not df_bloco.empty else bloco
    
    with st.expander(f"{prefixo_bloco}", expanded=True):
        for _, row in df_bloco.iterrows():
            item_id = row["ID"]
            label = f'({item_id})' + (' (R)' if row["Reverso"] == 'SIM' else '')
            widget_key = f"radio_{item_id}"
            st.radio(
                label, options=["N/A", 1, 2, 3, 4, 5],
                horizontal=True, key=widget_key,
                on_change=registrar_resposta, args=(item_id, widget_key)
            )

# O campo de observações foi removido desta seção

# --- BOTÃO DE FINALIZAR E LÓGICA DE RESULTADOS/EXPORTAÇÃO ---
if st.button("Finalizar e Enviar Respostas", type="primary"):
    if not st.session_state.respostas:
        st.warning("Nenhuma resposta foi preenchida.")
    else:
        st.subheader("Resultados e Envio")

        # --- LÓGICA DE CÁLCULO ---
        respostas_list = []
        for index, row in df_itens.iterrows():
            item_id = row['ID']
            resposta_usuario = st.session_state.respostas.get(item_id)
            respostas_list.append({
                "Bloco": row["Bloco"], "Item": row["Item"],
                "Resposta": resposta_usuario, "Reverso": row["Reverso"]
            })
        dfr = pd.DataFrame(respostas_list)

        dfr_numerico = dfr[pd.to_numeric(dfr['Resposta'], errors='coerce').notna()].copy()
        if not dfr_numerico.empty:
            dfr_numerico['Resposta'] = dfr_numerico['Resposta'].astype(int)
            def ajustar_reverso(row):
                return (6 - row["Resposta"]) if row["Reverso"] == "SIM" else row["Resposta"]
            dfr_numerico["Pontuação"] = dfr_numerico.apply(ajustar_reverso, axis=1)
            media_geral = dfr_numerico["Pontuação"].mean()
            resumo_blocos = dfr_numerico.groupby("Bloco")["Pontuação"].mean().round(2).reset_index(name="Média").sort_values("Média")
        else:
            media_geral = 0
            resumo_blocos = pd.DataFrame(columns=["Bloco", "Média"])

        st.metric("Pontuação Média Geral (somente itens de 1 a 5)", f"{media_geral:.2f}")

        if not resumo_blocos.empty:
            st.subheader("Média por Dimensão")
            st.dataframe(resumo_blocos.rename(columns={"Bloco": "Dimensão"}), use_container_width=True, hide_index=True)
            st.subheader("Gráfico Comparativo por Dimensão")
            
            # --- CÓDIGO DO GRÁFICO DE PIZZA ---
            # Cria a figura e os eixos do gráfico
            fig, ax = plt.subplots()
            
            # Gera o gráfico de pizza, com cores diferentes para cada fatia
            ax.pie(x=resumo_blocos["Média"], labels=resumo_blocos["Bloco"], autopct='%1.1f%%', startangle=90)
            
            # Garante que o gráfico seja desenhado como um círculo
            ax.axis('equal')  
            
            # Exibe o gráfico gerado no Streamlit
            st.pyplot(fig)
            # --- FIM DO CÓDIGO DO GRÁFICO DE PIZZA ---
        
        # --- LÓGICA DE ENVIO PARA GOOGLE SHEETS ---
        with st.spinner("Enviando dados para a planilha..."):
            try:
                timestamp_str = datetime.now().isoformat(timespec="seconds")
                respostas_para_enviar = []
                
                for _, row in dfr.iterrows():
                    respostas_para_enviar.append([
                        timestamp_str,
                        respondente,
                        data,
                        organizacao_coletora,
                        row["Bloco"],
                        row["Item"],
                        row["Resposta"] if pd.notna(row["Resposta"]) else "N/A",
                    ])
                
                ws_respostas.append_rows(respostas_para_enviar, value_input_option='USER_ENTERED')
                
                st.success("Suas respostas foram enviadas com sucesso para a planilha!")
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao enviar dados para a planilha: {e}")

            with st.container():
                st.markdown('<div id="autoclick-div">', unsafe_allow_html=True)
                if st.button("Ping Button", key="autoclick_button"):
                # A ação aqui pode ser um simples print no log do Streamlit
                  print("Ping button clicked by automation.")
                st.markdown('</div>', unsafe_allow_html=True)