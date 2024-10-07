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

# Menu dropdown na barra superior
selected = option_menu(
    menu_title=None,  # Título do menu, None para esconder
    options=["Aplicação", "Semeadura", "Colheita", "Preparo de Solo"],  # Opções do menu
    icons=['tractor', 'spray-can', 'a'],  # Ícones para cada opção
    menu_icon="cast",  # Ícone do menu
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