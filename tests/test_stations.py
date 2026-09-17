"""Tests du référentiel de gares.

Ces tests vérifient la cohérence interne du référentiel, pas sa justesse
vis-à-vis de l'API. La vérification des codes UIC contre l'API relève d'un
script de résolution, pas d'un test unitaire.
"""

from collector.stations import BY_SLUG, STATIONS


def test_slugs_uniques():
    assert len(BY_SLUG) == len(STATIONS)


def test_positions_corridor_ordonnees_et_contigues():
    positions = sorted(s.corridor_position for s in STATIONS)
    assert positions == list(range(1, len(STATIONS) + 1))


def test_codes_uic_bien_formes():
    for station in STATIONS:
        assert station.uic.isdigit(), station.slug
        assert len(station.uic) == 8, station.slug
        assert station.uic.startswith("87"), station.slug


def test_stop_area_au_format_navitia():
    for station in STATIONS:
        assert station.stop_area == f"stop_area:SNCF:{station.uic}"


def test_marseille_est_le_seul_terminus_a_retournement():
    reversals = [s.slug for s in STATIONS if s.is_terminus_reversal]
    assert reversals == ["marseille_st_charles"]
