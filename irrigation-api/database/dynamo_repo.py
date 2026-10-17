import os
import boto3
from database.base import BaseUserRepository


class DynamoUserRepository(BaseUserRepository):
    def __init__(self):
        table_name = os.getenv("DYNAMODB_TABLE_USERS", "Users")
        region = os.getenv("AWS_REGION", "eu-central-1")
        dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = dynamodb.Table(table_name)

    def get_user_by_username(self, username: str):
        response = self.table.get_item(Key={"username": username})
        item = response.get("Item")
        if item:
            return item["username"], item["user_password"]
        return None

    def create_user(self, username: str, hashed_pwd: str):
        self.table.put.item(
            Item={
                "username": username,
                "user_password": str(hashed_pwd)
            }
        )
        return True
