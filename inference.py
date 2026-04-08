import asyncio
from typing import List

from my_env.env import EmailEnv
from my_env.models import EmailAction

TASK_NAME = "email_task"
BENCHMARK = "email_env"
MODEL_NAME = "rule-based-agent"
MAX_STEPS = 3


def log_start():
    print(f"[START] task={TASK_NAME} env={BENCHMARK} model={MODEL_NAME}")


def log_step(step, action, reward, done):
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error=null")


def log_end(success, steps, rewards: List[float]):
    rewards_str = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} rewards={rewards_str}")


def simple_agent(obs):
    text = obs.email_text.lower()

    if "urgent" in text:
        return "high"
    elif "order" in text:
        return "shopping"
    elif "meeting" in text:
        return "add_to_calendar"
    return "low"


async def main():
    env = EmailEnv()
    rewards = []

    log_start()

    obs = env.reset()

    for step in range(1, MAX_STEPS + 1):
        action_text = simple_agent(obs)
        action = EmailAction(response=action_text)

        result = env.step(action)

        reward = result.reward
        done = result.done

        rewards.append(reward)

        log_step(step, action_text, reward, done)

        if done:
            break

    success = sum(rewards) > 0
    log_end(success, step, rewards)


if __name__ == "__main__":
    asyncio.run(main())