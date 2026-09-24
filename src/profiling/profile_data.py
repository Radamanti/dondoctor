from pathlib import Path
import pandas as pd


RAW_DIR = Path("data/raw")

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
        "id_cita_origen":"cita_origen_id"
    },
    "ips_sur_citas.csv": {
        "sexo": "genero"
    },
}

#Se encarga de renombrar las columnas de acuerdo al diccionario
def standardize_columns(df,file):
    rename_columns = DICT_FILES[file]
    return df.rename(columns=rename_columns)

#Se encarga de estandarizar los valores anómalos de las columnas
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

#Genera los números descriptivos por cada columna de cada archivo teniendo en cuenta su formato
def profile_csv(path: Path) -> None:
    print("=" * 80)
    print(f"ARCHIVO: {path.name}")
    print("=" * 80)
    
    sep = ","
    if path.name == "ips_occidente_citas.csv":
        sep = ";"
    
    df = pd.read_csv(path,sep=sep,encoding="UTF-8")
    df = standardize_columns(df, path.name)
    df = standarize_values(df)

    print(f"\nFilas: {len(df):,}")
    print(f"Columnas: {len(df.columns):,}")

    print("\nColumnas:")
    for column in df.columns:
        print(f" - {column}")

    print("\nTipos:")
    print(df.dtypes)

    print("\nValores nulos:")
    nulls = df.isna().sum()
    null_pct = df.isna().mean() * 100

    null_summary = pd.DataFrame({
        "null_count": nulls,
        "null_pct": null_pct.round(2)
    })

    print(null_summary)

    print("\nPrimeras Filas:")
    print(df.head)

    print("\nDuplicados completos:")
    print(df.duplicated().sum())

    print("\nEstadísticas:")
    print(df.describe(include="all").transpose())

    print("\nValidación Columna Edad")
    Edad_Nula = (df['edad'] > 77).sum()
    print(f"Cantidad Registros por encima de 77 años (Promedio edad): {Edad_Nula} ({Edad_Nula / len(df) * 100}%)")
    Edad_Nula = (df['edad'] < 1).sum()
    print(f"Cantidad Registros por debajo de 0 años: {Edad_Nula} ({Edad_Nula / len(df) * 100}%)")

    print("\nValidación Columna Estado")
    print(df["estado"].value_counts())

    print("\nValidación Consistencia Información - Citas Pendientes con motivos de cierre")
    Registros_Inconsistentes = ((df['estado'] == 'PENDIENTE') & (df['motivo_cierre'].notna()) & (df['motivo_cierre'] != '')).sum()
    print(f'Registros con inconsistencia: {Registros_Inconsistentes} ({Registros_Inconsistentes / len(df) * 100}%)')

# almacena y procesa cada archivo .CSV en la carpeta RAW_DIR
def main():
    csv_files = sorted(RAW_DIR.glob("*.csv"))

    if not csv_files:
        raise FileNotFoundError(
            "No se encontraron archivos CSV en data/raw/"
        )

    for path in csv_files:
        profile_csv(path)


if __name__ == "__main__":
    main()