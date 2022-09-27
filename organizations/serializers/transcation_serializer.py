from rest_framework import serializers
from organizations.models.transactions import Transaction

class TurfCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'