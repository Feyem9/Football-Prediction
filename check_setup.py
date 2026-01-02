# check_setup.py
import subprocess
import sys

def check_command(command, name):
    try:
        # Using shell=True for complex commands like 'redis-cli ping' or version checks
        result = subprocess.run(command, capture_output=True, text=True, shell=True, timeout=5)
        stdout = result.stdout.strip()
        stderr = result.stderr.strip()
        
        # Special case for Redis PONG
        if "redis-cli ping" in command:
            if "PONG" in stdout.upper():
                print(f"✅ {name}: Connecté (PONG)")
                return True
            else:
                print(f"❌ {name}: Impossible de joindre le serveur")
                return False

        version = stdout or stderr
        if result.returncode == 0:
            print(f"✅ {name}: {version.split('\n')[0] if version else 'Installé'}")
            return True
        else:
            print(f"❌ {name}: Erreur lors de l'exécution ({version[:50]})")
            return False
    except subprocess.TimeoutExpired:
        print(f"❌ {name}: Temps d'attente dépassé")
        return False
    except Exception as e:
        print(f"❌ {name}: NON INSTALLÉ ({str(e)})")
        return False

print("🔍 VÉRIFICATION DE L'ENVIRONNEMENT (Football Predictions)\n")

checks = [
    ("python3 --version", "Python"),
    ("pip3 --version", "pip"),
    ("node --version", "Node.js"),
    ("npm --version", "npm"),
    ("git --version", "Git"),
    ("psql --version", "PostgreSQL"),
    ("redis-cli --version", "Redis CLI"),
    ("redis-cli ping", "Serveur Redis"),
    ("code --version", "VS Code"),
]

results = []
for cmd, name in checks:
    results.append(check_command(cmd, name))

print(f"\n📊 RÉSULTAT: {sum(results)}/{len(results)} outils/états validés")

if all(results):
    print("\n🎉 PARFAIT ! Vous êtes prêt pour le 1er janvier 2026 !")
else:
    print("\n⚠️  Certains outils manquent ou ne sont pas configurés.")
    print("Veuillez installer les composants indiqués par ❌.")
