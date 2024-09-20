import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync


class FileTransferConsumer(WebsocketConsumer):
    """
    A WebSocket consumer for handling real-time file transfer between users.
    """

    def connect(self):
        """
        Handle the WebSocket connection when a client connects.
        """
        self.room_group_name = "global"
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        """
        Handle the WebSocket disconnection.
        """
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def receive(self, text_data):
        """
        Handle incoming WebSocket files from clients.
        """
        data = json.loads(text_data)  # Parse the JSON data
        file_name = data["file_name"]  # Extract file name
        file_content = data["file"]  # Extract file content

        # Broadcast the file & its metadata
        # to all users in the room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                "type": "send_file",
                "file_name": file_name,
                "file": file_content,
            },
        )

    def send_file(self, event):
        """
        Send the file to the WebSocket clients.
        """
        file_name = event["file_name"]
        file_content = event["file"]

        self.send(
            text_data=json.dumps(
                {
                    "type": "send_file",
                    "file_name": file_name,
                    "file": file_content,
                }
            )
        )
