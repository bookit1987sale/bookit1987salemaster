from consumer.models import ClientMember
from rest_framework import serializers


class ClientMemberSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ClientMember
        fields = ('url', 'first_name', 'last_name', 'username',
        	'phone_number', 'alt_phone_number', 'email', 'initial_password',
        	'spouse_name', 'street_address', 'city', 'state', 'zip_code')
