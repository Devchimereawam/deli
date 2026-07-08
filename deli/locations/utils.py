import re

from .models import (
    Area,
    City,
    State,
)


def normalize_location_text(value):

    return re.sub(
        r"[^a-z0-9]+",
        " ",
        str(value or "").lower(),
    ).strip()


def text_matches_location(text, name):

    text = normalize_location_text(text)
    name = normalize_location_text(name)

    if not text or not name:
        return False

    if name in text:
        return True

    name_parts = [
        part
        for part in name.split()
        if len(part) > 1
    ]

    if not name_parts:
        return False

    return all(part in text for part in name_parts)


def first_area_with_restaurant():

    from restaurants.models import Restaurant

    restaurant = (
        Restaurant.objects
        .filter(
            is_active=True,
            area__isnull=False,
        )
        .select_related(
            "area",
            "area__city",
            "area__city__state",
        )
        .order_by(
            "-rating",
            "name",
        )
        .first()
    )

    if restaurant:
        return restaurant.area

    return Area.objects.select_related(
        "city",
        "city__state",
    ).first()


def find_state(name):
    if not name:
        return None

    state = State.objects.filter(
        name__iexact=name
    ).first()

    if state:
        return state

    normalized_name = normalize_location_text(name)

    for candidate in State.objects.all():
        if text_matches_location(normalized_name, candidate.name):
            return candidate

    return None


def find_city(state, name):
    if not name:
        return None

    cities = City.objects.all()

    if state:
        cities = cities.filter(state=state)

    city = cities.filter(name__iexact=name).first()

    if city:
        return city

    normalized_name = normalize_location_text(name)

    for candidate in cities.select_related("state"):
        if text_matches_location(normalized_name, candidate.name):
            return candidate

    return None


def find_area(city, name):
    if not name:
        return None

    areas = Area.objects.all()

    if city:
        areas = areas.filter(city=city)

    area = areas.filter(name__iexact=name).first()

    if area:
        return area

    normalized_name = normalize_location_text(name)

    for candidate in areas.select_related(
        "city",
        "city__state",
    ):
        if text_matches_location(normalized_name, candidate.name):
            return candidate

    return None


def resolve_location_parts(
    *values,
    latitude=None,
    longitude=None,
    fallback_area=None,
):

    text = " ".join(
        str(value)
        for value in values
        if value
    )

    state = find_state(text)
    city = find_city(state, text)
    area = find_area(city, text)

    if not area and text:
        area = find_area(None, text)

    if latitude is not None and longitude is not None:
        nearest = nearest_area(latitude, longitude)
        if nearest:
            return nearest.city.state, nearest.city, nearest

    if area:
        city = area.city
        state = city.state
        return state, city, area

    if city:
        state = city.state
        return state, city, None

    area = fallback_area

    if not area and text and not state:
        area = first_area_with_restaurant()

    if area:
        return area.city.state, area.city, area

    return state, None, None


def nearest_area(latitude, longitude):

    areas = Area.objects.exclude(
        latitude__isnull=True,
    ).exclude(
        longitude__isnull=True,
    ).select_related(
        "city",
        "city__state",
    )

    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return None

    best_area = None
    best_score = None

    for area in areas:
        score = (
            (area.latitude - latitude) ** 2
            + (area.longitude - longitude) ** 2
        )

        if best_score is None or score < best_score:
            best_area = area
            best_score = score

    return best_area
