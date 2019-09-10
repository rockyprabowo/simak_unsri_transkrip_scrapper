import os
from dotenv import load_dotenv
from pathlib import Path
defaults_path = Path('.') / 'defaults.txt'
dotenv_default_path = Path('.') / '.env'
dotenv_path = dotenv_default_path if os.path.isfile(dotenv_default_path) else defaults_path
load_dotenv(dotenv_path=dotenv_path)

default_nim = os.getenv("DEFAULT_NIM")
default_password = os.getenv("DEFAULT_PASSWORD")
default_fakultas = os.getenv("DEFAULT_FAKULTAS")
default_prodi = os.getenv("DEFAULT_PRODI")
default_firefox_binary_path = os.getenv("DEFAULT_FIREFOX_BINARY_PATH")
webdriver_headless = True if os.getenv("WEBDRIVER_HEADLESS") == "true" else False

print("JSON Dumper Transkrip Nilai SIMAK Universitas Sriwijaya")
print(f"Menggunakan opsi dari file {dotenv_path}")
print("Here we go...")