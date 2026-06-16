import pytest
from app.schemas.schemas import CalculoRiesgoRequest, NivelRiesgo


class TestScorePais:
    def test_pais_alto_riesgo_iran(self, riesgo_service):
        data = CalculoRiesgoRequest(pais_residencia="iran", pais_residencia_fiscal="iran")
        assert riesgo_service._calcular_score_pais(data) == 100

    def test_pais_alto_riesgo_corea_norte(self, riesgo_service):
        data = CalculoRiesgoRequest(pais_residencia="corea del norte")
        assert riesgo_service._calcular_score_pais(data) == 100

    def test_pais_alto_riesgo_venezuela(self, riesgo_service):
        data = CalculoRiesgoRequest(pais_residencia="venezuela")
        assert riesgo_service._calcular_score_pais(data) == 100

    def test_pais_offshore_panama(self, riesgo_service):
        data = CalculoRiesgoRequest(pais_residencia="panama")
        assert riesgo_service._calcular_score_pais(data) == 80

    def test_pais_offshore_belize(self, riesgo_service):
        data = CalculoRiesgoRequest(pais_residencia="belize")
        assert riesgo_service._calcular_score_pais(data) == 80

    def test_pais_offshore_islas_caiman(self, riesgo_service):
        data = CalculoRiesgoRequest(pais_residencia="islas caiman")
        assert riesgo_service._calcular_score_pais(data) == 80

    def test_pais_normal_espana(self, riesgo_service):
        data = CalculoRiesgoRequest(pais_residencia="espana")
        assert riesgo_service._calcular_score_pais(data) == 25

    def test_pais_normal_alemania(self, riesgo_service):
        data = CalculoRiesgoRequest(pais_residencia="alemania")
        assert riesgo_service._calcular_score_pais(data) == 25

    def test_pais_vacio_retorna_25(self, riesgo_service):
        data = CalculoRiesgoRequest()
        assert riesgo_service._calcular_score_pais(data) == 25

    def test_pais_residencia_fiscal_prioritario(self, riesgo_service):
        data = CalculoRiesgoRequest(pais_residencia="espana", pais_residencia_fiscal="iran")
        assert riesgo_service._calcular_score_pais(data) == 100


class TestScoreCargo:
    def test_no_pep_retorna_10(self, riesgo_service):
        data = CalculoRiesgoRequest(es_pep=False)
        assert riesgo_service._calcular_score_cargo(data) == 10

    def test_presidente_retorna_100(self, riesgo_service):
        data = CalculoRiesgoRequest(es_pep=True, cargo_pep="Presidente")
        assert riesgo_service._calcular_score_cargo(data) == 100

    def test_ministro_retorna_100(self, riesgo_service):
        data = CalculoRiesgoRequest(es_pep=True, cargo_pep="Ministro de Economia")
        assert riesgo_service._calcular_score_cargo(data) == 100

    def test_magistrado_retorna_100(self, riesgo_service):
        data = CalculoRiesgoRequest(es_pep=True, cargo_pep="Magistrado")
        assert riesgo_service._calcular_score_cargo(data) == 100

    def test_jefe_retorna_60(self, riesgo_service):
        data = CalculoRiesgoRequest(es_pep=True, cargo_pep="Jefe de Departamento")
        assert riesgo_service._calcular_score_cargo(data) == 60

    def test_coordinador_retorna_60(self, riesgo_service):
        data = CalculoRiesgoRequest(es_pep=True, cargo_pep="Coordinador")
        assert riesgo_service._calcular_score_cargo(data) == 60

    def test_cargo_desconocido_retorna_40(self, riesgo_service):
        data = CalculoRiesgoRequest(es_pep=True, cargo_pep="Analista")
        assert riesgo_service._calcular_score_cargo(data) == 40

    def test_cargo_vacio_es_pep_retorna_40(self, riesgo_service):
        data = CalculoRiesgoRequest(es_pep=True)
        assert riesgo_service._calcular_score_cargo(data) == 40


class TestScoreSector:
    def test_construccion_retorna_100(self, riesgo_service):
        data = CalculoRiesgoRequest(sector_economico="construccion")
        assert riesgo_service._calcular_score_sector(data) == 100

    def test_bienes_raiz_retorna_100(self, riesgo_service):
        data = CalculoRiesgoRequest(sector_economico="bienes raiz")
        assert riesgo_service._calcular_score_sector(data) == 100

    def test_metales_preciosos_retorna_100(self, riesgo_service):
        data = CalculoRiesgoRequest(sector_economico="oro")
        assert riesgo_service._calcular_score_sector(data) == 100

    def test_casino_retorna_100(self, riesgo_service):
        data = CalculoRiesgoRequest(sector_economico="casinos")
        assert riesgo_service._calcular_score_sector(data) == 100

    def test_comercio_internacional_retorna_50(self, riesgo_service):
        data = CalculoRiesgoRequest(sector_economico="comercio internacional")
        assert riesgo_service._calcular_score_sector(data) == 50

    def test_servicios_financieros_retorna_50(self, riesgo_service):
        data = CalculoRiesgoRequest(sector_economico="servicios financieros")
        assert riesgo_service._calcular_score_sector(data) == 50

    def test_actividad_economica_usada_si_sector_vacio(self, riesgo_service):
        data = CalculoRiesgoRequest(actividad_economica="importacion")
        assert riesgo_service._calcular_score_sector(data) == 50

    def test_sector_bajo_riesgo_retorna_20(self, riesgo_service):
        data = CalculoRiesgoRequest(sector_economico="tecnologia")
        assert riesgo_service._calcular_score_sector(data) == 20

    def test_sector_vacio_retorna_20(self, riesgo_service):
        data = CalculoRiesgoRequest()
        assert riesgo_service._calcular_score_sector(data) == 20


