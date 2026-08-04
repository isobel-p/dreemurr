import click
import subprocess
import sys
from pathlib import Path
import shutil
from dreemurr.core import generate, DEFAULT_MODEL, API_KEY
from dreemurr.utils import sanitise, unique
from yaspin import yaspin
from PIL import UnidentifiedImageError
from tqdm import tqdm

@click.group()
def cli():
    pass

@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path), required=False)
@click.option("--model", default=DEFAULT_MODEL, help="Model to use for generating names as an OpenRouter Model ID.")
@click.option("--confirm", help="Confirm changes before writing.", is_flag=True)
@click.option("--copy", help="Create a copy with the new name instead of overwriting the old one.", is_flag=True)
def single(file:Path, model:str, confirm:bool, copy:bool):
    is_gum = True
    if shutil.which("gum") is None:
        click.echo("Warning: Gum not installed.")
        is_gum = False
    if API_KEY is None:
        click.echo("Warning: API key not found. Please use an OpenRouter API key!")
        if is_gum:
            new_key = subprocess.run(["gum", "input", "--placeholder", "Enter your API key..."], stdout=subprocess.PIPE, text=True)
            new_key = new_key.stdout.strip()
        else:
            new_key = click.prompt("Enter your API key: ", type=str)
        with open("dreemurr/.env", "w") as f:
            f.write(f"API_KEY={new_key}")
        click.echo("API key set successfully. Restart Dreemurr to use the new key.")
        sys.exit(1)
    if file is None:
        if not is_gum:
            click.echo("Please install Gum or provide a file path.", err=True)
        result = subprocess.run(["gum", "file", str(Path.home())], stdout=subprocess.PIPE, text=True)
        file_path = result.stdout.strip()
        if result.returncode != 0 or not file_path:
            sys.exit(1)
        file = Path(file_path)
        if not file.exists():
            click.echo("File does not exist", err=True)
    try:
        with yaspin(text="Generating name...") as spinner:
            new = sanitise(generate(str(file), model=model))
            spinner.ok("✓")
        new += file.suffix
        new_path = file.parent / new
        new_path = unique(new_path)
        if confirm:
            if not is_gum:
                confirmed = click.confirm(f"Will rename {file.name} to {new_path.name}. Proceed?")
            else:
                try:
                    result = subprocess.run(["gum", "confirm", f"Will rename {file.name} to {new_path.name}. Proceed?"])
                    confirmed = result.returncode==0
                except FileNotFoundError:
                    confirmed =  click.confirm(f"Will rename {file.name} to {new_path.name}. Proceed?")
        else:
            confirmed = True
        if confirmed:
            if copy:
                shutil.copy2(file, new_path)
            else:
                file.rename(new_path)
            click.echo(f"Renamed {file.name} to {new_path.name}.")
    except UnidentifiedImageError:
        click.echo("Not a valid image, skipping.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@cli.command()
@click.argument("folder", type=click.Path(exists=True, path_type=Path), required=False)
@click.option("--model", default=DEFAULT_MODEL, help="Model to use for generating names as an OpenRouter Model ID.")
@click.option("--confirm", help="Confirm changes before writing.", is_flag=True)
@click.option("--copy", help="Create a copy with the new name instead of overwriting the old one.", is_flag=True)
@click.option("--recursive", help="Recursively renames all files in a folder.", is_flag=True)
def batch(folder:Path, model:str, confirm:bool, copy:bool, recursive:bool):
    is_gum = True
    if shutil.which("gum") is None:
        click.echo("Warning: Gum not installed.")
        is_gum = False
    if API_KEY is None:
        click.echo("Warning: API key not found. Please use an OpenRouter API key!")
        if is_gum:
            new_key = subprocess.run(["gum", "input", "--placeholder", "Enter your API key..."], stdout=subprocess.PIPE, text=True)
            new_key = new_key.stdout.strip()
        else:
            new_key = click.prompt("Enter your API key: ", type=str)
        with open("dreemurr/.env", "w") as f:
            f.write(f"API_KEY={new_key}")
        click.echo("API key set successfully. Restart Dreemurr to use the new key.")
        sys.exit(1)
    if folder is None:
        if not is_gum:
            click.echo("Please install Gum or provide a file path.", err=True)
        result = subprocess.run(["gum", "file", "--directory", str(Path.home())], stdout=subprocess.PIPE, text=True)
        folder_path = result.stdout.strip()
        if result.returncode != 0 or not folder_path:
            sys.exit(1)
        folder = Path(folder_path)
        if not folder.exists():
            click.echo("Folder does not exist", err=True)
    pattern = "**/*" if recursive else "*"
    if not folder.is_dir():
        click.echo("Error: Batch requires a directory, not a file.", err=True)
    files = list(folder.glob(pattern))
    if not files:
        click.echo("No valid images found.", err=True)
    if confirm and not gum_confirm(f"Will rename {len(files)} in {folder}. Proceed?"):
        click.echo("Aborted. No files were changed.")
        sys.exit(0)
    success = 0
    failed = 0
    with tqdm(total=len(files), desc="Processing", unit="img") as pbar:
        for file in files:
            try:
                new = sanitise(generate(str(file), model=model))
                new += file.suffix
                new_path = file.parent / new
                new_path = unique(new_path)

                # if not confirm or gum_confirm(f"Will rename {file.name} to {new_path.name}. Proceed?"):
                #     if copy:
                #         shutil.copy2(file, new_path)
                #     else:
                #         file.rename(new_path)
                if copy:
                    shutil.copy2(file, new_path)
                else:
                    file.rename(new_path)
                tqdm.write(f"Renamed {file.name} to {new_path.name}.")
                success += 1
            except UnidentifiedImageError:
                tqdm.write("Not a valid image, skipping.")
            except IsADirectoryError:
                pass
            except Exception as e:
                tqdm.write(f"Error on {file.name}: {e}")
                failed += 1
            finally:
                pbar.update(1)
    click.echo(f"Done. {success} succeeded, {failed} failed.")

if __name__ == "__main__":
    cli()