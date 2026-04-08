def grade_response(task_type, user_response, correct_answer):
    user_response = user_response.lower().strip()
    correct_answer = correct_answer.lower().strip()

    # Task 1: Classification
    if task_type == "classification":
        if user_response == correct_answer:
            return 1.0
        else:
            return 0.0

    # Task 2: Priority
    elif task_type == "priority":
        if user_response == correct_answer:
            return 1.0
        elif user_response in ["urgent", "important"]:
            return 0.5
        else:
            return 0.0

    # Task 3: Action
    elif task_type == "action":
        if user_response == correct_answer:
            return 1.0
        elif "calendar" in user_response:
            return 0.5
        else:
            return 0.0

    return 0.0