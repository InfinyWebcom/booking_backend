from rest_framework import serializers
from slotapp.models.slot import Slot

class SlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = Slot
        fields = '__all__'