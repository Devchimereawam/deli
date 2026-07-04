from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):

    default_address = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = "__all__"

    def get_default_address(self, obj):

        address = obj.default_address

        if not address:
            return None

        return {
            "formatted_address": address.formatted_address,
            "latitude": address.latitude,
            "longitude": address.longitude,
            "state": address.state.name if address.state else None,
            "city": address.city.name if address.city else None,
            "area": address.area.name if address.area else None,
        }