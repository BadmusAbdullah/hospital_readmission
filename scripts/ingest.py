import yaml
import argparse
from pathlib import Path
from hospital_readmission.ingestion.load_data import download_and_extract, verify_files

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def main():
    parser = argparse.ArgumentParser(description="Ingest raw data")
    parser.add_argument("--force", action="store_true", help="Force fresh download")
    args = parser.parse_args()

    config_path = PROJECT_ROOT / "configs" / "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    url = config["data_source"]["url"]
    zip_filename = config["data_source"]["zip_filename"]
    expected_files = config["data_source"]["expected_files"]
    
    expected_checksum = config["data_source"].get("checksum") 
    
    raw_dir = PROJECT_ROOT / config["paths"]["raw_dir"]

    download_and_extract(
        url, 
        raw_dir, 
        zip_filename, 
        expected_files, 
        expected_checksum=expected_checksum, 
        force=args.force
    )
    verify_files(raw_dir, expected_files)
    print("Ingestion pipeline complete!")

if __name__ == "__main__":
    main()