#app/tests/etl/test_pokeapi_conversion.py
from decimal import Decimal

def test_height_weight_conversion():
    height_dm = 7
    weight_hg = 69

    height_m = Decimal(height_dm) / 10
    weight_kg = Decimal(weight_hg) / 10

    assert height_m == Decimal("0.7")
    assert weight_kg == Decimal("6.9")
