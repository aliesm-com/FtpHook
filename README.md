# GitHub Release FTP Deploy

A Python Flask webhook handler that automatically deploys GitHub releases to cPanel hosting via FTP.

## Features

- **GitHub Webhook Integration**: Automatically triggered when new releases are published
- **Release Download**: Downloads the latest release assets from GitHub
- **Archive Extraction**: Supports ZIP and TAR.GZ archives
- **FTP Upload**: Uploads extracted files to cPanel hosting via FTP
- **Manual Deployment**: API endpoint for manual deployments
- **Health Monitoring**: Health check endpoint for monitoring

## Setup

### 1. Environment Configuration

Copy `.env.example` to `.env` and configure your settings:

```bash
cp .env.example .env
```

Edit `.env` with your actual values:

```env
# GitHub Token (optional, for private repos)
GITHUB_TOKEN=your_github_personal_access_token

# FTP Configuration (required)
FTP_HOST=ftp.yourdomain.com
FTP_USER=username@yourdomain.com
FTP_PASSWORD=your_secure_password
FTP_REMOTE_DIR=/public_html

# Flask Configuration
PORT=5000
DEBUG=false
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Application

```bash
python app.py
```

The service will start on `http://localhost:5000` (or your configured port).

## API Endpoints

### Webhook Endpoint
- **URL**: `POST /webhook/github`
- **Purpose**: Receives GitHub release notifications
- **Headers**: Set this as your GitHub webhook URL

### Manual Deployment
- **URL**: `POST /deploy/<owner>/<repo>`
- **Purpose**: Manually trigger deployment of the latest release
- **Example**: `POST /deploy/aliesm-com/FtpHook`

### Health Check
- **URL**: `GET /health`
- **Purpose**: Check service status

### API Info
- **URL**: `GET /`
- **Purpose**: Get API information and available endpoints

## GitHub Webhook Setup

1. Go to your GitHub repository settings
2. Navigate to **Webhooks** section
3. Click **Add webhook**
4. Set the Payload URL to: `http://your-server.com:5000/webhook/github`
5. Content type: `application/json`
6. Select **Let me select individual events**
7. Check only **Releases**
8. Ensure **Active** is checked
9. Save the webhook

## Usage Example

### Manual Deployment via API

```bash
# Deploy latest release of FtpHook repository
curl -X POST http://localhost:5000/deploy/aliesm-com/FtpHook
```

### Response Example

```json
{
  "success": true,
  "message": "Successfully deployed release v1.0.0",
  "release_info": {
    "tag_name": "v1.0.0",
    "name": "Release v1.0.0",
    "published_at": "2025-07-19T12:00:00Z"
  }
}
```

## Configuration Details

### FTP Settings
- **FTP_HOST**: Your cPanel FTP hostname
- **FTP_USER**: FTP username (usually email@domain.com for cPanel)
- **FTP_PASSWORD**: FTP password
- **FTP_REMOTE_DIR**: Target directory on server (e.g., `/public_html`)

### GitHub Token
- Optional for public repositories
- Required for private repositories
- Create at: GitHub Settings → Developer settings → Personal access tokens
- Required scopes: `repo` (for private repos) or `public_repo` (for public repos)

## Deployment

### Using Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

### Using systemd (Linux)

Create `/etc/systemd/system/github-deploy.service`:

```ini
[Unit]
Description=GitHub Release FTP Deploy
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/your/app
Environment=PATH=/path/to/your/venv/bin
ExecStart=/path/to/your/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Security Considerations

1. **Environment Variables**: Never commit `.env` file to version control
2. **HTTPS**: Use HTTPS in production for webhook endpoints
3. **Webhook Secret**: Consider implementing GitHub webhook secret validation
4. **FTP Credentials**: Use secure FTP passwords and consider SFTP if available
5. **Network Security**: Restrict access to the webhook endpoint if possible

## Troubleshooting

### Common Issues

1. **FTP Connection Failed**
   - Verify FTP credentials
   - Check if FTP service is enabled in cPanel
   - Ensure correct hostname and port

2. **GitHub API Rate Limiting**
   - Add GITHUB_TOKEN for higher rate limits
   - Check API usage in GitHub settings

3. **Archive Extraction Failed**
   - Ensure release contains valid ZIP or TAR.GZ files
   - Check file permissions

### Logs

The application logs all operations. Check console output for detailed error messages.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
