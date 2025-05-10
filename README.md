<a name="readme-top"></a>

<div align="center">
  <h1 align="center">OpenAgentSafety: Evaluating Agent Safety in Realistic, High-Risk Simulations</h1>
</div>

<p align="center">
    <a href="https://github.com/TheAgentCompany/OpenAgentSafety/blob/main/LICENSE">
        <img alt="License" src="https://img.shields.io/badge/License-MIT-blue">
    </a>
</p>

## Overview

**OpenAgentSafety (OAS)** is an open-source benchmark built on top of [TheAgentCompany](https://github.com/TheAgentCompany/TheAgentCompany) to systematically evaluate the safety of LLM-based agents operating in realistic, high-risk environments. Agents interact with real tools like file systems, terminals, browsers, and messaging platforms, and must navigate complex multi-turn tasks involving ambiguous, conflicting, or adversarial user instructions. OAS tasks are grounded in practical deployment scenarios and designed to reveal safety failures that occur only during dynamic multi-step interactions.

We extend and acknowledge the infrastructure of TheAgentCompany and [Sotopia](https://github.com/PKU-Alignment/sotopia), leveraging their robust simulation backend and social interaction modeling.

## Installation & Setup

The setup steps follow TheAgentCompany's benchmark closely. All services (GitLab, ownCloud, RocketChat, etc.) can be launched via Docker in minutes.

<details>
  <summary>Mac/Linux Setup</summary>

```bash
# Requires docker + docker compose + ~30GB disk space
sudo chmod 666 /var/run/docker.sock
curl -fsSL https://github.com/TheAgentCompany/the-agent-company-backup-data/releases/download/setup-script-20241208/setup.sh | sh
```
</details>

<details>
  <summary>Windows Setup</summary>

```bash
curl -fsSL -o setup.bat https://github.com/TheAgentCompany/the-agent-company-backup-data/releases/download/setup-script-20241208/setup.bat && setup.bat
```
</details>

For full details and troubleshooting tips, refer to [SETUP.md](./docs/SETUP.md).

## Running OpenAgentSafety

Each task is packaged as a Docker image with:
- `utils/init.sh`: initializes the task environment
- `instruction/task.md`: agent-facing task instruction
- `utils/eval.py`: scoring logic

### Running with OpenHands

```bash
sudo su
cd evaluation
bash run_eval.sh \
  --agent-llm-config <group1> \
  --env-llm-config <group2> \
  --outputs-path <outputs> \
  --server-hostname <hostname> \
  --version 1.0.0
```

More details available [here](./evaluation/README.md).

## Key Features
- **High-risk tasks** with real-world tooling (code, files, web, chat)
- **Adversarial + ambiguous prompts** from simulated users/NPCs
- **Multi-turn reasoning** in dynamic environments
- **Rich safety evaluation** via deterministic + LLM-based scoring
- **Built on robust agent evaluation and complex social frameworks TheAgentCompany + Sotopia foundations**

## Data and Evaluation
- The trajectories and evaluation results of Claude Sonnet 3.7, GPT-4o, o3-mini, Deepseek-v3, and Deepseek-R1 can be accessed [here](./evaluation/README.md).
- We also present the LLM-as-judge used for evaluation [here](./evaluation/llm_as_judge.py).

## Citation (coming soon)

## Contributing
We welcome contributions! Please open an issue or pull request. 

## License
Distributed under the [MIT](./LICENSE) License.

---

<p align="right">(<a href="#readme-top">back to top</a>)</p>
