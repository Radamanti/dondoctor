from pathlib import Path
import pandas as pd

DICT_FILES = {
    "ips_norte_citas.csv": {
        "sexo": "genero"
    },
    "ips_occidente_citas.csv": {
        "id_cita": "cita_id",
        "id_paciente": "paciente_id",
        "edad_paciente": "edad",
        "regimen_salud": "regimen",
        "estado_cita": "estado",
        "id_cita_origen": "cita_origen_id"
    },
    "ips_sur_citas.csv": {
        "sexo": "genero"
    },
}


# Este identificador permite separar los datos de cada IPS
ID_SITES = {
    "ips_norte_citas.csv": "IPS_NORTE",
    "ips_occidente_citas.csv": "IPS_OCCIDENTE",
    "ips_sur_citas.csv": "IPS_SUR",
}


#Renombramos y normalizamos los dataframes
def normalize_column_names(df) -> pd.DataFrame:
    new_columns = []
    for column in df.columns:
        column = str(column).strip().lower()
        column = column.replace(" ", "_")
        replacements = {
            "á": "a",
            "é": "e",
            "í": "i",
            "ó": "o",
            "ú": "u",
            "ü": "u",
            "ñ": "n",
        }

        for old, new in replacements.items():
            column = column.replace(old, new)

        column = "".join(
            char if char.isalnum() or char == "_" else "_"
            for char in column
        )

        while "__" in column:
            column = column.replace("__", "_")

        column = column.strip("_")
        new_columns.append(column)

    df.columns = new_columns
    return df

def standarize_values(df):
    new_values = {
        "ATD": "ATENDIDA",
        "CAN": "CANCELADA",
        "NAS": "NO_ASISTIO",
        "REP": "REAGENDADA",
        "PEN": "PENDIENTE",
        "CONF": "CONFIRMADA"
    }
    df["estado"] = df["estado"].replace(new_values)
    return df

def apply_column_mapping(df,filename) -> pd.DataFrame:
    df = df.copy()
    new_columns = DICT_FILES.get(filename, {})
    if new_columns:
        df = df.rename(columns=new_columns)
    return df

def normalize_dates(df) -> pd.DataFrame:
    df = df.copy()
    date_candidates = [
        "fecha_cita",
        "fecha_creacion",
        "fecha_actualizacion"
    ]

    for column in date_candidates:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column],errors="coerce")

    return df

def add_metadata(df,filename) -> pd.DataFrame:
    df = df.copy()
    tenant_id = ID_SITES[filename]
    df["tenant_id"] = tenant_id
    df["source_system"] = filename
    df["silver_processed_at"] = pd.Timestamp.now('UTC')
    df["appointment_key"] = (df["tenant_id"].astype("string")+ "|" + df["cita_id"].astype("string"))
    return df



def transform_to_silver(df,filename) -> pd.DataFrame:
    df = df.copy()

    #Normalizamos nombres originales
    df = normalize_column_names(df)

    # Aplicar diccionario de homologación
    df = apply_column_mapping(df,filename)

    # Normalizar nuevamente nombres
    df = normalize_column_names(df)

    # Normalizar nuevamente nombres
    df = add_metadata(df,filename)

    # Normalizar fechas
    df = normalize_dates(df)

    # Normalizar valores estado cita
    df = standarize_values(df)

    return df


# ============================================================
# CONSOLIDACIÓN
# ============================================================

def build_silver(raw_dataframes) -> pd.DataFrame:

    silver_dataframes = []
    for filename, df in raw_dataframes.items():
        print(f"Procesando Silver: {filename}")
        silver_df = transform_to_silver(df,filename)
        silver_dataframes.append(silver_df)

    silver = pd.concat(silver_dataframes,ignore_index=True,sort=False)
    return silver



