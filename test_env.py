from my_env.env import EmailEnv
from my_env.models import EmailAction

env = EmailEnv()

obs = env.reset()
print("Observation:", obs)

# Try different responses
user_input = input("Enter your response: ")

action = EmailAction(response=user_input)
result = env.step(action)

print("Result:", result)