# Maze Runner

Navigate through a procedurally generated maze to reach the exit using **Pygame**.

## Setup

```bash
pip install -r requirements.txt
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| W / UP | Move up |
| S / DOWN | Move down |
| A / LEFT | Move left |
| D / RIGHT | Move right |
| H | Toggle shortest-path hint |
| R | Generate a new maze at the selected difficulty |

## Implemented Tasks

### Task 1: Shortest Path Hint
Press **H** to toggle a BFS shortest-path hint from the player's current cell to the exit.

### Task 2: Fog of War
Only maze cells within a radius of **3 cells** around the player are revealed; the rest is dark.

### Task 3: Timer Leaderboard
Completion times are persisted in `leaderboard.json`. The five fastest valid times are retained and shown after solving.

### Task 4: Difficulty Tiers
Select one of the following at startup:

- **Easy:** 10x8
- **Medium:** 15x13
- **Hard:** 20x18

The selected dimensions are used for maze generation, collision, goal detection, hint, fog, and timer gameplay.

## Submission Checklist

- [x] All 4 tasks completed
- [x] Maze is generated fresh each session / with R
- [x] Fog of war renders with radius 3
- [x] Timer leaderboard persists to JSON
- [x] Code reviewed
