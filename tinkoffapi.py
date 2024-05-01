import hashlib
from typing import List
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
    terminal_key: str | None = None
    status: str | None = None
    payment_id: int | None = None
    order_id: str | None = None
    amount: int | None = None
    paymentURL: str | None = None
    message: str | None = None
    details: str | None = None

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
    terminal_key: str | None = None
    order_id: str | None = None
    message: str | None = None
    details: str | None = None
    params: any = None

def check_payment(terminal_key: str, password: str, payment_id: int) -> CheckPaymentResponse:
    request = CheckPaymentRequest(terminal_key, payment_id)
    signed_data = sign_data(request.to_dict(), password)
    
    response = requests.post(url=f"{TINKOFF_URL}/v2/GetState", json=signed_data)
    return CheckPaymentResponse.from_dict(response.json())


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class CheckOrderRequest:
    terminal_key: str
    order_id: int

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class CheckOrderPaymentsResponse:
    success: bool
    payment_id: str
    amount: int
    status: str
    error_code: int | None = None
    RRN: str | None = None
    message: str | None = None

@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class CheckOrderResponse:
    success: bool
    error_code: int
    terminal_key: str | None = None
    order_id: str | None = None
    message: str | None = None
    details: str | None = None
    payments: List[CheckOrderPaymentsResponse] | None = None

def check_order(terminal_key: str, password: str, order_id: int) -> CheckOrderResponse:
    request = CheckOrderRequest(terminal_key, order_id)
    signed_data = sign_data(request.to_dict(), password)
    
    response = requests.post(url=f"{TINKOFF_URL}/v2/CheckOrder", json=signed_data)
    return CheckOrderResponse.from_dict(response.json())

print(check_order("TinkoffBankTest", "TinkoffBankTest", "1337"))