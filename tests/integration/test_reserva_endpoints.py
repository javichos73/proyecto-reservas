def get_auth_token(client, email="jugador@test.com", password="password123"):
    client.post("/usuarios/", json={"email": email, "password": password})
    res = client.post(
        "/usuarios/token", data={"username": email, "password": password}
    )
    return res.json()["access_token"]


# --- Tests POST /reservas/ ---


def test_crear_reserva_endpoint_exitosa(client):
    token = get_auth_token(client, "user1@test.com")
    response = client.post(
        "/reservas/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "cancha": "Cancha Estrellas",
            "fecha": "2026-09-25",
            "hora_inicio": "18:00",
            "hora_fin": "19:00",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["cancha"] == "Cancha Estrellas"
    assert data["hora_inicio"] == "18:00"
    assert data["hora_fin"] == "19:00"
    assert "id" in data
    assert "usuario_id" in data


def test_crear_reserva_endpoint_solapamiento(client):
    token1 = get_auth_token(client, "user_solap1@test.com")
    token2 = get_auth_token(client, "user_solap2@test.com")

    # Usuario 1 reserva 18:00 a 20:00
    r1 = client.post(
        "/reservas/",
        headers={"Authorization": f"Bearer {token1}"},
        json={
            "cancha": "Cancha Estrellas",
            "fecha": "2026-09-25",
            "hora_inicio": "18:00",
            "hora_fin": "20:00",
        },
    )
    assert r1.status_code == 201

    # Usuario 2 intenta reservar 19:00 a 21:00 (solapamiento)
    r2 = client.post(
        "/reservas/",
        headers={"Authorization": f"Bearer {token2}"},
        json={
            "cancha": "Cancha Estrellas",
            "fecha": "2026-09-25",
            "hora_inicio": "19:00",
            "hora_fin": "21:00",
        },
    )
    assert r2.status_code == 400
    assert "conflicto de horario" in r2.json()["detail"]


def test_crear_reserva_endpoint_horario_invalido(client):
    token = get_auth_token(client, "user_inv@test.com")
    response = client.post(
        "/reservas/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "cancha": "Cancha Estrellas",
            "fecha": "2026-09-25",
            "hora_inicio": "19:00",
            "hora_fin": "18:00",
        },
    )
    assert response.status_code == 400
    assert "estrictamente posterior" in response.json()["detail"]


def test_crear_reserva_endpoint_minutos_fraccionados(client):
    token = get_auth_token(client, "user_frac@test.com")
    response = client.post(
        "/reservas/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "cancha": "Cancha Estrellas",
            "fecha": "2026-09-25",
            "hora_inicio": "18:30",
            "hora_fin": "19:30",
        },
    )
    # Pydantic schema pattern validation returns 422
    assert response.status_code == 422


def test_crear_reserva_sin_auth_401(client):
    response = client.post(
        "/reservas/",
        json={
            "cancha": "Cancha Estrellas",
            "fecha": "2026-09-25",
            "hora_inicio": "18:00",
            "hora_fin": "19:00",
        },
    )
    assert response.status_code == 401


# --- Tests GET /reservas/ ---


def test_listar_reservas_aislamiento_usuario(client):
    token_a = get_auth_token(client, "user_a@test.com")
    token_b = get_auth_token(client, "user_b@test.com")

    # User A crea 2 reservas
    client.post(
        "/reservas/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "cancha": "Cancha Estrellas",
            "fecha": "2026-09-26",
            "hora_inicio": "10:00",
            "hora_fin": "11:00",
        },
    )
    client.post(
        "/reservas/",
        headers={"Authorization": f"Bearer {token_a}"},
        json={
            "cancha": "Cancha Estrellas",
            "fecha": "2026-09-26",
            "hora_inicio": "12:00",
            "hora_fin": "13:00",
        },
    )

    # User B crea 1 reserva
    client.post(
        "/reservas/",
        headers={"Authorization": f"Bearer {token_b}"},
        json={
            "cancha": "Cancha Estrellas",
            "fecha": "2026-09-26",
            "hora_inicio": "14:00",
            "hora_fin": "15:00",
        },
    )

    # Consulta User A
    res_a = client.get("/reservas/", headers={"Authorization": f"Bearer {token_a}"})
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert len(data_a) == 2

    # Consulta User B
    res_b = client.get("/reservas/", headers={"Authorization": f"Bearer {token_b}"})
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert len(data_b) == 1


def test_listar_reservas_sin_auth_401(client):
    res = client.get("/reservas/")
    assert res.status_code == 401


# --- Tests DELETE /reservas/{id} ---


def test_cancelar_reserva_propia_exitosa(client):
    token = get_auth_token(client, "user_del@test.com")
    create_res = client.post(
        "/reservas/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "cancha": "Cancha Estrellas",
            "fecha": "2026-09-27",
            "hora_inicio": "18:00",
            "hora_fin": "19:00",
        },
    )
    reserva_id = create_res.json()["id"]

    delete_res = client.delete(
        f"/reservas/{reserva_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_res.status_code == 204


def test_cancelar_reserva_ajena_403(client):
    token_owner = get_auth_token(client, "owner@test.com")
    token_attacker = get_auth_token(client, "attacker@test.com")

    create_res = client.post(
        "/reservas/",
        headers={"Authorization": f"Bearer {token_owner}"},
        json={
            "cancha": "Cancha Estrellas",
            "fecha": "2026-09-27",
            "hora_inicio": "20:00",
            "hora_fin": "21:00",
        },
    )
    reserva_id = create_res.json()["id"]

    delete_res = client.delete(
        f"/reservas/{reserva_id}",
        headers={"Authorization": f"Bearer {token_attacker}"},
    )
    assert delete_res.status_code == 403
    assert "No tiene permiso" in delete_res.json()["detail"]


def test_cancelar_reserva_inexistente_404(client):
    token = get_auth_token(client, "user_notfound@test.com")
    delete_res = client.delete(
        "/reservas/99999",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert delete_res.status_code == 404
    assert "no fue encontrada" in delete_res.json()["detail"]
