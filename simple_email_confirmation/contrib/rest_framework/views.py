from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from simple_email_confirmation import get_email_address_model
from simple_email_confirmation.exceptions import (
    EmailConfirmationExpired, EmailIsPrimary, EmailNotConfirmed,
)

from . import permissions, serializers, utils


class EmailViewSet(
    utils.ActionSerializerMixin,
    utils.CurrentUserMixin,
    viewsets.ModelViewSet,
):
    email_address_model = get_email_address_model()
    queryset = email_address_model.objects.all()
    user_field = 'user'
    permission_classes = [permissions.EmailViewSetPermission]

    serializer_class = serializers.EmailAddressSerializer
    action_serializers = {
        'send_confirmation': None,
        'confirm': serializers.ConfirmEmailAddressSerializer,
        'set_primary': None,
    }

    def create(self, request, *args, **kwargs):
        try:
            # Add the new unconfirmed email
            request.user.add_unconfirmed_email(request.data['email'])

            # Retrieve the new email
            new_email = request.user.email_address_set.filter(
                email=request.data['email']
            ).first()

            # Return serialized email
            serializer = self.get_serializer(new_email)
            return Response(serializer.data)

        except IntegrityError:
            return Response(
                {'errors': ['Email already exists']},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def destroy(self, request, *args, **kwargs):
        email = self.get_object()

        try:
            # Delete the email
            request.user.remove_email(email.email)

            return Response({'status': 'OK'})

        except EmailIsPrimary:
            return Response(
                {'errors': ['Cannot delete the primary email']},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=['post'], detail=True)
    def send_confirmation(self, request, pk=None):
        """
        Send a confirmation email.
        """

        # Retrive email
        email = self.get_object()

        # Confirm email
        email.user.reset_email_confirmation(email.email)
        email.user.send_confirmation_email(email.email)

        # Success!
        return Response({'status': 'OK'})

    @action(methods=['post'], detail=False)
    def confirm(self, request):
        """
        Confirm an email.
        """

        try:
            # Parse data
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            # Retrieve email
            email = get_object_or_404(
                self.email_address_model,
                pk=serializer.data['id'],
            )

            # Retrieve user
            email.user.confirm_email(serializer.data['code'])

            # Success!
            return Response({'status': 'OK'})

        except EmailConfirmationExpired:
            return Response(
                {'errors': ['Confirmation key is not valid']},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(methods=['post'], detail=True)
    def set_primary(self, request, pk=None):
        """
        Set an email as primary.
        """

        # Retrive email
        email = self.get_object()

        try:
            # Set email as primary
            email.user.set_primary_email(email.email)

            # Success!
            return Response({'status': 'OK'})

        except EmailNotConfirmed:
            return Response(
                {'errors': [
                    'Email must be confirmed before it can be set as primary'
                ]},
                status=status.HTTP_400_BAD_REQUEST,
            )
