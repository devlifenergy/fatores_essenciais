# app_fatores_essenciais_final.py
import streamlit as st
import pandas as pd
from datetime import datetime
import gspread

# --- PALETA DE CORES E CONFIGURAÇÃO DA PÁGINA ---
COLOR_PRIMARY = "#70D1C6"
COLOR_TEXT_DARK = "#333333"
COLOR_BACKGROUND = "#FFFFFF"

st.set_page_config(
    page_title="Inventário — Fatores Essenciais",
    layout="wide"
)

# --- CSS CUSTOMIZADO (Omitido para economizar espaço) ---
st.markdown(f"""<style>...</style>""", unsafe_allow_html=True)

# --- CONEXÃO COM GOOGLE SHEETS (MODIFICADO) ---
@st.cache_resource
def connect_to_gsheet():
    """Conecta ao Google Sheets e retorna o objeto da aba de respostas."""
    try:
        creds_dict = dict(st.secrets["google_credentials"])
        creds_dict['private_key'] = creds_dict['private_key'].replace('\\n', '\n')
        
        gc = gspread.service_account_from_dict(creds_dict)
        
        spreadsheet = gc.open("Respostas Formularios")
        
        # Retorna apenas a aba de respostas que vamos usar
        return spreadsheet.worksheet("Fatores")
    except Exception as e:
        st.error(f"Erro ao conectar com o Google Sheets: {e}")
        return None

# Apenas uma variável é retornada agora
ws_respostas = connect_to_gsheet()

if ws_respostas is None:
    st.error("Não foi possível conectar à aba 'Fatores' da planilha. Verifique o nome e as permissões.")
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

# O campo de observações continua aqui, mas não será enviado
observacoes = st.text_area("Observações (opcional):")

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
            st.bar_chart(resumo_blocos.set_index("Bloco")["Média"])
        
        # --- LÓGICA DE ENVIO PARA GOOGLE SHEETS (MODIFICADA) ---
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
                
                # Envia os dados para a aba de respostas
                ws_respostas.append_rows(respostas_para_enviar, value_input_option='USER_ENTERED')
                
                # O bloco de código que enviava para ws_observacoes foi removido

                st.success("Suas respostas foram enviadas com sucesso para a planilha!")
                st.balloons()
            except Exception as e:
                st.error(f"Erro ao enviar dados para a planilha: {e}")