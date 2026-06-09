<div align="center">
  <img src="static/favicon.png" width="150"/>
  <p><strong>FileShare: </strong>Send and receive files over the network.<br>Written in Python/Django</p>
</div>

## How It Works

### Sender Process

1. The file is first `byte encoded` (client side).
2. The encoded file is then `encrypted` using AES 256 bit encryption (server side).
3. The encrypted file is `transferred` to the recipient (still encrypted).

### Receiver Process

1. The received file is `decrypted` using the same encryption key (server side).
2. The decrypted data is `byte decoded` (client side).
3. The original file is `reconstructed` and made available for download.

This way only the intended recipient can access the file throughout the transfer.

## Usage

### Local Development

First install `uv` and sync the project dependencies:

```bash
cd path/to/root/directory
pip install uv
uv sync
```

Set up your environment variables:

```bash
cp .env.example .env
nano .env  # modify file, instructions inside
```

Migrate database:

```bash
uv run manage.py migrate
```

Run Django server:

```bash
uv run manage.py runserver
```

Access web application at `http://127.0.0.1:8000` or `http://localhost:8000`.  
Open two browser windows to transfer files between users.

## Run Tests

```bash
uv run manage.py test
```

## Demo Image

![demo image](/assets/demo_image.png)

## Demo Videos

### user 1 -> user 2

![user1_to_user2](/assets/user1_to_user2.mp4)

### user 2 -> user 1

![user2_to_user1](/assets/user2_to_user1.mp4)

## Contributing Guidelines

### Pull Requests

* **Simplicity**: Keep changes focused and easy to review.
* **Libraries**: Avoid adding non-standard libraries unless discussed via an issue.
* **Testing**: Ensure code runs error-free, passes all tests, and meets coding standards.

### Bug Reports

* Report bugs via GitHub Issues.
* Submit pull requests via GitHub Pull Requests.

Thank you for supporting FileShare!
