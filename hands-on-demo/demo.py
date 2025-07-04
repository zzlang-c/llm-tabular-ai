# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ========= Copyright 2023-2024 @ CAMEL-AI.org. All Rights Reserved. =========
# run_ollama.py by tj-scripts（https://github.com/tj-scripts）

import sys
from dotenv import load_dotenv
from camel.models import ModelFactory
from camel.toolkits import (
    CodeExecutionToolkit,
    ExcelToolkit,
    ImageAnalysisToolkit,
    SearchToolkit,
    BrowserToolkit,
    FileWriteToolkit,
)
from camel.types import ModelPlatformType

from owl.utils import run_society

from camel.societies import RolePlaying

from camel.logger import set_log_level

import pathlib

base_dir = pathlib.Path(__file__).parent.parent
env_path = base_dir / "owl" / ".env"
load_dotenv(dotenv_path=str(env_path))

set_log_level(level="DEBUG")


def construct_society(question: str) -> RolePlaying:
    r"""Construct a society of agents based on the given question.

    Args:
        question (str): The task or question to be addressed by the society.

    Returns:
        RolePlaying: A configured society of agents ready to address the question.
    """

    # Create models for different components
    models = {
        "user": ModelFactory.create(
            model_platform=ModelPlatformType.OLLAMA,
            model_type="qwen2.5:72b",
            url="http://localhost:11434/v1",
            model_config_dict={"temperature": 0.8, "max_tokens": 1000000},
        ),
        "assistant": ModelFactory.create(
            model_platform=ModelPlatformType.OLLAMA,
            model_type="qwen2.5:72b",
            url="http://localhost:11434/v1",
            model_config_dict={"temperature": 0.2, "max_tokens": 1000000},
        ),
        "browsing": ModelFactory.create(
            model_platform=ModelPlatformType.OLLAMA,
            model_type="llava:latest",
            url="http://localhost:11434/v1",
            model_config_dict={"temperature": 0.4, "max_tokens": 1000000},
        ),
        "planning": ModelFactory.create(
            model_platform=ModelPlatformType.OLLAMA,
            model_type="qwen2.5:72b",
            url="http://localhost:11434/v1",
            model_config_dict={"temperature": 0.4, "max_tokens": 1000000},
        ),
        "image": ModelFactory.create(
            model_platform=ModelPlatformType.OLLAMA,
            model_type="llava:latest",
            url="http://localhost:11434/v1",
            model_config_dict={"temperature": 0.4, "max_tokens": 1000000},
        ),
    }

    # Configure toolkits
    tools = [
        *BrowserToolkit(
            headless=False,  # Set to True for headless mode (e.g., on remote servers)
            web_agent_model=models["browsing"],
            planning_agent_model=models["planning"],
        ).get_tools(),
        *CodeExecutionToolkit(sandbox="subprocess", verbose=True).get_tools(),
        *ImageAnalysisToolkit(model=models["image"]).get_tools(),
        SearchToolkit().search_duckduckgo,
        # SearchToolkit().search_google,  # Comment this out if you don't have google search
        SearchToolkit().search_wiki,
        *ExcelToolkit().get_tools(),
        *FileWriteToolkit(output_dir="./").get_tools(),
    ]

    # Configure agent roles and parameters
    user_agent_kwargs = {"model": models["user"]}
    assistant_agent_kwargs = {"model": models["assistant"], "tools": tools}

    # Configure task parameters
    task_kwargs = {
        "task_prompt": question,
        "with_task_specify": False,
    }

    # Create and return the society
    society = RolePlaying(
        **task_kwargs,
        user_role_name="user",
        user_agent_kwargs=user_agent_kwargs,
        assistant_role_name="assistant",
        assistant_agent_kwargs=assistant_agent_kwargs,
    )

    return society


def main():
    # ✅ Excel analysis prompt you wanted
    default_task = (
        "Please read the file 'sales.xlsx' in the current directory, "
        "calculate the total revenue for each product by quarter, "
        "write the result to a sheet named 'Summary' in a new Excel file, "
        "and generate a bar chart using Python and save it as 'summary.png'."
    )

    task = sys.argv[1] if len(sys.argv) > 1 else default_task
    society = construct_society(task)
    answer, chat_history, token_count = run_society(society)

    print(f"\033[94mAnswer: {answer}\033[0m")


if __name__ == "__main__":
    main()