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

![fileshare](https://github.com/user-attachments/assets/df026073-42c8-43f9-92ce-b57b0e9a01b6)

## Demo Videos

### User 1

<https://github.com/user-attachments/assets/10552c38-0d08-4040-9fb5-e9093528b5ef>

### User 2

<https://github.com/user-attachments/assets/f07322d1-35b1-4569-b496-c61578b32e1b>

## Contributing Guidelines

### Pull Requests

* **Simplicity**: Keep changes focused and easy to review.
* **Libraries**: Avoid adding non-standard libraries unless discussed via an issue.
* **Testing**: Ensure code runs error-free, passes all tests, and meets coding standards.

### Bug Reports

* Report bugs via GitHub Issues.
* Submit pull requests via GitHub Pull Requests.

Thank you for supporting FileShare!
