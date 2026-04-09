def user_serializer(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "age": user["age"]
    }


def auth_serializer(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "surname": user["surname"],
        "email": user["email"],
        "privacy_level": user.get("privacy_level", 1)
    }