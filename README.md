<a name="readme-top"></a>

<div align="center">
  <img src="./docs/images/OAS_logo.png" alt="Logo" width="200">
  <h1 align="center">OpenAgentSafety: Evaluating Agent Safety in Realistic, High-Risk Simulations</h1>
</div>

<p align="center">
    <a href="https://github.com/TheAgentCompany/OpenAgentSafety/blob/main/LICENSE">
        <img alt="License" src="https://img.shields.io/badge/License-MIT-blue">
    </a>
</p>

<p align="center">
<a href="https://the-agent-company.com/">Website</a> •
<a href="https://arxiv.org/abs/2412.14161">TheAgentCompany Paper</a> •
<a href="https://the-agent-company.com/#/leaderboard">Leaderboard</a>
</p>

## Overview

**OpenAgentSafety (OAS)** is an open-source benchmark built on top of [TheAgentCompany](https://github.com/TheAgentCompany/TheAgentCompany) to systematically evaluate the safety of LLM-based agents operating in realistic, high-risk environments. Agents interact with real tools like file systems, terminals, browsers, and messaging platforms, and must navigate complex multi-turn tasks involving ambiguous, conflicting, or adversarial user instructions. OAS tasks are grounded in practical deployment scenarios and designed to reveal safety failures that occur only during dynamic multi-step interactions.

We extend and acknowledge the infrastructure of TheAgentCompany and [Sotopia](https://github.com/PKU-Alignment/sotopia), leveraging their robust simulation backend and social interaction modeling.

<div align="center">
  <img src="./docs/images/OAS_architecture.png">
</div>

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

### Option 1: Running with OpenHands

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

### Option 2: Running Manually

#### Step 1: Start the container
```bash
docker run --name <container_name> --network host -it <image_name> /bin/bash
```

#### Step 2: Initialize the environment
```bash
SERVER_HOSTNAME=<hostname> \
LITELLM_API_KEY=<env_llm_api_key> \
LITELLM_BASE_URL=<env_llm_base_url> \
LITELLM_MODEL=<env_llm_model> \
bash /utils/init.sh
```

#### Step 3: Prompt the agent
Prompt based on `/instruction/task.md`, for example:
> Complete the task in /instruction/task.md

#### Step 4: Run the evaluator
```bash
LITELLM_API_KEY=<env_llm_api_key> \
LITELLM_BASE_URL=<env_llm_base_url> \
LITELLM_MODEL=<env_llm_model> \
DECRYPTION_KEY='theagentcompany is all you need' \
python_default /utils/eval.py --trajectory_path TRAJ_PATH --output_path OUTPUT_PATH
```

### Option 3: Running with Sotopia (Coming Soon)
<!-- TODO: Add instructions for using Sotopia as interaction frontend -->

## Key Features
- **High-risk tasks** with real-world tooling (code, files, web, chat)
- **Adversarial + ambiguous prompts** from simulated users/NPCs
- **Multi-turn reasoning** in dynamic environments
- **Rich safety evaluation** via deterministic + LLM-based scoring
- **Built on TheAgentCompany + Sotopia foundations**

## Citation
```bibtex
@misc{xu2024theagentcompanybenchmarkingllmagents,
      title={TheAgentCompany: Benchmarking LLM Agents on Consequential Real World Tasks},
      author={Frank F. Xu and Yufan Song and Boxuan Li and others},
      year={2024},
      eprint={2412.14161},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2412.14161},
}
```

## Contributing
We welcome contributions! Please open an issue or pull request. For questions, contact [Frank F. Xu](https://frankxfz.me/) or collaborators listed in the original TheAgentCompany repo.

## License
Distributed under the [MIT](./LICENSE) License.

---

<p align="right">(<a href="#readme-top">back to top</a>)</p>
