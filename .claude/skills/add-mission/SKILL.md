---
name: add-mission
description: Scaffold a new RaccoonOS mission in this project following the repo's conventions. Use when the user wants to add, create, or insert a new mission (a new match phase / behaviour) into ExampleBot.
---

# Adding a mission

Missions are declarative sequences of steps in `src/missions/`. Use the CLI to create
them so file name, class name, numbering and registration in `config/missions.yml`
stay consistent. Do not create mission files or edit `config/missions.yml` by hand.

## 1. Create the mission with `raccoon missions`

```bash
raccoon missions create M040PushCubes   # explicit position
raccoon missions create PushCubes       # next free number (steps of 10)
raccoon missions create Drive Collect   # several at once
```

- `M040PushCubes` creates `src/missions/m040_push_cubes_mission.py` with class
  `M040PushCubesMission` and registers it in `config/missions.yml`.
- The prefix is `M` plus **exactly three digits**: `000` = setup, `010`–`990` = main
  missions (steps of 10 leave room to insert), `999` = shutdown. `M000` and `M999`
  are reserved. A number that is already used is refused.
- The number sets the run order (ascending).

Other useful commands:

```bash
raccoon missions list                      # table of number, class, file, type
raccoon missions rename M040 CollectCubes  # keeps the number, patches references
raccoon missions remove M040               # --keep-file only unregisters it
raccoon missions reorder M030 M010 M020    # renumbers and moves files
```

## 2. Fill in the sequence

Open the generated file and implement `sequence()`:

```python
from raccoon import *

from src.hardware.defs import Defs


class M040PushCubesMission(Mission):
    """One-line summary of what this phase accomplishes."""

    def sequence(self) -> Sequential:
        return seq([
            mark_heading_reference(),
            # ... compose steps: seq / parallel / drive_* / turn_* / follow_line_*
        ])
```

Rules:
- Sequencing only — **no loops or business logic** in the mission. If you need real
  Python at runtime, put it in a step (`src/steps/`); if you need shared state, a
  service (`src/service/`).
- Prefer built-in `raccoon` primitives. Introspect before inventing:
  `RACCOON_PLATFORM=mock python -c "import raccoon; print(inspect...)"`.

## 3. Nothing else to wire

`src/hardware/robot.py` is generated: `raccoon run` (or `raccoon codegen`) rebuilds its
mission list from `config/missions.yml`. Do not edit it by hand.

## 4. Verify it builds

```bash
raccoon missions list
raccoon codegen   # regenerates src/hardware/ from config/*.yml
RACCOON_PLATFORM=mock python -c "from src.hardware.robot import Robot; \
  [m.sequence() for m in Robot().missions]; print('OK')"
```

This catches DSL/import errors without a Wombat. Then run on hardware with the
`raccoon-run` skill.
