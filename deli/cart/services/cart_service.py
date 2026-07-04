from cart.models import (
    Cart,
    CartItem,
)


class CartService:

    @staticmethod
    def get_cart(customer):

        cart, _ = Cart.objects.get_or_create(
            customer=customer,
        )

        return cart

    @classmethod
    def add_item(
        cls,
        customer,
        menu_item,
        quantity=1,
    ):

        cart = cls.get_cart(customer)

        item, created = (
            CartItem.objects.get_or_create(
                cart=cart,
                menu_item=menu_item,
                defaults={
                    "quantity": quantity,
                },
            )
        )

        if not created:

            item.quantity += quantity
            item.save()

        return item

    @classmethod
    def update_quantity(
        cls,
        customer,
        menu_item,
        quantity,
    ):

        cart = cls.get_cart(customer)

        try:

            item = CartItem.objects.get(
                cart=cart,
                menu_item=menu_item,
            )

        except CartItem.DoesNotExist:

            return None

        if quantity <= 0:

            item.delete()
            return None

        item.quantity = quantity
        item.save()

        return item

    @classmethod
    def remove_item(
        cls,
        customer,
        menu_item,
    ):

        cart = cls.get_cart(customer)

        CartItem.objects.filter(
            cart=cart,
            menu_item=menu_item,
        ).delete()

    @classmethod
    def clear_cart(
        cls,
        customer,
    ):

        cart = cls.get_cart(customer)

        cart.items.all().delete()

    @classmethod
    def get_items(
        cls,
        customer,
    ):

        cart = cls.get_cart(customer)

        return (
            cart.items
            .select_related(
                "menu_item",
                "menu_item__restaurant",
            )
            .order_by(
                "created_at",
            )
        )

    @classmethod
    def cart_summary(
        cls,
        customer,
    ):

        cart = cls.get_cart(customer)

        return {
            "cart": cart,
            "items": cls.get_items(customer),
            "subtotal": cart.subtotal,
            "delivery_fee": cart.delivery_fee,
            "total": cart.total,
            "total_items": cart.total_items,
        }