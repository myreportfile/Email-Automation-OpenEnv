# Email Automation OpenEnv

`Email Automation OpenEnv` is a small reinforcement-learning-style environment that simulates an email assistant. The environment gives an agent an email plus a task type, accepts a text response, and returns a reward based on how correct that response is.

This project is intentionally simple and easy to understand. It is a good starting point for:

- learning how an evaluation environment works
- testing rule-based or LLM-based email assistants
- exposing the environment through a FastAPI server
- experimenting with reward design for automation tasks

## What This Project Does

The environment currently supports 3 email-related tasks:

1. `classification` - classify an email into a category
2. `priority` - identify how urgent an email is
3. `action` - suggest the next action to take

Each episode works like this:

1. The environment picks one sample email task at random.
2. It returns an observation containing:
   - `email_text`
   - `task_type`
3. The agent sends back a text response.
4. The environment grades that response.
5. A reward is returned and the episode ends.

Right now, each episode is only one step long because `done=True` after the first call to `step()`.

## Project Structure

```text
email_env_project/
|-- Dockerfile
|-- README.md
|-- inference.py
|-- openenv.yaml
|-- pyproject.toml
|-- requirements.txt
|-- test_env.py
|-- uv.lock
|-- my_env/
|   |-- __init__.py
|   |-- env.py
|   |-- grader.py
|   `-- models.py
`-- server/
    `-- app.py
```

## Core Components

### `my_env/env.py`

This is the heart of the project. It defines the `EmailEnv` class, which:

- loads the built-in email tasks
- chooses a random task on `reset()`
- returns the current observation
- accepts an `EmailAction`
- calculates reward through the grader
- returns a `StepResult`

The environment currently contains 3 hardcoded sample tasks:

- `"Your Amazon order has been shipped"` -> task: `classification` -> answer: `shopping`
- `"URGENT: Server is down. Fix ASAP."` -> task: `priority` -> answer: `high`
- `"Meeting scheduled tomorrow at 10 AM"` -> task: `action` -> answer: `add_to_calendar`

### `my_env/grader.py`

This file contains the reward logic. It compares the agent response with the correct answer and returns:

- `1.0` for a correct answer
- `0.5` for a partially correct answer in some tasks
- `0.0` for an incorrect answer

Examples:

- For `priority`, answers like `urgent` or `important` receive partial credit when the correct answer is `high`.
- For `action`, any response containing `calendar` receives partial credit when the correct answer is `add_to_calendar`.

### `my_env/models.py`

This file defines the Pydantic data models used across the project:

- `EmailObservation`
- `EmailAction`
- `StepResult`

These models make the environment interface structured and easy to validate.

### `inference.py`

This is a simple local runner that demonstrates how an agent can interact with the environment.

It:

- creates an `EmailEnv`
- resets the environment
- uses a small rule-based agent
- sends an `EmailAction`
- logs rewards and completion status

The included rule-based agent uses keyword matching:

- if email contains `urgent` -> returns `high`
- if email contains `order` -> returns `shopping`
- if email contains `meeting` -> returns `add_to_calendar`
- otherwise -> returns `low`

Although `MAX_STEPS` is set to `3`, the environment ends after the first successful `step()` because each episode is single-step.

### `test_env.py`

This is a very simple manual test script. It:

- resets the environment
- prints the observation
- asks the user for a response
- shows the resulting reward and metadata

This is useful for quickly checking the environment without running the API server.

### `server/app.py`

This file exposes the environment as a FastAPI application.

It provides two endpoints:

- `POST /reset` - returns a new observation
- `POST /step` - accepts an action and returns observation, reward, done flag, and info

The server uses one global `EmailEnv` instance, so it behaves like a simple shared in-memory environment.

### `openenv.yaml`

This file declares environment metadata such as:

- environment name and version
- entry point: `my_env.env:EmailEnv`
- supported tasks
- action space
- observation space

This is the configuration that describes the environment in a portable OpenEnv-style format.

## Architecture Explanation

The project follows a clean and simple layered design.

```text
User / Agent
    |
    v
Action text
    |
    v
EmailEnv (my_env/env.py)
    |
    |-- creates observations
    |-- stores current task
    |-- calls grader
    v
Reward Logic (my_env/grader.py)
    |
    v
StepResult
    |
    +--> used by local scripts (inference.py, test_env.py)
    |
    `--> returned through API (server/app.py)
```

### Architecture Layers

#### 1. Data layer

