from decimal import Decimal, InvalidOperation


def money(value):

    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return f"₦{value}"

    if amount == amount.to_integral_value():
        return f"₦{int(amount):,}"

    return f"₦{amount:,.2f}"
