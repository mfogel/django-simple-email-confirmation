class CurrentUserMixin:
    def get_queryset(self):
        queryset = super().get_queryset()

        # Get configuration
        current_user = self.request.user
        user_field = self.user_field

        return queryset.filter(**{
            user_field: current_user
        })


class ActionSerializerMixin:
    action_serializers = {}

    def get_action_serializers(self):
        return self.action_serializers

    def get_serializer_class(self):
        if self.action in self.get_action_serializers():
            return self.action_serializers.get(self.action, None)

        else:
            return super().get_serializer_class()
