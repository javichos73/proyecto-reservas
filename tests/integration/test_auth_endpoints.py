def test_registrar_usuario_endpoint_exitoso(client):
    response = client.post(
        "/usuarios/",
        json={"email": "nuevo@ejemplo.com", "password": "password123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "nuevo@ejemplo.com"
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_registrar_usuario_email_duplicado(client):
    client.post(
        "/usuarios/",
        json={"email": "duplicado@ejemplo.com", "password": "password123"},
    )
    response = client.post(
        "/usuarios/",
        json={"email": "duplicado@ejemplo.com", "password": "otrapassword123"},
    )
    assert response.status_code == 400
    assert "ya se encuentra registrado" in response.json()["detail"]


def test_registrar_usuario_validacion_password_corta(client):
    response = client.post(
        "/usuarios/",
        json={"email": "invalido@ejemplo.com", "password": "123"},
    )
    assert response.status_code == 422


def test_login_token_exitoso(client):
    client.post(
        "/usuarios/",
        json={"email": "login@ejemplo.com", "password": "password123"},
    )

    response = client.post(
        "/usuarios/token",
        data={"username": "login@ejemplo.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_credenciales_invalidas(client):
    client.post(
        "/usuarios/",
        json={"email": "login2@ejemplo.com", "password": "password123"},
    )

    response = client.post(
        "/usuarios/token",
        data={"username": "login2@ejemplo.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert "Credenciales de acceso inválidas" in response.json()["detail"]
