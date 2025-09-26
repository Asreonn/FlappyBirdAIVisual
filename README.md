# Flappy Bird AI Visual Trainer

Interactive NEAT experiment that trains birds to play Flappy Bird while visualising the population in real time. The project focuses on delivering a smooth training loop, informative overlays, and quick insight into how genomes evolve.

## Table of Contents
- [Overview](#overview)
- [Highlights](#highlights)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [Running a Session](#running-a-session)
- [Controls](#controls)
- [Dashboard Anatomy](#dashboard-anatomy)
- [Configuring NEAT](#configuring-neat)
- [Project Layout](#project-layout)
- [Troubleshooting](#troubleshooting)
- [Next Steps](#next-steps)

## Overview
This repository contains a self-contained demo that couples the `neat-python` library with a Pygame implementation of Flappy Bird. It is designed for anyone who wants to observe evolution-driven learning without juggling multiple tools or windows.

## Highlights
- Persistent window surface so the game never flickers between generations.
- Evolution monitor panel that shares population metrics, pipe geometry, and an event timeline.
- Inline neural-network renderer that colour-codes inputs, hidden nodes, and outputs while annotating connection weights.
- Event logging that captures notable training milestones such as new high scores or out-of-bounds birds.
- Top-bird summary showing distance to the next pipe and the last action taken.

## Requirements
- Python 3.10 or newer
- `pygame` and `neat-python` (listed in `requirements.txt`)
- SDL2 dependencies for your platform (usually pulled automatically with `pygame`)
- A display that can render a 860x800 window

## Quick Start
```bash
# Clone the repository
git clone https://github.com/Asreonn/FlappyBirdAIVisual.git
cd FlappyBirdAIVisual

# (Optional) set up a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running a Session
```bash
python Flappy.py
```
The training window opens immediately and stays active while NEAT steps through generations. Console output mirrors the population reporter provided by `neat-python`.

## Controls
- `SPACE` or `UP` — manually trigger a jump when running in manual experiments.
- `ESC` or closing the window — terminate the session.

## Dashboard Anatomy
The right-hand panel explains what NEAT is doing:
- **Metrics** — generation counters, alive birds, best score, fitness averages, and elapsed time.
- **Target Pipe** — live geometry of the obstacle the population is currently approaching.
- **Network Topology** — schematic of the strongest genome with weight magnitude and sign indicated by line thickness and colour.
- **Top Performers** — up to three birds with fitness, position deltas, and last action.
- **Recent Events** — rolling log of important moments (crashes, new highs, generation summaries).

## Configuring NEAT
- Global evolutionary parameters live in `Config.txt`. Adjust population size, mutation rates, or activation functions there.
- Visual panel text is defined in `Flappy.py`. You can tweak font choices, panel width, or the number of tracked birds by editing the corresponding constants.
- The pipe velocity escalates slightly with each score increase. Modify `Pipe.vel` and the increment logic if you prefer consistent speed.

## Project Layout
```
.
├── Flappy.py        # Game loop, dashboard renderer, and NEAT integration
├── Config.txt       # NEAT configuration file consumed by neat-python
├── requirements.txt # Python dependencies
└── imgs/            # Sprite assets for birds, pipes, background, and base
```

## Troubleshooting
- **Window closes instantly** — ensure SDL libraries are available; try reinstalling `pygame` for your platform.
- **ImportError: neat not found** — install dependencies via `pip install -r requirements.txt`.
- **Birds hugging the ceiling/floor** — reduce gravity by lowering the constant used in `Bird.move`, or widen the gap in `Pipe.gap` for easier early generations.
- **No network diagram showing** — the topology appears after the first genome gains enabled connections; step through a few generations.

## Next Steps
- Capture GIFs of the dashboard for documentation or presentations.
- Experiment with additional inputs (e.g., vertical velocity) by extending the bird state passed into the network.
- Add checkpoints or persistence by wiring up `neat.Checkpointer`.
