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

def generate_pdf_aplicacao(df_aplicacao, figures, background_image_first_page=None, background_image_other_pages=None):
    pdf_buffer = BytesIO()
    
    # Tamanho A4 em retrato
    page_width, page_height = A4  # A4 em retrato (595 x 842 pontos)
    
    # Criar o canvas com tamanho A4 em retrato
    c = canvas.Canvas(pdf_buffer, pagesize=(page_width, page_height))

    # Margens para o layout
    x_margin = 40  # Margem lateral
    y_margin = 40  # Margem superior
    header_space_other_pages = 70  # Espaço para o cabeçalho

    # Definir as posições e tamanhos dos gráficos conforme sua descrição
    graph_positions_and_sizes = [
        # Gráfico 1 (canto esquerdo abaixo do título)
        {'name': 'fig_haaplicada_aplicacao','x': x_margin, 'y': page_height - y_margin - 250, 'width': 270, 'height': 200},  # Gráfico 1

        # Gráficos 2, 3, 4 (à direita do gráfico 1)
        {'name': 'fig_mediaVelocidade_aplicacao','x': x_margin + 250, 'y': page_height - y_margin - 250, 'width': 250, 'height': 200},  # Gráfico 2
        {'name': 'fig_eficiencia_aplicacao','x': x_margin + 250, 'y': page_height - y_margin - 470, 'width': 250, 'height': 200},  # Gráfico 3
        {'name': 'fig_media_combustivel_aplicacao','x': x_margin + 270, 'y': page_height - y_margin - 678, 'width': 235, 'height': 200},  # Gráfico 4

        # Gráfico 5 (pequeno abaixo do gráfico 1)
        {'name': 'fig_taxa_aplicacao','x': x_margin, 'y': page_height - y_margin - 472, 'width': 250, 'height': 200},  # Gráfico 5

        # Gráfico 6 (comprido no final da página)
        {'name': 'fig_somacombustivel_aplicacao','x': x_margin, 'y': page_height - y_margin - 680, 'width': 250, 'height': 200},  # Gráfico 6 (comprido)
    ]

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

    # Segunda página com gráficos
    set_background(1)

    # Adicionar informações relevantes na segunda página
    if 'Clientes' in df_aplicacao.columns:
        cliente = df_aplicacao['Clientes'].iloc[0]
        c.setFont("Helvetica", 10)
        c.drawString(x_margin - 20, page_height - 40, f"Cliente: {cliente}")

    try:
        # Certifique-se de que as datas estão no formato datetime
        if 'Primeiro Aplicado' in df_aplicacao.columns:
            df_aplicacao['Primeiro Aplicado'] = pd.to_datetime(df_aplicacao['Primeiro Aplicado'], errors='coerce')
            primeiro_aplicado = df_aplicacao['Primeiro Aplicado'].min()
            primeiro_aplicado_str = primeiro_aplicado.strftime('%d/%m/%Y') if pd.notnull(primeiro_aplicado) else "Data inválida"

        if 'Última Aplicação' in df_aplicacao.columns:
            df_aplicacao['Última Aplicação'] = pd.to_datetime(df_aplicacao['Última Aplicação'], errors='coerce')
            ultima_aplicacao = df_aplicacao['Última Aplicação'].max()
            ultima_aplicacao_str = ultima_aplicacao.strftime('%d/%m/%Y') if pd.notnull(ultima_aplicacao) else "Data inválida"

        # Adicionar as datas ao PDF
        c.drawString(x_margin - 20, page_height - 60, f"Primeira Aplicação: {primeiro_aplicado_str}")
        c.drawString(x_margin - 20, page_height - 80, f"Última Aplicação: {ultima_aplicacao_str}")

    except Exception as e:
        print(f"Erro ao processar datas: {e}")

    graph_index = 0
    # Antes de salvar cada gráfico, defina o tamanho das fontes do gráfico.
    for position_and_size in graph_positions_and_sizes:
        if graph_index >= len(figures):
            break  # Não há mais gráficos para adicionar

        fig = figures[graph_index]

        if not isinstance(fig, plt.Figure):
            print(f"Skipping non-Matplotlib figure: {type(fig)}")
            graph_index += 1
            continue

        # Ajustando o tamanho das fontes para garantir legibilidade maior
        for ax in fig.get_axes():
            ax.title.set_fontsize(18)
            ax.xaxis.label.set_fontsize(20)
            ax.yaxis.label.set_fontsize(20)
            ax.tick_params(axis='both', labelsize=14)  # Aumentar um pouco mais os ticks
            if ax.legend():
                ax.legend(fontsize=16)  # Melhorar a visibilidade da legenda

        # Aumentar os números dentro do gráfico (valores nos pontos ou barras)
        for text in ax.texts:
            text.set_fontsize(18)  # Ajuste conforme necessário
            text.set_fontweight("bold")  # Deixar os números mais visíveis

        # Salvar gráfico como imagem
        img_data = BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight')
        img_data.seek(0)

        # Posição e tamanho do gráfico
        x_position = position_and_size['x']
        y_position = position_and_size['y']
        graph_width = position_and_size['width']
        graph_height = position_and_size['height']

        # Inserir gráfico na posição e tamanho definidos
        c.drawImage(ImageReader(img_data), x_position, y_position, width=graph_width, height=graph_height)
        graph_index += 1


    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

