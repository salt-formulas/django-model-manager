
from rest_framework import serializers
from .models import User, Organisation

user_fields = ("username", "organisation", 'organisation_name', "first_name",
               "last_name", "email", "operator", "id", "phone", "key_account", "manager")


class OrganisationSerializerBase(serializers.ModelSerializer):

    class Meta:
        model = Organisation


class UserSerializer(serializers.ModelSerializer):

    organisation_name = serializers.ReadOnlyField()
    manage_organisations = serializers.StringRelatedField(
        many=True, read_only=True, source='key_account')

    class Meta:
        model = User
        fields = user_fields + ('manage_organisations',)


class UserSerializerCreate(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = user_fields + ("password",)


class UserTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = user_fields
        depth = 1


class OrganisationSerializer(serializers.ModelSerializer):

    user_set = UserSerializer(many=True, required=False, read_only=True)
    actual_credit = serializers.ReadOnlyField()

    class Meta:
        model = Organisation

