from users.constants import HOME


class NavigationService:

    MAX_HISTORY = 20

    @classmethod
    def push(
        cls,
        conversation,
        state,
    ):

        stack = conversation.navigation_stack or [HOME]

        # Don't push duplicate consecutive states
        if stack and stack[-1] == state:
            return

        stack.append(state)

        conversation.navigation_stack = stack[-cls.MAX_HISTORY:]

        conversation.save(
            update_fields=[
                "navigation_stack",
                "updated_at",
            ]
        )

    @classmethod
    def back(
        cls,
        conversation,
    ):

        stack = conversation.navigation_stack or []

        if len(stack) <= 1:

            conversation.navigation_stack = [HOME]

            conversation.save(
                update_fields=[
                    "navigation_stack",
                    "updated_at",
                ]
            )

            return HOME

        stack.pop()

        previous = stack[-1]

        conversation.navigation_stack = stack

        conversation.save(
            update_fields=[
                "navigation_stack",
                "updated_at",
            ]
        )

        return previous

    @classmethod
    def reset(
        cls,
        conversation,
    ):

        conversation.navigation_stack = [HOME]

        conversation.save(
            update_fields=[
                "navigation_stack",
                "updated_at",
            ]
        )