# FtpHook

FtpHook is a Flask-based application designed to download the latest release from a GitHub repository and manage files via FTP.

## Features

- Fetch the latest release from a GitHub repository.
- Download release assets matching a specific pattern (`release-*.tar.gz`).
- Upload files to an FTP server.
- Environment variable support using `python-dotenv`.

## Requirements

- Python 3.7 or higher
- Docker (optional, for containerized deployment)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aliesm-com/FtpHook.git
   cd FtpHook
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   API_KEY=your_api_key
   GITHUB_TOKEN=your_github_token
   FTP_HOST=ftp_host
   FTP_USER=ftp_user
   FTP_PASSWORD=ftp_password
   ```

## Usage

### Running Locally

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Access the application at `http://localhost:5000`.

### Running with Docker

1. Build and run the Docker container:
   ```bash
   docker-compose up --build
   ```

2. Access the application at `http://localhost:5000`.

## Project Structure

- `app.py`: Main application logic.
- `requirements.txt`: Python dependencies.
- `Dockerfile`: Docker image configuration.
- `docker-compose.yml`: Docker Compose configuration.
- `README.md`: Project documentation.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Contact

For any inquiries, please contact the repository owner.