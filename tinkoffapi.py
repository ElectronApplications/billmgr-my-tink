import hashlib
import requests
import json
from dataclasses import dataclass

TINKOFF_URL = "https://securepay.tinkoff.ru"

def sign_data(data: dict, password: str) -> dict:
    fields = list(data.items())
    fields.append(("Password", password))
    fields.sort(key=lambda x: x[0])

    values = "".join([str(x[1]) for x in fields])
    token = hashlib.sha256(bytes(values, encoding="utf-8"))

    new_data = data.copy()
    new_data["Token"] = token.hexdigest()

    return new_data

@dataclass
class StandardPaymentRequest:
    TerminalKey: str
    Amount: int
    OrderId: str
    Description: str
    SuccessURL: str

@dataclass
class StandardPaymentResponse:
    Success: bool
    ErrorCode: int
    TerminalKey: str | None = None
    Status: str | None = None
    PaymentId: int | None = None
    OrderId: str | None = None
    Amount: int | None = None
    PaymentURL: str | None = None
    Message: str | None = None
    Details: str | None = None

def init_standard(terminal_key: str, password: str, amount: int, order_id: str) -> StandardPaymentResponse:
    request = StandardPaymentRequest(terminal_key, amount, order_id, "тестовое описание", "https://google.com")
    signed_data = sign_data(vars(request), password)
    
    response = requests.post(url=f"{TINKOFF_URL}/v2/Init", json=signed_data)
    return StandardPaymentResponse(**response.json())

@dataclass
class CheckPaymentRequest:
    TerminalKey: str
    PaymentId: int

@dataclass
class CheckPaymentResponse:
    Success: bool
    ErrorCode: int
    TerminalKey: str | None = None
    Status: str | None = None
    PaymentId: int | None = None
    OrderId: str | None = None
    Amount: int | None = None
    Message: str | None = None
    Details: str | None = None
    Params: any = None

def check_payment(terminal_key: str, password: str, payment_id: int):
    request = CheckPaymentRequest(terminal_key, payment_id)
    signed_data = sign_data(vars(request), password)
    
    response = requests.post(url=f"{TINKOFF_URL}/v2/GetState", json=signed_data)
    return CheckPaymentResponse(**response.json())