class TestScoreVinculos:
    def test_sin_vinculos_retorna_10(self, riesgo_service):
        data = CalculoRiesgoRequest(vinculos_pep=0)
        assert riesgo_service._calcular_score_vinculos(data) == 10

    def test_un_vinculo_retorna_40(self, riesgo_service):
        data = CalculoRiesgoRequest(vinculos_pep=1)
        assert riesgo_service._calcular_score_vinculos(data) == 40

    def test_dos_vinculos_retorna_70(self, riesgo_service):
        data = CalculoRiesgoRequest(vinculos_pep=2)
        assert riesgo_service._calcular_score_vinculos(data) == 70

    def test_tres_vinculos_retorna_70(self, riesgo_service):
        data = CalculoRiesgoRequest(vinculos_pep=3)
        assert riesgo_service._calcular_score_vinculos(data) == 70

    def test_cinco_vinculos_retorna_100(self, riesgo_service):
        data = CalculoRiesgoRequest(vinculos_pep=5)
        assert riesgo_service._calcular_score_vinculos(data) == 100

    def test_muchos_vinculos_retorna_100(self, riesgo_service):
        data = CalculoRiesgoRequest(vinculos_pep=10)
        assert riesgo_service._calcular_score_vinculos(data) == 100


class TestScoreOrigenFondos:
    def test_documentado_retorna_10(self, riesgo_service):
        data = CalculoRiesgoRequest(origen_fondos_documentado=True)
        assert riesgo_service._calcular_score_origen_fondos(data) == 10

    def test_no_documentado_retorna_80(self, riesgo_service):
        data = CalculoRiesgoRequest(origen_fondos_documentado=False)
        assert riesgo_service._calcular_score_origen_fondos(data) == 80


class TestDeterminarNivel:
    def test_score_0_retorna_bajo(self, riesgo_service):
        assert riesgo_service._determinar_nivel(0) == NivelRiesgo.BAJO

    def test_score_35_retorna_bajo(self, riesgo_service):
        assert riesgo_service._determinar_nivel(35) == NivelRiesgo.BAJO

    def test_score_36_retorna_medio(self, riesgo_service):
        assert riesgo_service._determinar_nivel(36) == NivelRiesgo.MEDIO

    def test_score_65_retorna_medio(self, riesgo_service):
        assert riesgo_service._determinar_nivel(65) == NivelRiesgo.MEDIO

    def test_score_66_retorna_alto(self, riesgo_service):
        assert riesgo_service._determinar_nivel(66) == NivelRiesgo.ALTO

    def test_score_100_retorna_alto(self, riesgo_service):
        assert riesgo_service._determinar_nivel(100) == NivelRiesgo.ALTO


class TestCalculoRiesgoCompleto:
    def test_riesgo_bajo_input(self, riesgo_service, riesgo_bajo_input):
        resultado = riesgo_service.calcular_riesgo(riesgo_bajo_input)
        assert resultado.nivel_riesgo == NivelRiesgo.BAJO
        assert resultado.score_total <= 35
        assert isinstance(resultado.variables, dict)
        assert len(resultado.ponderacion) == 5

    def test_riesgo_alto_input(self, riesgo_service, riesgo_alto_input):
        resultado = riesgo_service.calcular_riesgo(riesgo_alto_input)
        assert resultado.nivel_riesgo == NivelRiesgo.ALTO
        assert resultado.score_total >= 66

    def test_riesgo_medio_input(self, riesgo_service, riesgo_medio_input):
        resultado = riesgo_service.calcular_riesgo(riesgo_medio_input)
        assert 36 <= resultado.score_total <= 65

    def test_score_total_formula_correcta(self, riesgo_service):
        data = CalculoRiesgoRequest(
            pais_residencia="iran",
            pais_residencia_fiscal="iran",
            es_pep=True,
            cargo_pep="Presidente",
            sector_economico="construccion",
            vinculos_pep=5,
            origen_fondos_documentado=False,
        )
        resultado = riesgo_service.calcular_riesgo(data)
        expected = (100 * 0.25 + 100 * 0.30 + 100 * 0.15 + 100 * 0.20 + 80 * 0.10)
        assert resultado.score_total == round(expected, 2)

    def test_variables_contienen_todas_las_categorias(self, riesgo_service, riesgo_bajo_input):
        resultado = riesgo_service.calcular_riesgo(riesgo_bajo_input)
        assert "pais" in resultado.variables
        assert "cargo" in resultado.variables
        assert "sector" in resultado.variables
        assert "vinculos" in resultado.variables
        assert "origen_fondos" in resultado.variables

    def test_ponderaciones_sumadas_1(self, riesgo_service, riesgo_bajo_input):
        resultado = riesgo_service.calcular_riesgo(riesgo_bajo_input)
        total_peso = sum(resultado.ponderacion.values())
        assert abs(total_peso - 1.0) < 0.001

    def test_pep_flag_eleva_riesgo(self, riesgo_service):
        no_pep = CalculoRiesgoRequest(es_pep=False)
        si_pep = CalculoRiesgoRequest(es_pep=True, cargo_pep="Director")
        resultado_no = riesgo_service.calcular_riesgo(no_pep)
        resultado_si = riesgo_service.calcular_riesgo(si_pep)
        assert resultado_si.score_total > resultado_no.score_total

    def test_multiples_pep_cargos(self, riesgo_service):
        cargos = ["Presidente", "Ministro", "Director", "Gerente General"]
        for cargo in cargos:
            data = CalculoRiesgoRequest(es_pep=True, cargo_pep=cargo)
            resultado = riesgo_service.calcular_riesgo(data)
            assert resultado.score_total > 30
