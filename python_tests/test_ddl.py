import re

from scripts.generate_data import HEADERS
from scripts.load_snowflake import DDL


def test_all_generated_tables_have_loading_schema():
    assert set(HEADERS) == set(DDL)
    for table, header in HEADERS.items():
        # Keep commas inside NUMBER(18,2) when splitting column definitions.
        normalized = re.sub(r"NUMBER\(\d+,\d+\)", "NUMBER", DDL[table])
        fields = [piece.strip().split()[0].lower() for piece in normalized.split(",")]
        assert fields == header
