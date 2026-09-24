import pandas as pd


def test_appointment_id_not_null():
    df = pd.DataFrame({
        "appointment_id": ["A1", "A2", "A3"]
    })

    assert df["appointment_id"].notna().all()


def test_appointment_id_unique():
    df = pd.DataFrame({
        "appointment_id": ["A1", "A2", "A3"]
    })

    assert df["appointment_id"].is_unique