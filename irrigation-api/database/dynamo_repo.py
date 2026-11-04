import os
import boto3
from database.base import BaseUserRepository, BaseZoneRepository


class DynamoUserRepository(BaseUserRepository):
    def __init__(self):
        table_name = os.getenv("DYNAMODB_TABLE_USERS", "users")
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
        self.table.put_item(
            Item={
                "username": username,
                "user_password": str(hashed_pwd)
            }
        )
        return True


class DynamoZoneRepository(BaseZoneRepository):
    def __init__(self):
        table_name = os.getenv("DYNAMODB_TABLE_ZONES", "zones")
        region = os.getenv("AWS_REGION", "eu-central-1")
        dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = dynamodb.Table(table_name)

    def get_all_zones(self) -> dict:
        response = self.table.scan()
        items = response.get("Items", [])
        # Връщаме ги като речник, подредени по zone_id
        zones_dict = {}
        for item in items:
            z_id = int(item["zone_id"])
            zones_dict[z_id] = {
                "name": item.get("name"),
                "status": item.get("status", "off"),
                "last_watered": item.get("last_watered", "Never")
            }
        return zones_dict

    def toggle_zone(self, zone_id: int, event_time: str) -> dict:
        response = self.table.get_item(Key={"zone_id": zone_id})
        item = response.get("Item")
        if not item:
            return None

        current_status = item.get("status", "off")
        new_status = "off" if current_status == "on" else "on"
        new_watered = event_time if new_status == "on" else item.get("last_watered", "Never")

        self.table.update_item(
            Key={"zone_id": zone_id},
            UpdateExpression="SET #st = :s, last_watered = :w",
            ExpressionAttributeNames={"#st": "status"},
            ExpressionAttributeValues={":s": new_status, ":w": new_watered}
        )

        return {
            "name": item.get("name"),
            "status": new_status,
            "last_watered": new_watered
        }