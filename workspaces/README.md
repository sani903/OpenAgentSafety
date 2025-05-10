## Workspaces directory

This directory hosts tasks that are local to the examinee (e.g. agents or human testers). It is structured as follows:

```
├── openagentsafety_base_image/
│   ├── Dockerfile
│   ├── init.sh
│   ├── eval.py
│   └── ...
├── tasks/
│   └── safety-abusive-apology/
│       ├── checkpoints.md
│       ├── scenarios.json
│       ├── task.md
|       ├── utils
|           ├── evaluator.py
|           └── dependencies.yml
|       ├── workspace
|           ├── financials.csv
|           └── budget.csv
|   └── ...
```

Explanations:
- openagentsafety_base_image is the folder that contains shared functions, evaluation utilities, image build scripts, and other scaffolds.
- tasks is the folder for definitions of all 356 tasks, within which
  - evaluator.py defines the rule-based grading functions
  - checkpoints.md is the documentation for the expected malicious behavior (for human reference or LLM-as-judge only)
  - dependencies.yml defines the list of service dependencies
  - task.md is the task specification, contains background and requirements of each task, and is the **only** file that should be prompted to agents


