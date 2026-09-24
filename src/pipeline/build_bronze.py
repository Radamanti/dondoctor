from pathlib import Path
import shutil


RAW_DIR = Path("data/raw")
BRONZE_DIR = Path("data/processed/bronze")


def prepare_bronze():
    BRONZE_DIR.mkdir(parents=True, exist_ok=True)

    source_files = [
        "ips_norte_citas.csv",
        "ips_sur_citas.csv",
        "ips_occidente_citas.csv",
        "whatsapp_eventos.jsonl",
    ]

    for filename in source_files:
        source = RAW_DIR / filename
        destination = BRONZE_DIR / filename

        if not source.exists():
            raise FileNotFoundError(
                f"No existe la fuente: {source}"
            )

        shutil.copy2(source, destination)

        print(f"Copiado: {filename}")


if __name__ == "__main__":
    prepare_bronze()