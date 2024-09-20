import json
import uuid
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class FileTransferConsumer(WebsocketConsumer):
    """
    A WebSocket consumer that handles file transfers between users,
    based on unique identifiers.
    """

    def connect(self):
        """
        Assign a unique ID to the connected user.
        Update the list of connected peers.
        """
        # Generate a unique ID for the connected user
        self.user_id = str(uuid.uuid4())
        self.room_group_name = "global"

        # Add the user to the WebSocket group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )

        self.accept()

        # Send the unique ID back to the user
        self.send(
            text_data=json.dumps(
                {
                    "type": "user_id",
                    "user_id": self.user_id,
                }
            )
        )

        # Update the list of connected peers
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "user_connected",
                "user_id": self.user_id,
            },
        )

    def disconnect(self, close_code):
        """
        Remove the user from the group when they disconnect.
        Update the list of connected peers.
        """
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

        # Update the list of connected peers
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "user_disconnected",
                "user_id": self.user_id,
            },
        )

    def receive(self, text_data):
        """
        Handle incoming files from specific users based on user_id.
        """
        data = json.loads(text_data)  # Parse the JSON data

        # Check if JSON data contain a file and a target user ID
        if "file" in data and "target_user_id" in data:
            # Extract target user id, file name, file content
            target_user_id = data["target_user_id"]
            file_name = data["file_name"]
            file_content = data["file"]

            # Send the file only to the specific user,
            # based on their user_id
            self.send_to_user(
                target_user_id,
                {
                    "type": "file_offer",
                    "file_name": file_name,
                    "file": file_content,
                    "sender_id": self.user_id,
                },
            )

    def send_to_user(self, target_user_id, file_data):
        """
        Send a file to a specific user identified by their user_id.
        """
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "send_file",
                "file_data": file_data,
                "target_user_id": target_user_id,
            },
        )

    def send_file(self, event):
        """
        Send the file to the specific target user.
        """
        file_data = event["file_data"]
        target_user_id = event["target_user_id"]

        if self.user_id == target_user_id:
            self.send(text_data=json.dumps(file_data))

    def user_connected(self, event):
        """
        Update the list of connected peers when a user joins.
        """
        self.send(
            text_data=json.dumps(
                {
                    "type": "user_connected",
                    "user_id": event["user_id"],
                }
            )
        )

    def user_disconnected(self, event):
        """
        Update the list of connected peers when a user leaves.
        """
        self.send(
            text_data=json.dumps(
                {
                    "type": "user_disconnected",
                    "user_id": event["user_id"],
                }
            )
        )