`my_env/models.py` defines the structure of observations, actions, and step results.

This keeps the input/output format explicit and consistent across scripts and API calls.

#### 2. Environment layer

`my_env/env.py` manages episode state and task selection.

Responsibilities:

- load task samples
- reset the environment
- keep track of the current task
- call the grader with the user response
- return a standardized result object

#### 3. Reward layer

`my_env/grader.py` decides how good a response is.

This separation is helpful because reward logic can evolve independently from the environment itself.

#### 4. Interface layer

There are two ways to interact with the environment:

- local scripts:
  - `inference.py`
  - `test_env.py`
- HTTP API:
  - `server/app.py`

This means the same environment logic can be reused in both CLI-style testing and web/server-based integration.

## Data Flow

Here is the full flow of one episode:

1. `EmailEnv.reset()` randomly chooses one task from `self.tasks`
2. An `EmailObservation` is returned with:
   - `email_text`
   - `task_type`
3. The agent submits `EmailAction(response="...")`
4. `EmailEnv.step()` reads:
   - the user response
   - the expected answer
   - the task type
5. `grade_response()` computes a reward
6. `EmailEnv.step()` returns a `StepResult` containing:
   - observation
   - reward
   - done
   - info

## Reward Design

The reward system is small but clear.

### Classification task

- exact match -> `1.0`
- anything else -> `0.0`

### Priority task

- exact match -> `1.0`
- `urgent` or `important` -> `0.5`
- anything else -> `0.0`

### Action task

- exact match -> `1.0`
- any response containing `calendar` -> `0.5`
- anything else -> `0.0`

This design allows the environment to reward approximate but still useful behavior in some cases.

## Setup

### Requirements

The project uses Python packages listed in `requirements.txt` and `pyproject.toml`.

Main dependencies:

- `pydantic`
- `fastapi`
- `uvicorn`
- `openenv-core`

### Install with pip

```bash
pip install -r requirements.txt
```

### Or install from project metadata

```bash
pip install -e .
```

## How to Run

### 1. Run the local inference demo

```bash
python inference.py
```

This runs the rule-based agent against one randomly selected email task and prints structured logs.

### 2. Run the manual test script

```bash
python test_env.py
```

You will see the observation and can type your own response manually.

### 3. Run the FastAPI server

```bash
python -m server.app
```

Or, if the script entry point is installed:

```bash
server
```

The API starts on `http://0.0.0.0:8000`.

## API Usage

### Reset the environment

```http
POST /reset
```

Example response:

```json
{
  "email_text": "URGENT: Server is down. Fix ASAP.",
  "task_type": "priority"
}
```

### Submit an action

```http
POST /step
Content-Type: application/json
```

Example request:

```json
{
  "response": "high"
}
```

Example response:

```json
{
  "observation": {
    "email_text": "URGENT: Server is down. Fix ASAP.",
    "task_type": "priority"
  },
  "reward": 1.0,
  "done": true,
  "info": {
    "agent_response": "high",
    "correct_answer": "high"
  }
}
```

## Docker

The project includes a simple `Dockerfile`.

Build:

```bash
docker build -t email-env .
```

Run:

```bash
docker run --rm email-env
```

At the moment, the container runs `python inference.py` by default.

## OpenEnv Configuration

The `openenv.yaml` file describes the environment with:

- name: `email_env`
- version: `1.0`
- entry point: `my_env.env:EmailEnv`
- text action space
- object observation space with:
  - `email_text`
  - `task_type`

This makes the project easier to register and integrate with systems expecting OpenEnv-style metadata.

## Current Limitations

The current implementation is intentionally minimal. Important limitations include:

- only 3 hardcoded email examples
- no train/validation/test split
- one-step episodes only
- random task selection without seeding control
- shared global environment in the API server
- grading is rule-based and string-matching only
- no persistence, database, or user session management

## How to Extend This Project

Good next improvements would be:

- add more realistic email datasets
- support multi-step workflows
- add stronger normalization and semantic grading
- track separate user sessions in the API
- add automated tests
- add deterministic seeding for reproducibility
- replace the rule-based agent with an LLM-based policy

## Summary

This repository is a compact email-task evaluation environment built around a simple idea:

- show an email
- specify the task
- accept a text response
- assign a reward

Because the design is small and modular, it is easy to understand, demo, and extend. The environment logic, reward logic, data models, CLI scripts, and API layer are all separated cleanly, which makes this a solid foundation for a larger email automation benchmark.
