import argparse
import subprocess
import platform

def run_command(cmd: str):
    print(f"\n▶ {cmd}...")
    try:
        subprocess.run(cmd, check=True, shell=True)
        print(f"{cmd} afgerond.")
    except subprocess.CalledProcessError as e:
        print(f"Fout bij uitvoeren van {cmd}: {e}")

def main():
    parser = argparse.ArgumentParser()

    default_python = "python3" if platform.system() != "Windows" else "python"

    parser.add_argument(
        "--py", default=default_python,
        help="Kies de Python executable (bijv. 'python' of 'python3')"
    )
    parser.add_argument(
        "--max_page", type=int, default=None,
        help="Maximaal aantal pagina’s dat spider 2 (organisaties) moet scrapen"
    )
    args = parser.parse_args()

    py = args.py
    max_page_arg = f"-a max_page={args.max_page}" if args.max_page is not None else ""

    # Stap 1: Scrape organisatietypes
    run_command("scrapy crawl zorgkaart_types")

    # Stap 2: Update organisatietypes met eerdere scraped aantallen
    run_command(f"{py} update_organisatie_count.py")

    # Stap 3: Bereken start_page voor organisaties op basis van details
    run_command(f"{py} update_type.py")

    # Stap 4: Scrape organisaties (met optioneel max_page)
    run_command(f"scrapy crawl zorgkaart_organisaties {max_page_arg}")

    # 👉 NIEUWE STAP: Filter organisaties die al in details staan
    run_command(f"{py} update_organisatie_names.py")

    # Stap 5: Scrape details op basis van gefilterde organisaties
    run_command("scrapy crawl zorgkaart_details")

    # Stap 6: Update details.json bestand met nieuwe/gewijzigde
    run_command(f"{py} update_details.py")

    # Stap 7: Exporteer naar Excel
    run_command(f"{py} export_to_excel.py")

if __name__ == "__main__":
    main()
