from django.test import TransactionTestCase
from channels.testing import WebsocketCommunicator
from ..consumers import FileTransfer


class FileTransferTests(TransactionTestCase):

    async def test_connect(self):
        communicator = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        # Receive the user ID from the server
        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "user_id")
        self.assertIn("user_id", response)

        await communicator.disconnect()

    async def test_disconnect(self):
        communicator = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        await communicator.connect()
        await communicator.disconnect()

    async def test_file_transfer(self):
        # Create communicator for the sender
        communicator_sender = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        await communicator_sender.connect()

        # Create communicator for the receiver
        communicator_receiver = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        await communicator_receiver.connect()

        # Get the receiver user ID
        receiver_response = await communicator_receiver.receive_json_from()
        receiver_id = receiver_response["user_id"]

        # Mock file transfer
        file_name = "test_file.txt"
        file_content = "Hello, World!"  # The original file content

        # Send the file from sender to receiver
        await communicator_sender.send_json_to(
            {
                "type": "file_offer",
                "target_user_id": receiver_id,
                "file_name": file_name,
                "file": file_content,
            }
        )

        # Receive the actual file on the receiver's side
        receiver_event = await communicator_receiver.receive_json_from()

        # Check that the file offer event was received
        self.assertEqual(receiver_event["type"], "file_offer")
        self.assertEqual(receiver_event["file_name"], file_name)

        # Encryption check: The receiver should get the decrypted content
        self.assertEqual(
            receiver_event["file"], file_content
        )  # Decrypted content matches original

        # Disconnect both communicators
        await communicator_sender.disconnect()
        await communicator_receiver.disconnect()
