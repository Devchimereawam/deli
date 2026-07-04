from .models import (
    Area,
    City,
    State,
)


def find_state(name):
    if not name:
        return None

    return State.objects.filter(
        name__iexact=name
    ).first()


def find_city(state, name):
    if not state or not name:
        return None

    return City.objects.filter(
        state=state,
        name__iexact=name,
    ).first()


def find_area(city, name):
    if not city or not name:
        return None

    return Area.objects.filter(
        city=city,
        name__iexact=name,
    ).first()