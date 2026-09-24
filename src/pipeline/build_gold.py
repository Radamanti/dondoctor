import pandas as pd

# DIMENSIONES
def build_dim_date(fact_appointments) -> pd.DataFrame:
    dates = (fact_appointments["fecha_cita"].dropna().dt.date.drop_duplicates())

    dim_date = pd.DataFrame({"date": pd.to_datetime(dates)})
    dim_date["year"] = dim_date["date"].dt.year
    dim_date["month"] = dim_date["date"].dt.month
    dim_date["month_name"] = dim_date["date"].dt.month_name()
    dim_date["day"] = dim_date["date"].dt.day
    dim_date["day_of_week"] = dim_date["date"].dt.dayofweek + 1
    dim_date["day_name"] = dim_date["date"].dt.day_name()
    return dim_date.sort_values("date").reset_index(drop=True)


def build_dim_patient(fact_appointments) -> pd.DataFrame:
    columns = ["tenant_id","paciente_id"]
    dim_patient = (fact_appointments[columns].drop_duplicates().reset_index(drop=True))
    dim_patient["patient_key"] = (dim_patient["tenant_id"].astype("string") + "|" + dim_patient["paciente_id"].astype("string"))
    return dim_patient[["patient_key","tenant_id","paciente_id"]]


def build_dim_specialty(fact_appointments) -> pd.DataFrame:
    columns = ["tenant_id","especialidad"]
    dim_specialty = (fact_appointments[columns].drop_duplicates().reset_index(drop=True))
    dim_specialty["specialty_key"] = (dim_specialty["tenant_id"].astype("string") + "|" + dim_specialty["especialidad"].astype("string"))
    return dim_specialty[["specialty_key","tenant_id","especialidad"]]


# HECHOS
def build_fact_appointments(silver: pd.DataFrame) -> pd.DataFrame:
    fact = silver.copy()
    fact["fecha_cita"] = pd.to_datetime(fact["fecha_cita"],errors="coerce")

    # Normalización básica de estados
    fact["estado"] = (fact["estado"].astype("string").str.strip().str.upper())

    # Indicador principal de negocio
    fact["es_no_show"] = (fact["estado"] == "NO_ASISTIO").astype(int)

    # Fecha para relación con dim_date
    fact["fecha"] = fact["fecha_cita"].dt.date

    columns = [
        "appointment_key",
        "tenant_id",
        "cita_id",
        "paciente_id",
        "fecha_cita",
        "fecha",
        "especialidad",
        "medico_id",
        "sede",
        "canal_agendamiento",
        "regimen",
        "estado",
        "recordatorio_enviado",
        "confirmada",
        "gestion_recuperacion",
        "es_no_show"
    ]

    return fact[columns].copy()


# MÉTRICAS
def calculate_kpi(fact) -> pd.DataFrame:
    result = (fact.groupby("tenant_id").agg(total_citas=("appointment_key", "count"),citas_no_show=("es_no_show", "sum")).reset_index())
    result["ausentismo_pct"] = (result["citas_no_show"]/ result["total_citas"]* 100)
    return result.sort_values("ausentismo_pct",ascending=False)


def calculate_kpi_by_specialty(fact) -> pd.DataFrame:
    result = (fact.groupby(["tenant_id", "especialidad"]).agg(total_citas=("appointment_key", "count"),citas_no_show=("es_no_show", "sum")).reset_index())
    result["ausentismo_pct"] = (result["citas_no_show"]/ result["total_citas"]* 100)
    return result


# GOLD COMPLET
def build_gold(silver: pd.DataFrame) -> dict:
    fact = build_fact_appointments(silver)
    dim_date = build_dim_date(fact)
    dim_patient = build_dim_patient(fact)
    dim_specialty = build_dim_specialty(fact)
    kpi = calculate_kpi(fact)
    kpi_specialty = (
        calculate_kpi_by_specialty(fact)
    )

    return {
        "fact_appointments": fact,
        "dim_date": dim_date,
        "dim_patient": dim_patient,
        "dim_specialty": dim_specialty,
        "kpi": kpi,
        "kpi_specialty": kpi_specialty
    }