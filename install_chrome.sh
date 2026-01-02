#!/bin/bash
echo "🚀 Téléchargement de Google Chrome..."
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb

echo "📦 Installation de Google Chrome..."
sudo apt update
sudo apt install -y ./google-chrome-stable_current_amd64.deb

echo "🧹 Nettoyage..."
rm google-chrome-stable_current_amd64.deb

echo "✅ Google Chrome a été installé avec succès !"
