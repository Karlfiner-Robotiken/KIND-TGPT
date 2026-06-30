#!/data/data/com.termux/files/usr/bin/bash
echo "🚀 Installing Karlfine GOD MODE..."
pkg update -y && pkg upgrade -y
pkg install python git nodejs clang cmake wget -y
pip install --upgrade pip
pip install -r requirements.txt
pkg reinstall libcurl -y
pkg install openssl -y
chmod +x start.sh
echo "✅ GOD MODE INSTALLED"
