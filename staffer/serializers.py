from rest_framework import serializers
from staffer.models import StaffMember


class StaffMemberSerializer(serializers.HyperlinkedModelSerializer):

    friendly_name = serializers.ReadOnlyField(source='get_friendly_name')
    skill_set = serializers.StringRelatedField(many=True)

    class Meta:
        model = StaffMember
        fields = ('url', 'pk', 'friendly_name', 'skill_set')

