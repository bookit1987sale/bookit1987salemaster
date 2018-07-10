from django.contrib.auth.models import User
# from consumer.models import ClientMember
# from staffer.models import StaffMember
# from service.models import Service
from rest_framework import serializers

# from snippets.models import Snippet
from event.models import ClientEvent


class CreateEventSerializer(serializers.Serializer):
    # id = serializers.IntegerField(read_only=True)
    # title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    # code = serializers.CharField(style={'base_template': 'textarea.html'})
    # linenos = serializers.BooleanField(required=False)
    # language = serializers.ChoiceField(choices=LANGUAGE_CHOICES, default='python')
    # style = serializers.ChoiceField(choices=STYLE_CHOICES, default='friendly')

    def create(self, validated_data):
        print(attr(self), "  self")
        print(validated_data, "  validated_data")
        # 'user_client': '2', 'client_service': <Service: Men's Basic Cut>, 'staff': '2', 'start': '2018-06-12T12:25:00'}): 
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return ClientEvent.objects.create(**validated_data)


class ClientEventSerializer(serializers.HyperlinkedModelSerializer):
    staff = serializers.ReadOnlyField(source='staff.get_friendly_name')
    client_service = serializers.ReadOnlyField(source='client_service.retail_service')
    user_client = serializers.ReadOnlyField(source='user_client.get_friendly_name')
    minutes = serializers.ReadOnlyField(source='client_service.minutes')
    # highlight = serializers.HyperlinkedIdentityField(
    #     view_name='snippet-highlight', format='html')

    class Meta:
        model = ClientEvent
        fields = ('url', 'pk', 'staff', 'start', 'end', 'client_service', 'user_client', 
        	'status', 'meeting_number', 'minutes')

    # def __init__(self, *args, **kwargs):
    #     print(dir(kwargs['context']['request']['data']))
    #     print(kwargs['context']['request']['data'])
    #     return super().__init__(self, *args, **kwargs)
        

class GetAvailDateSerializer(serializers.Serializer):
    # id = serializers.IntegerField(read_only=True)
    # title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    # code = serializers.CharField(style={'base_template': 'textarea.html'})
    # linenos = serializers.BooleanField(required=False)
    dates = serializers.CharField()#, default='python')  



# client_service = models.ForeignKey(
#         Service,
#         on_delete=models.CASCADE,
#         related_name='client_service'
#     )
#     user_client = models.ForeignKey(
#         ClientMember,
#         on_delete=models.CASCADE,
#         related_name='user_client',
#         verbose_name=_("Client Member")
#     )
#     staff
#     StaffMember,
#         on_delete=models.CASCADE,
#         related_name='staff_for_client_event',
#         verbose_name=_("Staff Member")
#     )

# class SnippetSerializer(serializers.HyperlinkedModelSerializer):
#     owner = serializers.ReadOnlyField(source='owner.username')
#     highlight = serializers.HyperlinkedIdentityField(
#         view_name='snippet-highlight', format='html')

#     class Meta:
#         model = Snippet
#         fields = ('url', 'id', 'highlight', 'owner', 'title', 'code',
#                   'linenos', 'language', 'style')


# class UserSerializer(serializers.HyperlinkedModelSerializer):
#     snippets = serializers.HyperlinkedRelatedField(
#         many=True, view_name='snippet-detail', read_only=True)

#     class Meta:
#         model = User
#         fields = ('url', 'id', 'username', 'snippets')