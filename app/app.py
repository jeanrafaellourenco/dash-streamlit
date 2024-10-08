import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configurações da página
st.set_page_config(
    page_title="Dashboard Gestão de Vulnerabilidades",  # Define o título da página no navegador
    page_icon="📊",  # Define o ícone da página (pode ser um emoji ou caminho de imagem)
    layout="wide",  # Define o layout da página como "wide" (mais espaço horizontal)
    initial_sidebar_state="collapsed",  # Define o estado inicial da barra lateral como recolhido
)

# CSS customizado para esconder o menu padrão, rodapé e cabeçalho do Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;} /* Esconde o menu de opções padrão */
    footer {visibility: hidden;}    /* Esconde o rodapé */
    header {visibility: hidden;}    /* Esconde o cabeçalho que inclui o botão "Deploy" */
    </style>
"""

# Aplica o estilo customizado à página
# unsafe_allow_html=True permite que HTML seja processado no Markdown, o que normalmente é desativado por questões de segurança
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Definir o caminho do arquivo Excel que armazena os relatórios e vulnerabilidades
EXCEL_FILE = "app/vulnerabilidades_relatorios.xlsx"

# Função para criar um arquivo Excel vazio com as abas necessárias, caso o arquivo ainda não exista
def inicializar_excel():
    if not os.path.exists(EXCEL_FILE):
        # Cria um arquivo Excel com abas "Vulnerabilidades" e "Relatorios"
        with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl') as writer:
            # Criação da aba "Vulnerabilidades" com colunas definidas
            pd.DataFrame(columns=["Vulnerabilidade ID", "Relatorio ID", "Título", "Descrição", "Criticidade", "Status"]).to_excel(writer, sheet_name="Vulnerabilidades", index=False)
            # Criação da aba "Relatorios" com colunas definidas
            pd.DataFrame(columns=["Relatorio ID", "Nome Relatorio"]).to_excel(writer, sheet_name="Relatorios", index=False)
        st.success(f"Arquivo {EXCEL_FILE} criado com sucesso!")

# Função para carregar os dados de uma aba específica do arquivo Excel
def carregar_dados(sheet_name="Vulnerabilidades"):
    # Verifica se o arquivo Excel existe antes de carregar os dados
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, engine='openpyxl')
    else:
        # Se o arquivo não existir, cria um novo e então carrega os dados
        inicializar_excel()
        return pd.read_excel(EXCEL_FILE, sheet_name=sheet_name, engine='openpyxl')

# Função para salvar dados em uma aba específica do arquivo Excel
def salvar_dados(df, sheet_name="Vulnerabilidades"):
    # Escreve os dados no arquivo Excel, substituindo a aba especificada
    with pd.ExcelWriter(EXCEL_FILE, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)

# Função para cadastrar novos relatórios de vulnerabilidade
def cadastrar_relatorio():
    st.title("Cadastro de Relatórios de Vulnerabilidades")

    # Carregar os dados existentes na aba "Relatorios"
    df_relatorios = carregar_dados(sheet_name="Relatorios")

    # Botão para gerar um novo relatório de vulnerabilidades
    if st.button("Criar Novo Relatório"):
        novo_id = len(df_relatorios) + 1  # Gera um novo ID para o relatório
        nome_relatorio = f"RELATÓRIO DE VULNERABILIDADES #{novo_id}"  # Nome do relatório gerado
        novo_relatorio = pd.DataFrame({"Relatorio ID": [novo_id], "Nome Relatorio": [nome_relatorio]})
        df_relatorios = pd.concat([df_relatorios, novo_relatorio], ignore_index=True)
        salvar_dados(df_relatorios, sheet_name="Relatorios")  # Salva o novo relatório no Excel
        st.success(f"Relatório '{nome_relatorio}' criado com sucesso!")

    # Exibir a lista de relatórios já cadastrados
    st.subheader("Relatórios Cadastrados")
    st.dataframe(df_relatorios)

# Função para cadastrar novas vulnerabilidades associadas a relatórios
def cadastrar_vulnerabilidade():
    st.title("Cadastro de Vulnerabilidades")

    # Carregar os dados existentes de vulnerabilidades e relatórios
    df_vulnerabilidades = carregar_dados(sheet_name="Vulnerabilidades")
    df_relatorios = carregar_dados(sheet_name="Relatorios")

    # Verifica se há relatórios cadastrados antes de permitir o cadastro de vulnerabilidades
    if df_relatorios.empty:
        st.warning("Nenhum relatório cadastrado. Por favor, cadastre um relatório primeiro.")
        return

    # Preparar a lista de relatórios disponíveis para associar a vulnerabilidades
    opcoes_relatorio = df_relatorios["Relatorio ID"].astype(str) + " - " + df_relatorios["Nome Relatorio"]

    # Formulário para entrada de dados de uma nova vulnerabilidade
    with st.form("cadastro_form"):
        relatorio_escolhido = st.selectbox("Selecione o Relatório", opcoes_relatorio)
        relatorio_id = relatorio_escolhido.split(" - ")[0]  # Extrai o ID do relatório escolhido

        titulo = st.text_input("Título da Vulnerabilidade")
        descricao = st.text_area("Descrição")
        criticidade = st.selectbox("Criticidade", ["Informativa", "Baixa", "Média", "Alta", "Crítica"])
        status = st.selectbox("Status", ["Não Corrigida", "Mitigada", "Corrigida", "Risco Aceito"])

        # Botão de submissão do formulário
        submit = st.form_submit_button("Cadastrar Vulnerabilidade")

        if submit:
            # Se a descrição não for preenchida, define um valor padrão
            if not descricao:
                descricao = "Sem descrição"

            novo_id = len(df_vulnerabilidades) + 1  # Gera um novo ID para a vulnerabilidade
            nova_vulnerabilidade = pd.DataFrame({
                "Vulnerabilidade ID": [novo_id],
                "Relatorio ID": [relatorio_id],
                "Título": [titulo],
                "Descrição": [descricao],
                "Criticidade": [criticidade],
                "Status": [status]
            })
            df_vulnerabilidades = pd.concat([df_vulnerabilidades, nova_vulnerabilidade], ignore_index=True)
            salvar_dados(df_vulnerabilidades, sheet_name="Vulnerabilidades")  # Salva a nova vulnerabilidade no Excel
            st.success("Vulnerabilidade cadastrada com sucesso!")

# Função para exibir gráficos do tipo "donut" com Plotly e tooltip personalizado
def plot_plotly_donut(data, labels, title, colors, legend_title):
    # Criação do gráfico de pizza com um "buraco" central, transformando-o em um gráfico do tipo "donut"
    fig = px.pie(
        values=data, 
        names=labels, 
        title=title, 
        hole=0.4,  # Define a proporção do "buraco" central
        color=labels, 
        color_discrete_sequence=colors  # Define a paleta de cores para o gráfico
    )

    # Customização do tooltip para mostrar rótulo, porcentagem e valor absoluto
    fig.update_traces(
        hoverinfo="label+percent+value",  # Exibe o rótulo, porcentagem e valor no hover
        textinfo="label+percent",  # Exibe o rótulo e porcentagem dentro do gráfico
        textposition="inside"  # Posiciona o texto dentro das fatias
    )

    # Customizações adicionais do layout do gráfico
    fig.update_layout(
        title_font_size=20,
        showlegend=True,
        legend_title=legend_title,  # Define o título da legenda
        legend=dict(
            orientation="h",  # Define a legenda na horizontal
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )

    return fig

# Função para exibir a dashboard com filtros e gráficos interativos
def dashboard():
    st.title("📊 Dashboard Gestão de Vulnerabilidades")

    # Carregar os dados de vulnerabilidades e relatórios do arquivo Excel
    df_vulnerabilidades = carregar_dados(sheet_name="Vulnerabilidades")
    df_relatorios = carregar_dados(sheet_name="Relatorios")

    # Verifica se existem vulnerabilidades cadastradas
    if df_vulnerabilidades.empty:
        st.write("Nenhuma vulnerabilidade cadastrada.")
    else:
        # Substitui valores nulos na coluna "Descrição" por "Sem descrição"
        df_vulnerabilidades["Descrição"] = df_vulnerabilidades["Descrição"].fillna("Sem descrição").replace("None", "Sem descrição")

        # Configuração de filtros interativos para Criticidade, Status e Relatórios
        col1, col2 = st.columns(2)
        with col1:
            with st.expander("Filtrar por Criticidade"):
                criticidade_options = df_vulnerabilidades["Criticidade"].unique()  
                criticidade_filter = [st.checkbox(criticidade, value=True) for criticidade in criticidade_options]
                criticidade_selecionadas = [criticidade for i, criticidade in enumerate(criticidade_options) if criticidade_filter[i]]

        with col2:
            with st.expander("Filtrar por Status"):
                status_options = df_vulnerabilidades["Status"].unique()
                status_filter = [st.checkbox(status, value=True) for status in status_options]
                status_selecionados = [status for i, status in enumerate(status_options) if status_filter[i]]

        with st.expander("Filtrar por Relatório"):
            relatorio_options = df_vulnerabilidades["Relatorio ID"].unique()
            relatorio_filter = [st.checkbox(str(relatorio), value=True) for relatorio in relatorio_options]
            relatorios_selecionados = [relatorio for i, relatorio in enumerate(relatorio_options) if relatorio_filter[i]]

        # Aplicação dos filtros selecionados
        df_filtered = df_vulnerabilidades[
            (df_vulnerabilidades["Status"].isin(status_selecionados)) &
            (df_vulnerabilidades["Criticidade"].isin(criticidade_selecionadas)) &
            (df_vulnerabilidades["Relatorio ID"].isin(relatorios_selecionados))
        ]

        # Exibir métricas de total de vulnerabilidades e número de relatórios distintos após aplicar os filtros
        col1, col2 = st.columns(2)
        col1.metric("Total de Vulnerabilidades", len(df_filtered))
        col2.metric("Número Distinto de Relatórios", df_filtered["Relatorio ID"].nunique())

        # Exibir gráficos de donut lado a lado (Criticidade e Status)
        col1, col2 = st.columns(2)

        # Definir cores para os gráficos
        criticidade_colors = ['#0000FF', '#FFFF00', '#FFA500', '#FF0000', '#800080']  # Informativa (azul), Baixa (amarelo), Média (laranja), Alta (vermelho), Crítica (roxo)
        criticidade_order = ['Informativa', 'Baixa', 'Média', 'Alta', 'Crítica']
        status_colors = ['#FF0000', '#FFFF00', '#008000', '#FFA500']  # Não Corrigida (vermelho), Mitigada (amarelo), Corrigida (verde), Risco Aceito (laranja)
        status_order = ['Não Corrigida', 'Mitigada', 'Corrigida', 'Risco Aceito']

        # Gráfico de distribuição por criticidade
        criticidade_counts = df_filtered["Criticidade"].value_counts().reindex(criticidade_order, fill_value=0)
        fig1 = plot_plotly_donut(criticidade_counts.values, criticidade_counts.index, "Distribuição por Criticidade", criticidade_colors, "Criticidade")
        col1.plotly_chart(fig1, use_container_width=True)

        # Gráfico de distribuição por status
        status_counts = df_filtered["Status"].value_counts().reindex(status_order, fill_value=0)
        fig2 = plot_plotly_donut(status_counts.values, status_counts.index, "Distribuição por Status", status_colors, "Status")
        col2.plotly_chart(fig2, use_container_width=True)

        # Exibir o histórico de vulnerabilidades filtradas
        st.subheader("Histórico de Vulnerabilidades")
        st.dataframe(df_filtered[["Vulnerabilidade ID", "Relatorio ID", "Título", "Descrição", "Criticidade", "Status"]], use_container_width=True)

# Definir a dashboard como a tela principal da aplicação, com outras opções de menu
menu = st.sidebar.selectbox("Menu", ["Dashboard", "Cadastro de Relatórios", "Cadastro de Vulnerabilidades"])

# Condicional para exibir as opções de menu
if menu == "Cadastro de Relatórios":
    cadastrar_relatorio()
elif menu == "Cadastro de Vulnerabilidades":
    cadastrar_vulnerabilidade()
elif menu == "Dashboard":
    dashboard()
