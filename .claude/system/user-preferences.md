# User Preferences
# Set during first-run setup — editable anytime

setup_complete: true

## Execution
execution_mode: auto          # auto / simple / advanced
                              # auto = neuro decides per task

## Model
# neuro always decides model automatically based on task complexity
# sonnet for simple/standard | opus for advanced/architecture
model_override: none          # none = auto | sonnet | opus (manual override only)

## Features
suggestion_mode: off          # on = suggest missing features based on project_type
auto_agent_upgrade: no        # yes = agents self-update version on repeated patterns
continuous_learning: no       # yes = learn from every task, store patterns/mistakes
edge_case_checking: complex-only  # always / complex-only / off

## Project
project_type: school erp              # e.g. school erp — used for suggestion engine