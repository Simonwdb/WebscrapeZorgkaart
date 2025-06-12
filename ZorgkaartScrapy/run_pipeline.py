import argparse
import subprocess

def run_command(cmd: str):
    print(f"\n▶ {cmd}...")
    try:
        subprocess.run(cmd, check=True, shell=True)
        print(f"{cmd} afgerond.")
    except subprocess.CalledProcessError as e:
        print(f"Fout bij uitvoeren van {cmd}: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--py", default="python3",
        help="Kies de Python executable (bijv. 'python' of 'python3')"
    )
    parser.add_argument(
        "--max_page", type=int, default=None,
        help="Maximaal aantal pagina’s dat spider 2 (organisaties) moet scrapen"
    )
    args = parser.parse_args()

    py = args.py
    max_page_arg = f"-a max_page={args.max_page}" if args.max_page is not None else ""

    run_command("scrapy crawl zorgkaart_types")
    run_command(f"{py} update_organisatie_count.py")
    run_command(f"{py} update_type.py")

    # Bouw scrapy crawl command dynamisch op
    cmd_organisaties = "scrapy crawl zorgkaart_organisaties"
    if max_page_arg:
        cmd_organisaties += f" {max_page_arg}"
    run_command(cmd_organisaties)

    run_command("scrapy crawl zorgkaart_details")
    run_command(f"{py} update_details.py")
    run_command(f"{py} export_to_excel.py")

if __name__ == "__main__":
    main()