def profile_silver(silver) -> dict:
    report = {}
    report["rows"] = len(silver)
    report["columns"] = len(silver.columns)
    report["tenants"] = (silver["tenant_id"].value_counts(dropna=False).to_dict())
    report["null_cita_id"] = int(silver["cita_id"].isna().sum())
    report["null_appointment_key"] = int(silver["appointment_key"].isna().sum())
    report["duplicated_appointment_rows"] = int(silver["appointment_key"].duplicated(keep=False).sum())
    report["unique_appointment_keys"] = int(silver["appointment_key"].nunique(dropna=True))
    report["status_distribution"] = (silver["estado"].value_counts(dropna=False).to_dict())
    return report


def run_quality_checks(silver) -> pd.DataFrame:
    results = []

    # CHECK 1
    null_tenant = silver["tenant_id"].isna().sum()
    results.append({
        "rule": "tenant_id_not_null",
        "passed": null_tenant == 0,
        "invalid_rows": int(null_tenant),
        "description": (
            "Todos los registros Silver deben "
            "tener tenant_id."
        )
    })

    # CHECK 2
    null_appointment = silver["cita_id"].isna().sum()
    results.append({
        "rule": "cita_id_not_null",
        "passed": null_appointment == 0,
        "invalid_rows": int(null_appointment),
        "description": (
            "La cita debe tener identificador "
            "de origen."
        )
    })

    # CHECK 3
    null_key = silver["appointment_key"].isna().sum()
    results.append({
        "rule": "appointment_key_not_null",
        "passed": null_key == 0,
        "invalid_rows": int(null_key),
        "description": (
            "La clave canónica de cita no debe "
            "ser nula."
        )
    })

    # CHECK 4
    duplicate_keys = (
        silver["appointment_key"]
        .duplicated(keep=False)
        .sum()
    )

    results.append({
        "rule": "appointment_key_unique",
        "passed": duplicate_keys == 0,
        "invalid_rows": int(duplicate_keys),
        "description": (
            "Se espera una clave de cita única. "
            "Los duplicados requieren análisis antes "
            "de eliminar registros."
        )
    })

    # CHECK 5
    if "edad" in silver.columns:

        invalid_age = (
            silver["edad"].notna()
            & (
                (silver["edad"] < 0)
                | (silver["edad"] > 120)
            )
        ).sum()

    else:

        invalid_age = 0

    results.append({
        "rule": "age_valid_range",
        "passed": invalid_age == 0,
        "invalid_rows": int(invalid_age),
        "description": (
            "Cuando existe edad, debe estar "
            "en un rango razonable."
        )
    })

    return pd.DataFrame(results)

# ============================================================
# EJECUCIÓN DEL PIPELINE SILVER
# ============================================================

BRONZE_DIR = Path("data/processed/bronze")
df_norte = pd.read_csv(BRONZE_DIR/"ips_norte_citas.csv",sep=",",encoding="UTF-8")
df_occidente = pd.read_csv(BRONZE_DIR/"ips_occidente_citas.csv",sep=";",encoding="UTF-8")
df_sur = pd.read_csv(BRONZE_DIR/"ips_sur_citas.csv",sep=",",encoding="UTF-8")

raw_dataframes = {
    "ips_norte_citas.csv": df_norte,
    "ips_occidente_citas.csv": df_occidente,
    "ips_sur_citas.csv": df_sur,
}

silver = build_silver(raw_dataframes)

print("\n===== SILVER =====")
print(f"Filas: {len(silver)}")
print(f"Columnas: {len(silver.columns)}")

print("\nColumnas:")
print(silver.columns.tolist())

# Perfilamiento
print("\n===== PERFILAMIENTO =====")

silver_report = profile_silver(silver)

for key, value in silver_report.items():
    print(f"{key}: {value}")

# Quality checks
print("\n===== QUALITY CHECKS =====")

quality_results = run_quality_checks(silver)

print(quality_results)

# Mostrar primeras filas
print("\n===== SAMPLE =====")

print(
    silver[
        [
            "tenant_id",
            "cita_id",
            "appointment_key"
        ]
    ].head(20)
)