import pytest
from fastapi import status


class TestRegister:
    """Tests pour l'endpoint /auth/register."""
    
    def test_register_success(self, client, test_user_data):
        """Test: création d'utilisateur réussie."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data
        assert data["is_active"] == True
        assert "password" not in data  # Le mot de passe ne doit pas être retourné
    
    def test_register_duplicate_email(self, client, test_user_data, registered_user):
        """Test: email déjà utilisé."""
        response = client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "existe déjà" in response.json()["detail"]
    
    def test_register_duplicate_username(self, client, test_user_data, registered_user):
        """Test: username déjà utilisé."""
        new_user = {
            "username": test_user_data["username"],  # Même username
            "email": "different@example.com",
            "password": "different123"
        }
        response = client.post("/api/v1/auth/register", json=new_user)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "nom d'utilisateur" in response.json()["detail"]
    
    def test_register_invalid_email(self, client):
        """Test: format email invalide."""
        response = client.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "invalid-email",
            "password": "password123"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """Tests pour l'endpoint /auth/login."""
    
    def test_login_success(self, client, test_user_data, registered_user):
        """Test: connexion réussie."""
        response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, client, test_user_data, registered_user):
        """Test: mot de passe incorrect."""
        response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": "wrongpassword"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()
    
    def test_login_nonexistent_email(self, client):
        """Test: email inexistant."""
        response = client.post("/api/v1/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "somepassword"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_invalid_email_format(self, client):
        """Test: format email invalide."""
        response = client.post("/api/v1/auth/login", json={
            "email": "not-an-email",
            "password": "password"
        })
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestProtectedRoutes:
    """Tests pour les routes protégées."""
    
    def test_me_with_valid_token(self, client, test_user_data, auth_token):
        """Test: accès à /me avec token valide."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
    
    def test_me_without_token(self, client):
        """Test: accès à /me sans token."""
        response = client.get("/api/v1/auth/me")
        
        # HTTPBearer retourne 403 (Not authenticated) sans token
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]
    
    def test_me_with_invalid_token(self, client):
        """Test: accès à /me avec token invalide."""
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_profile_without_token(self, client):
        """Test: accès à /profile sans token."""
        response = client.get("/api/v1/profile")
        
        # HTTPBearer retourne 403 (Not authenticated) sans token
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]


class TestRefreshToken:
    """Tests pour le refresh token."""
    
    def test_refresh_token_success(self, client, test_user_data, registered_user):
        """Test: refresh token valide."""
        # Login pour obtenir le refresh token
        login_response = client.post("/api/v1/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Utiliser le refresh token
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()
    
    def test_refresh_token_invalid(self, client):
        """Test: refresh token invalide."""
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid_refresh_token"
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestLogout:
    """Tests pour le logout."""
    
    def test_logout_success(self, client, auth_token):
        """Test: logout réussi."""
        response = client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "réussie" in response.json()["message"]
    
    def test_token_blacklisted_after_logout(self, client, auth_token):
        """Test: token blacklisté après logout."""
        # Logout
        client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Essayer d'utiliser le même token
        response = client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "révoqué" in response.json()["detail"]
