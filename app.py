import pandas as pd
import streamlit as st

# Carregar base de dados BD_GEO (base oficial para consulta)
@st.cache_data
def carregar_base():
    bd_geo = pd.read_excel('BASE_NEW.xlsx')

    # Tentar reconhecer e renomear colunas, se necessário
    if set(['SP', 'km', 'Latitude', 'Longitude']).issubset(bd_geo.columns):
        bd_geo = bd_geo.rename(columns={
            'SP': 'Rodovia',
            'km': 'KM',
            'Latitude': 'lat',
            'Longitude': 'long'
        })

    # Garantir que as colunas certas existam
    if not set(['Rodovia', 'KM', 'lat', 'long']).issubset(bd_geo.columns):
        st.error("O arquivo de base não contém as colunas corretas: 'Rodovia', 'KM', 'lat', 'long'")
        st.stop()

    bd_geo['KM'] = bd_geo['KM'].astype(float)
    return bd_geo

bd_geo = carregar_base()

# Título do app
st.title('Calculadora de Latitude/Longitude por Rodovia e KM - DER SP')

# Upload do arquivo
arquivo = st.file_uploader("Envie o arquivo .xlsx com as colunas 'Rodovia' e 'KM'", type=["xlsx"])

if arquivo is not None:
    entrada = pd.read_excel(arquivo)

    # Checar se colunas necessárias estão presentes
    if {'Rodovia', 'KM'}.issubset(entrada.columns):
        entrada['KM'] = entrada['KM'].astype(float)

        # Inicializar colunas de resultado
        entrada['lat'] = None
        entrada['long'] = None

        # Para relatório
        encontrados = 0
        nao_encontrados = 0

        # Loop para busca aproximada
        for idx, row in entrada.iterrows():
            rodovia = str(row['Rodovia']).strip().upper()
            km = row['KM']

            candidatos = bd_geo[(bd_geo['Rodovia'].str.strip().str.upper() == rodovia) & (bd_geo['KM'].between(km - 0.5, km + 0.5))]
            if not candidatos.empty:
                melhor = candidatos.iloc[(candidatos['KM'] - km).abs().argsort()].iloc[0]
                entrada.at[idx, 'lat'] = melhor['lat']
                entrada.at[idx, 'long'] = melhor['long']
                encontrados += 1
            else:
                nao_encontrados += 1

        # Mostrar o resultado
        st.success(f"Arquivo processado! {encontrados} correspondências encontradas e {nao_encontrados} não encontradas.")
        st.write("### Resultado:", entrada)

        # Download do resultado
        def converter_para_excel(df):
            from io import BytesIO
            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Resultado')
            output.seek(0)
            return output

        st.download_button(
            label="⬇️ Baixar resultado em Excel",
            data=converter_para_excel(entrada),
            file_name='resultado_latlong.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    else:
        st.error("O arquivo precisa ter as colunas 'Rodovia' e 'KM'.")
else:
    st.info("Aguardando upload do arquivo .xlsx.")
