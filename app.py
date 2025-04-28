
import pandas as pd
import streamlit as st

# Carregar base de dados BD_GEO (base oficial para consulta)
@st.cache_data
def carregar_base():
    bd_geo = pd.read_excel('NOVA_BASE_DE_GEOLOCALIZACAO.xlsx')
    bd_geo = bd_geo[['SP', 'km', 'Latitude', 'Longitude']]
    bd_geo['km'] = bd_geo['km'].astype(float)
    return bd_geo

bd_geo = carregar_base()

# Título do app
st.title('Calculadora de Latitude/Longitude por Rodovia e KM')

# Upload do arquivo
arquivo = st.file_uploader("Envie o arquivo .xlsx com as colunas 'Rodovia' e 'KM'", type=["xlsx"])

if arquivo is not None:
    entrada = pd.read_excel(arquivo)

    # Checar se colunas necessárias estão presentes
    if {'Rodovia', 'KM'}.issubset(entrada.columns):
        entrada['KM'] = entrada['KM'].astype(float)

        # Merge aproximado
        resultado = entrada.merge(
            bd_geo,
            left_on=['Rodovia', 'KM'],
            right_on=['SP', 'km'],
            how='left'
        )

        # Selecionar e renomear colunas para a saída
        resultado_final = resultado[['Rodovia', 'KM', 'Latitude', 'Longitude']]

        # Mostrar o resultado
        st.write("### Resultado:", resultado_final)

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
            data=converter_para_excel(resultado_final),
            file_name='resultado_latlong.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    else:
        st.error("O arquivo precisa ter as colunas 'Rodovia' e 'KM'.")
else:
    st.info("Aguardando upload do arquivo .xlsx.")
