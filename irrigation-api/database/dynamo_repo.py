"""
AWS DynamoDB repository implementation using Boto3.
Handles serverless user persistence and irrigation zone management for AWS deployments.
"""

import os
import time
import boto3
from fastapi import HTTPException
from boto3.dynamodb.conditions import Key, Attr
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


class DynamoZoneRepository(BaseZoneRepository):  # type: ignore
    """Repository handling irrigation zone management and telemetry state in AWS DynamoDB."""

    def __init__(self):
        table_name = os.getenv("DYNAMODB_TABLE_ZONES", "zones")
        region = os.getenv("AWS_REGION", "eu-central-1")
        dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = dynamodb.Table(table_name)

    def get_all_zones(self) -> dict:
        """Scans and retrieves all irrigation zones (fallback), returning them mapped by their zone IDs."""
        response = self.table.scan()
        items = response.get("Items", [])

        zones_dict = {}
        for item in items:
            z_id = int(item["zone_id"])
            zones_dict[z_id] = {
                "name": item.get("name"),
                "status": item.get("status", "off"),
                "last_watered": item.get("last_watered", "Never"),
                "last_watered_duration": item.get("last_watered_duration", "00:00")
            }
        return zones_dict

    def get_zones_by_user(self, owner: str) -> dict:
        """Retrieves irrigation zones strictly for a specific user using a filter."""
        response = self.table.scan(
            FilterExpression=Attr('owner').eq(owner)
        )
        items = response.get("Items", [])

        zones_dict = {}
        for item in items:
            z_id = int(item["zone_id"])
            zones_dict[z_id] = {
                "name": item.get("name"),
                "status": item.get("status", "off"),
                "last_watered": item.get("last_watered", "Never"),
                "last_watered_duration": item.get("last_watered_duration", "00:00")
            }
        return zones_dict

    def toggle_zone(self, zone_id: int, event_time: str, owner: str = None) -> dict:  # type: ignore
        """
        Toggles a zone's operational state ('on'/'off') in DynamoDB.
        Calculates running duration and respects owner isolation.
        """
        response = self.table.get_item(Key={"zone_id": zone_id})
        item = response.get("Item")
        if not item:
            return None  # type: ignore

        if owner and item.get("owner") != owner:
            return None  # type: ignore

        current_status = item.get("status", "off")
        current_time = time.time()
        duration = item.get("last_watered_duration", "00:00")
        new_watered = item.get("last_watered", "Never")

        if current_status == "off":
            new_status = "on"
            started_at = str(current_time)

            self.table.update_item(
                Key={"zone_id": zone_id},
                UpdateExpression="SET #st = :s, started_at = :sa",
                ExpressionAttributeNames={"#st": "status"},
                ExpressionAttributeValues={":s": new_status, ":sa": started_at}
            )
        else:
            new_status = "off"
            new_watered = event_time
            started_at_str = item.get("started_at")

            if started_at_str:
                elapsed_seconds = int(current_time - float(started_at_str))
                days = elapsed_seconds // 86400
                hours = (elapsed_seconds % 86400) // 3600
                minutes = (elapsed_seconds % 3600) // 60
                seconds = elapsed_seconds % 60

                if days > 0:
                    duration = f"{days}d {hours}h {minutes}m"
                elif hours > 0:
                    duration = f"{hours}h {minutes}m"
                elif minutes > 0:
                    duration = f"{minutes}m {seconds}s"
                else:
                    duration = f"{seconds}s"
            else:
                duration = "N/A"

            self.table.update_item(
                Key={"zone_id": zone_id},
                UpdateExpression="SET #st = :s, last_watered = :w, last_watered_duration = :d, started_at = :sa",
                ExpressionAttributeNames={"#st": "status"},
                ExpressionAttributeValues={
                    ":s": new_status,
                    ":w": new_watered,
                    ":d": duration,
                    ":sa": None
                }
            )

        return {
            "name": item.get("name"),
            "status": new_status,
            "last_watered": new_watered,
            "last_watered_duration": duration
        }

    def add_zone(self, name: str, owner: str = "default_user") -> dict:
        """Adds a new irrigation zone linked to the active user in DynamoDB with limits and checks."""
        user_zones = self.get_zones_by_user(owner)
        if len(user_zones) >= 20:
            raise HTTPException(status_code=400, detail="Maximum limit of 20 zones reached for this account.")

        for z_id, z_data in user_zones.items():
            if z_data["name"] == name:
                raise HTTPException(status_code=400, detail="A zone with this name already exists!")

        zone_id = int(time.time() * 1000)

        new_item = {
            "zone_id": zone_id,
            "name": name,
            "owner": owner,
            "status": "off",
            "last_watered": "Never",
            "last_watered_duration": "00:00",
            "started_at": None
        }

        self.table.put_item(Item=new_item)

        return {
            "id": zone_id,
            "name": name,
            "status": "off",
            "last_watered": "Never",
            "last_watered_duration": "00:00"
        }

    def delete_zone(self, zone_id: int, owner: str = None) -> bool:  # type: ignore
        """Deletes an irrigation zone by its ID and owner from DynamoDB."""
        response = self.table.get_item(Key={"zone_id": zone_id})
        item = response.get("Item")

        if not item:
            return False

        if owner and item.get("owner") != owner:
            return False

        self.table.delete_item(Key={"zone_id": zone_id})
        return True