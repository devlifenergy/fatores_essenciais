# app_fatores_essenciais_v2.py
import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from gspread_dataframe import set_with_dataframe
# --- PALETA DE CORES E CONFIGURAÇÃO DA PÁGINA ---
COLOR_PRIMARY = "#70D1C6" # Cor da logo Wedja
COLOR_TEXT_DARK = "#333333"
COLOR_BACKGROUND = "#FFFFFF"

st.set_page_config(
    page_title="Inventário — Fatores Essenciais",
    layout="wide"
)

# --- CSS CUSTOMIZADO PARA A INTERFACE ---
st.markdown(f"""
    <style>
        /* Remoção de elementos do Streamlit Cloud */
        div[data-testid="stHeader"], div[data-testid="stDecoration"] {{
            visibility: hidden; height: 0%; position: fixed;
        }}
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
        /* Labels dos Inputs */
        div[data-testid="textInputRootElement"] > label,
        div[data-testid="stTextArea"] > label,
        div[data-testid="stRadioGroup"] > label {{
            color: {COLOR_TEXT_DARK}; font-weight: 600;
        }}
        /* Bordas dos campos de input */
        div[data-testid="stTextInput"] input,
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

try:
    # Cria uma cópia editável das credenciais
    creds_dict = dict(st.secrets["google_credentials"])
    # Corrige a formatação da chave privada
    creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
    
    # Autentica no Google
    gc = gspread.service_account_from_dict(creds_dict)
    
    # Abre a planilha pelo nome exato
    spreadsheet = gc.open("Respostas Formularios")
    
    # Seleciona a primeira aba
    worksheet = spreadsheet.sheet1

except Exception as e:
    st.error(f"Erro ao conectar com o Google Sheets: {e}")
    st.stop()

# Seleciona as abas fora da função de cache
ws_respostas = spreadsheet.worksheet("Fatores")
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


# --- SEÇÃO DE IDENTIFICAÇÃO (MODIFICADA) ---
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
    with st.expander(f"Dimensão: {bloco}", expanded=True):
        df_bloco = df_itens[df_itens["Bloco"] == bloco]
        for _, row in df_bloco.iterrows():
            item_id = row["ID"]
            label = f'({item_id}) {row["Item"]}' + (' (R)' if row["Reverso"] == 'SIM' else '')
            widget_key = f"radio_{item_id}"
            st.radio(
                label, options=["N/A", 1, 2, 3, 4, 5],
                horizontal=True, key=widget_key,
                on_change=registrar_resposta, args=(item_id, widget_key)
            )


# --- BOTÃO DE FINALIZAR E LÓGICA DE RESULTADOS/EXPORTAÇÃO ---
if st.button("Finalizar e Gerar Relatório", type="primary"):
    if not st.session_state.respostas:
        st.warning("Nenhuma resposta foi preenchida.")
    else:
        st.subheader("Resultados e Exportação")

        # --- LÓGICA DE CÁLCULO ---
        respostas_list = []
        for index, row in df_itens.iterrows():
            item_id = row['ID']
            resposta_usuario = st.session_state.respostas.get(item_id)
            respostas_list.append({
                "Bloco": row["Bloco"],
                "Item": row["Item"],
                "Resposta": resposta_usuario,
                "Reverso": row["Reverso"]
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
            st.bar_chart(resumo_blocos.set_index("Bloco")["Média"])

        with st.spinner("Enviando dados para a planilha..."):
            try:
                # 1. Preparar dados para o envio
                timestamp_str = datetime.now().isoformat(timespec="seconds")
                respostas_para_enviar = []
                
                # O DataFrame 'dfr' já foi criado na seção de cálculo
                for _, row in dfr.iterrows():
                    respostas_para_enviar.append([
                        timestamp_str,
                        respondente,
                        data,
                        organizacao_coletora,
                        row["Bloco"],
                        row["Item"],
                        row["Resposta"] if pd.notna(row["Resposta"]) else "N/A",
                        observacoes # Adiciona as observações em cada linha
                    ])
                
                # 2. Enviar para a aba "Fatores Essenciais"
                ws_respostas.append_rows(respostas_para_enviar, value_input_option='USER_ENTERED')
                
                st.success("Suas respostas foram enviadas com sucesso para a planilha!")

            except Exception as e:
                st.error(f"Erro ao enviar dados para a planilha: {e}")
        # --- FIM DO TRECHO DE ENVIO ---