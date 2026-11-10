"""
AWS DynamoDB repository implementation using Boto3.
Handles serverless user persistence and irrigation zone management for AWS deployments.
"""

import os
import boto3
from database.base import BaseUserRepository, BaseZoneRepository


class DynamoUserRepository(BaseUserRepository):
    """Repository handling user data operations against AWS DynamoDB."""

    def __init__(self):
        table_name = os.getenv("DYNAMODB_TABLE_USERS", "users")
        region = os.getenv("AWS_REGION", "eu-central-1")
        dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = dynamodb.Table(table_name)

    def get_user_by_username(self, username: str):
        """Retrieves a user record by username from DynamoDB."""
        response = self.table.get_item(Key={"username": username})
        item = response.get("Item")
        if item:
            return item["username"], item["user_password"]
        return None

    def create_user(self, username: str, hashed_pwd: str):
        """Persists a new user record into the DynamoDB users table."""
        self.table.put_item(
            Item={
                "username": username,
                "user_password": str(hashed_pwd)
            }
        )
        return True


class DynamoZoneRepository(BaseZoneRepository):
    """Repository handling irrigation zone management and telemetry state in AWS DynamoDB."""

    def __init__(self):
        table_name = os.getenv("DYNAMODB_TABLE_ZONES", "zones")
        region = os.getenv("AWS_REGION", "eu-central-1")
        dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = dynamodb.Table(table_name)

    def get_all_zones(self) -> dict:
        """Scans and retrieves all irrigation zones, returning them mapped by their zone IDs."""
        response = self.table.scan()
        items = response.get("Items", [])

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
        """
        Toggles a zone's operational state ('on'/'off') in DynamoDB using update expressions.
        Records the current timestamp if turned 'on'.
        """
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