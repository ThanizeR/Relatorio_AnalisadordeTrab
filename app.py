import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import plotly._subplots as sp
from streamlit_option_menu import option_menu
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from PIL import Image
import plotly.graph_objects as go
from datetime import timedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import plotly.io as pio
from reportlab.lib.colors import black
import textwrap

st.set_page_config("📊Analisador de Trabalho", page_icon="", layout="wide")

# Função para carregar o arquivo por tipo de máquina
@st.cache_data
def load_data(file, file_type, encoding='utf-8'):
    try:
        if file_type == "CSV":
            df = pd.read_excel(file, engine='openpyxl')
        return df
    except UnicodeDecodeError:
        st.error(f"Erro: Não foi possível decodificar o arquivo usando o encoding '{encoding}'. "
                 "Verifique o formato do arquivo ou tente novamente com um encoding diferente.")
        
# Lógica para página de Tratores
#st.sidebar.title('Selecione a página:')
#pagina_selecionada = st.sidebar.radio("Selecione a página:", ("Tratores", "Pulverizadores", "Colheitadeira"))

# Função para quebrar linhas dos nomes das máquinas
def wrap_labels(labels, width):
    return ['\n'.join(textwrap.wrap(label, width)) for label in labels]

def generate_pdf_aplicacao(df_aplicacao, figures, background_image_first_page=None, background_image_other_pages=None):
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=landscape(A4))

    page_width, page_height = landscape(A4)
    x_margin = 60  # Margem lateral
    y_margin = 40  # Margem vertical ajustada para subir o gráfico
    header_space_other_pages = 70  # Espaço para o cabeçalho

    # Tamanho do gráfico
    graph_width = page_width - 2 * x_margin  # Largura do gráfico
    graph_height = page_height - header_space_other_pages - 2 * y_margin  # Altura do gráfico

    def set_background(page_num):
        if page_num == 0 and background_image_first_page:
            background = ImageReader(background_image_first_page)
        elif background_image_other_pages:
            background = ImageReader(background_image_other_pages)
        else:
            return
        c.drawImage(background, 0, 0, width=page_width, height=page_height)

    # Primeira página (capa)
    set_background(0)
    c.showPage()

    # Segunda página com informações da aplicação e gráficos
    set_background(1)

    # Adicionando informações relevantes na segunda página
    if 'Clientes' in df_aplicacao.columns:
        cliente = df_aplicacao['Clientes'].iloc[0]

        # Texto à esquerda com espaçamento como dois Tabs
        c.setFont("Helvetica", 10)
        c.drawString(x_margin - 20, page_height - 40, f"Cliente: {cliente}")

    page_num = 1
    graph_index = 0

    while graph_index < len(figures):
        fig = figures[graph_index]

        if not isinstance(fig, plt.Figure):
            print(f"Skipping non-Matplotlib figure: {type(fig)}")
            continue

        # Salvar gráfico como imagem
        img_data = BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight')
        img_data.seek(0)

        # Centralizar o gráfico e movê-lo um pouco mais para cima
        c.drawImage(ImageReader(img_data), x_margin, y_margin + 20, width=graph_width, height=graph_height)  # Aumentar para subir
        graph_index += 1

        if graph_index < len(figures):
            c.showPage()
            page_num += 1
            set_background(page_num)

    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

# Caminho para as imagens de fundo
background_image_first_page_tratores = 'Aplicação.jpg'
background_image_other_pages = 'outraspáginas.jpg'

# Menu dropdown na barra superior
selected = option_menu(
    menu_title=None,  # Título do menu, None para esconder
    options=["Aplicação", "Semeadura", "Colheita", "Preparo de Solo"],  # Opções do menu
    icons=['-', '-', '-', '-'],  # Ícones para cada opção
    #menu_icon="cast",  # Ícone do menu
    default_index=0,  # Índice padrão
    orientation="horizontal",  # Orientação horizontal
)

# Lógica para exibir o conteúdo com base na opção selecionada
if selected == "Aplicação":
    pass
elif selected == "Semeadura":
    pass
elif selected == "Colheita":
    pass
elif selected == "Preparo de Solo":
    pass

