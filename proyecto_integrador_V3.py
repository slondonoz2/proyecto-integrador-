# Paso Importar las bibliotecas necesarias
import pandas as pd
import streamlit as st
import pydeck as pdk
import plotly.express as px
import matplotlib.pyplot as plt

# Configuración de encabezado
st.title("Análisis del Talento Humano en Ciencia y Tecnología en Colombia")
st.markdown("""
Este tablero permite analizar los datos sobre la demanda del talento humano en ciencia, tecnología e innovación (TIC), 
así como su déficit de capital humano formado en Colombia.

Los datos fueron tomados del portal web datos abiertos y del Sistema Nacional de Información de la Educación Superior (SNIES).
""")

# Cargar las bases de datos desde los enlaces proporcionados

@st.cache_data
def cargar_datos():
    
    df_perfiles = pd.read_csv('perfiles_referenciados.csv')
    df_formacion = pd.read_csv('formacion_2017_1018.csv')
    df_graduados_tic = pd.read_csv('graduados_tic_2023.csv')
    return df_perfiles, df_formacion, df_graduados_tic

df_perfiles, df_formacion, df_graduados_tic= cargar_datos()

# Visualizacipon de datos nulos o erroneos
df_perfiles.head()
df_perfiles.info()
nulos_perfiles = df_perfiles.isnull().sum()
duplicados_perfiles = df_perfiles.duplicated().sum()
print('los valores nulos son:'+ str(nulos_perfiles))
print('los valores duplicados son:'+ str(duplicados_perfiles))

df_formacion.head()
df_formacion.info()
nulos_formacion = df_formacion.isnull().sum()
duplicados_formacion = df_formacion.duplicated().sum()
print('los valores nulos son:'+ str(nulos_formacion))
print('los valores duplicados son:'+ str(duplicados_formacion))

df_graduados_tic.head()
df_graduados_tic.info()

tab1,tab2, tab3, tab4, tab5, tab6 = st.tabs(['perfiles demandados', 'perfiles por municipio', 'mapa', 'demanda por municipio', 'Formación talento humano TIC','comparacion' ])

# Transformaciones
# Eliminar columnas innecesarias
df_perfiles = df_perfiles.drop(['Ocupación_CIUO','Ocupación_CNO'], axis= 1)

#df demanda de perfiles tic
df_demanda_perfiles = df_perfiles.groupby('Cargo_identificado').count()['ID_CARGO'].reset_index()
df_demanda_perfiles = df_demanda_perfiles.sort_values(by='ID_CARGO',ascending= False)

print(df_demanda_perfiles.info())


#df_talento humano en áreas TIC graduados en 2023
df_graduados_tic.loc[len(df_graduados_tic)] = [7,'BARRANQUILLA',10.96854, -74.78132,1016]
df_th_tic= df_graduados_tic.groupby('MUNICIPIO').sum()['graduados_2023']

#df_variación porcentual (2017-2018) de matriculados en programas de formación en TIC
df_deficit_formacion = df_formacion.groupby('Cargo u oficio por entrevistados')['VARIACION_PORCENTUAL_2018_2017'].mean().reset_index()
df_deficit_formacion['VARIACION_PORCENTUAL_2018_2017']=round(df_deficit_formacion['VARIACION_PORCENTUAL_2018_2017']*100,ndigits=1)
#Visualizaciones Streamlit 

with tab1:
     df_demanda_perfiles=df_demanda_perfiles.rename(columns={"ID_CARGO":"Total demandados"})
     st.header('Demanda por perfiles TIC en 2023')
     with st.container(border=True):
         st.markdown('Perfiles demandados en aréas TIC según empresas encuestadas')
         st.bar_chart(df_demanda_perfiles,x='Cargo_identificado', y='Total demandados')
     
     
     ver_df_demanda_perfiles = st.toggle('Ver perfiles por orden de demanda', value=True)
     
     if ver_df_demanda_perfiles:
          st.dataframe(df_demanda_perfiles, hide_index=True)

   

