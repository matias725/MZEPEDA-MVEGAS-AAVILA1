# Consumo de API externa - Calidad del Aire
# API: AQICN (NO usar OpenWeatherMap como dice la profe)
# Justificacion: datos de contaminacion son importantes para EcoTech

import requests
import json
from datetime import datetime

# Error para cuando falla la API
class APIError(Exception):
    pass

# Clase para consumir la API de calidad del aire
class ServicioAPI:
    def __init__(self):
        self.url = "https://api.waqi.info"
        self.token = "demo"  # token de prueba
    
    # Obtener datos de calidad del aire
    def get_calidad_aire(self, ciudad="Mexico"):
        try:
            url = f"{self.url}/feed/{ciudad}/?token={self.token}"
            # print(f"Consultando API: {url}")  # debug
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            datos = response.json()
            
            if datos.get('status') != 'ok':
                raise APIError(f"API error: {datos.get('data', 'unknown')}")
            
            info = self._procesar_datos(datos['data'])
            return info
            
        except requests.exceptions.Timeout:
            raise APIError("Timeout conectando a la API")
        except requests.exceptions.ConnectionError:
            raise APIError("No se pudo conectar")
        except requests.exceptions.HTTPError as e:
            raise APIError(f"HTTP error: {e}")
        except json.JSONDecodeError:
            raise APIError("Error parseando JSON")
        except Exception as e:
            raise APIError(f"Error: {e}")
    
    # Procesar los datos que vienen de la API (deserializacion JSON)
    def _procesar_datos(self, datos):
        aqi = datos.get('aqi', 'N/A')
        estacion = datos.get('city', {}).get('name', 'Desconocida')
        coords = datos.get('city', {}).get('geo', [])
        iaqi = datos.get('iaqi', {})
        tiempo = datos.get('time', {}).get('s', 'N/A')
        
        info = {
            'aqi': aqi,
            'estacion': estacion,
            'coordenadas': coords,
            'clasificacion': self._clasificar(aqi),
            'nivel': self._get_nivel(aqi),
            'contaminantes': {
                'pm25': iaqi.get('pm25', {}).get('v', 'N/A'),
                'pm10': iaqi.get('pm10', {}).get('v', 'N/A'),
                'o3': iaqi.get('o3', {}).get('v', 'N/A'),
                'no2': iaqi.get('no2', {}).get('v', 'N/A'),
                'so2': iaqi.get('so2', {}).get('v', 'N/A'),
                'co': iaqi.get('co', {}).get('v', 'N/A')
            },
            'temp': iaqi.get('t', {}).get('v', 'N/A'),
            'humedad': iaqi.get('h', {}).get('v', 'N/A'),
            'presion': iaqi.get('p', {}).get('v', 'N/A'),
            'tiempo': tiempo
        }
        return info
    
    # Clasificar el AQI
    def _clasificar(self, aqi):
        if aqi == 'N/A':
            return 'Desconocido'
        try:
            aqi = int(aqi)
            if aqi <= 50:
                return 'Bueno'
            elif aqi <= 100:
                return 'Moderado'
            elif aqi <= 150:
                return 'Danino para grupos sensibles'
            elif aqi <= 200:
                return 'Danino'
            elif aqi <= 300:
                return 'Muy danino'
            else:
                return 'Peligroso'
        except:
            return 'Desconocido'
    
    # Nivel de peligro
    def _get_nivel(self, aqi):
        if aqi == 'N/A':
            return 'DESCONOCIDO'
        try:
            aqi = int(aqi)
            if aqi <= 50:
                return 'BAJO'
            elif aqi <= 100:
                return 'MEDIO'
            elif aqi <= 200:
                return 'ALTO'
            else:
                return 'CRITICO'
        except:
            return 'DESCONOCIDO'
    
    # Mostrar datos en consola
    def mostrar_datos(self, ciudad="Mexico"):
        try:
            datos = self.get_calidad_aire(ciudad)
            
            print("\n" + "=" * 70)
            print(" INFORME DE CALIDAD DEL AIRE - EcoTech Solutions")
            print("=" * 70)
            
            print(f"\nEstacion: {datos['estacion']}")
            print(f"Fecha/Hora: {datos['tiempo']}")
            
            if datos['coordenadas']:
                print(f"Coordenadas: {datos['coordenadas']}")
            
            print(f"\nIndice AQI: {datos['aqi']}")
            print(f"Clasificacion: {datos['clasificacion']}")
            print(f"Nivel de Peligro: {datos['nivel']}")
            
            print("\nCONTAMINANTES:")
            print("-" * 70)
            cont = datos['contaminantes']
            print(f"  PM2.5: {cont['pm25']}")
            print(f"  PM10: {cont['pm10']}")
            print(f"  O3 (Ozono): {cont['o3']}")
            print(f"  NO2: {cont['no2']}")
            print(f"  SO2: {cont['so2']}")
            print(f"  CO: {cont['co']}")
            
            print("\nCONDICIONES METEOROLOGICAS:")
            print("-" * 70)
            print(f"  Temperatura: {datos['temp']}C")
            print(f"  Humedad: {datos['humedad']}%")
            print(f"  Presion: {datos['presion']} hPa")
            
            print("\nANALISIS PARA ECOTECH:")
            print("-" * 70)
            self._recomendaciones(datos['aqi'])
            
            print("\n" + "=" * 70)
            
        except APIError as e:
            print(f"\nError obteniendo datos: {e}")
    
    # Recomendaciones basadas en AQI
    def _recomendaciones(self, aqi):
        try:
            val = int(aqi) if aqi != 'N/A' else 0
            
            if val <= 50:
                print("  Calidad del aire optima")
                print("  Buenas condiciones para actividades exteriores")
            elif val <= 100:
                print("  Calidad aceptable, monitorear")
                print("  Considerar estrategias preventivas")
            elif val <= 200:
                print("  ALERTA: Implementar medidas inmediatas")
                print("  Limitar actividades contaminantes")
            else:
                print("  CRITICO: Plan de emergencia")
                print("  Suspender actividades no esenciales")
        except:
            print("  No hay datos suficientes")
    
    # Retornar en formato JSON
    def get_json(self, ciudad="Mexico"):
        try:
            datos = self.get_calidad_aire(ciudad)
            return json.dumps(datos, indent=2, ensure_ascii=False)
        except APIError as e:
            return json.dumps({'error': str(e)}, indent=2)

# Funcion de prueba (no la uso mucho)
# def test_api():
#     api = ServicioAPI()
#     api.mostrar_datos("Mexico")
