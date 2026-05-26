from core.service import query_prefix  # noqa: F401


def normalize_phone(phone: str) -> str:
    phone = phone.strip()
    if phone.startswith('8'):
        phone = '+7' + phone[1:]
    return phone
