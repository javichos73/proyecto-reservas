from datetime import datetime, timezone
import pytest

from app.services.auth_service import (
    CredencialesInvalidasError,
    EmailDuplicadoError,
    TokenInvalidoError,
    autenticar_usuario,
    crear_access_token,
    hash_password,
    registrar_usuario,
    verificar_token,
    verify_password,
)


class FakeUsuario:
    def __init__(self, id: int, email: str, password_hash: str):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.creado_en = datetime.now(timezone.utc)


class RepositorioFalsoUsuario:
    def __init__(self):
        self.usuarios: dict[int, FakeUsuario] = {}
        self.next_id = 1

    def get_by_id(self, user_id: int, db=None):
        return self.usuarios.get(user_id)

    def get_by_email(self, email: str, db=None):
        for u in self.usuarios.values():
            if u.email == email:
                return u
        return None

    def create(self, email: str, password_hash: str, db=None):
        u = FakeUsuario(self.next_id, email, password_hash)
        self.usuarios[self.next_id] = u
        self.next_id += 1
        return u


def test_hash_and_verify_password():
    password = "secret_password_123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False


def test_crear_y_verificar_token_valido():
    data = {"sub": "1", "email": "test@example.com"}
    token = crear_access_token(data)

    payload = verificar_token(token)
    assert payload["sub"] == "1"
    assert payload["email"] == "test@example.com"
    assert "exp" in payload


def test_verificar_token_invalido():
    with pytest.raises(TokenInvalidoError):
        verificar_token("invalid.token.structure")


def test_registrar_usuario_exitoso():
    repo = RepositorioFalsoUsuario()
    user = registrar_usuario("jugador@test.com", "mypassword", repo=repo)

    assert user.id == 1
    assert user.email == "jugador@test.com"
    assert verify_password("mypassword", user.password_hash) is True


def test_registrar_usuario_email_duplicado():
    repo = RepositorioFalsoUsuario()
    registrar_usuario("jugador@test.com", "mypassword", repo=repo)

    with pytest.raises(EmailDuplicadoError, match="ya se encuentra registrado"):
        registrar_usuario("jugador@test.com", "another_pass", repo=repo)


def test_autenticar_usuario_exitoso():
    repo = RepositorioFalsoUsuario()
    registrar_usuario("jugador@test.com", "mypassword", repo=repo)

    user = autenticar_usuario("jugador@test.com", "mypassword", repo=repo)
    assert user.email == "jugador@test.com"


def test_autenticar_usuario_inexistente():
    repo = RepositorioFalsoUsuario()
    with pytest.raises(CredencialesInvalidasError):
        autenticar_usuario("no_existe@test.com", "password", repo=repo)


def test_autenticar_usuario_password_incorrecta():
    repo = RepositorioFalsoUsuario()
    registrar_usuario("jugador@test.com", "mypassword", repo=repo)

    with pytest.raises(CredencialesInvalidasError):
        autenticar_usuario("jugador@test.com", "wrong_pass", repo=repo)
