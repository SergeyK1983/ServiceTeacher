
class AccountSWSchema:

    register_user = {
        "summary": "Registration the user",
        "description": """
        Регистрация пользователя в системе. Если пользователь уже существует, то будет поднято исключение.
        """,
        "response_description": "Return user",
        # "deprecated": True  # Пометка, что операция пути устаревшая
    }
