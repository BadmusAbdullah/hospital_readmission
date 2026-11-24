
import hashlib
import urllib.request
import zipfile
from pathlib import Path

def generate_checksum(file_path: Path, chunk_size: int = 8192) -> str:
    """Generates an MD5 checksum (hash) of a file to verify data integrity."""
    md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            md5.update(chunk)
    return md5.hexdigest()

def download_and_extract(
    url: str, 
    target_dir: Path, 
    zip_filename: str, 
    expected_files: list,
    expected_checksum: str = None, 
    force: bool = False
):
    target_dir = Path(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    
    zip_path = target_dir / zip_filename
    temp_zip_path = target_dir / f"{zip_filename}.part"
    files_exist = all((target_dir / f).exists() for f in expected_files)
    
    if files_exist and not force:
        print(f"Data already exists in {target_dir}. Skipping download and extraction.")
        return

    if not zip_path.exists() or force:
        print(f"Downloading from {url}...")
        try:
            urllib.request.urlretrieve(url, temp_zip_path)
            temp_zip_path.replace(zip_path)
            print("Download complete.")
        except Exception as e:
            if temp_zip_path.exists():
                temp_zip_path.unlink()
            raise RuntimeError(f"Failed to download data: {e}") from e
    else:
        print(f"Zip file already exists at {zip_path}. Skipping download.")

    print(f"Generating checksum for {zip_filename}...")
    actual_checksum = generate_checksum(zip_path)
    print(f"Checksum (MD5): {actual_checksum}")

    if expected_checksum:
        if actual_checksum != expected_checksum:
            raise ValueError(
                f"Checksum mismatch! The data may have changed or been corrupted.\n"
                f"Expected: {expected_checksum}\n"
                f"Actual:   {actual_checksum}"
            )
        print("Checksum verified successfully.")
    else:
        print("\n" + "="*50)
        print("WARNING: No reference checksum found in config.yaml.")
        print(f"To enable verification, add this to your config: checksum: '{actual_checksum}'")
        print("="*50 + "\n")

    if not files_exist or force:
        print("Extracting files...")
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
            print(f"Extracted to {target_dir}")
        except zipfile.BadZipFile as e:
            raise RuntimeError("Downloaded file is not a valid zip file. Try running with --force.") from e
    else:
        print("Files already extracted. Skipping extraction.")


def verify_files(target_dir: Path, expected_files: list):
    target_dir = Path(target_dir)
    missing_files = [str(target_dir / f) for f in expected_files if not (target_dir / f).exists()]
            
    if missing_files:
        raise FileNotFoundError(f"Missing expected files after extraction: {missing_files}")
    
    print("All expected files are present and verified.")