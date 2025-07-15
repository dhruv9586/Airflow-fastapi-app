from bson import ObjectId


def parse_json(data):
    """Convert MongoDB documents to JSON-serializable format."""
    if isinstance(data, list):
        return [parse_json(item) for item in data]

    if isinstance(data, dict):
        return {key: parse_json(value) for key, value in data.items()}

    if isinstance(data, ObjectId):
        return str(data)

    return data
