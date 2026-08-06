# Dreemurr
A CLI that renames your images with AI.

> [!NOTE]
> Dreemurr is a fan-made project and is not affiliated with, endorsed by or connected to Toby Fox, Undertale or Deltarune.

Dreemurr is a command-line tool that uses AI to give your image files descriptive, human-readable names. Never have another file called `Untitled (10).jpg` again.
 
![Demo of Dreemurr in action](https://raw.githubusercontent.com/isobel-p/dreemurr/main/demo.gif)

## Why Dreemurr?
Unlike other AI renamer tools:
- Open source - which also means it's free
- Batch processing - with no paywalls or monthly limits
- Beautiful terminal UI - it uses Gum with a native Python fallback if necessary
- No accounts - all you need is to BYOK
- Privacy - Dreemurr doesn't store any information about your files
- Cross-platform - works on Windows, macOS and the goat Linux
- AI-powered, not AI-generated - and choose your own model

## Install
### Prerequisites
- Python 3.8 or higher
- [Gum](https://github.com/charmbracelet/gum#installation) (optional, but recommended)
- [OpenRouter](https://openrouter.ai/) (or [HCAI](https://ai.hackclub.com)) API key

### Installation
Install via pip.
```bash
pip install dreemurr
```
To manually set the environment variables go to `~/.config/dreemurr/.env`. Alternatively you can set this up when Dreemurr first runs.

> [!WARNING]
> The API key must be an OpenRouter API key. If you're a Hack Clubber using the HCAI proxy, also set `SERVER_URL` to https://ai.hackclub.com/proxy/v1. Otherwise, your token won't be accepted.
> 
## Quickstart
### Rename a single file
```bash
dreemurr single ~/Pictures/photo.jpg
```
### Rename a folder
```bash
dreemurr batch ~/Pictures
```

### Rename a folder and subfolders
```bash
dreemurr batch ~/Pictures --recursive
```

### Confirm changes before renaming
```bash
dreemurr batch ~/Pictures --recursive --confirm
```

### See all options
```bash
dreemurr --help
```

## Contributing
Contributions welcome! Feel free to open issues or submit PRs.

## License
This project is open source and available under the GNU GPLv3 License. See the [LICENSE.md](LICENSE.md) for more details.

*This README was written by a human. :3*