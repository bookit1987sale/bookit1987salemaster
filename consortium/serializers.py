from rest_framework import serializers
from consortium.models import Company


class CompanyDetailsSerializer(serializers.ModelSerializer):
    # staff = serializers.ReadOnlyField(source='staff.get_friendly_name')
    # client_service = serializers.ReadOnlyField(source='client_service.retail_service')
    # user_client = serializers.ReadOnlyField(source='user_client.get_friendly_name')
    # minutes = serializers.ReadOnlyField(source='client_service.minutes')

    class Meta:
        model = Company
        fields = ('company', 'company_phone', 'email', 'owner', 'street_address', 
            'city', 'state', 'zip_code', 'caption', 'bio', 'alert')

    # def __init__(self, *args, **kwargs):
    #     print(dir(kwargs['context']['request']['data']))
    #     print(kwargs['context']['request']['data'])
    #     return super().__init__(self, *args, **kwargs)
 