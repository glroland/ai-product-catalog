import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def main():
    install("psycopg[binary]")

if __name__ == "__main__":
    main()
