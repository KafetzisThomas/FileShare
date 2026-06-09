from django.test import TransactionTestCase
from channels.testing import WebsocketCommunicator
from ..consumers import FileTransfer


class FileTransferTests(TransactionTestCase):

    async def test_connect(self):
        communicator = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

        response = await communicator.receive_json_from()
        self.assertEqual(response["type"], "user_id")
        self.assertIn("user_id", response)

        await communicator.disconnect()

    async def test_disconnect(self):
        communicator = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        await communicator.connect()
        await communicator.disconnect()

    async def test_file_transfer(self):
        communicator_sender = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        await communicator_sender.connect()

        communicator_receiver = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        await communicator_receiver.connect()

        receiver_response = await communicator_receiver.receive_json_from()
        receiver_id = receiver_response["user_id"]

        filename = "test.txt"
        file = "test content"

        await communicator_sender.send_json_to(
            {
                "type": "file",
                "target_user_id": receiver_id,
                "filename": filename,
                "file": file,
            }
        )

        receiver_event = await communicator_receiver.receive_json_from()
        self.assertEqual(receiver_event["type"], "file")
        self.assertEqual(receiver_event["filename"], filename)
        self.assertEqual(receiver_event["file"], file)

        await communicator_sender.disconnect()
        await communicator_receiver.disconnect()

    async def test_send_to_nonexistent_user(self):
        communicator = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        await communicator.connect()
        await communicator.receive_json_from()

        await communicator.send_json_to(
            {
                "type": "file",
                "target_user_id": "nonexistent",
                "filename": "test.txt",
                "file": "test content",
            }
        )

        self.assertTrue(await communicator.receive_nothing(timeout=0.5))

        await communicator.disconnect()

    async def test_receive_malformed_data_missing_keys(self):
        communicator = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        await communicator.connect()

        await communicator.receive_json_from()

        # missing file key
        await communicator.send_json_to(
            {
                "target_user_id": "some_id",
            }
        )
        self.assertTrue(await communicator.receive_nothing(timeout=0.5))

        # missing target_user_id key
        await communicator.send_json_to(
            {
                "file": "test content",
            }
        )
        self.assertTrue(await communicator.receive_nothing(timeout=0.5))

        # empty data
        await communicator.send_json_to({})
        self.assertTrue(await communicator.receive_nothing(timeout=0.5))

        await communicator.disconnect()

    async def test_sender_does_not_receive_own_file(self):
        communicator_sender = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        await communicator_sender.connect()

        communicator_receiver = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        await communicator_receiver.connect()

        await communicator_sender.receive_json_from()
        receiver_response = await communicator_receiver.receive_json_from()
        receiver_id = receiver_response["user_id"]

        await communicator_sender.send_json_to(
            {
                "type": "file",
                "target_user_id": receiver_id,
                "filename": "test.txt",
                "file": "test content",
            }
        )

        receiver_event = await communicator_receiver.receive_json_from()
        self.assertEqual(receiver_event["type"], "file")
        self.assertTrue(await communicator_sender.receive_nothing(timeout=0.5))

        await communicator_sender.disconnect()
        await communicator_receiver.disconnect()

    async def test_sender_id_in_received_event(self):
        communicator_sender = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        await communicator_sender.connect()

        communicator_receiver = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        await communicator_receiver.connect()

        sender_response = await communicator_sender.receive_json_from()
        sender_id = sender_response["user_id"]

        receiver_response = await communicator_receiver.receive_json_from()
        receiver_id = receiver_response["user_id"]

        await communicator_sender.send_json_to(
            {
                "type": "file",
                "target_user_id": receiver_id,
                "filename": "test.txt",
                "file": "test content",
            }
        )

        receiver_event = await communicator_receiver.receive_json_from()
        self.assertEqual(receiver_event["sender_id"], sender_id)

        await communicator_sender.disconnect()
        await communicator_receiver.disconnect()

    async def test_multiple_concurrent_transfers(self):
        communicator_a = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        communicator_b = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")
        communicator_c = WebsocketCommunicator(FileTransfer.as_asgi(), "/ws/socket-server/")

        await communicator_a.connect()
        await communicator_b.connect()
        await communicator_c.connect()

        await communicator_a.receive_json_from()
        response_b = await communicator_b.receive_json_from()
        response_c = await communicator_c.receive_json_from()

        id_b = response_b["user_id"]
        id_c = response_c["user_id"]

        # a -> b
        await communicator_a.send_json_to(
            {
                "type": "file",
                "target_user_id": id_b,
                "filename": "test_b.txt",
                "file": "test content",
            }
        )

        # a -> c
        await communicator_a.send_json_to(
            {
                "type": "file",
                "target_user_id": id_c,
                "filename": "test_c.txt",
                "file": "test content",
            }
        )

        # b should receive their file
        event_b = await communicator_b.receive_json_from()
        self.assertEqual(event_b["filename"], "test_b.txt")
        self.assertEqual(event_b["file"], "test content")

        # c should receive their file
        event_c = await communicator_c.receive_json_from()
        self.assertEqual(event_c["filename"], "test_c.txt")
        self.assertEqual(event_c["file"], "test content")

        # b should not receive c's file and vice versa
        self.assertTrue(await communicator_b.receive_nothing(timeout=0.5))
        self.assertTrue(await communicator_c.receive_nothing(timeout=0.5))

        await communicator_a.disconnect()
        await communicator_b.disconnect()
        await communicator_c.disconnect()
