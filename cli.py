import click
import subprocess
import sys
from pathlib import Path
import shutil
from dreemurr.core import generate, DEFAULT_MODEL
from dreemurr.utils import sanitise, unique
from yaspin import yaspin
from PIL import UnidentifiedImageError
from tqdm import tqdm

def gum_confirm(msg:str) -> bool:
    # handles gum confirm message when --confirm flag is used
    if shutil.which("gum") is None:
        return click.confirm(msg)
    try:
        result = subprocess.run(["gum", "confirm", msg])
        return result.returncode==0
    except FileNotFoundError:
        return click.confirm(msg)

def rename(file:Path, model:str, confirm:bool):
    # rename one file
    try:
        with yaspin(text="Generating name...") as spinner:
            new = sanitise(generate(str(file), model=model))
            spinner.ok("✓")
        new += file.suffix
        new_path = file.parent / new
        new_path = unique(new_path)

        if confirm and gum_confirm(f"Will rename {file.name} to {new_path.name}. Proceed?"):
            file.rename(new_path)
            click.echo(f"Renamed {file.name} to {new_path.name}.")
        elif not confirm:
            file.rename(new_path)
            click.echo(f"Renamed {file.name} to {new_path.name}.")
    except UnidentifiedImageError:
        click.echo("Not a valid image, skipping.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

def copy(file:Path, model:str, confirm:bool):
    # copy one file
    try:
        with yaspin(text="Generating name...") as spinner:
            new = sanitise(generate(str(file), model=model))
            spinner.ok("✓")
        new += file.suffix
        new_path = file.parent / new
        new_path = unique(new_path)

        if confirm and gum_confirm(f"Will copy {file.name} to {new_path.name}. Proceed?"):
            shutil.copy2(file, new_path)
            click.echo(f"Copied {file.name} to {new_path.name}.")
        elif not confirm:
            shutil.copy2(file, new_path)
            click.echo(f"Copied {file.name} to {new_path.name}.")
    except UnidentifiedImageError:
        click.echo("Not a valid image, skipping.")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)

@click.group()
def cli():
    pass

@cli.command()
@click.argument("file", type=click.Path(exists=True, path_type=Path), required=False)
@click.option("--model", default=DEFAULT_MODEL, help="Model to use for generating names as an OpenRouter Model ID.")
@click.option("--confirm", help="Confirm changes before writing.", is_flag=True)
@click.option("--copy", help="Create a copy with the new name instead of overwriting the old one.", is_flag=True)
def single(file:Path, model:str, confirm:bool, copy:bool):
    # use gum file picker to get file name, renames one file at a time
    if shutil.which("gum") is None:
        click.echo("Warning: Gum not installed.")
    if file is None:
        if shutil.which("gum") is None:
            click.echo("Please install Gum or provide a file path.", err=True)
        result = subprocess.run(["gum", "file", str(Path.home())], stdout=subprocess.PIPE, text=True)
        file_path = result.stdout.strip()
        if result.returncode != 0 or not file_path:
            sys.exit(1)
        file = Path(file_path)
        if not file.exists():
            click.echo("File does not exist", err=True)
    if copy:
        copy(file, model, confirm)
    else:
        rename(file, model, confirm)

@cli.command()
@click.argument("folder", type=click.Path(exists=True, path_type=Path), required=False)
@click.option("--model", default=DEFAULT_MODEL, help="Model to use for generating names as an OpenRouter Model ID.")
@click.option("--confirm", help="Confirm changes before writing.", is_flag=True)
@click.option("--copy", help="Create a copy with the new name instead of overwriting the old one.", is_flag=True)
@click.option("--recursive", help="Recursively download all files in a folder.", is_flag=True)
def batch(folder:Path, model:str, confirm:bool, copy:bool, recursive:bool):
    # use gum file picker to get file name, renames one file at a time
    if shutil.which("gum") is None:
        click.echo("Warning: Gum not installed.")
    if folder is None:
        if shutil.which("gum") is None:
            click.echo("Please install Gum or provide a file path.", err=True)
        result = subprocess.run(["gum", "file", "--directory", str(Path.home())], stdout=subprocess.PIPE, text=True)
        folder_path = result.stdout.strip()
        if result.returncode != 0 or not folder_path:
            sys.exit(1)
        folder = Path(folder_path)
        if not folder.exists():
            click.echo("Folder does not exist", err=True)
    pattern = "**/*" if recursive else "*"
    files = list(folder.glob(pattern))
    
    if not files:
        click.echo("No valid images found.", err=True)

    if confirm and not gum_confirm(f"Will rename {len(files)} in {folder}. Proceed?"):
        click.echo("Aborted. No files were changed.")
        sys.exit("0")
    
    success = 0
    failed = 0
    with tqdm(total=len(files), desc="Processing", unit="img") as pbar:
        for file in files:
            try:
                if copy:
                    copy(file, model, confirm)
                else:
                    rename(file, model, confirm)
                success += 1
            except Exception as e:
                click.echo(f"Error on {file.name}: {e}")
                failed += 1
            finally:
                pbar.update(1)
    click.echo(f"Done. {success} succeeded, {failed} failed.")

if __name__ == "__main__":
    cli()