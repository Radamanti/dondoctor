from pathlib import Path
import pandas as pd

from src.pipeline.build_bronze import prepare_bronze
from src.pipeline.build_silver import ejec_silver
from src.pipeline.build_gold import build_gold


SILVER_PATH = Path("data/processed/silver/silver_appointments.parquet")
GOLD_DIR = Path("data/processed/gold")
GOLD_DIR.mkdir(parents=True, exist_ok=True)

prepare_bronze
ejec_silver
silver = pd.read_parquet(SILVER_PATH)

# CONSTRUIR GOLD
gold = build_gold(silver)

# GUARDAR GOLD
for table_name, dataframe in gold.items():
    output_path = (GOLD_DIR / f"{table_name}.parquet")
    dataframe.to_parquet(output_path,index=False)
    print(f"{table_name}: "f"{len(dataframe):,} registros")


# RESULTADO DE AUSENTISMO
print("\n===== AUSENTISMO POR IPS =====")
print(gold["kpi"].to_string(index=False))
print("\n===== AUSENTISMO POR ESPECIALIDAD =====")
print(gold["kpi_specialty"].sort_values("ausentismo_pct",ascending=False).head(20).to_string(index=False))