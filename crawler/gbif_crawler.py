import requests
import pandas as pd
from pathlib import Path


BASE_URL = "https://api.gbif.org/v1/occurrence/search"

def fetch_species_records(species: str, limit: int = 10) -> pd.DataFrame:
    """Search for occurrence records of a species via GBIF API"""
    params = {"scientificName": species, "limit": limit}
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()
    data = response.json()["results"]

    if not data:
        print(f"No records found for {species}")
        return pd.DataFrame()

    records = []
    for item in data:
        records.append({
            "especie": item.get("species", species),
            "tipo": item.get("kingdom", "unknown"),
            "localizacao": item.get("locality", "not informed"),
            "data_hora": item.get("eventDate", None),
            "condicoes": {
                "latitude": item.get("decimalLatitude"),
                "longitude": item.get("decimalLongitude"),
            },
            "observador": item.get("recordedBy", "not informed")
        })
    return pd.DataFrame(records)

def save_records_to_csv(df: pd.DataFrame, species: str):
    """Saves records in CSV within crawler/datasets/"""
    output_dir = Path(__file__).parent / "datasets"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / f"{species.replace(' ', '_')}.csv"
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"Records of '{species}' saved in {output_file}")


if __name__ == "__main__":
    # Test
    species_list = ["Turdus rufiventris", "Danaus plexippus", "Tabebuia chrysotricha"]
    for sp in species_list:
        df = fetch_species_records(sp, limit=15)
        if not df.empty:
            save_records_to_csv(df, sp)
