# Flappy Bird Neuroevolution Suite

An enhanced take on the classic "NEAT learns Flappy Bird" project. The repo ships a polished training experience with:

- a persistent training window that never flickers between generations,
- a real-time evolution dashboard packed with actionable metrics,
- an inline neural-network topology renderer that visualizes weights, node roles, and layer depth, and
- curated documentation for process automation and industrial configuration needs.

## Table of Contents
- [Demo & Screenshots](#demo--screenshots)
- [Key Features](#key-features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Trainer](#running-the-trainer)
- [Controls](#controls)
- [Evolution Dashboard](#evolution-dashboard)
- [Configuration & Tuning](#configuration--tuning)
- [Project Layout](#project-layout)
- [Development Notes](#development-notes)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Demo & Screenshots
Capture gameplay while the dashboard updates to showcase the topology renderer and event log. Animated GIFs or short MP4 clips tend to communicate the system best.

## Key Features
- **NEAT-driven training** using the official `neat-python` implementation.
- **Live metrics dashboard** highlighting generation, score, fitness statistics, and pipe geometry.
- **Neural topology visualization** with signed weight shading and precise numeric labels for rapid debugging.
- **Event journal** that records score milestones, crashes, and per-generation summaries.
- **Persistent window management** so the display stays onscreen across generations.
- **Industrial documentation** under `docs/` describing sensor choices (e.g., MLX90614), process transitions, and JSON-based configuration expectations.

## Requirements
- Python 3.10+
- SDL-compatible environment for `pygame`
- System libraries for image and font rendering (usually provided by `pygame`
  packages)
- Dependencies listed in `requirements.txt`

## Installation
```bash
# Clone the repository
git clone https://github.com/<your-user>/Machien-Learning-FlappyBird.git
cd Machien-Learning-FlappyBird

# (Recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Trainer
```bash
python Flappy.py
```
The window launches immediately and remains open while NEAT iterates over generations. Console output shows NEAT statistics; the in-game dashboard mirrors the most relevant metrics.

## Controls
- `SPACE` or `UP`: manually trigger a bird jump when running in manual mode (for quick tests).
- `ESC` / window close icon: exit the simulation.

## Evolution Dashboard
The right-hand panel (default width **360 px**) renders:

- **Generation overview**: population size, alive agents, scores, and fitness aggregates.
- **Pipe geometry**: gap start/end, center, and horizontal offset to the active obstacle.
- **Network topology**: live schematic of the best genome including node roles (inputs, hidden, output) and numeric connection weights. Positive weights glow teal, negative weights glow red. Connection thickness maps to weight magnitude.
- **Top performers**: up to three leading birds with fitness, vertical offset, and recent action (Climb, Dive, Glide, Jump).
- **Event log**: chronological highlights for crashes, new highs, and generation completion summaries.

## Configuration & Tuning
- **NEAT parameters** live in `Config.txt`. Adjust population size, activation functions, or mutation rates to experiment with training dynamics.
- **Process automation notes** for industrial contexts are documented in `docs/process_notes.md` (e.g., MLX90614 sensor choice, `temp_stable` transition timing, and JSON configuration requirement named `industrial_config.json`).
- **Pipes** accelerate gradually (`Pipe.vel`) as the score increases to keep evolution challenging.

### Common Tweaks
| Setting | Location | Description |
|--------|----------|-------------|
| Population size | `Config.txt` (`pop_size`) | Larger populations explore more topologies but require more compute. |
| Input features | `Flappy.py` (`Bird` activation) | Adjust which sensors feed the network (currently bird Y, distance to gap top/bottom). |
| Event log depth | `Flappy.py` (`EVENT_LOG`) | Increase retention beyond 10 events by editing `log_event`. |

## Project Layout
```
.
├── Flappy.py               # Game loop, NEAT integration, dashboard rendering
├── Config.txt              # NEAT configuration file
├── requirements.txt        # Python dependencies
├── imgs/                   # Pygame assets (bird sprites, background, pipes)
└── docs/
    └── process_notes.md    # Automation & industrial process documentation
```

## Development Notes
- The neural renderer computes layered positions from enabled NEAT connections and paints a gradient background for clarity.
- `ensure_window()` keeps the Pygame window persistent, critical when packaging the project or streaming training sessions.
- Fonts are centralized at module load to reuse cached glyphs and avoid runtime instantiation penalties.
- All rendering pipelines stay within ASCII-compatible code for portability.

## Troubleshooting
| Issue | Cause | Fix |
|-------|-------|-----|
| Window closes after generation | Using older build without `ensure_window()` | Pull the latest main branch or merge `ensure_window()` changes. |
| Pygame raises `pkg_resources` warning | Deprecation notice from setuptools | Safe to ignore; optional to pin `setuptools<81`. |
| No birds survive the first pipe | Config too strict | Reduce gravity impact or expand population. |

## License
Add your preferred license file (MIT, Apache-2.0, etc.) before publishing. Update this section accordingly.
