import subprocess
import sys

def run_command(command: list[str], description: str):
    print(f"\n▶{description}...")
    try:
        subprocess.run(command, check=True)
        print(f"{description} afgerond.")
    except subprocess.CalledProcessError as e:
        print(f"Fout bij {description}: {e}")
        sys.exit(1)

def main():
    # Stap 1: Organisatietypes scrapen
    run_command(["scrapy", "crawl", "zorgkaart_types"], "Scrapen van organisatietypes")

    # Stap 2: Samenvoegen met eerdere organisatietypes
    run_command(["python", "update_organisatie.py"], "Updaten organisatietypes (types update)")

    # Stap 3: Tellen hoeveel al gescrapet is en nieuwe input aanmaken
    run_command(["python", "update_type.py"], "Updaten organisatietypes (scraped_count toevoegen)")

    # Stap 4: Organisaties scrapen (alleen pagina 1)
    run_command(["scrapy", "crawl", "zorgkaart_organisaties", "-a", "max_page=1"], "Scrapen van organisaties (alleen eerste pagina)")

    # Stap 5: Details scrapen
    run_command(["scrapy", "crawl", "zorgkaart_details"], "Scrapen van organisatie-details")

    # Stap 6: Updaten en samenvoegen van alle details
    run_command(["python", "update_details.py"], "Updaten organisatie-details (details update)")

    # Stap 7: Export naar Excel
    run_command(["python", "export_to_excel.py"], "Exporteren naar Excel")

if __name__ == "__main__":
    main()