with tab2:
     # Agrupar por municipio y contar el número de cargos demandados por cada perfil
     df_demanda_perfiles_municipio = df_perfiles.groupby(['Municipio', 'Cargo_identificado']).count()['ID_CARGO'].reset_index()

     # Para cada municipio, ordenar por demanda y quedarnos con el top 5
     df_top5_perfiles_municipio = df_demanda_perfiles_municipio.groupby('Municipio').apply(lambda x: x.nlargest(5, 'ID_CARGO')).reset_index(drop=True)

     # Visualización en Streamlit del top 5 de perfiles más demandados por municipio con filtro múltiple
     st.header('Perfiles TIC más demandados por municipio en Colombia')
     with st.container(border=True):
          st.markdown('Top 5 de los perfiles TIC mas demandados por municipio.')
      

     # Crear un filtro para seleccionar uno o varios municipios
          municipios = df_top5_perfiles_municipio['Municipio'].unique().tolist()
          municipios.append('Todos')  # Agregar la opción "Todos"
          municipios_seleccionados = st.multiselect('Selecciona Municipios', municipios, default='Todos')

          # Filtrar los datos según los municipios seleccionados
          if 'Todos' in municipios_seleccionados:
               df_municipios_filtrado = df_top5_perfiles_municipio  # Si se selecciona "Todos", no filtrar
          else:
               df_municipios_filtrado = df_top5_perfiles_municipio[df_top5_perfiles_municipio['Municipio'].isin(municipios_seleccionados)]

          # Visualización del top 5 de perfiles más demandados en los municipios seleccionados
          fig = px.bar(df_municipios_filtrado, 
                    x='Municipio', 
                    y='ID_CARGO', 
                    color='Cargo_identificado', 
                    labels={'Cargo_identificado': 'Perfil', 'ID_CARGO': 'Cantidad Demandada'},
                    barmode='group')

          st.plotly_chart(fig)

with tab3:
     # mapa de TH formado en 2023   
     with st.container(border=True):
          st.header('Mapa talento humano TIC')
          st.markdown('Distribución por algunos municipios de Colombia de talento humano graduado en areas TIC en el año 2023.')
          st.plotly_chart(
        px.scatter_mapbox(df_graduados_tic, lat = 'Latitud', lon = 'Longitud', size = 'graduados_2023',
                color = 'graduados_2023',
                color_continuous_scale = 'temps',
                zoom = 4.5,
                size_max=35,
                hover_data='graduados_2023',
                hover_name='MUNICIPIO',
                opacity=0.60,
                mapbox_style = 'open-street-map'
                )      
        )
          
with tab4:
     #comparación oferta vs demanda
     df_demanda_municipio=df_perfiles.groupby('Municipio').count()['ID_CARGO'].reset_index()
     df_demanda_municipio = df_demanda_municipio.rename(columns={'ID_CARGO':'Cargos_demandados','Municipio':'MUNICIPIO'})

     st.header('Demanda de Cargos TIC por municipio')
     #df=df_demanda_municipio.set_index('Municipio', inplace=True)
     with st.container(border=True):
           st.markdown('Total de cargos TIC referenciados por municipio')
           st.plotly_chart(px.pie(df_demanda_municipio,
                                  values='Cargos_demandados',
                                  names = 'MUNICIPIO',
                                  color = 'MUNICIPIO',
                                  width=8000,
                                  height=550,
                                  hole = 0.5
                                  )
                         )

     ver_df_demanda_municipio = st.toggle('Ver Dataframe municipio', value=True)
     if ver_df_demanda_municipio:
         df_of_dem = df_demanda_municipio.join(df_graduados_tic.set_index('MUNICIPIO'), on='MUNICIPIO', validate='m:1')
         df_of_dem = df_of_dem.drop(['Unnamed: 0','Latitud','Longitud'],axis=1)
         
     
#Formación Talento humano TIC
with tab5:
     st.bar_chart(df_deficit_formacion,
                  horizontal=True,
                  y= 'VARIACION_PORCENTUAL_2018_2017',
                  x='Cargo u oficio por entrevistados',
                  color='VARIACION_PORCENTUAL_2018_2017',
                  x_label='Variación % 2018-2017',
                  y_label='Cargo TIC'
                  )
     col1 = st.columns(1)
     col1.(label="Casos confirmados", value=confirmados)

with tab6:
     st.dataframe(df_of_dem, hide_index=True)
"""
Graficar deficit formación 
graficar demanda vs formados
mapa con total vacantes por municipio 
mostrar si hay deficit 
aplicar widgets y visualización por slider
"""
