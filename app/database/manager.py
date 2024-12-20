import os

def connect_to_database():
    """ Instantiate specific backend database. """
    database = os.getenv('DATABASE', 'DYNAMODB')
    if database == "POSTGRES":
        from database.postgres import PostgreSQL
        return PostgreSQL(os.environ["DATABASE_URL"])
    elif database == "DYNAMODB":
        from database.dynamo import DynamoDB
        return DynamoDB(os.environ["DATABASE_URL"])
    elif database == "REDIS":
        from database.redis import RedisWrapper
        return RedisWrapper()
    else:
        raise NotImplementedError("Requested database not supported. ")