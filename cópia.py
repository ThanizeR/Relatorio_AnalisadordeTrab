
def generate_pdf_aplicacao(df_aplicacao, figures, background_image_first_page_aplicacao=None, background_image_other_pages=None):
    pdf_buffer = BytesIO()
    
    # Tamanho A4 em paisagem
    page_width, page_height = landscape(A4)  # A4 em paisagem (842 x 595 pontos)
    
    # Criar o canvas com tamanho A4 em paisagem
    c = canvas.Canvas(pdf_buffer, pagesize=(page_width, page_height))

    # Margens para o layout
    x_margin = 40  # Margem lateral
    y_margin = 40  # Margem superior
    header_space_other_pages = 70  # Espaço para o cabeçalho

    graph_positions_and_sizes = [
    # Linha 1 (gráficos 1 a 3)
    {'name': 'fig_haaplicada_aplicacao',                 'x': x_margin,               'y': page_height - y_margin - 250, 'width': 240, 'height': 200},
    {'name': 'fig_mediaVelocidade_aplicacao',             'x': x_margin + 255,         'y': page_height - y_margin - 250, 'width': 240, 'height': 200},
    {'name': 'fig_eficiencia_aplicacao',  'x': x_margin + 255 * 2,     'y': page_height - y_margin - 170, 'width': 240, 'height': 200},

    # Linha 2 (gráficos 4 a 6)
    {'name': 'fig_media_combustivel_aplicacao',       'x': x_margin,               'y': page_height - y_margin - 490, 'width': 240, 'height': 200},
    {'name': 'fig_taxa_aplicacao',  'x': x_margin + 255,         'y': page_height - y_margin - 490, 'width': 240, 'height': 200},
    {'name': 'fig_produtoaplicado',         'x': x_margin + 255 * 2,     'y': page_height - y_margin - 380, 'width': 200, 'height': 160},

    # Linha 3 (gráfico extra centralizado abaixo do 6º gráfico, no lado direito)
    {'name': 'fig_somacombustivel_aplicacao', 'x': 600, 'y': 60, 'width': 160, 'height': 100},

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

        for ax in fig.get_axes():
            ax.title.set_fontsize(20)
            ax.xaxis.label.set_fontsize(20)
            ax.yaxis.label.set_fontsize(20)
            ax.tick_params(axis='both', labelsize=18)

            # Remove qualquer legenda existente
        legend = ax.get_legend()
        if legend:
            legend.remove()
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