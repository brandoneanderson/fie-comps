import zipfile
import re
import struct
from pathlib import Path

def _crx_to_zip_bytes(crx_path: Path) -> bytes:
    """
    Convert a .crx file to raw zip bytes by stripping the CRX header.
    Supports CRX2 and CRX3.

    CRX format:
    - magic: b'Cr24'
    - version: uint32 little-endian
    - CRX2: pubkey_len uint32, sig_len uint32, then pubkey+sig, then zip
    - CRX3: header_size uint32, then header bytes, then zip
    """
    data = crx_path.read_bytes()
    if len(data) < 16 or data[:4] != b"Cr24":
        # Some files labeled .crx are actually zip already
        return data

    version = struct.unpack("<I", data[4:8])[0]

    if version == 2:
        pubkey_len = struct.unpack("<I", data[8:12])[0]
        sig_len = struct.unpack("<I", data[12:16])[0]
        zip_start = 16 + pubkey_len + sig_len
        return data[zip_start:]

    if version == 3:
        header_size = struct.unpack("<I", data[8:12])[0]
        zip_start = 12 + header_size
        return data[zip_start:]

    if len(data) < 16 or data[:4] != b"Cr24":
        print(f"DEBUG: File does not have CRX header. Starts with: {data[:10]}")
        return data
    
    return data

# def extractExtension(filepath: Path) -> Path | None:
def extractExtension(filepath: Path):

    '''
        Extract a .zip or .crx into a folder under the same parent directory.
        Returns the extraction folder Path, or None if unsupported / failed.
    '''
    filepath = Path(filepath)

    if not filepath.exists():
            raise FileNotFoundError(filepath)

    filename = filepath.stem  # strips only the last suffix
    destination = filepath.parent / filename

    if destination.exists():
        print("File was already extracted! Name:", filename)
        return destination
    
    destination.mkdir(parents=True, exist_ok=True)

    try:
        if filepath.suffix == ".zip":
            with zipfile.ZipFile(filepath, "r") as zip_ref:
                zip_ref.extractall(destination)
            return destination

        elif filepath.suffix == ".crx":
            # Strip CRX header if needed, then treat payload as zip
            zip_bytes = _crx_to_zip_bytes(filepath)
            # Use ZipFile on bytes
            from io import BytesIO
            with zipfile.ZipFile(BytesIO(zip_bytes), "r") as zip_ref:
                zip_ref.extractall(destination)
            return destination

        else:
            print(f"Unsupported file type: {filepath.suffix} ({filepath.name})")
            return None

    except zipfile.BadZipFile as e:
        print(f"[WARN] Failed to extract {filepath.name}: not a valid zip payload ({e})")
        # Cleanup partial folder to avoid "already extracted" false positives
        try:
            for p in destination.rglob("*"):
                if p.is_file():
                    p.unlink()
            for p in sorted(destination.rglob("*"), reverse=True):
                if p.is_dir():
                    p.rmdir()
            destination.rmdir()
        except Exception:
            pass
        return None

    except Exception as e:
        print(f"[WARN] Failed to extract {filepath.name}: {e}")
        return None

def searchFolder(extensionFolderName):
    """Searches for extensions in a folder of type '.zip' and '.crx'."""    # Grab local path where this .py script is found
    script_dir = Path(__file__).parent
    extensionFolder = script_dir / extensionFolderName

    if not extensionFolder.exists():
        print("Extensions folder not located here:", extensionFolder)
        return []
    
    filesFound = list(extensionFolder.glob("*.zip")) + list(extensionFolder.glob("*.crx"))

    # avoid double-processing *.crx.zip artifacts if they exist
    # (folder sometimes has both .crx and .crx.zip)
    filesFound = [p for p in filesFound if not p.name.endswith(".crx.zip")]
    
    # print("FILES FOUND =", filesFound)
    for path in filesFound:
        print("We found the following file: ", path.name)
    
    return filesFound

def extractURLs(file: Path, extClass):
    """Extract URLs from a text file; tolerant of encoding issues."""
    try:
        with open(file, 'r', encoding='utf8', errors='ignore') as fileloaded:
            # grab entire script and store it as string
            content = fileloaded.read()
        curls = re.findall(
            r"(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?",
            content,
        )
        for url in curls:
            urlresult = {"file": file, "url": url[0] + "://" + url[1] + url[2]}
            if urlresult not in extClass.urls:
                extClass.urls.append(urlresult)

    except FileNotFoundError:
        print(f"Error: The file {file} was not found.")
    except Exception as e:
        print(f"An error occurred reading {file}: {e}")