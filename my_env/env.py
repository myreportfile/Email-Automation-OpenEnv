from .grader import grade_response
import random
from .models import EmailObservation, EmailAction, StepResult


class EmailEnv:

    def __init__(self):
        self.tasks = self.load_tasks()
        self.current_task = None
        self.done = False

    def load_tasks(self):
        return [
            {
                "email": "Your Amazon order has been shipped",
                "task": "classification",
                "answer": "shopping"
            },
            {
                "email": "URGENT: Server is down. Fix ASAP.",
                "task": "priority",
                "answer": "high"
            },
            {
                "email": "Meeting scheduled tomorrow at 10 AM",
                "task": "action",
                "answer": "add_to_calendar"
            }
        ]

    def reset(self):
        self.current_task = random.choice(self.tasks)
        self.done = False

        return EmailObservation(
            email_text=self.current_task["email"],
            task_type=self.current_task["task"]
        )

    def state(self):
        return EmailObservation(
            email_text=self.current_task["email"],
            task_type=self.current_task["task"]
        )

    def step(self, action: EmailAction):
        user_response = action.response
        correct_answer = self.current_task["answer"]
        task_type = self.current_task["task"]

        # 🎯 Calculate reward
        reward = grade_response(task_type, user_response, correct_answer)

        self.done = True

        return StepResult(
            observation=self.state(),
            reward=reward,
            done=self.done,
            info={
                "agent_response": user_response,
                "correct_answer": correct_answer
            }
        )   