def user_serializer(user: dict) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "age": user["age"]
    }


def auth_serializer(user):
    return {
        "id": str(user["_id"]),
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "email": user.get("email"),
        "agreement_id": user.get("agreement_id")
    }
