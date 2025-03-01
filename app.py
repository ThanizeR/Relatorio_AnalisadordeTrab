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
        

def generate_pdf_aplicacao(df_aplicacao, figures, background_image_first_page_aplicacao=None, background_image_other_pages=None):
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
        {'name': 'fig_haaplicada_aplicacao','x': x_margin, 'y': page_height - y_margin - 270, 'width': 270, 'height': 200},  # Gráfico 1

        # Gráficos 2, 3, 4 (à direita do gráfico 1)
        {'name': 'fig_mediaVelocidade_aplicacao','x': x_margin + 270, 'y': page_height - y_margin - 250, 'width': 250, 'height': 200},  # Gráfico 2
        {'name': 'fig_eficiencia_aplicacao','x': x_margin + 270, 'y': page_height - y_margin - 470, 'width': 250, 'height': 200},  # Gráfico 3
        {'name': 'fig_media_combustivel_aplicacao','x': x_margin + 290, 'y': page_height - y_margin - 678, 'width': 235, 'height': 200},  # Gráfico 4

        # Gráfico 5 (pequeno abaixo do gráfico 1)
        {'name': 'fig_taxa_aplicacao','x': x_margin, 'y': page_height - y_margin - 492, 'width': 250, 'height': 200},  # Gráfico 5

        # Gráfico 6 (comprido no final da página)
        {'name': 'fig_somacombustivel_aplicacao','x': x_margin, 'y': page_height - y_margin - 700, 'width': 250, 'height': 200},  # Gráfico 6 (comprido)
    ]


    def set_background(page_num):
        if page_num == 0 and background_image_first_page_aplicacao:
            background = ImageReader(background_image_first_page_aplicacao)
        elif background_image_other_pages:
            background = ImageReader(background_image_other_pages)
        else:
            return
        c.drawImage(background, 0, 0, width=page_width, height=page_height)

    # Primeira página (capa)
    set_background(0)

    # Adicionar informações de cliente e datas na primeira página
    if 'Clientes' in df_aplicacao.columns:
        cliente = df_aplicacao['Clientes'].iloc[0]
        c.setFillColorRGB(1, 1, 1)  # Cor branca (RGB: 1, 1, 1)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_margin, page_height - 100, f"Cliente: {cliente}")
    try:
        if 'Primeiro Aplicado' in df_aplicacao.columns:
            df_aplicacao['Primeiro Aplicado'] = pd.to_datetime(df_aplicacao['Primeiro Aplicado'], errors='coerce')
            primeiro_aplicado = df_aplicacao['Primeiro Aplicado'].min()
            primeiro_aplicado_str = primeiro_aplicado.strftime('%d/%m/%Y') if pd.notnull(primeiro_aplicado) else "Data inválida"

        if 'Última Aplicação' in df_aplicacao.columns:
            df_aplicacao['Última Aplicação'] = pd.to_datetime(df_aplicacao['Última Aplicação'], errors='coerce')
            ultima_aplicacao = df_aplicacao['Última Aplicação'].max()
            ultima_aplicacao_str = ultima_aplicacao.strftime('%d/%m/%Y') if pd.notnull(ultima_aplicacao) else "Data inválida"
        c.setFillColorRGB(1, 1, 1)  # Cor branca (RGB: 1, 1, 1)
        # Adicionar informações ao PDF na primeira página
        c.drawString(x_margin, page_height - 120, f"Data inicial: {primeiro_aplicado_str}")
        c.drawString(x_margin, page_height - 140, f"Data final: {ultima_aplicacao_str}")

    except Exception as e:
        print(f"Erro ao processar datas: {e}")

    c.showPage()  # Nova página para os gráficos e informações adicionais

    # Segunda página
    set_background(1)

    try:
        # Calcular métricas
        df_aplicacao['Área Aplicada'] = pd.to_numeric(df_aplicacao['Área Aplicada'], errors='coerce')
        df_aplicacao['Combustível Total'] = pd.to_numeric(df_aplicacao['Combustível Total'], errors='coerce')

        area_total_aplicada = df_aplicacao['Área Aplicada'].sum()
        combustivel_total = df_aplicacao['Combustível Total'].sum()
        total_equipamentos = df_aplicacao['Nome da Máquina'].nunique()

        # Formatar os números manualmente no formato brasileiro (com separador de milhar e vírgula para decimal)
        area_total_aplicada_formatada = f"{area_total_aplicada:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        combustivel_total_formatado = f"{combustivel_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # Adicionar informações na segunda página
        c.setFont("Helvetica", 8)
        c.drawString(x_margin, page_height - 40, f"Área Total Aplicada: {area_total_aplicada_formatada} ha")
        c.drawString(x_margin, page_height - 60, f"Combustível Total: {combustivel_total_formatado} L")
        c.drawString(x_margin, page_height - 80, f"Total de Equipamentos: {total_equipamentos}")


    except Exception as e:
        print(f"Erro ao calcular ou formatar os dados: {e}")

    # Adicionar gráficos na segunda página
    graph_index = 0
    for position_and_size in graph_positions_and_sizes:
        if graph_index >= len(figures):
            break

        fig = figures[graph_index]

        if not isinstance(fig, plt.Figure):
            print(f"Skipping non-Matplotlib figure: {type(fig)}")
            graph_index += 1
            continue

        # Ajustando o tamanho das fontes dos gráficos
        for ax in fig.get_axes():
            ax.title.set_fontsize(20)
            ax.xaxis.label.set_fontsize(20)
            ax.yaxis.label.set_fontsize(20)
            ax.tick_params(axis='both', labelsize=18)
            if ax.legend():
                ax.legend(fontsize=12)

        # Ajuste de números dentro dos gráficos
        for text in ax.texts:
            text.set_fontsize(18)
            text.set_fontweight("bold")

        # Salvar gráfico como imagem
        img_data = BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight')
        img_data.seek(0)

        # Inserir gráfico no PDF
        x_position = position_and_size['x']
        y_position = position_and_size['y']
        graph_width = position_and_size['width']
        graph_height = position_and_size['height']

        c.drawImage(ImageReader(img_data), x_position, y_position, width=graph_width, height=graph_height)
        graph_index += 1

    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

background_image_first_page_aplicacao = 'Aplicação.png'

def generate_pdf_colheita(df_colheita, figures, background_image_first_page_colheita=None, background_image_other_pages=None):
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
        {'name': 'fig_hacolhida','x': x_margin, 'y': page_height - y_margin - 270, 'width': 270, 'height': 200},  # Gráfico 1

        # Gráficos 2, 3, 4 (à direita do gráfico 1)
        {'name': 'fig_taxa_colheita','x': x_margin + 270, 'y': page_height - y_margin - 175, 'width': 250, 'height': 200},  # Gráfico 2
        {'name': 'fig_mediaVelocidade_colheita','x': x_margin + 270, 'y': page_height - y_margin - 380, 'width': 250, 'height': 200},  # Gráfico 3
        {'name': 'fig_eficiencia_colheita','x': x_margin + 270, 'y': page_height - y_margin - 600, 'width': 250, 'height': 200},  # Gráfico 4

        # Gráfico 5: Mais comprido e à esquerda
        {'name': 'fig_somacombustivel_colheita', 'x': x_margin, 'y': page_height - y_margin - 510, 'width': 250, 'height': 200},  

        # Gráfico 6: Mais para baixo e mais à esquerda (centralizado mais à esquerda)
        {'name': 'fig_hacolhida_cultura', 'x': x_margin + 310, 'y': page_height - y_margin - 760, 'width': 200, 'height': 130},  

        # Gráfico 6 (comprido no final da página)
        {'name': 'fig_media_combustivel_colheita','x': x_margin, 'y': page_height - y_margin - 740, 'width': 250, 'height': 200},  # Gráfico 7 (comprido)
    ]


    def set_background(page_num):
        if page_num == 0 and background_image_first_page_colheita:
            background = ImageReader(background_image_first_page_colheita)
        elif background_image_other_pages:
            background = ImageReader(background_image_other_pages)
        else:
            return
        c.drawImage(background, 0, 0, width=page_width, height=page_height)

    # Primeira página (capa)
    set_background(0)

    # Adicionar informações de cliente e datas na primeira página
    if 'Clientes' in df_colheita.columns:
        cliente = df_colheita['Clientes'].iloc[0]
        c.setFillColorRGB(1, 1, 1)  # Cor branca (RGB: 1, 1, 1)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_margin, page_height - 100, f"Cliente: {cliente}")
    try:
        if 'Primeiro Colhido' in df_colheita.columns:
            df_colheita['Primeiro Colhido'] = pd.to_datetime(df_colheita['Primeiro Colhido'], errors='coerce')
            primeiro_aplicado = df_colheita['Primeiro Colhido'].min()
            primeiro_aplicado_str = primeiro_aplicado.strftime('%d/%m/%Y') if pd.notnull(primeiro_aplicado) else "Data inválida"

        if 'Última Colheita' in df_colheita.columns:
            df_colheita['Última Colheita'] = pd.to_datetime(df_colheita['Última Colheita'], errors='coerce')
            ultima_aplicacao = df_colheita['Última Colheita'].max()
            ultima_aplicacao_str = ultima_aplicacao.strftime('%d/%m/%Y') if pd.notnull(ultima_aplicacao) else "Data inválida"
        c.setFillColorRGB(1, 1, 1)  # Cor branca (RGB: 1, 1, 1)
        # Adicionar informações ao PDF na primeira página
        c.drawString(x_margin, page_height - 120, f"Data inicial: {primeiro_aplicado_str}")
        c.drawString(x_margin, page_height - 140, f"Data final: {ultima_aplicacao_str}")

    except Exception as e:
        print(f"Erro ao processar datas: {e}")

    c.showPage()  # Nova página para os gráficos e informações adicionais

    # Segunda página
    set_background(1)

    try:
        # Calcular métricas
        df_colheita['Área Colhida'] = pd.to_numeric(df_colheita['Área Colhida'], errors='coerce')
        df_colheita['Combustível Total'] = pd.to_numeric(df_colheita['Combustível Total'], errors='coerce')

        area_total_aplicada = df_colheita['Área Colhida'].sum()
        combustivel_total = df_colheita['Combustível Total'].sum()
        total_equipamentos = df_colheita['Nome da Máquina'].nunique()

        # Formatar os números com a localidade brasileira
        area_total_aplicada_formatada = f"{area_total_aplicada:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        combustivel_total_formatado = f"{combustivel_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        c.setFont("Helvetica", 8)
        c.drawString(x_margin, page_height - 40, f"Área Total Colhida: {area_total_aplicada_formatada} ha")
        c.drawString(x_margin, page_height - 60, f"Combustível Total: {combustivel_total_formatado} L")
        c.drawString(x_margin, page_height - 80, f"Total de Equipamentos: {total_equipamentos}")

    except Exception as e:
        print(f"Erro ao calcular ou formatar os dados: {e}")

    # Adicionar gráficos na segunda página
    graph_index = 0
    for position_and_size in graph_positions_and_sizes:
        if graph_index >= len(figures):
            break

        fig = figures[graph_index]

        if not isinstance(fig, plt.Figure):
            print(f"Skipping non-Matplotlib figure: {type(fig)}")
            graph_index += 1
            continue

        # Ajustando o tamanho das fontes dos gráficos
        for ax in fig.get_axes():
            ax.title.set_fontsize(20)
            ax.xaxis.label.set_fontsize(20)
            ax.yaxis.label.set_fontsize(20)
            ax.tick_params(axis='both', labelsize=18)
            if ax.legend():
                ax.legend(fontsize=12)

        # Ajuste de números dentro dos gráficos
        for text in ax.texts:
            text.set_fontsize(18)
            text.set_fontweight("bold")

        # Salvar gráfico como imagem
        img_data = BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight')
        img_data.seek(0)

        # Inserir gráfico no PDF
        x_position = position_and_size['x']
        y_position = position_and_size['y']
        graph_width = position_and_size['width']
        graph_height = position_and_size['height']

        c.drawImage(ImageReader(img_data), x_position, y_position, width=graph_width, height=graph_height)
        graph_index += 1

    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer
background_image_first_page_colheita = 'Colheita.png'
# Caminho para as imagens de fundo

def generate_pdf_semeadura(df_semeadura, figures, background_image_first_page_semeadura=None, background_image_other_pages=None):
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
        {'name': 'fig_haaplicada_aplicacao','x': x_margin, 'y': page_height - y_margin - 270, 'width': 270, 'height': 200},  # Gráfico 1

        # Gráficos 2, 3, 4 (à direita do gráfico 1)
        {'name': 'fig_mediaVelocidade_aplicacao','x': x_margin + 270, 'y': page_height - y_margin - 290, 'width': 250, 'height': 200},  # Gráfico 2
        {'name': 'fig_eficiencia_aplicacao','x': x_margin + 310, 'y': page_height - y_margin - 480, 'width': 200, 'height': 140},  # Gráfico 3
        {'name': 'fig_media_combustivel_aplicacao','x': x_margin + 290, 'y': page_height - y_margin - 700, 'width': 250, 'height': 200},  # Gráfico 4

        # Gráfico 5 (pequeno abaixo do gráfico 1)
        {'name': 'fig_taxa_aplicacao','x': x_margin, 'y': page_height - y_margin - 492, 'width': 250, 'height': 200},  # Gráfico 5

        # Gráfico 6 (comprido no final da página)
        {'name': 'fig_somacombustivel_aplicacao','x': x_margin, 'y': page_height - y_margin - 700, 'width': 250, 'height': 200},  # Gráfico 6 (comprido)
    ]



    def set_background(page_num):
        if page_num == 0 and background_image_first_page_semeadura:
            background = ImageReader(background_image_first_page_semeadura)
        elif background_image_other_pages:
            background = ImageReader(background_image_other_pages)
        else:
            return
        c.drawImage(background, 0, 0, width=page_width, height=page_height)

    # Primeira página (capa)
    set_background(0)

    # Adicionar informações de cliente e datas na primeira página
    if 'Clientes' in df_semeadura.columns:
        cliente = df_semeadura['Clientes'].iloc[0]
        c.setFillColorRGB(1, 1, 1)  # Cor branca (RGB: 1, 1, 1)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_margin, page_height - 100, f"Cliente: {cliente}")
    try:
        if 'Primeiro Semeado' in df_semeadura.columns:
            df_semeadura['Primeiro Semeado'] = pd.to_datetime(df_semeadura['Primeiro Semeado'], errors='coerce')
            primeiro_aplicado = df_semeadura['Primeiro Semeado'].min()
            primeiro_aplicado_str = primeiro_aplicado.strftime('%d/%m/%Y') if pd.notnull(primeiro_aplicado) else "Data inválida"

        if 'Última Semeadura' in df_semeadura.columns:
            df_semeadura['Última Semeadura'] = pd.to_datetime(df_semeadura['Última Semeadura'], errors='coerce')
            ultima_aplicacao = df_semeadura['Última Semeadura'].max()
            ultima_aplicacao_str = ultima_aplicacao.strftime('%d/%m/%Y') if pd.notnull(ultima_aplicacao) else "Data inválida"
        c.setFillColorRGB(1, 1, 1)  # Cor branca (RGB: 1, 1, 1)
        # Adicionar informações ao PDF na primeira página
        c.drawString(x_margin, page_height - 120, f"Data inicial: {primeiro_aplicado_str}")
        c.drawString(x_margin, page_height - 140, f"Data final: {ultima_aplicacao_str}")

    except Exception as e:
        print(f"Erro ao processar datas: {e}")

    c.showPage()  # Nova página para os gráficos e informações adicionais

    # Segunda página
    set_background(1)

    try:
        # Calcular métricas
        df_semeadura['Área Semeada'] = pd.to_numeric(df_semeadura['Área Semeada'], errors='coerce')
        df_semeadura['Combustível Total'] = pd.to_numeric(df_semeadura['Combustível Total'], errors='coerce')

        area_total_aplicada = df_semeadura['Área Semeada'].sum()
        combustivel_total = df_semeadura['Combustível Total'].sum()
        total_equipamentos = df_semeadura['Nome da Máquina'].nunique()

        # Formatar os números com a localidade brasileira
        area_total_aplicada_formatada = f"{area_total_aplicada:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        combustivel_total_formatado = f"{combustivel_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # Adicionar informações na segunda página
        c.setFont("Helvetica", 8)
        c.drawString(x_margin, page_height - 40, f"Área Total Semeada: {area_total_aplicada_formatada} ha")
        c.drawString(x_margin, page_height - 60, f"Combustível Total: {combustivel_total_formatado} L")
        c.drawString(x_margin, page_height - 80, f"Total de Equipamentos: {total_equipamentos}")

    except Exception as e:
        print(f"Erro ao calcular ou formatar os dados: {e}")

    # Adicionar gráficos na segunda página
    graph_index = 0
    for position_and_size in graph_positions_and_sizes:
        if graph_index >= len(figures):
            break

        fig = figures[graph_index]

        if not isinstance(fig, plt.Figure):
            print(f"Skipping non-Matplotlib figure: {type(fig)}")
            graph_index += 1
            continue

        # Ajustando o tamanho das fontes dos gráficos
        for ax in fig.get_axes():
            ax.title.set_fontsize(20)
            ax.xaxis.label.set_fontsize(20)
            ax.yaxis.label.set_fontsize(20)
            ax.tick_params(axis='both', labelsize=18)
            if ax.legend():
                ax.legend(fontsize=12)

        # Ajuste de números dentro dos gráficos
        for text in ax.texts:
            text.set_fontsize(18)
            text.set_fontweight("bold")

        # Salvar gráfico como imagem
        img_data = BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight')
        img_data.seek(0)

        # Inserir gráfico no PDF
        x_position = position_and_size['x']
        y_position = position_and_size['y']
        graph_width = position_and_size['width']
        graph_height = position_and_size['height']

        c.drawImage(ImageReader(img_data), x_position, y_position, width=graph_width, height=graph_height)
        graph_index += 1

    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

background_image_first_page_semeadura = 'Semeadura.png'


def generate_pdf_preparo(df_preparo, figures, background_image_first_page_aplicacao=None, background_image_other_pages=None):
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
        {'name': 'fig_haaplicada_aplicacao','x': x_margin, 'y': page_height - y_margin - 270, 'width': 270, 'height': 200},  # Gráfico 1

        # Gráficos 2, 3, 4 (à direita do gráfico 1)
        {'name': 'fig_mediaVelocidade_aplicacao','x': x_margin + 270, 'y': page_height - y_margin - 250, 'width': 250, 'height': 200},  # Gráfico 2
        {'name': 'fig_eficiencia_aplicacao','x': x_margin + 270, 'y': page_height - y_margin - 470, 'width': 250, 'height': 200},  # Gráfico 3

        # Gráfico 5 (pequeno abaixo do gráfico 1)
        {'name': 'fig_taxa_aplicacao','x': x_margin, 'y': page_height - y_margin - 492, 'width': 250, 'height': 200},  # Gráfico 5

        # Gráfico 6 (comprido no final da página)
        {'name': 'fig_somacombustivel_aplicacao','x': x_margin, 'y': page_height - y_margin - 700, 'width': 250, 'height': 200},  # Gráfico 6 (comprido)
    ]


    def set_background(page_num):
        if page_num == 0 and background_image_first_page_preparo:
            background = ImageReader(background_image_first_page_aplicacao)
        elif background_image_other_pages:
            background = ImageReader(background_image_other_pages)
        else:
            return
        c.drawImage(background, 0, 0, width=page_width, height=page_height)

    # Primeira página (capa)
    set_background(0)

    # Adicionar informações de cliente e datas na primeira página
    if 'Clientes' in df_preparo.columns:
        cliente = df_preparo['Clientes'].iloc[0]
        c.setFillColorRGB(1, 1, 1)  # Cor branca (RGB: 1, 1, 1)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(x_margin, page_height - 100, f"Cliente: {cliente}")
    try:
        if 'Primeiro Cultivado' in df_preparo.columns:
            df_preparo['Primeiro Cultivado'] = pd.to_datetime(df_preparo['Primeiro Cultivado'], errors='coerce')
            primeiro_aplicado = df_preparo['Primeiro Cultivado'].min()
            primeiro_aplicado_str = primeiro_aplicado.strftime('%d/%m/%Y') if pd.notnull(primeiro_aplicado) else "Data inválida"

        if 'Última Preparo do Solo' in df_preparo.columns:
            df_preparo['Última Preparo do Solo'] = pd.to_datetime(df_preparo['Última Preparo do Solo'], errors='coerce')
            ultima_aplicacao = df_preparo['Último Preparo do Solo'].max()
            ultima_aplicacao_str = ultima_aplicacao.strftime('%d/%m/%Y') if pd.notnull(ultima_aplicacao) else "Data inválida"
        c.setFillColorRGB(1, 1, 1)  # Cor branca (RGB: 1, 1, 1)
        # Adicionar informações ao PDF na primeira página
        c.drawString(x_margin, page_height - 120, f"Data inicial: {primeiro_aplicado_str}")
        c.drawString(x_margin, page_height - 140, f"Data final: {ultima_aplicacao_str}")

    except Exception as e:
        print(f"Erro ao processar datas: {e}")

    c.showPage()  # Nova página para os gráficos e informações adicionais

    # Segunda página
    set_background(1)

    try:
        # Calcular métricas
        df_preparo['Área Cultivada'] = pd.to_numeric(df_preparo['Área Cultivada'], errors='coerce')
        df_preparo['Combustível Total'] = pd.to_numeric(df_preparo['Combustível Total'], errors='coerce')

        area_total_aplicada = df_preparo['Área Cultivada'].sum()
        combustivel_total = df_preparo['Combustível Total'].sum()
        total_equipamentos = df_preparo['Nome da Máquina'].nunique()

        # Formatar os números com a localidade brasileira
        area_total_aplicada_formatada = f"{area_total_aplicada:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        combustivel_total_formatado = f"{combustivel_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        # Adicionar informações na segunda página
        c.setFont("Helvetica", 8)
        c.drawString(x_margin, page_height - 40, f"Área Total Cultivada: {area_total_aplicada_formatada} ha")
        c.drawString(x_margin, page_height - 60, f"Combustível Total: {combustivel_total_formatado} L")
        c.drawString(x_margin, page_height - 80, f"Total de Equipamentos: {total_equipamentos}")

    except Exception as e:
        print(f"Erro ao calcular ou formatar os dados: {e}")

    # Adicionar gráficos na segunda página
    graph_index = 0
    for position_and_size in graph_positions_and_sizes:
        if graph_index >= len(figures):
            break

        fig = figures[graph_index]

        if not isinstance(fig, plt.Figure):
            print(f"Skipping non-Matplotlib figure: {type(fig)}")
            graph_index += 1
            continue

        # Ajustando o tamanho das fontes dos gráficos
        for ax in fig.get_axes():
            ax.title.set_fontsize(20)
            ax.xaxis.label.set_fontsize(20)
            ax.yaxis.label.set_fontsize(20)
            ax.tick_params(axis='both', labelsize=18)
            if ax.legend():
                ax.legend(fontsize=12)

        # Ajuste de números dentro dos gráficos
        for text in ax.texts:
            text.set_fontsize(18)
            text.set_fontweight("bold")

        # Salvar gráfico como imagem
        img_data = BytesIO()
        fig.savefig(img_data, format='png', bbox_inches='tight')
        img_data.seek(0)

        # Inserir gráfico no PDF
        x_position = position_and_size['x']
        y_position = position_and_size['y']
        graph_width = position_and_size['width']
        graph_height = position_and_size['height']

        c.drawImage(ImageReader(img_data), x_position, y_position, width=graph_width, height=graph_height)
        graph_index += 1

    c.showPage()
    c.save()
    pdf_buffer.seek(0)
    return pdf_buffer

background_image_first_page_preparo = 'Preparo de Solo.png'
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
            
            # Exibir organização (cliente)
            if 'Clientes' in df_aplicacao.columns:
                organização = df_aplicacao['Clientes'].iloc[0]

                col1, col2, col3, col4 = st.columns(4)
                col1.write(f"**Organização:** {organização}")

                # Garantir que os valores sejam numéricos antes de somar
                df_aplicacao['Área Aplicada'] = pd.to_numeric(df_aplicacao['Área Aplicada'], errors='coerce')
                df_aplicacao['Combustível Total'] = pd.to_numeric(df_aplicacao['Combustível Total'], errors='coerce')

                # Cálculo dos totais
                area_total_aplicada = df_aplicacao['Área Aplicada'].sum()
                combustivel_total = df_aplicacao['Combustível Total'].sum()
                total_equipamentos = df_aplicacao['Nome da Máquina'].nunique()

                # Exibir os valores nas colunas restantes
                col2.write(f"**Área Total Aplicada:** {area_total_aplicada:.2f} ha")
                col3.write(f"**Combustível Total Consumido:** {combustivel_total:.2f} L")
                col4.write(f"**Total de Equipamentos:** {total_equipamentos}")

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
            col5, col6 = st.columns(2)
            col5.pyplot(fig_haaplicada_aplicacao)



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
            col6.pyplot(fig_taxa_aplicacao)
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

            ax_Velocidade.set_ylim(0, df_medias_Velocidade["Velocidade"].max() * 1.1)

            # Adicionar os números de eficiência no topo de cada barra
            for bar in bars:
                height = bar.get_height()
                ax_Velocidade.text(bar.get_x() + bar.get_width() / 2, height, f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold', color='Black')

            # Configurar os eixos e título
            ax_Velocidade.set_xlabel('')
            ax_Velocidade.set_ylabel('')
            ax_Velocidade.set_title('Média de Velocidade por equipamento')

            plt.subplots_adjust(top=0.9)

            # Adicionar legenda
            col7, col8 = st.columns(2)
            col7.pyplot(fig_mediaVelocidade_aplicacao)
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
            #ax_eficiencia.legend()

            # Exibir o gráfico no Streamlit
            col8.pyplot(fig_eficiencia_aplicacao)

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

            ax_combustivel.set_ylim(0, df_medias_combustivel["Taxa de Combustível (Área)"].max() * 1.1)

            # Adicionar rótulos nos pontos da linha
            for i, row in df_medias_combustivel.iterrows():
                ax_combustivel.text(row["Nome da Máquina"], row["Taxa de Combustível (Área)"] + 0.2, 
                                    f'{row["Taxa de Combustível (Área)"]:.1f}', 
                                    ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

            # Configurar eixos e título
            ax_combustivel.set_xlabel('')
            ax_combustivel.set_ylabel('')
            ax_combustivel.set_title('Média de Combustível por Equipamento (l/ha)')

            plt.subplots_adjust(top=0.9)

            # Adicionar grade
            ax_combustivel.grid(True, linestyle='--', alpha=0.7)

            # Adicionar legenda
            ax_combustivel.legend()

            # Exibir no Streamlit
            col9, col10 = st.columns(2)
            col9.pyplot(fig_media_combustivel_aplicacao)
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
            col10.pyplot(fig_somacombustivel_aplicacao)

            ###################################################GERAR PDF##################################################
            if st.button('Gerar PDF para Aplicação'):
                # Supondo que 'Nome_Organizacao' seja uma coluna no dataframe 
                first_organization_name = df_aplicacao['Clientes'].iloc[0].split()[0]

                # Gerar o PDF
                figures = [fig_haaplicada_aplicacao,fig_mediaVelocidade_aplicacao,fig_eficiencia_aplicacao, fig_media_combustivel_aplicacao, fig_taxa_aplicacao ,fig_somacombustivel_aplicacao]
                pdf_buffer = generate_pdf_aplicacao(df_aplicacao, figures, background_image_first_page_aplicacao, background_image_other_pages)

                # Configurar o nome do arquivo dinamicamente
                file_name = f"relatorio_aplicacao_{first_organization_name}.pdf"

                # Download do PDF
                st.download_button(
                    label="Baixar PDF",
                    data=pdf_buffer,
                    file_name=file_name,
                    mime="application/pdf"
                )

if selected == "Colheita":
    st.subheader("Analisador de Trabalho - Colheita")
    col1,col2,col3=st.columns(3)
    # Seleção do tipo de arquivo e upload
    file_type_colheita = st.radio("Selecione o tipo de arquivo:", ("CSV",))
    uploaded_file_colheita = st.file_uploader(f"Escolha um arquivo {file_type_colheita} para Colheita", type=["xlsx"])

    if uploaded_file_colheita is not None:
        df_colheita = load_data(uploaded_file_colheita, file_type_colheita)

        if df_colheita is not None:
            st.subheader('Dados do Arquivo Carregado para Colheita')
            
            # Exibir organização (cliente)
            if 'Clientes' in df_colheita.columns:
                organização = df_colheita['Clientes'].iloc[0]

                col1, col2, col3, col4 = st.columns(4)
                col1.write(f"**Organização:** {organização}")

                # Garantir que os valores sejam numéricos antes de somar
                df_colheita['Área Colhida'] = pd.to_numeric(df_colheita['Área Colhida'], errors='coerce')
                df_colheita['Combustível Total'] = pd.to_numeric(df_colheita['Combustível Total'], errors='coerce')

                # Cálculo dos totais
                area_total_colhida = df_colheita['Área Colhida'].sum()
                combustivel_total = df_colheita['Combustível Total'].sum()
                total_equipamentos = df_colheita['Nome da Máquina'].nunique()

                # Exibir os valores nas colunas restantes
                col2.write(f"**Área Total Colhida:** {area_total_colhida:.2f} ha")
                col3.write(f"**Combustível Total Consumido:** {combustivel_total:.2f} L")
                col4.write(f"**Total de Equipamentos:** {total_equipamentos}")

                # Criar dicionário para cores
                colors = {
                    'Event': 'rgb(31, 119, 180)',
                    'Other Event': 'rgb(255, 127, 14)'
                }
                #####################################SOMA DE AREA APLICADA#######################################
            # Definir os dados
                selected_columns_hacolhida = ["Nome da Máquina", "Área Colhida"]
                df_selected_hacolhida = df_colheita[selected_columns_hacolhida].copy()

                # Agrupar os dados por "Nome da Máquina" e somar "Área Aplicada"
                df_soma_hacolhida = df_selected_hacolhida.groupby("Nome da Máquina").sum().reset_index()

                # Ordenar o DataFrame com base na soma da área aplicada
                df_soma_hacolhida = df_soma_hacolhida.sort_values(by="Área Colhida", ascending=True)  # Ordem crescente para horizontal

                # Configurar o gráfico
                fig_hacolhida, ax_hacolhida = plt.subplots(figsize=(12, 9))

                # Extrair dados para plotagem
                maquinas_hacolhida = df_soma_hacolhida["Nome da Máquina"]
                hacolhida = df_soma_hacolhida["Área Colhida"]

                # Definir a altura das barras
                num_maquinas = len(maquinas_hacolhida)
                bar_height = 0.2 if num_maquinas >= 3 else 0.4  # Se houver menos de 3 equipamentos, usar barras mais largas

                # Plotar barras horizontais
                bars = ax_hacolhida.barh(maquinas_hacolhida, hacolhida, color='limegreen', height=bar_height)

                # Adicionar valores ao lado das barras
                for bar, area in zip(bars, hacolhida):
                    ax_hacolhida.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2, 
                                        f'{area:.2f} ha', ha='left', va='center', fontsize=10, fontweight='bold')

                # Configurar os eixos e título
                ax_hacolhida.set_xlabel('')
                ax_hacolhida.set_ylabel('')
                ax_hacolhida.set_title('Área Colhida por Equipamento (ha)')

                # Remover moldura superior e direita para um visual mais limpo
                ax_hacolhida.spines['top'].set_visible(False)
                ax_hacolhida.spines['right'].set_visible(False)

                # Mostrar o gráfico no Streamlit
                col5, col6 = st.columns(2)
                col5.pyplot(fig_hacolhida)

                #########################MÉDIA TAXA ALVO E TAXA APLICADA###################################
                # Definir os dados
                selected_columns_taxas = ["Nome da Máquina", "Rendimento líquido", "Rendimento Bruto"]
                df_selected_taxas = df_colheita.copy()

                # Verificar se as colunas existem e, se não existirem, adicionar com valores 0
                if "Rendimento líquido" not in df_selected_taxas.columns:
                    df_selected_taxas["Rendimento líquido"] = 0  

                if "Rendimento Bruto" not in df_selected_taxas.columns:
                    df_selected_taxas["Rendimento Bruto"] = 0  

                # Converter as colunas para numéricas, tratando erros
                df_selected_taxas["Rendimento líquido"] = pd.to_numeric(df_selected_taxas["Rendimento líquido"], errors='coerce').fillna(0)
                df_selected_taxas["Rendimento Bruto"] = pd.to_numeric(df_selected_taxas["Rendimento Bruto"], errors='coerce').fillna(0)

                df_medias_taxas = df_selected_taxas.groupby("Nome da Máquina")[["Rendimento líquido", "Rendimento Bruto"]].mean().reset_index()

                # Calcular as médias gerais
                media_taxa_aplicada = df_medias_taxas["Rendimento líquido"].mean()
                media_taxa_alvo = df_medias_taxas["Rendimento Bruto"].mean()

                # Configurar o gráfico
                fig_taxa_colheita, ax_taxas = plt.subplots(figsize=(12, 8))

                # Definir a largura das barras
                bar_width = 0.35  
                posicoes = range(len(df_medias_taxas))

                # Plotar as barras verticais
                bars1 = ax_taxas.bar(posicoes, df_medias_taxas["Rendimento líquido"], width=bar_width, color='midnightblue', label='Taxa Aplicada')
                bars2 = ax_taxas.bar([p + bar_width for p in posicoes], df_medias_taxas["Rendimento Bruto"], width=bar_width, color='dodgerblue', label='Taxa Alvo')

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
                ax_taxas.set_title('Rendimento líquido vs Rendimento Bruto')

                # Adicionar legenda
                ax_taxas.legend(loc='upper right')
                col6.pyplot(fig_taxa_colheita)
                #############################MÉDIA VELOCIDADE##########################################
                # Definir os dados
                selected_columns_Velocidade = ["Nome da Máquina", "Velocidade"]
                df_selected_Velocidade = df_colheita.copy()

                # Verificar se a coluna "Velocidade" existe e, se não existir, adicionar com valor 0
                if "Velocidade" not in df_selected_Velocidade.columns:
                    df_selected_Velocidade["Velocidade"] = 0  # Adicionar coluna com valor 0 se não existir

                # Converter a coluna para numérica, tratando erros
                df_selected_Velocidade["Velocidade"] = pd.to_numeric(df_selected_Velocidade["Velocidade"], errors='coerce').fillna(0)

                # Calcular as médias da Velocidade por Máquina
                df_medias_Velocidade = df_selected_Velocidade.groupby("Nome da Máquina")["Velocidade"].mean().reset_index()

                # Configurar o gráfico
                fig_mediaVelocidade_colheita, ax_Velocidade = plt.subplots(figsize=(12, 8))

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
                col7, col8 = st.columns(2)
                col7.pyplot(fig_mediaVelocidade_colheita)
                ############################MÉDIA EFICIÊNCIA#####################################
                # Definir os dados
                selected_columns_eficiencia = ["Nome da Máquina", "Eficiência Operacional"]
                df_selected_eficiencia = df_colheita.copy()

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
                fig_eficiencia_colheita, ax_eficiencia = plt.subplots(figsize=(12, 8.5))

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
                #ax_eficiencia.legend()

                # Exibir o gráfico no Streamlit
                col8.pyplot(fig_eficiencia_colheita)

                ##############################################MÉDIA COMBUSTIVEL#################################
                # Definir os dados
                selected_columns_combustivel = ["Nome da Máquina", "Taxa de Combustível (Área)"]
                df_selected_combustivel = df_colheita.copy()

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
                fig_media_combustivel_colheita, ax_combustivel = plt.subplots(figsize=(12, 8))
                
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
                #ax_combustivel.legend()

                # Exibir no Streamlit
                col9, col10 = st.columns(2)
                col9.pyplot(fig_media_combustivel_colheita)
                ##############################################SOMA COMBUSTIVEL#################################

                selected_columns_combustivel = ["Nome da Máquina", "Combustível Total"]
                df_selected_combustivel = df_colheita.copy()

                # Selecionar colunas relevantes
                selected_columns_hacombustivel = ["Nome da Máquina", "Combustível Total"]
                df_selected_hacombustivel = df_colheita[selected_columns_hacombustivel].copy()

                # Verificar se os dados estão carregados corretamente
                #st.write("Pré-processamento - Dados Selecionados:", df_selected_haaplicada)

                # Garantir que "Combustível Total" seja numérico
                df_selected_hacombustivel["Combustível Total"] = pd.to_numeric(df_selected_hacombustivel["Combustível Total"], errors="coerce")

                # Verificar se há valores NaN
                #if df_selected_haaplicada["Combustível Total"].isna().sum() > 0:
                    #st.error("Há valores inválidos em 'Combustível Total'!")

                # Agrupar os dados por "Nome da Máquina" e somar "Combustível Total"
                df_soma_hacombustivel = df_selected_hacombustivel.groupby("Nome da Máquina", as_index=False)["Combustível Total"].sum()

                # Verificar se o agrupamento foi bem-sucedido
                #st.write("Dados Agrupados:", df_soma_haaplicada)

                # Verificar se a coluna "Combustível Total" existe após agrupamento
                if "Combustível Total" not in df_soma_hacombustivel.columns:
                    st.error("Erro: A coluna 'Combustível Total' não foi encontrada após a agregação.")
                    st.stop()

                # Ordenar o DataFrame
                df_soma_hacombustivel = df_soma_hacombustivel.sort_values(by="Combustível Total", ascending=False)

                # Configurar o gráfico
                fig_somacombustivel_colheita, ax_hacombustivel = plt.subplots(figsize=(12, 8))

                # Extrair dados para plotagem
                maquinas_hacombustivel = df_soma_hacombustivel["Nome da Máquina"]
                hacombustivel = df_soma_hacombustivel["Combustível Total"]

                # Definir a largura das barras
                #num_maquinas = len(maquinas_haaplicada)
            # bar_width = 0.2 if num_maquinas >= 3 else 0.4  

                # Criar gráfico de barras
                bars = ax_hacombustivel.bar(maquinas_hacombustivel, hacombustivel, color='dodgerblue', width=bar_width)

                # Adicionar valores nas barras
                for bar, area in zip(bars, hacombustivel):
                    ax_hacombustivel.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, 
                                        f'{area:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

                # Configuração do gráfico
                ax_hacombustivel.set_xlabel('')
                ax_hacombustivel.set_ylabel('')
                ax_hacombustivel.set_title('Combustível Total gasto por Equipamento')
                ax_hacombustivel.set_xticklabels(maquinas_hacombustivel, rotation=45, ha='right')

                # Exibir gráfico no Streamlit
                col10.pyplot(fig_somacombustivel_colheita)

                ###############################################################################################
                selected_columns_hacolhida = ["Tipo de Cultura", "Área Colhida"]
                df_selected_hacolhida = df_colheita[selected_columns_hacolhida].copy()

                # Agrupar os dados por "Tipo de Cultura" e somar "Área Colhida"
                df_soma_hacolhida = df_selected_hacolhida.groupby("Tipo de Cultura").sum().reset_index()

                # Configurar o gráfico de pizza
                fig_hacolhida_cultura, ax_pizza = plt.subplots(figsize=(6, 6))
                # Criar rótulos com nome e soma da área semeada (ha)
                labels = [f"{cultura} ({area:.2f} ha)" for cultura, area in zip(df_soma_hacolhida["Tipo de Cultura"], df_soma_hacolhida["Área Colhida"])]

                # Plotar gráfico de pizza (rosca)
                ax_pizza.pie(df_soma_hacolhida["Área Colhida"], labels=labels, 
                            autopct='%1.1f%%', colors=plt.cm.Paired.colors, startangle=90, 
                            wedgeprops={"edgecolor": "black"})

                # Adicionar título
                ax_pizza.set_title("Distribuição da Área Colhida por Tipo de Cultura")
                                # Mostrar o gráfico no Streamlit
                col11, col12 = st.columns(2)
                col11.pyplot(fig_hacolhida_cultura)
                ###################################################GERAR PDF##################################################
            if st.button('Gerar PDF para Colheita'):
                    # Supondo que 'Nome_Organizacao' seja uma coluna no dataframe 
                    first_organization_name = df_colheita['Clientes'].iloc[0].split()[0]

                    # Gerar o PDF
                    figures = [fig_hacolhida, fig_eficiencia_colheita, fig_media_combustivel_colheita, fig_somacombustivel_colheita, fig_taxa_colheita, fig_hacolhida_cultura, fig_mediaVelocidade_colheita]
                    pdf_buffer = generate_pdf_colheita(df_colheita, figures, background_image_first_page_colheita, background_image_other_pages)

                    # Configurar o nome do arquivo dinamicamente
                    file_name = f"relatorio_colheita_{first_organization_name}.pdf"

                    # Download do PDF
                    st.download_button(
                        label="Baixar PDF",
                        data=pdf_buffer,
                        file_name=file_name,
                        mime="application/pdf"
                    )

if selected == "Semeadura":
        st.subheader("Analisador de Trabalho - Semeadura")
        col1,col2,col3=st.columns(3)
        # Seleção do tipo de arquivo e upload
        file_type_Semeadura = st.radio("Selecione o tipo de arquivo:", ("CSV",))
        uploaded_file_Semeadura = st.file_uploader(f"Escolha um arquivo {file_type_Semeadura} para Semeadura", type=["xlsx"])

        if uploaded_file_Semeadura is not None:
            df_semeadura = load_data(uploaded_file_Semeadura, file_type_Semeadura)

            if df_semeadura is not None:
                st.subheader('Dados do Arquivo Carregado para Semeadura')
                
                # Exibir organização (cliente)
                if 'Clientes' in df_semeadura.columns:
                    organização = df_semeadura['Clientes'].iloc[0]

                    col1, col2, col3, col4 = st.columns(4)
                    col1.write(f"**Organização:** {organização}")

                    # Garantir que os valores sejam numéricos antes de somar
                    df_semeadura['Área Semeada'] = pd.to_numeric(df_semeadura['Área Semeada'], errors='coerce')
                    df_semeadura['Combustível Total'] = pd.to_numeric(df_semeadura['Combustível Total'], errors='coerce')

                    # Cálculo dos totais
                    area_total_colhida = df_semeadura['Área Semeada'].sum()
                    combustivel_total = df_semeadura['Combustível Total'].sum()
                    total_equipamentos = df_semeadura['Nome da Máquina'].nunique()

                    # Exibir os valores nas colunas restantes
                    col2.write(f"**Área Total Semeada:** {area_total_colhida:.2f} ha")
                    col3.write(f"**Combustível Total Consumido:** {combustivel_total:.2f} L")
                    col4.write(f"**Total de Equipamentos:** {total_equipamentos}")

                    # Criar dicionário para cores
                    colors = {
                        'Event': 'rgb(31, 119, 180)',
                        'Other Event': 'rgb(255, 127, 14)'
                    }

                selected_columns_hasemeada = ["Nome da Máquina", "Área Semeada"]
                df_selected_hasemeada = df_semeadura[selected_columns_hasemeada].copy()

                # Agrupar os dados por "Nome da Máquina" e somar "Área Aplicada"
                df_soma_hasemeada = df_selected_hasemeada.groupby("Nome da Máquina").sum().reset_index()

                # Ordenar o DataFrame com base na soma da área aplicada
                df_soma_hasemeada = df_soma_hasemeada.sort_values(by="Área Semeada", ascending=True)  # Ordem crescente para horizontal

                # Configurar o gráfico
                fig_hasemeada_semeadura, ax_hasemeada = plt.subplots(figsize=(12, 9))

                # Extrair dados para plotagem
                maquinas_hasemeada = df_soma_hasemeada["Nome da Máquina"]
                hasemeada = df_soma_hasemeada["Área Semeada"]

                # Definir a altura das barras
                num_maquinas = len(maquinas_hasemeada)
                bar_height = 0.2 if num_maquinas >= 3 else 0.4  # Se houver menos de 3 equipamentos, usar barras mais largas

                # Plotar barras horizontais
                bars = ax_hasemeada.barh(maquinas_hasemeada, hasemeada, color='limegreen', height=bar_height)

                # Adicionar valores ao lado das barras
                for bar, area in zip(bars, hasemeada):
                    ax_hasemeada.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2, 
                                        f'{area:.2f} ha', ha='left', va='center', fontsize=10, fontweight='bold')

                # Configurar os eixos e título
                ax_hasemeada.set_xlabel('')
                ax_hasemeada.set_ylabel('')
                ax_hasemeada.set_title('Área Semeada por Equipamento (ha)')

                # Remover moldura superior e direita para um visual mais limpo
                ax_hasemeada.spines['top'].set_visible(False)
                ax_hasemeada.spines['right'].set_visible(False)

                # Mostrar o gráfico no Streamlit
                col5, col6 = st.columns(2)
                col5.pyplot(fig_hasemeada_semeadura)

                selected_columns_Velocidade = ["Nome da Máquina", "Velocidade"]
                df_selected_Velocidade = df_semeadura.copy()

                # Verificar se a coluna "Velocidade" existe e, se não existir, adicionar com valor 0
                if "Velocidade" not in df_selected_Velocidade.columns:
                    df_selected_Velocidade["Velocidade"] = 0  # Adicionar coluna com valor 0 se não existir

                # Converter a coluna para numérica, tratando erros
                df_selected_Velocidade["Velocidade"] = pd.to_numeric(df_selected_Velocidade["Velocidade"], errors='coerce').fillna(0)

                # Calcular as médias da Velocidade por Máquina
                df_medias_Velocidade = df_selected_Velocidade.groupby("Nome da Máquina")["Velocidade"].mean().reset_index()

                # Configurar o gráfico
                fig_mediaVelocidade_semeadura, ax_Velocidade = plt.subplots(figsize=(12, 8))

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
                col6.pyplot(fig_mediaVelocidade_semeadura)
                ############################MÉDIA EFICIÊNCIA#####################################
                # Definir os dados
                selected_columns_eficiencia = ["Nome da Máquina", "Eficiência Operacional"]
                df_selected_eficiencia = df_semeadura.copy()

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
                fig_eficiencia_semeadura, ax_eficiencia = plt.subplots(figsize=(12, 8.5))

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
                #ax_eficiencia.legend()

                # Exibir o gráfico no Streamlitv
                col7, col8 = st.columns(2)
                col7.pyplot(fig_eficiencia_semeadura)

                ##############################################MÉDIA COMBUSTIVEL#################################
                # Definir os dados
                selected_columns_combustivel = ["Nome da Máquina", "Taxa de Combustível (Área)"]
                df_selected_combustivel = df_semeadura.copy()

                # Garantir que a coluna "Taxa de Combustível (Área)" existe
                if "Taxa de Combustível (Área)" not in df_selected_combustivel.columns:
                    df_selected_combustivel["Taxa de Combustível (Área)"] = 0  # Criar a coluna se não existir

                # Converter a coluna para numérico e tratar NaN
                df_selected_combustivel["Taxa de Combustível (Área)"] = pd.to_numeric(
                    df_selected_combustivel["Taxa de Combustível (Área)"], errors='coerce').fillna(0)

                # Calcular a média da Taxa de Combustível por Máquina
                df_medias_combustivel = df_selected_combustivel.groupby("Nome da Máquina")["Taxa de Combustível (Área)"].mean().reset_index()
                df_medias_combustivel = df_medias_combustivel.sort_values(by="Taxa de Combustível (Área)", ascending=False)


                # Configurar o gráfico de linhas
                fig_media_combustivel_semeadura, ax_combustivel = plt.subplots(figsize=(12, 8))
                
                # Plotar a linha com marcadores
                ax_combustivel.plot(df_medias_combustivel["Nome da Máquina"], 
                                    df_medias_combustivel["Taxa de Combustível (Área)"], 
                                    marker='o', linestyle='-', color='mediumblue', label='Média de Combustível')

                ax_combustivel.set_ylim(0, df_medias_combustivel["Taxa de Combustível (Área)"].max() * 1.1)

                # Adicionar rótulos nos pontos da linha
                for i, row in df_medias_combustivel.iterrows():
                    ax_combustivel.text(row["Nome da Máquina"], row["Taxa de Combustível (Área)"] + 0.2, 
                                        f'{row["Taxa de Combustível (Área)"]:.1f}', 
                                        ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

                # Configurar eixos e título
                ax_combustivel.set_xlabel('')
                ax_combustivel.set_ylabel('')
                ax_combustivel.set_title('Média de Combustível por Equipamento (l/ha)')
                plt.subplots_adjust(top=0.9)
                # Adicionar grade
                ax_combustivel.grid(True, linestyle='--', alpha=0.7)

                # Adicionar legenda
                #ax_combustivel.legend()

                # Exibir no Streamlit
                
                col8.pyplot(fig_media_combustivel_semeadura)
                ##############################################SOMA COMBUSTIVEL#################################

                selected_columns_combustivel = ["Nome da Máquina", "Combustível Total"]
                df_selected_combustivel = df_semeadura.copy()

                # Selecionar colunas relevantes
                selected_columns_hacombustivel = ["Nome da Máquina", "Combustível Total"]
                df_selected_hacombustivel = df_semeadura[selected_columns_hacombustivel].copy()

                # Verificar se os dados estão carregados corretamente
                #st.write("Pré-processamento - Dados Selecionados:", df_selected_haaplicada)

                # Garantir que "Combustível Total" seja numérico
                df_selected_hacombustivel["Combustível Total"] = pd.to_numeric(df_selected_hacombustivel["Combustível Total"], errors="coerce")

                # Verificar se há valores NaN
                #if df_selected_haaplicada["Combustível Total"].isna().sum() > 0:
                    #st.error("Há valores inválidos em 'Combustível Total'!")

                # Agrupar os dados por "Nome da Máquina" e somar "Combustível Total"
                df_soma_hacombustivel = df_selected_hacombustivel.groupby("Nome da Máquina", as_index=False)["Combustível Total"].sum()

                # Verificar se o agrupamento foi bem-sucedido
                #st.write("Dados Agrupados:", df_soma_haaplicada)

                # Verificar se a coluna "Combustível Total" existe após agrupamento
                if "Combustível Total" not in df_soma_hacombustivel.columns:
                    st.error("Erro: A coluna 'Combustível Total' não foi encontrada após a agregação.")
                    st.stop()

                # Ordenar o DataFrame
                df_soma_hacombustivel = df_soma_hacombustivel.sort_values(by="Combustível Total", ascending=False)

                # Configurar o gráfico
                fig_somacombustivel_semeadura, ax_hacombustivel = plt.subplots(figsize=(12, 8))

                # Extrair dados para plotagem
                maquinas_hacombustivel = df_soma_hacombustivel["Nome da Máquina"]
                hacombustivel = df_soma_hacombustivel["Combustível Total"]

                # Definir a largura das barras
                #num_maquinas = len(maquinas_haaplicada)
            #       bar_width = 0.2 if num_maquinas >= 3 else 0.4  
                bar_width = 0.4  # ou outro valor adequado

                # Criar gráfico de barras
                bars = ax_hacombustivel.bar(maquinas_hacombustivel, hacombustivel, color='dodgerblue', width=bar_width)

                # Adicionar valores nas barras
                for bar, area in zip(bars, hacombustivel):
                    ax_hacombustivel.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, 
                                        f'{area:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

                # Configuração do gráfico
                ax_hacombustivel.set_xlabel('')
                ax_hacombustivel.set_ylabel('')
                ax_hacombustivel.set_title('Combustível Total gasto por Equipamento')
                ax_hacombustivel.set_xticklabels(maquinas_hacombustivel, rotation=45, ha='right')
                col9, col10 = st.columns(2)
                # Exibir gráfico no Streamlit
                col9.pyplot(fig_somacombustivel_semeadura)

                ###############################################################################################
                # Selecionar colunas
                selected_columns_hacolhida = ["Tipo de Cultura", "Área Semeada"]
                df_selected_hacolhida = df_semeadura[selected_columns_hacolhida].copy()

                # Agrupar os dados por "Tipo de Cultura" e somar "Área Semeada"
                df_soma_hacolhida = df_selected_hacolhida.groupby("Tipo de Cultura").sum().reset_index()

                # Configurar o gráfico de pizza (rosca)
                fig_hacolhida_cultura_semeadura, ax_pizza = plt.subplots(figsize=(6, 6))

                # Criar rótulos com nome e soma da área semeada (ha)
                labels = [f"{cultura} ({area:.2f} ha)" for cultura, area in zip(df_soma_hacolhida["Tipo de Cultura"], df_soma_hacolhida["Área Semeada"])]

                # Plotar gráfico de pizza (rosca)
                ax_pizza.pie(df_soma_hacolhida["Área Semeada"], labels=labels, 
                            autopct='%1.1f%%', colors=plt.cm.Paired.colors, startangle=90, 
                            wedgeprops={"edgecolor": "black"})

                # Adicionar título
                ax_pizza.set_title("Distribuição da Área Semeada por Tipo de Cultura")

                # Mostrar o gráfico no Streamlit
                col11, col12 = st.columns(2)
                col10.pyplot(fig_hacolhida_cultura_semeadura)

                if st.button('Gerar PDF para Semeadura'):
                    # Supondo que 'Nome_Organizacao' seja uma coluna no dataframe 
                    first_organization_name = df_semeadura['Clientes'].iloc[0].split()[0]

                    # Gerar o PDF
                    figures = [fig_hasemeada_semeadura, fig_eficiencia_semeadura, fig_hacolhida_cultura_semeadura, fig_somacombustivel_semeadura, fig_media_combustivel_semeadura, fig_mediaVelocidade_semeadura]
                    pdf_buffer = generate_pdf_semeadura(df_semeadura, figures, background_image_first_page_semeadura, background_image_other_pages)

                    # Configurar o nome do arquivo dinamicamente
                    file_name = f"relatorio_semeadura_{first_organization_name}.pdf"

                    # Download do PDF
                    st.download_button(
                        label="Baixar PDF",
                        data=pdf_buffer,
                        file_name=file_name,
                        mime="application/pdf"
                    )

if selected == "Preparo de Solo":
        st.subheader("Analisador de Trabalho - Preparo de Solo")
        col1,col2,col3=st.columns(3)
        # Seleção do tipo de arquivo e upload
        file_type_Preparo = st.radio("Selecione o tipo de arquivo:", ("CSV",))
        uploaded_file_Preparo  = st.file_uploader(f"Escolha um arquivo {file_type_Preparo} para Preparo de Solo", type=["xlsx"])

        if uploaded_file_Preparo  is not None:
            df_preparo = load_data(uploaded_file_Preparo, file_type_Preparo)

            if df_preparo is not None:
                st.subheader('Dados do Arquivo Carregado para Preparo de Solo')
                
                # Exibir organização (cliente)
                if 'Clientes' in df_preparo.columns:
                    organização = df_preparo['Clientes'].iloc[0]

                    col1, col2, col3, col4 = st.columns(4)
                    col1.write(f"**Organização:** {organização}")

                    # Garantir que os valores sejam numéricos antes de somar
                    df_preparo['Área Cultivada'] = pd.to_numeric(df_preparo['Área Cultivada'], errors='coerce')
                    df_preparo['Combustível Total'] = pd.to_numeric(df_preparo['Combustível Total'], errors='coerce')

                    # Cálculo dos totais
                    area_total_colhida = df_preparo['Área Cultivada'].sum()
                    combustivel_total = df_preparo['Combustível Total'].sum()
                    total_equipamentos = df_preparo['Nome da Máquina'].nunique()

                    # Exibir os valores nas colunas restantes
                    col2.write(f"**Área Total Cultivada:** {area_total_colhida:.2f} ha")
                    col3.write(f"**Combustível Total Consumido:** {combustivel_total:.2f} L")
                    col4.write(f"**Total de Equipamentos:** {total_equipamentos}")

                    # Criar dicionário para cores
                    colors = {
                        'Event': 'rgb(31, 119, 180)',
                        'Other Event': 'rgb(255, 255, 255)'
                    }

                selected_columns_hasemeada = ["Nome da Máquina", "Área Cultivada"]
                df_selected_hasemeada = df_preparo[selected_columns_hasemeada].copy()

                # Agrupar os dados por "Nome da Máquina" e somar "Área Aplicada"
                df_soma_hasemeada = df_selected_hasemeada.groupby("Nome da Máquina").sum().reset_index()

                # Ordenar o DataFrame com base na soma da área aplicada
                df_soma_hasemeada = df_soma_hasemeada.sort_values(by="Área Cultivada", ascending=True)  # Ordem crescente para horizontal

                # Configurar o gráfico
                fig_hasemeada_cultura, ax_hasemeada = plt.subplots(figsize=(12, 9))

                # Extrair dados para plotagem
                maquinas_hasemeada = df_soma_hasemeada["Nome da Máquina"]
                hasemeada = df_soma_hasemeada["Área Cultivada"]

                # Definir a altura das barras
                num_maquinas = len(maquinas_hasemeada)
                bar_height = 0.2 if num_maquinas >= 3 else 0.4  # Se houver menos de 3 equipamentos, usar barras mais largas

                # Plotar barras horizontais
                bars = ax_hasemeada.barh(maquinas_hasemeada, hasemeada, color='limegreen', height=bar_height)

                # Adicionar valores ao lado das barras
                for bar, area in zip(bars, hasemeada):
                    ax_hasemeada.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2, 
                                        f'{area:.2f} ha', ha='left', va='center', fontsize=10, fontweight='bold')

                # Configurar os eixos e título
                ax_hasemeada.set_xlabel('')
                ax_hasemeada.set_ylabel('')
                ax_hasemeada.set_title('Área Cultivada por Equipamento (ha)')

                # Remover moldura superior e direita para um visual mais limpo
                ax_hasemeada.spines['top'].set_visible(False)
                ax_hasemeada.spines['right'].set_visible(False)

                # Mostrar o gráfico no Streamlit
                col5, col6 = st.columns(2)
                col5.pyplot(fig_hasemeada_cultura)
############################################################################################################################################
                selected_columns_Velocidade = ["Nome da Máquina", "Velocidade"]
                df_selected_Velocidade = df_preparo.copy()

                # Verificar se a coluna "Velocidade" existe e, se não existir, adicionar com valor 0
                if "Velocidade" not in df_selected_Velocidade.columns:
                    df_selected_Velocidade["Velocidade"] = 0  # Adicionar coluna com valor 0 se não existir

                # Converter a coluna para numérica, tratando erros
                df_selected_Velocidade["Velocidade"] = pd.to_numeric(df_selected_Velocidade["Velocidade"], errors='coerce').fillna(0)

                # Calcular as médias da Velocidade por Máquina
                df_medias_Velocidade = df_selected_Velocidade.groupby("Nome da Máquina")["Velocidade"].mean().reset_index()

                # Configurar o gráfico
                fig_mediaVelocidade_cultivada, ax_Velocidade = plt.subplots(figsize=(12, 8))

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
                col6.pyplot(fig_mediaVelocidade_cultivada)
                ############################MÉDIA EFICIÊNCIA#####################################
                # Definir os dados
                selected_columns_eficiencia = ["Nome da Máquina", "Eficiência Operacional"]
                df_selected_eficiencia = df_preparo.copy()

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
                fig_eficiencia_cultivada, ax_eficiencia = plt.subplots(figsize=(12, 8.5))

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
                #ax_eficiencia.legend()

                # Exibir o gráfico no Streamlitv
                col7, col8 = st.columns(2)
                col7.pyplot(fig_eficiencia_cultivada)

                ##############################################MÉDIA COMBUSTIVEL#################################
                # Definir os dados
                selected_columns_combustivel = ["Nome da Máquina", "Taxa de Combustível (Área)"]
                df_selected_combustivel = df_preparo.copy()

                # Garantir que a coluna "Taxa de Combustível (Área)" existe
                if "Taxa de Combustível (Área)" not in df_selected_combustivel.columns:
                    df_selected_combustivel["Taxa de Combustível (Área)"] = 0  # Criar a coluna se não existir

                # Converter a coluna para numérico e tratar NaN
                df_selected_combustivel["Taxa de Combustível (Área)"] = pd.to_numeric(
                    df_selected_combustivel["Taxa de Combustível (Área)"], errors='coerce').fillna(0)

                # Calcular a média da Taxa de Combustível por Máquina
                df_medias_combustivel = df_selected_combustivel.groupby("Nome da Máquina")["Taxa de Combustível (Área)"].mean().reset_index()
                df_medias_combustivel = df_medias_combustivel.sort_values(by="Taxa de Combustível (Área)", ascending=False)


                # Configurar o gráfico de linhas
                fig_media_combustivel_cultivada, ax_combustivel = plt.subplots(figsize=(12, 8))
                
                # Plotar a linha com marcadores
                ax_combustivel.plot(df_medias_combustivel["Nome da Máquina"], 
                                    df_medias_combustivel["Taxa de Combustível (Área)"], 
                                    marker='o', linestyle='-', color='mediumblue', label='Média de Combustível')

                ax_combustivel.set_ylim(0, df_medias_combustivel["Taxa de Combustível (Área)"].max() * 1.1)

                # Adicionar rótulos nos pontos da linha
                for i, row in df_medias_combustivel.iterrows():
                    ax_combustivel.text(row["Nome da Máquina"], row["Taxa de Combustível (Área)"] + 0.2, 
                                        f'{row["Taxa de Combustível (Área)"]:.1f}', 
                                        ha='center', va='bottom', fontsize=10, fontweight='bold', color='black')

                # Configurar eixos e título
                ax_combustivel.set_xlabel('')
                ax_combustivel.set_ylabel('')
                ax_combustivel.set_title('Média de Combustível por Equipamento (l/ha)')
                plt.subplots_adjust(top=0.9)
                # Adicionar grade
                ax_combustivel.grid(True, linestyle='--', alpha=0.7)

                # Adicionar legenda
                #ax_combustivel.legend()

                # Exibir no Streamlit
                
                col8.pyplot(fig_media_combustivel_cultivada)
                ##############################################SOMA COMBUSTIVEL#################################

                selected_columns_combustivel = ["Nome da Máquina", "Combustível Total"]
                df_selected_combustivel = df_preparo.copy()

                # Selecionar colunas relevantes
                selected_columns_hacombustivel = ["Nome da Máquina", "Combustível Total"]
                df_selected_hacombustivel = df_preparo[selected_columns_hacombustivel].copy()

                # Verificar se os dados estão carregados corretamente
                #st.write("Pré-processamento - Dados Selecionados:", df_selected_haaplicada)

                # Garantir que "Combustível Total" seja numérico
                df_selected_hacombustivel["Combustível Total"] = pd.to_numeric(df_selected_hacombustivel["Combustível Total"], errors="coerce")

                # Verificar se há valores NaN
                #if df_selected_haaplicada["Combustível Total"].isna().sum() > 0:
                    #st.error("Há valores inválidos em 'Combustível Total'!")

                # Agrupar os dados por "Nome da Máquina" e somar "Combustível Total"
                df_soma_hacombustivel = df_selected_hacombustivel.groupby("Nome da Máquina", as_index=False)["Combustível Total"].sum()

                # Verificar se o agrupamento foi bem-sucedido
                #st.write("Dados Agrupados:", df_soma_haaplicada)

                # Verificar se a coluna "Combustível Total" existe após agrupamento
                if "Combustível Total" not in df_soma_hacombustivel.columns:
                    st.error("Erro: A coluna 'Combustível Total' não foi encontrada após a agregação.")
                    st.stop()

                # Ordenar o DataFrame
                df_soma_hacombustivel = df_soma_hacombustivel.sort_values(by="Combustível Total", ascending=False)

                # Configurar o gráfico
                fig_somacombustivel_cultivada, ax_hacombustivel = plt.subplots(figsize=(12, 8))

                # Extrair dados para plotagem
                maquinas_hacombustivel = df_soma_hacombustivel["Nome da Máquina"]
                hacombustivel = df_soma_hacombustivel["Combustível Total"]

                # Definir a largura das barras
                #num_maquinas = len(maquinas_haaplicada)
            #       bar_width = 0.2 if num_maquinas >= 3 else 0.4  
                bar_width = 0.4  # ou outro valor adequado

                # Criar gráfico de barras
                bars = ax_hacombustivel.bar(maquinas_hacombustivel, hacombustivel, color='dodgerblue', width=bar_width)

                # Adicionar valores nas barras
                for bar, area in zip(bars, hacombustivel):
                    ax_hacombustivel.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3, 
                                        f'{area:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

                # Configuração do gráfico
                ax_hacombustivel.set_xlabel('')
                ax_hacombustivel.set_ylabel('')
                ax_hacombustivel.set_title('Combustível Total gasto por Equipamento')
                ax_hacombustivel.set_xticklabels(maquinas_hacombustivel, rotation=45, ha='right')
                col9, col10 = st.columns(2)
                # Exibir gráfico no Streamlit
                col9.pyplot(fig_somacombustivel_cultivada)
                ###########################################################

                if st.button('Gerar PDF para Preparo de Solo'):
                    # Supondo que 'Nome_Organizacao' seja uma coluna no dataframe 
                    first_organization_name = df_preparo['Clientes'].iloc[0].split()[0]

                    # Gerar o PDF
                    figures = [fig_hasemeada_cultura, fig_eficiencia_cultivada, fig_somacombustivel_cultivada, fig_media_combustivel_cultivada, fig_mediaVelocidade_cultivada]
                    pdf_buffer = generate_pdf_preparo(df_preparo, figures, background_image_first_page_preparo, background_image_other_pages)

                    # Configurar o nome do arquivo dinamicamente
                    file_name = f"relatorio_preparo_{first_organization_name}.pdf"

                    # Download do PDF
                    st.download_button(
                        label="Baixar PDF",
                        data=pdf_buffer,
                        file_name=file_name,
                        mime="application/pdf"
                    )
