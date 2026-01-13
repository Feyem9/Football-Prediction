"""
Tests E2E (End-to-End) pour le workflow complet utilisateur.

Flow testé:
1. Register un nouvel utilisateur
2. Login avec cet utilisateur
3. Récupérer les matchs (avec token)
4. Récupérer les classements
5. Récupérer les statistiques d'équipes
"""
import pytest
from fastapi import status


class TestE2EUserFlow:
    """
    Test E2E complet: register → login → get matches → get standings → get team stats.
    
    Ces tests simulent le parcours complet d'un utilisateur.
    """
    
    def test_full_user_journey(self, client):
        """
        Test E2E: Parcours complet d'un nouvel utilisateur.
        
        1. Création de compte
        2. Connexion
        3. Accès aux données matchs
        4. Accès aux classements
        5. Accès aux stats équipes
        """
        # Données utilisateur unique pour ce test
        user_data = {
            "username": "e2e_testuser",
            "email": "e2e_test@pronoscore.com",
            "password": "SecureP@ss123"
        }
        
        # ========== ÉTAPE 1: REGISTER ==========
        print("\n📝 Étape 1: Création de compte...")
        register_response = client.post("/api/v1/auth/register", json=user_data)
        
        assert register_response.status_code == status.HTTP_201_CREATED, \
            f"Registration failed: {register_response.json()}"
        
        user = register_response.json()
        assert user["username"] == user_data["username"]
        assert user["email"] == user_data["email"]
        assert "id" in user
        print(f"   ✅ Utilisateur créé avec ID: {user['id']}")
        
        # ========== ÉTAPE 2: LOGIN ==========
        print("\n🔐 Étape 2: Connexion...")
        login_response = client.post("/api/v1/auth/login", json={
            "email": user_data["email"],
            "password": user_data["password"]
        })
        
        assert login_response.status_code == status.HTTP_200_OK, \
            f"Login failed: {login_response.json()}"
        
        tokens = login_response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens
        access_token = tokens["access_token"]
        print(f"   ✅ Token obtenu: {access_token[:20]}...")
        
        # Headers d'authentification pour les requêtes suivantes
        auth_headers = {"Authorization": f"Bearer {access_token}"}
        
        # ========== ÉTAPE 3: GET MATCHES ==========
        print("\n⚽ Étape 3: Récupération des matchs...")
        matches_response = client.get(
            "/api/v1/matches?limit=5",
            headers=auth_headers
        )
        
        # Les matchs sont accessibles même sans auth, mais on teste avec token
        assert matches_response.status_code == status.HTTP_200_OK, \
            f"Get matches failed: {matches_response.json()}"
        
        matches_data = matches_response.json()
        assert "matches" in matches_data
        assert "count" in matches_data
        print(f"   ✅ {matches_data['count']} matchs récupérés")
        
        # ========== ÉTAPE 4: GET STANDINGS ==========
        print("\n📊 Étape 4: Récupération des classements (Premier League)...")
        standings_response = client.get(
            "/api/v1/matches/competitions/PL/standings",
            headers=auth_headers
        )
        
        assert standings_response.status_code == status.HTTP_200_OK, \
            f"Get standings failed: {standings_response.json()}"
        
        standings_data = standings_response.json()
        assert "standings" in standings_data
        assert "competition_code" in standings_data
        assert standings_data["competition_code"] == "PL"
        print(f"   ✅ {len(standings_data['standings'])} entrées de classement")
        
        # Vérifier la structure d'une entrée
        if standings_data["standings"]:
            first_team = standings_data["standings"][0]
            assert "team_name" in first_team
            assert "points" in first_team
            assert "position" in first_team
            print(f"   📈 Leader: {first_team['team_name']} ({first_team['points']} pts)")
        
        # ========== ÉTAPE 5: GET TEAM STATS ==========
        print("\n📈 Étape 5: Récupération des statistiques d'équipe...")
        # On récupère l'ID d'une équipe depuis les standings
        if standings_data["standings"]:
            team_id = standings_data["standings"][0]["team_id"]
            competition_code = standings_data["competition_code"]
            
            stats_response = client.get(
                f"/api/v1/teams/{team_id}/stats?competition={competition_code}",
                headers=auth_headers
            )
            
            # 200 si stats trouvées, 404 si équipe pas encore dans stats
            assert stats_response.status_code in [200, 404], \
                f"Get team stats failed: {stats_response.json()}"
            
            if stats_response.status_code == 200:
                stats_data = stats_response.json()
                print(f"   ✅ Stats récupérées pour team_id={team_id}")
                if "wins" in stats_data:
                    print(f"   📊 V: {stats_data['wins']} | D: {stats_data.get('losses', 'N/A')}")
            else:
                print(f"   ⚠️ Pas de stats pour team_id={team_id} (404 attendu)")
        
        # ========== ÉTAPE 6: VERIFY USER PROFILE ==========
        print("\n👤 Étape 6: Vérification du profil utilisateur...")
        me_response = client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert me_response.status_code == status.HTTP_200_OK, \
            f"Get profile failed: {me_response.json()}"
        
        profile = me_response.json()
        assert profile["email"] == user_data["email"]
        print(f"   ✅ Profil vérifié: {profile['username']}")
        
        print("\n🎉 TEST E2E COMPLET - SUCCÈS !")
    
    def test_unauthenticated_access_to_public_routes(self, client):
        """
        Test: Les routes publiques sont accessibles sans authentification.
        """
        # Matchs (public)
        matches_response = client.get("/api/v1/matches?limit=3")
        assert matches_response.status_code == status.HTTP_200_OK
        
        # Standings (public)
        standings_response = client.get("/api/v1/matches/competitions/PL/standings")
        assert standings_response.status_code == status.HTTP_200_OK
        
        # Competitions (public)
        competitions_response = client.get("/api/v1/matches/competitions")
        assert competitions_response.status_code in [200, 502]  # 502 si API externe down
    
    def test_protected_routes_require_auth(self, client):
        """
        Test: Les routes protégées nécessitent une authentification.
        """
        # /me sans token
        me_response = client.get("/api/v1/auth/me")
        assert me_response.status_code in [401, 403]
        
        # /profile sans token
        profile_response = client.get("/api/v1/profile")
        assert profile_response.status_code in [401, 403]


class TestE2EDataIntegrity:
    """
    Tests E2E pour vérifier l'intégrité des données.
    """
    
    def test_standings_have_required_fields(self, client):
        """Vérifie que les standings ont tous les champs requis."""
        response = client.get("/api/v1/matches/competitions/PL/standings")
        
        if response.status_code == 200:
            data = response.json()
            for team in data.get("standings", []):
                assert "position" in team
                assert "team_id" in team
                assert "team_name" in team
                assert "points" in team
                assert "played_games" in team
                assert "won" in team
                assert "draw" in team
                assert "lost" in team
    
    def test_matches_have_required_fields(self, client):
        """Vérifie que les matchs ont tous les champs requis."""
        response = client.get("/api/v1/matches?limit=5")
        
        if response.status_code == 200:
            data = response.json()
            for match in data.get("matches", []):
                assert "id" in match
                assert "home_team" in match
                assert "away_team" in match
                assert "match_date" in match
                assert "status" in match
