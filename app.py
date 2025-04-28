
import pandas as pd
import streamlit as st

# Carregar base de dados BD_GEO (base oficial para consulta)
@st.cache_data
def carregar_base():
    bd_geo = pd.read_excel('NOVA_BASE_DE_GEOLOCALIZACAO.xlsx')
    bd_geo = bd_geo[['Rodovia', 'KM', 'lat', 'long']]
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

        # Loop para busca aproximada
        for idx, row in entrada.iterrows():
            rodovia = row['Rodovia']
            km = row['KM']

            candidatos = bd_geo[(bd_geo['Rodovia'] == rodovia) & (bd_geo['KM'].between(km - 0.5, km + 0.5))]
            if not candidatos.empty:
                melhor = candidatos.iloc[(candidatos['KM'] - km).abs().argsort()].iloc[0]
                entrada.at[idx, 'lat'] = melhor['lat']
                entrada.at[idx, 'long'] = melhor['long']

        # Mostrar o resultado
        st.success("Arquivo processado com sucesso!")
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
