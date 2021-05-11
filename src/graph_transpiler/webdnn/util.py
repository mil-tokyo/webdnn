import uuid

def make_random_identifier():
    return "_" + str(uuid.uuid4()).replace("-", "")