# Caminho para as imagens de fundo
background_image_first_page_tratores = 'Aplicação.png'
background_image_other_pages = 'outraspáginas.png'

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

            # Ordenar o DataFrame com base na soma da área aplicada
            df_soma_haaplicada = df_soma_haaplicada.sort_values(by="Área Aplicada", ascending=True)  # Ordem crescente para horizontal

            # Configurar o gráfico
            fig_haaplicada_aplicacao, ax_haaplicada = plt.subplots(figsize=(12, 9))

            # Extrair dados para plotagem
            maquinas_haaplicada = df_soma_haaplicada["Nome da Máquina"]
            haaplicada = df_soma_haaplicada["Área Aplicada"]

            # Definir a altura das barras
            num_maquinas = len(maquinas_haaplicada)
            bar_height = 0.2 if num_maquinas >= 3 else 0.4  # Se houver menos de 3 equipamentos, usar barras mais largas

            # Plotar barras horizontais
            bars = ax_haaplicada.barh(maquinas_haaplicada, haaplicada, color='limegreen', height=bar_height)

            # Adicionar valores ao lado das barras
            for bar, area in zip(bars, haaplicada):
                ax_haaplicada.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2, 
                                    f'{area:.2f} ha', ha='left', va='center', fontsize=10, fontweight='bold')

            # Configurar os eixos e título
            ax_haaplicada.set_xlabel('')
            ax_haaplicada.set_ylabel('')
            ax_haaplicada.set_title('Área Aplicada por Equipamento (ha)')

            # Remover moldura superior e direita para um visual mais limpo
            ax_haaplicada.spines['top'].set_visible(False)
            ax_haaplicada.spines['right'].set_visible(False)

            # Mostrar o gráfico no Streamlit
            col4, col5 = st.columns(2)
            col4.pyplot(fig_haaplicada_aplicacao)



            #########################MÉDIA TAXA ALVO E TAXA APLICADA###################################
            # Definir os dados
            selected_columns_taxas = ["Nome da Máquina", "Taxa Aplicada", "Taxa Alvo"]
            df_selected_taxas = df_aplicacao.copy()

            # Verificar se as colunas existem e, se não existirem, adicionar com valores 0
            if "Taxa Aplicada" not in df_selected_taxas.columns:
                df_selected_taxas["Taxa Aplicada"] = 0  

            if "Taxa Alvo" not in df_selected_taxas.columns:
                df_selected_taxas["Taxa Alvo"] = 0  

            # Converter as colunas para numéricas, tratando erros
            df_selected_taxas["Taxa Aplicada"] = pd.to_numeric(df_selected_taxas["Taxa Aplicada"], errors='coerce').fillna(0)
            df_selected_taxas["Taxa Alvo"] = pd.to_numeric(df_selected_taxas["Taxa Alvo"], errors='coerce').fillna(0)

            # Calcular as médias da Taxa Aplicada e Taxa Alvo por Máquina
            df_medias_taxas = df_selected_taxas.groupby("Nome da Máquina")[["Taxa Aplicada", "Taxa Alvo"]].mean().reset_index()

            # Calcular as médias gerais
            media_taxa_aplicada = df_medias_taxas["Taxa Aplicada"].mean()
            media_taxa_alvo = df_medias_taxas["Taxa Alvo"].mean()

            # Configurar o gráfico
            fig_taxa_aplicacao, ax_taxas = plt.subplots(figsize=(12, 8))

            # Definir a largura das barras
            bar_width = 0.35  
            posicoes = range(len(df_medias_taxas))

            # Plotar as barras verticais
            bars1 = ax_taxas.bar(posicoes, df_medias_taxas["Taxa Aplicada"], width=bar_width, color='midnightblue', label='Taxa Aplicada')
            bars2 = ax_taxas.bar([p + bar_width for p in posicoes], df_medias_taxas["Taxa Alvo"], width=bar_width, color='dodgerblue', label='Taxa Alvo')

            # Adicionar rótulos nas barras
            for bar in bars1:
                height = bar.get_height()
                ax_taxas.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

            for bar in bars2:
                height = bar.get_height()
                ax_taxas.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

            # Configurar os eixos e rótulos
            ax_taxas.set_xticks([p + bar_width / 2 for p in posicoes])  
            ax_taxas.set_xticklabels(df_medias_taxas["Nome da Máquina"], rotation=45, ha='right')

            ax_taxas.set_xlabel('')
            ax_taxas.set_ylabel('')
            ax_taxas.set_title('Taxa Aplicada vs Taxa Alvo por Máquina')

            # Adicionar legenda
            ax_taxas.legend(loc='upper right')
            col5.pyplot(fig_taxa_aplicacao)
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
            fig_mediaVelocidade_aplicacao, ax_Velocidade = plt.subplots(figsize=(12, 8))

            # Definir as posições das barras
            posicoes = range(len(df_medias_Velocidade))

            # Plotar as barras verticais
            bars = ax_Velocidade.bar(posicoes, df_medias_Velocidade["Velocidade"], color='goldenrod', label='Velocidade')

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
            ax_Velocidade.set_title('Média de Velocidade por equipamento')

            # Adicionar legenda
            #ax_Velocidade.legend(loc='upper right', bbox_to_anchor=(1.24, 1.0))
            col6, col7 = st.columns(2)
            col6.pyplot(fig_mediaVelocidade_aplicacao)
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

            # Calcular a média geral da Eficiência Operacional
            media_geral = df_medias_eficiencia["Eficiência Operacional"].mean()

            # Configurar o gráfico
            fig_eficiencia_aplicacao, ax_eficiencia = plt.subplots(figsize=(12, 8.5))

            # Definir as posições das barras
            posicoes = range(len(df_medias_eficiencia))

            # Plotar as barras verticais
            bars = ax_eficiencia.bar(posicoes, df_medias_eficiencia["Eficiência Operacional"], color='darkolivegreen', label='Eficiência Operacional')

            # Adicionar os rótulos das máquinas
            ax_eficiencia.set_xticks(posicoes)
            ax_eficiencia.set_xticklabels(df_medias_eficiencia["Nome da Máquina"], rotation=45, ha='right')

            # Adicionar os números de eficiência no topo de cada barra
            for bar in bars:
                height = bar.get_height()
                ax_eficiencia.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='Black')

            # Adicionar linha horizontal representando a média geral
            ax_eficiencia.axhline(media_geral, color='darkslategray', linestyle='dashed', linewidth=2, label='Média Geral')

            # Adicionar o valor da média à esquerda do gráfico
            ax_eficiencia.text(-0.6, media_geral, f'Média: {media_geral:.2f}', va='center', ha='right', fontsize=12, fontweight='bold', color='darkslategray')

            # Configurar os eixos e título
            ax_eficiencia.set_xlabel('')
            ax_eficiencia.set_ylabel('')
            ax_eficiencia.set_title('Média de Eficiência Operacional (ha/h)')

            # Exibir legenda
            ax_eficiencia.legend()

            # Exibir o gráfico no Streamlit
            col7.pyplot(fig_eficiencia_aplicacao)

            ##############################################MÉDIA COMBUSTIVEL#################################
            # Definir os dados
            selected_columns_combustivel = ["Nome da Máquina", "Taxa de Combustível (Área)"]
            df_selected_combustivel = df_aplicacao.copy()

            # Garantir que a coluna "Taxa de Combustível (Área)" existe
            if "Taxa de Combustível (Área)" not in df_selected_combustivel.columns:
                df_selected_combustivel["Taxa de Combustível (Área)"] = 0  # Criar a coluna se não existir

            # Converter a coluna para numérico e tratar NaN
            df_selected_combustivel["Taxa de Combustível (Área)"] = pd.to_numeric(
                df_selected_combustivel["Taxa de Combustível (Área)"], errors='coerce'
            ).fillna(0)

            # Calcular a média da Taxa de Combustível por Máquina
            df_medias_combustivel = df_selected_combustivel.groupby("Nome da Máquina")["Taxa de Combustível (Área)"].mean().reset_index()
            df_medias_combustivel = df_medias_combustivel.sort_values(by="Taxa de Combustível (Área)", ascending=False)


            # Configurar o gráfico de linhas
            fig_media_combustivel_aplicacao, ax_combustivel = plt.subplots(figsize=(12, 8))
            
            # Plotar a linha com marcadores
            ax_combustivel.plot(df_medias_combustivel["Nome da Máquina"], 
                                df_medias_combustivel["Taxa de Combustível (Área)"], 
                                marker='o', linestyle='-', color='mediumblue', label='Média de Combustível')

            # Adicionar rótulos nos pontos da linha
            for i, row in df_medias_combustivel.iterrows():
                ax_combustivel.text(row["Nome da Máquina"], row["Taxa de Combustível (Área)"] + 0.2, 
                                    f'{row["Taxa de Combustível (Área)"]:.1f}', 
                                    ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

            # Configurar eixos e título
            ax_combustivel.set_xlabel('')
            ax_combustivel.set_ylabel('')
            ax_combustivel.set_title('Média de Combustível por Equipamento (l/ha)')

            # Adicionar grade
            ax_combustivel.grid(True, linestyle='--', alpha=0.7)

            # Adicionar legenda
            ax_combustivel.legend()

            # Exibir no Streamlit
            col8, col9 = st.columns(2)
            col8.pyplot(fig_media_combustivel_aplicacao)
            ##############################################SOMA COMBUSTIVEL#################################

            selected_columns_combustivel = ["Nome da Máquina", "Combustível Total"]
            df_selected_combustivel = df_aplicacao.copy()

            # Selecionar colunas relevantes
            selected_columns_haaplicada = ["Nome da Máquina", "Combustível Total"]
            df_selected_haaplicada = df_aplicacao[selected_columns_haaplicada].copy()

            # Verificar se os dados estão carregados corretamente
            #st.write("Pré-processamento - Dados Selecionados:", df_selected_haaplicada)

            # Garantir que "Combustível Total" seja numérico
            df_selected_haaplicada["Combustível Total"] = pd.to_numeric(df_selected_haaplicada["Combustível Total"], errors="coerce")

            # Verificar se há valores NaN
            #if df_selected_haaplicada["Combustível Total"].isna().sum() > 0:
                #st.error("Há valores inválidos em 'Combustível Total'!")

            # Agrupar os dados por "Nome da Máquina" e somar "Combustível Total"
            df_soma_haaplicada = df_selected_haaplicada.groupby("Nome da Máquina", as_index=False)["Combustível Total"].sum()

            # Verificar se o agrupamento foi bem-sucedido
            #st.write("Dados Agrupados:", df_soma_haaplicada)

            # Verificar se a coluna "Combustível Total" existe após agrupamento
            if "Combustível Total" not in df_soma_haaplicada.columns:
                st.error("Erro: A coluna 'Combustível Total' não foi encontrada após a agregação.")
                st.stop()

            # Ordenar o DataFrame
            df_soma_haaplicada = df_soma_haaplicada.sort_values(by="Combustível Total", ascending=False)

            # Configurar o gráfico
            fig_somacombustivel_aplicacao, ax_haaplicada = plt.subplots(figsize=(12, 8))

            # Extrair dados para plotagem
            maquinas_haaplicada = df_soma_haaplicada["Nome da Máquina"]
            haaplicada = df_soma_haaplicada["Combustível Total"]

            # Definir a largura das barras
            #num_maquinas = len(maquinas_haaplicada)
           # bar_width = 0.2 if num_maquinas >= 3 else 0.4  

            # Criar gráfico de barras
            bars = ax_haaplicada.bar(maquinas_haaplicada, haaplicada, color='dodgerblue', width=bar_width)

            # Adicionar valores nas barras
            for bar, area in zip(bars, haaplicada):
                ax_haaplicada.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, 
                                    f'{area:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

            # Configuração do gráfico
            ax_haaplicada.set_xlabel('')
            ax_haaplicada.set_ylabel('')
            ax_haaplicada.set_title('Combustível Total gasto por Equipamento')
            ax_haaplicada.set_xticklabels(maquinas_haaplicada, rotation=45, ha='right')

            # Exibir gráfico no Streamlit
            col9.pyplot(fig_somacombustivel_aplicacao)

            ###################################################GERAR PDF##################################################
            if st.button('Gerar PDF para Aplicação'):
                # Supondo que 'Nome_Organizacao' seja uma coluna no dataframe 
                first_organization_name = df_aplicacao['Clientes'].iloc[0].split()[0]

                # Gerar o PDF
                figures = [fig_haaplicada_aplicacao,fig_mediaVelocidade_aplicacao,fig_eficiencia_aplicacao, fig_media_combustivel_aplicacao, fig_taxa_aplicacao ,fig_somacombustivel_aplicacao]
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