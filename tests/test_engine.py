import pytest
import json
from pathlib import Path
from src.processing.smart_recommendation_engine import SmartRecommendationEngine


class TestSmartRecommendationEngine:
    """Tests para el motor de recomendaciones"""
    
    @pytest.fixture
    def engine(self):
        """Fixture que carga el motor una vez"""
        return SmartRecommendationEngine()
    
    # ========== TESTS DE INICIALIZACIÓN ==========
    
    def test_engine_inicializa(self, engine):
        """Test que el motor se inicializa correctamente"""
        assert engine.medicamentos is not None
        assert engine.enfermedades is not None
        assert len(engine.medicamentos) > 0
        assert len(engine.enfermedades) > 0
    
    def test_cargar_datos(self, engine):
        """Test que se cargan todos los datos"""
        assert len(engine.medicamentos) >= 1660
        assert len(engine.enfermedades) >= 44
        assert len(engine.dosis) > 0
    
    # ========== TESTS DE EXTRACCIÓN ==========
    
    def test_extraer_parametros_peso(self, engine):
        """Test extracción de peso"""
        params = engine.extraer_parametros_texto("Perro de 25kg con dolor")
        assert params['peso'] == 25
    
    def test_extraer_parametros_especie(self, engine):
        """Test extracción de especie"""
        params_perro = engine.extraer_parametros_texto("Perro con picazón")
        assert params_perro['especie'] == 'Perro'
        
        params_gato = engine.extraer_parametros_texto("Gato con vómito")
        assert params_gato['especie'] == 'Gato'
    
    def test_extraer_parametros_sintomas(self, engine):
        """Test extracción de síntomas"""
        params = engine.extraer_parametros_texto("Perro con otitis y dolor")
        assert 'otitis' in params['sintomas']
        assert 'dolor' in params['sintomas']
    
    def test_extraer_parametros_raza(self, engine):
        """Test extracción de raza"""
        params = engine.extraer_parametros_texto("Boxer de 30kg")
        assert params['raza'] == 'Boxer'
    
    def test_extraer_parametros_condicion(self, engine):
        """Test extracción de condición"""
        params_cachorro = engine.extraer_parametros_texto("Cachorro con diarrea")
        assert params_cachorro['condicion'] == 'cachorro'
    
    # ========== TESTS DE BÚSQUEDA ==========
    
    def test_buscar_medicamento(self, engine):
        """Test búsqueda de medicamento"""
        resultados = engine.buscar_medicamento("DEXAVEX")
        assert len(resultados) > 0
        assert 'DEXAVEX' in resultados[0]['nombre']
    
    def test_buscar_medicamento_inexistente(self, engine):
        """Test búsqueda de medicamento inexistente"""
        resultados = engine.buscar_medicamento("MEDICAMENTOFICTICIO")
        assert len(resultados) == 0
    
    # ========== TESTS DE CATEGORIZACIÓN ==========
    
    def test_obtener_categoria(self, engine):
        """Test obtención de categoría"""
        categoria = engine.obtener_categoria_medicamento(['DEXAMETASONA FOSFATO SODIO'])
        assert isinstance(categoria, str)
        assert len(categoria) > 0
    
    def test_obtener_categoria_vacia(self, engine):
        """Test categoría para principios vacíos"""
        categoria = engine.obtener_categoria_medicamento([])
        assert categoria == 'Generico'
    
    # ========== TESTS DE PUNTUACIÓN ==========
    
    def test_calcular_puntuacion(self, engine):
        """Test cálculo de puntuación"""
        # Usar ID real de medicamento
        med_id = 'med_0'  # DEXAVEX
        puntuacion = engine.calcular_puntuacion(
            med_id, 
            'Dermatitis alérgica', 
            'Perro',
            peso=25,
            raza='Boxer'
        )
        assert puntuacion >= 0
    
    def test_calcular_puntuacion_med_inexistente(self, engine):
        """Test puntuación para medicamento inexistente"""
        puntuacion = engine.calcular_puntuacion(
            'med_fake',
            'Dermatitis alérgica',
            'Perro'
        )
        assert puntuacion == 0
    
    # ========== TESTS DE RECOMENDACIÓN ==========
    
    def test_recomendar_top_10(self, engine):
        """Test recomendación TOP 10"""
        recomendaciones = engine.recomendar_top_10(
            'Dermatitis alérgica',
            'Perro',
            peso=25,
            raza='Boxer'
        )
        
        assert len(recomendaciones) <= 10
        if len(recomendaciones) > 0:
            assert 'nombre' in recomendaciones[0]
            assert 'puntuacion' in recomendaciones[0]
    
    def test_recomendar_enfermedad_inexistente(self, engine):
        """Test recomendación para enfermedad inexistente"""
        recomendaciones = engine.recomendar_top_10(
            'Enfermedad Ficticia',
            'Perro'
        )
        assert len(recomendaciones) == 0
    
    # ========== TESTS DE CONSULTA CHAT ==========
    
    def test_procesar_consulta_chat(self, engine):
        """Test procesamiento de consulta completa"""
        resultado = engine.procesar_consulta_chat(
            "Boxer de 30kg con picazón en la piel"
        )
        
        assert 'parametros' in resultado
        assert 'medicamentos_recomendados' in resultado
        assert resultado['parametros']['especie'] == 'Perro'
        assert resultado['parametros']['peso'] == 30
        assert 'picazón' in resultado['parametros']['sintomas']
    
    def test_procesar_consulta_sin_sintomas(self, engine):
        """Test consulta sin síntomas claros"""
        resultado = engine.procesar_consulta_chat("Boxer de 30kg")
        
        assert resultado['parametros']['peso'] == 30
        assert len(resultado['parametros']['sintomas']) == 0


class TestNormalizacion:
    """Tests para funciones de normalización"""
    
    def test_normalizar_acentos(self):
        """Test normalización de acentos"""
        texto = SmartRecommendationEngine._normalizar_texto("PERRO COCKER")
        assert texto == "perro cocker"
        
        texto_acentos = SmartRecommendationEngine._normalizar_texto("Pastor Alemán")
        assert 'á' not in texto_acentos


if __name__ == '__main__':
    pytest.main([__file__, '-v'])