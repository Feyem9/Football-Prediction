#!/bin/bash

# Script d'installation de pgAdmin 4 pour Ubuntu
# Source: https://www.pgadmin.org/download/pgadmin-4-apt/

echo "🚀 Configuration du dépôt pgAdmin 4..."

# Installer la clé publique
curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /usr/share/keyrings/packages-pgadmin-org.gpg

# Créer le fichier de configuration du dépôt (On utilise 'noble' car 'plucky' n'est pas encore dispo)
sudo sh -c 'echo "deb [signed-by=/usr/share/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/noble pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list'

# Mettre à jour et installer
echo "📦 Installation de pgAdmin 4 (Bureau et Web)..."
sudo apt update
sudo apt install -y pgadmin4

echo "✅ pgAdmin 4 a été installé."
echo "----------------------------------------------------"
echo "ATTENTION : Pour configurer le mode WEB, vous devez exécuter :"
echo "sudo /usr/pgadmin4/bin/setup-web.sh"
echo "----------------------------------------------------"
