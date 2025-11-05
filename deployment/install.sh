#!/bin/bash

# TGPC Automation Installation Script
# This script sets up the TGPC automation system for daily updates

set -e

echo "🚀 Installing TGPC Automation System..."

# Configuration
INSTALL_DIR="/opt/tgpc"
SERVICE_USER="tgpc"
SERVICE_NAME="tgpc-automation"

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

# Create service user
echo "👤 Creating service user..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd --system --home-dir "$INSTALL_DIR" --shell /bin/bash "$SERVICE_USER"
    echo "✅ Created user: $SERVICE_USER"
else
    echo "ℹ️ User $SERVICE_USER already exists"
fi

# Create installation directory
echo "📁 Creating installation directory..."
mkdir -p "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR/data"
mkdir -p "$INSTALL_DIR/data/backups"
mkdir -p "$INSTALL_DIR/logs"

# Copy application files
echo "📋 Copying application files..."
cp -r tgpc/ "$INSTALL_DIR/"
cp requirements.txt "$INSTALL_DIR/"
cp pyproject.toml "$INSTALL_DIR/"
cp .env.example "$INSTALL_DIR/"

# Set ownership
chown -R "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR"

# Create Python virtual environment
echo "🐍 Setting up Python virtual environment..."
sudo -u "$SERVICE_USER" python3 -m venv "$INSTALL_DIR/venv"
sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install --upgrade pip
sudo -u "$SERVICE_USER" "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt"

# Install systemd service
echo "⚙️ Installing systemd service..."
cp deployment/tgpc-automation.service /etc/systemd/system/
systemctl daemon-reload

# Create environment file
echo "🔧 Creating environment configuration..."
if [ ! -f "$INSTALL_DIR/.env" ]; then
    cp "$INSTALL_DIR/.env.example" "$INSTALL_DIR/.env"
    chown "$SERVICE_USER:$SERVICE_USER" "$INSTALL_DIR/.env"
    echo "ℹ️ Created .env file from template - please configure as needed"
fi

# Create log rotation
echo "📝 Setting up log rotation..."
cat > /etc/logrotate.d/tgpc << EOF
$INSTALL_DIR/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 644 $SERVICE_USER $SERVICE_USER
}
EOF

# Enable and start service
echo "🎯 Enabling and starting service..."
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

# Create CLI symlink
echo "🔗 Creating CLI symlink..."
ln -sf "$INSTALL_DIR/venv/bin/python" /usr/local/bin/tgpc-cli
cat > /usr/local/bin/tgpc << 'EOF'
#!/bin/bash
cd /opt/tgpc
exec /opt/tgpc/venv/bin/python -m tgpc.cli.commands "$@"
EOF
chmod +x /usr/local/bin/tgpc

echo ""
echo "✅ TGPC Automation System installed successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Configure /opt/tgpc/.env with your settings"
echo "2. Test the installation: tgpc automation status"
echo "3. Start automation: tgpc automation start"
echo "4. Check service status: systemctl status tgpc-automation"
echo ""
echo "📊 Service will automatically:"
echo "• Update rx.json daily at 2:00 AM"
echo "• Validate data integrity and remove duplicates"
echo "• Create secure backups with checksums"
echo "• Perform safety checks and rollback protection"
echo ""
echo "🔧 Management commands:"
echo "• tgpc automation status    - Check automation status"
echo "• tgpc automation start     - Start daily automation"
echo "• tgpc automation stop      - Stop automation"
echo "• tgpc automation update    - Run manual update"
echo "• tgpc automation validate  - Validate current data"
echo ""
echo "📁 Important paths:"
echo "• Data: /opt/tgpc/data/rx.json"
echo "• Backups: /opt/tgpc/data/backups/"
echo "• Logs: journalctl -u tgpc-automation -f"
echo "• Config: /opt/tgpc/.env"