if selected == "Aplicação":
    st.subheader("Analisador de Trabalho - Aplicação")
    col1,col2,col3=st.columns(3)
    # Seleção do tipo de arquivo e upload
    file_type_aplicacao = st.radio("Selecione o tipo de arquivo:", ("CSV",))
    uploaded_file_aplicacao = st.file_uploader(f"Escolha um arquivo {file_type_aplicacao} para Tratores", type=["xlsx"])

    if uploaded_file_aplicacao is not None:
        df_aplicacao = load_data(uploaded_file_aplicacao, file_type_aplicacao)

        if df_aplicacao is not None:
            st.subheader('Dados do Arquivo Carregado para Aplicação')
            # Exibir data de início e data final
            if 'Clientes' in df_aplicacao.columns:
                # Especificar que o dia vem primeiro
                organização = df_aplicacao['Clientes'].iloc[0]

                col1, col2, col3 = st.columns(3)
                col1.write(f"Organização: {organização}")

                # Criar dicionário para cores
                colors = {
                    'Event': 'rgb(31, 119, 180)',
                    'Other Event': 'rgb(255, 127, 14)'
                }
            #####################################SOMA DE AREA APLICADA#######################################
            # Definir os dados
            selected_columns_haaplicada = ["Nome da Máquina", "Área Aplicada"]
            df_selected_haaplicada = df_aplicacao[selected_columns_haaplicada].copy()

            # Agrupar os dados por "Nome da Máquina" e somar "Área Aplicada"
            df_soma_haaplicada = df_selected_haaplicada.groupby("Nome da Máquina").sum().reset_index()

            # Ordenar o DataFrame com base na soma da área aplicada usando sort_values
            df_soma_haaplicada = df_soma_haaplicada.sort_values(by="Área Aplicada", ascending=False)

            # Configurar o gráfico
            fig_haaplicada, ax_haaplicada = plt.subplots(figsize=(12, 8))

            # Extrair dados para plotagem
            maquinas_haaplicada = df_soma_haaplicada["Nome da Máquina"]
            haaplicada = df_soma_haaplicada["Área Aplicada"]
            wrapped_labels = wrap_labels(maquinas_haaplicada, width=10)  # Ajuste a largura conforme necessário

            # Ajustar a altura das barras dinamicamente
            bar_height_hrmotor = 0.4
            if len(maquinas_haaplicada) == 1:
                bar_height_hrmotor = 0.2  # Barra mais fina

            # Plotar barras horizontais com cor verde musgo claro
            bars = ax_haaplicada.barh(maquinas_haaplicada, haaplicada, height=bar_height_hrmotor, color='blue')
            labels_hrmotor = ['Área Aplicada (ha)']

            # Adicionar os valores da área aplicada no final de cada barra
            for bar, area in zip(bars, haaplicada):
                ax_haaplicada.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2, f'{area:.2f} ha',
                                va='center', ha='left', fontsize=10, fontweight='bold')

            # Configurar os eixos e título
            ax_haaplicada.set_xlabel('Área Aplicada (ha)')
            ax_haaplicada.set_ylabel('')
            ax_haaplicada.set_title('Área Aplicada por Máquina')
            ax_haaplicada.set_yticklabels(wrapped_labels)

            # Centralizar a barra única
            if len(maquinas_haaplicada) == 1:
                ax_haaplicada.set_ylim(-0.5, 0.5)  # Centralizar a barra no meio do gráfico

            # Adicionar legenda única para Área Aplicada
            ax_haaplicada.legend(labels_hrmotor, loc='upper right', bbox_to_anchor=(1.22, 1.0))

            # Mostrar o gráfico
            col4, col5 = st.columns(2)
            col4.pyplot(fig_haaplicada)

            #########################MÉDIA TAXA ALVO E TAXA APLICADA###################################
            ## Definir os dados
            # Definir os dados
            selected_columns_taxas = ["Nome da Máquina", "Taxa Aplicada", "Taxa Alvo"]
            df_selected_taxas = df_aplicacao.copy()

            # Verificar se as colunas existem e, se não existirem, adicionar com valores 0
            if "Taxa Aplicada" not in df_selected_taxas.columns:
                df_selected_taxas["Taxa Aplicada"] = 0  # Adicionar coluna de Taxa Aplicada com valor 0 se não existir

            if "Taxa Alvo" not in df_selected_taxas.columns:
                df_selected_taxas["Taxa Alvo"] = 0  # Adicionar coluna de Taxa Alvo com valor 0 se não existir

            # Converter as colunas para numéricas, tratando erros
            df_selected_taxas["Taxa Aplicada"] = pd.to_numeric(df_selected_taxas["Taxa Aplicada"], errors='coerce').fillna(0)
            df_selected_taxas["Taxa Alvo"] = pd.to_numeric(df_selected_taxas["Taxa Alvo"], errors='coerce').fillna(0)

            # Calcular as médias da Taxa Aplicada e Taxa Alvo por Máquina
            df_medias_taxas = df_selected_taxas.groupby("Nome da Máquina")[["Taxa Aplicada", "Taxa Alvo"]].mean().reset_index()

            # Configurar o gráfico
            fig_taxas, ax_taxas = plt.subplots(figsize=(12, 8))

            # Definir a largura das barras
            bar_width = 0.35  # Largura das barras

            # Definir as posições das barras
            posicoes = range(len(df_medias_taxas))

            # Plotar as barras verticais
            bars1 = ax_taxas.bar(posicoes, df_medias_taxas["Taxa Aplicada"], width=bar_width, color='green', label='Taxa Aplicada')
            bars2 = ax_taxas.bar([p + bar_width for p in posicoes], df_medias_taxas["Taxa Alvo"], width=bar_width, color='orange', label='Taxa Alvo')

            # Adicionar os rótulos das máquinas
            ax_taxas.set_xticks([p + bar_width / 2 for p in posicoes])  # Ajustar ticks para o meio das barras
            ax_taxas.set_xticklabels(df_medias_taxas["Nome da Máquina"], rotation=45, ha='right')

            # Adicionar os números de taxa aplicadas e alvo no topo de cada barra
            for bar in bars1:
                height = bar.get_height()
                ax_taxas.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

            for bar in bars2:
                height = bar.get_height()
                ax_taxas.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='Black')

            # Configurar os eixos e título
            ax_taxas.set_xlabel('')
            ax_taxas.set_ylabel('')
            ax_taxas.set_title('')

            # Adicionar legenda
            ax_taxas.legend(loc='upper right', bbox_to_anchor=(1.22, 1.0))
            # Mostrar o gráfico
            col5.pyplot(fig_taxas)
            ############################MÉDIA EFICIÊNCIA#####################################
            # Definir os dados
            selected_columns_eficiencia = ["Nome da Máquina", "Eficiência Operacional"]
            df_selected_eficiencia = df_aplicacao.copy()

            # Verificar se a coluna "Eficiência Operacional" existe e, se não existir, adicionar com valor 0
            if "Eficiência Operacional" not in df_selected_eficiencia.columns:
                df_selected_eficiencia["Eficiência Operacional"] = 0  # Adicionar coluna com valor 0 se não existir

            # Converter a coluna para numérica, tratando erros
            df_selected_eficiencia["Eficiência Operacional"] = pd.to_numeric(df_selected_eficiencia["Eficiência Operacional"], errors='coerce').fillna(0)

            # Calcular as médias da Eficiência Operacional por Máquina
            df_medias_eficiencia = df_selected_eficiencia.groupby("Nome da Máquina")["Eficiência Operacional"].mean().reset_index()

            # Configurar o gráfico
            fig_eficiencia, ax_eficiencia = plt.subplots(figsize=(12, 8))

            # Definir as posições das barras
            posicoes = range(len(df_medias_eficiencia))

            # Plotar as barras verticais
            bars = ax_eficiencia.bar(posicoes, df_medias_eficiencia["Eficiência Operacional"], color='purple', label='Eficiência Operacional')

            # Adicionar os rótulos das máquinas
            ax_eficiencia.set_xticks(posicoes)
            ax_eficiencia.set_xticklabels(df_medias_eficiencia["Nome da Máquina"], rotation=45, ha='right')

            # Adicionar os números de eficiência no topo de cada barra
            for bar in bars:
                height = bar.get_height()
                ax_eficiencia.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='Black')

            # Configurar os eixos e título
            ax_eficiencia.set_xlabel('')
            ax_eficiencia.set_ylabel('')
            ax_eficiencia.set_title('')

            # Adicionar legenda
            ax_eficiencia.legend(loc='upper right', bbox_to_anchor=(1.24, 1.0))
            col6, col7 = st.columns(2)
            col6.pyplot(fig_eficiencia)
            #############################MÉDIA VELOCIDADE##########################################
            # Definir os dados
            selected_columns_Velocidade = ["Nome da Máquina", "Velocidade"]
            df_selected_Velocidade = df_aplicacao.copy()

            # Verificar se a coluna "Velocidade" existe e, se não existir, adicionar com valor 0
            if "Velocidade" not in df_selected_Velocidade.columns:
                df_selected_Velocidade["Velocidade"] = 0  # Adicionar coluna com valor 0 se não existir

            # Converter a coluna para numérica, tratando erros
            df_selected_Velocidade["Velocidade"] = pd.to_numeric(df_selected_Velocidade["Velocidade"], errors='coerce').fillna(0)

            # Calcular as médias da Velocidade por Máquina
            df_medias_Velocidade = df_selected_Velocidade.groupby("Nome da Máquina")["Velocidade"].mean().reset_index()

            # Configurar o gráfico
            fig_Velocidade, ax_Velocidade = plt.subplots(figsize=(12, 8))

            # Definir as posições das barras
            posicoes = range(len(df_medias_Velocidade))

            # Plotar as barras verticais
            bars = ax_Velocidade.bar(posicoes, df_medias_Velocidade["Velocidade"], color='brown', label='Velocidade')

            # Adicionar os rótulos das máquinas
            ax_Velocidade.set_xticks(posicoes)
            ax_Velocidade.set_xticklabels(df_medias_Velocidade["Nome da Máquina"], rotation=45, ha='right')

            # Adicionar os números de eficiência no topo de cada barra
            for bar in bars:
                height = bar.get_height()
                ax_Velocidade.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='Black')

            # Configurar os eixos e título
            ax_Velocidade.set_xlabel('')
            ax_Velocidade.set_ylabel('')
            ax_Velocidade.set_title('')

            # Adicionar legenda
            ax_Velocidade.legend(loc='upper right', bbox_to_anchor=(1.24, 1.0))
            col7.pyplot(fig_Velocidade)

            ##############################################MÉDIA COMBUSTIVEL#################################
            # Definir os dados
            selected_columns_combustivel = ["Nome da Máquina", "Combustível"]
            df_selected_combustivel = df_aplicacao.copy()

            # Verificar se a coluna "Combustível" existe e, se não existir, adicionar com valor 0
            if "Combustível" not in df_selected_combustivel.columns:
                df_selected_combustivel["Combustível"] = 0  # Adicionar coluna com valor 0 se não existir

            # Converter a coluna para numérica, tratando erros
            df_selected_combustivel["Combustível"] = pd.to_numeric(df_selected_combustivel["Combustível"], errors='coerce').fillna(0)

            # Calcular as médias do Combustível por Máquina
            df_medias_combustivel = df_selected_combustivel.groupby("Nome da Máquina")["Combustível"].mean().reset_index()

            # Configurar o gráfico
            fig_combustivel, ax_combustivel = plt.subplots(figsize=(12, 8))

            # Definir as posições das barras
            posicoes = range(len(df_medias_combustivel))

            # Plotar as barras verticais com cor vermelha
            bars = ax_combustivel.bar(posicoes, df_medias_combustivel["Combustível"], color='red', label='Combustível')

            # Adicionar os rótulos das máquinas
            ax_combustivel.set_xticks(posicoes)
            ax_combustivel.set_xticklabels(df_medias_combustivel["Nome da Máquina"], rotation=45, ha='right')

            # Adicionar os números de eficiência no topo de cada barra
            for bar in bars:
                height = bar.get_height()
                ax_combustivel.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

            # Configurar os eixos e título
            ax_combustivel.set_xlabel('')
            ax_combustivel.set_ylabel('')
            ax_combustivel.set_title('')

            # Adicionar legenda
            ax_combustivel.legend(loc='upper right', bbox_to_anchor=(1.24, 1.0))
            col8, col9 = st.columns(2)
            col8.pyplot(fig_combustivel)

            ##########################SOMA HA POR PRODUTO##########################################################
            # Definir os dados
            selected_columns_haaplicada = ["Produtos", "Área Aplicada"]
            df_selected_haaplicada = df_aplicacao[selected_columns_haaplicada].copy()

            # Agrupar os dados por "Produtos" e somar "Área Aplicada"
            df_soma_haaplicada = df_selected_haaplicada.groupby("Produtos")["Área Aplicada"].sum().reset_index()

            # Ordenar o DataFrame com base na soma da área aplicada usando sort_values
            df_soma_haaplicada = df_soma_haaplicada.sort_values(by="Área Aplicada", ascending=False)

            # Configurar o gráfico
            fig_haaplicada_pd, ax_haaplicada = plt.subplots(figsize=(12, 8))

            # Extrair dados para plotagem
            produtos_haaplicada = df_soma_haaplicada["Produtos"]
            haaplicada = df_soma_haaplicada["Área Aplicada"]

            # Ajustar a altura das barras dinamicamente
            bar_height_hrmotor = 0.4
            if len(produtos_haaplicada) == 1:
                bar_height_hrmotor = 0.2  # Barra mais fina

            # Plotar barras horizontais com cor verde
            bars = ax_haaplicada.barh(produtos_haaplicada, haaplicada, height=bar_height_hrmotor, color='green')

            # Adicionar os valores da área aplicada no final de cada barra
            for bar, area in zip(bars, haaplicada):
                ax_haaplicada.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2, f'{area:.1f}',
                                va='center', ha='left', fontsize=10, fontweight='bold')

            # Configurar os eixos e título
            ax_haaplicada.set_xlabel('')
            ax_haaplicada.set_ylabel('')
            ax_haaplicada.set_title('')

            # Centralizar a barra única
            if len(produtos_haaplicada) == 1:
                ax_haaplicada.set_ylim(-0.5, 0.5)  # Centralizar a barra no meio do gráfico

            # Adicionar legenda única para Área Aplicada
            ax_haaplicada.legend(['Área Aplicada (ha)'], loc='upper right', bbox_to_anchor=(1.22, 1.0))
            col9.pyplot(fig_haaplicada_pd)

            #######################SOMA COMBUSTIVEL POR PRODUTO#######################################
            # Definir os dados
            selected_columns_combustivel = ["Produtos", "Combustível"]
            df_selected_combustivel = df_aplicacao[selected_columns_combustivel].copy()

            # Garantir que a coluna "Combustível" seja numérica, convertendo strings para NaN e substituindo por 0
            df_selected_combustivel["Combustível"] = pd.to_numeric(df_selected_combustivel["Combustível"], errors='coerce').fillna(0)

            # Agrupar os dados por "Produtos" e somar "Combustível"
            df_soma_combustivel = df_selected_combustivel.groupby("Produtos")["Combustível"].sum().reset_index()

            # Ordenar o DataFrame com base na soma do combustível usando sort_values
            df_soma_combustivel = df_soma_combustivel.sort_values(by="Combustível", ascending=False)

            # Configurar o gráfico
            fig_combustivel, ax_combustivel = plt.subplots(figsize=(12, 8))

            # Extrair dados para plotagem
            produtos_combustivel = df_soma_combustivel["Produtos"]
            combustivel = df_soma_combustivel["Combustível"]

            # Ajustar a altura das barras dinamicamente
            bar_height_hrmotor = 0.4
            if len(produtos_combustivel) == 1:
                bar_height_hrmotor = 0.2  # Barra mais fina

            # Plotar barras horizontais com cor verde
            bars = ax_combustivel.barh(produtos_combustivel, combustivel, height=bar_height_hrmotor, color='yellow')

            # Adicionar os valores do combustível no final de cada barra, mostrando apenas a parte inteira
            for bar, comb in zip(bars, combustivel):
                ax_combustivel.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2, f'{int(comb)}',
                                    va='center', ha='left', fontsize=10, fontweight='bold')

            # Configurar os eixos e título
            ax_combustivel.set_xlabel('')
            ax_combustivel.set_ylabel('')
            ax_combustivel.set_title('')

            # Centralizar a barra única
            if len(produtos_combustivel) == 1:
                ax_combustivel.set_ylim(-0.5, 0.5)  # Centralizar a barra no meio do gráfico

            # Adicionar legenda única para Combustível
            ax_combustivel.legend(['Combustível (L)'], loc='upper right', bbox_to_anchor=(1.22, 1.0))

            # Mostrar o gráfico
            col10, col11 = st.columns(2)
            col10.pyplot(fig_combustivel)

            if st.button('Gerar PDF para Aplicação'):
                # Supondo que 'Nome_Organizacao' seja uma coluna no dataframe 
                first_organization_name = df_aplicacao['Clientes'].iloc[0].split()[0]

                # Gerar o PDF
                figures = [fig_eficiencia,fig_combustivel, fig_haaplicada, fig_taxas, fig_Velocidade, fig_haaplicada_pd]
                pdf_buffer = generate_pdf_aplicacao(df_aplicacao, figures, background_image_first_page_tratores, background_image_other_pages)

                # Configurar o nome do arquivo dinamicamente
                file_name = f"relatorio_aplicacao_{first_organization_name}.pdf"

                # Download do PDF
                st.download_button(
                    label="Baixar PDF",
                    data=pdf_buffer,
                    file_name=file_name,
                    mime="application/pdf"
                )