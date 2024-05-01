from typing import Optional
import hashlib
import requests
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase

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


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class StandardPaymentRequest:
    terminal_key: str
    amount: int
    order_id: str
    description: str
    successURL: str
    failURL: str

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class StandardPaymentResponse:
    success: bool
    error_code: int
    terminal_key: Optional[str] = None
    status: Optional[str] = None
    payment_id: Optional[int] = None
    order_id: Optional[str] = None
    amount: Optional[int] = None
    paymentURL: Optional[str] = None
    message: Optional[str] = None
    details: Optional[str] = None

def init_standard(terminal_key: str, password: str, amount: int, order_id: str, description: str, success_url: str, fail_url: str) -> StandardPaymentResponse:
    request = StandardPaymentRequest(terminal_key, amount, order_id, description, success_url, fail_url)
    signed_data = sign_data(request.to_dict(), password)
    
    response = requests.post(url=f"{TINKOFF_URL}/v2/Init", json=signed_data)
    return StandardPaymentResponse.from_dict(response.json())


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class CheckPaymentRequest:
    terminal_key: str
    payment_id: int

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class CheckPaymentResponse:
    success: bool
    error_code: int
    terminal_key: Optional[str] = None
    order_id: Optional[str] = None
    payment_id: Optional[str] = None
    status: Optional[str] = None
    message: Optional[str] = None
    details: Optional[str] = None
    params = None

def check_payment(terminal_key: str, password: str, payment_id: int) -> CheckPaymentResponse:
    request = CheckPaymentRequest(terminal_key, payment_id)
    signed_data = sign_data(request.to_dict(), password)
    
    response = requests.post(url=f"{TINKOFF_URL}/v2/GetState", json=signed_data)
    return CheckPaymentResponse.from_dict(response.json())