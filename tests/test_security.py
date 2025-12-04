"""
Pruebas unitarias para el módulo de seguridad (JWT tokens).
Generado por IA - Fecha: 2024-12-19
"""
import pytest
from datetime import datetime, timedelta, timezone
from app.core.security import create_access_token, verify_token, TokenError


class TestSecurity:
    """
    Generado por IA - Fecha: 2024-12-19
    Descripción: Suite de pruebas para funciones de seguridad JWT
    """
    
    def test_create_access_token_success(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que se pueda crear un token JWT válido con datos básicos
        Parámetros de entrada:
            - data: dict con {"sub": "1", "rol": "uploader"}
            - expires_minutes: None (usa el valor por defecto)
        Retorno esperado: String con token JWT válido
        """
        data = {"sub": "1", "rol": "uploader"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # Los JWT tienen formato: header.payload.signature
    
    def test_create_access_token_with_custom_expiration(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que se pueda crear un token con tiempo de expiración personalizado
        Parámetros de entrada:
            - data: dict con {"sub": "2", "rol": "viewer"}
            - expires_minutes: 30
        Retorno esperado: String con token JWT válido que expira en 30 minutos
        """
        data = {"sub": "2", "rol": "viewer"}
        token = create_access_token(data, expires_minutes=30)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Verificar que el token contiene el claim de expiración
        payload = verify_token(token)
        assert "exp" in payload
    
    def test_verify_token_success(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que se pueda validar un token JWT válido y extraer su payload
        Parámetros de entrada:
            - token: String con token JWT válido generado por create_access_token
        Retorno esperado: Dict con el payload del token (sub, rol, exp)
        """
        data = {"sub": "1", "rol": "uploader"}
        token = create_access_token(data)
        payload = verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["rol"] == "uploader"
        assert "exp" in payload
    
    def test_verify_token_invalid_token(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que se lance TokenError al intentar verificar un token inválido
        Parámetros de entrada:
            - token: String con token inválido "invalid_token"
        Retorno esperado: TokenError con mensaje "Invalid token"
        """
        invalid_token = "invalid_token"
        
        with pytest.raises(TokenError) as exc_info:
            verify_token(invalid_token)
        
        assert "Invalid token" in str(exc_info.value)
    
    def test_verify_token_expired_token(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que se lance TokenError al intentar verificar un token expirado
        Parámetros de entrada:
            - token: String con token JWT expirado (creado con expires_minutes negativo)
        Retorno esperado: TokenError con mensaje "Token expired"
        """
        data = {"sub": "1", "rol": "uploader"}
        # Crear token que expira en el pasado
        token = create_access_token(data, expires_minutes=-1)
        
        # Esperar un momento para asegurar que expire
        import time
        time.sleep(2)
        
        with pytest.raises(TokenError) as exc_info:
            verify_token(token)
        
        assert "Token expired" in str(exc_info.value) or "expired" in str(exc_info.value).lower()
    
    def test_create_jwt_alias(self):
        """
        Generado por IA - Fecha: 2024-12-19
        Descripción: Verifica que create_jwt sea un alias funcional de create_access_token
        Parámetros de entrada:
            - data: dict con {"sub": "3", "rol": "admin"}
            - minutes: 60
        Retorno esperado: String con token JWT válido
        """
        from app.core.security import create_jwt
        
        data = {"sub": "3", "rol": "admin"}
        token = create_jwt(data, minutes=60)
        
        assert token is not None
        assert isinstance(token, str)
        payload = verify_token(token)
        assert payload["sub"] == "3"
        assert payload["rol"] == "admin"

