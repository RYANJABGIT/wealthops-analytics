from scripts.generate_data import HEADERS
from scripts.load_snowflake import DDL


def test_all_generated_tables_have_loading_schema():
    assert set(HEADERS) == set(DDL)
    for table, header in HEADERS.items():
        assert [piece.strip().split()[0].lower() for piece in DDL[table].split(",")] == header

