"""
Validadores customizados
"""
import re
from datetime import datetime
from app.utils.exceptions import ValidationException


def validate_email(email: str) -> str:
    """Valida formato de email"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValidationException("Email inválido")
    return email.lower()


def validate_phone(phone: str) -> str:
    """Valida formato de telefone"""
    # Remove caracteres não numéricos
    clean_phone = re.sub(r"\D", "", phone)
    if len(clean_phone) < 10:
        raise ValidationException("Telefone deve ter pelo menos 10 dígitos")
    return phone


def validate_password(password: str) -> str:
    """Valida força da senha"""
    if len(password) < 6:
        raise ValidationException("Senha deve ter no mínimo 6 caracteres")
    return password


def validate_future_datetime(dt: datetime) -> datetime:
    """Valida se a data/hora é no futuro"""
    if dt <= datetime.now():
        raise ValidationException("Data e hora devem ser no futuro")
    return dt


def validate_price(price: float) -> float:
    """Valida preço"""
    if price <= 0:
        raise ValidationException("Preço deve ser maior que zero")
    return round(price, 2)


def validate_pagination(page: int = 1, limit: int = 10) -> tuple[int, int]:
    """Valida parâmetros de paginação"""
    if page < 1:
        raise ValidationException("Página deve ser maior que 0")
    if limit < 1 or limit > 100:
        raise ValidationException("Limite deve estar entre 1 e 100")
    return page, limit