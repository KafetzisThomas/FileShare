import json
import uuid
from django.conf import settings
from channels.generic.websocket import AsyncWebsocketConsumer
from cryptography.fernet import Fernet

fernet = Fernet(settings.ENCRYPTION_KEY)


class FileTransfer(AsyncWebsocketConsumer):

    async def connect(self):
        # generate unique id for connected user
        self.user_id = str(uuid.uuid4())[:10]
        self.room_group_name = "global"

        # add user to websocket group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

        # send unique id back to user for display
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_id",
                    "user_id": self.user_id,
                }
            )
        )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)

        if "file" in data and "target_user_id" in data:
            target_user_id = data["target_user_id"]
            file_name = data["file_name"]
            file_content = data["file"]

            # NOTE: FOR DEVELOPMENT ONLY !!!
            # print("Original: ", file_content[:10])

            encrypted_content = fernet.encrypt(file_content.encode()).decode()

            # NOTE: FOR DEVELOPMENT ONLY !!!
            # print("Encrypted: ", encrypted_content[:10])

            # send file only to the specific user based on their id
            await self.send_to_user(
                target_user_id,
                {
                    "type": "file_offer",
                    "file_name": file_name,
                    "file": encrypted_content,
                    "sender_id": self.user_id,
                },
            )

    async def send_to_user(self, target_user_id, file_data):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_file",
                "file_data": file_data,
                "target_user_id": target_user_id,
            },
        )

    async def send_file(self, event):
        file_data = event["file_data"]
        target_user_id = event["target_user_id"]

        if self.user_id == target_user_id:
            encrypted_file_content = file_data["file"]
            decrypted_content = fernet.decrypt(encrypted_file_content.encode()).decode()

            # NOTE: FOR DEVELOPMENT ONLY !!!
            # print("Decrypted: ", decrypted_content[:10])

            await self.send(
                text_data=json.dumps(
                    {
                        "type": "file_offer",
                        "file_name": file_data["file_name"],
                        "file": decrypted_content,
                        "sender_id": file_data["sender_id"],
                    }
                )
            )
