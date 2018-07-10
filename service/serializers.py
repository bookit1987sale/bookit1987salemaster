from rest_framework import serializers

from event.models import Service


class ServicesSerializer(serializers.HyperlinkedModelSerializer):
    # staff = serializers.ReadOnlyField(source='staff.get_friendly_name')
    branch = serializers.ReadOnlyField(source='service_branch.service_branch_description')
    tot_cost = serializers.ReadOnlyField(source='get_tot_service_cost')
    # initial_service = serializers.ReadOnlyField(source='get_tot_service_cost')
    # staff_list = serializers.ReadOnlyField(source='get_staff_list')
    # highlight = serializers.HyperlinkedIdentityField(
    #     view_name='snippet-highlight', format='html')

    class Meta:
        model = Service
        fields = ('url', 'branch', 'pk', 'retail_service', 'minutes', 'tot_cost')

    # def __init__(self, *args, **kwargs):
    #     print(dir(kwargs['context']['request']['data']))
    #     print(kwargs['context']['request']['data'])
    #     return super().__init__(self, *args, **kwargs)
        

    



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