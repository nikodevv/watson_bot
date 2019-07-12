from rest_framework import serializers
from watson_bot.models import Message, Hobby

class MessageSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    sender_id = serializers.CharField(read_only=True)
    recipient_id = serializers.CharField(read_only=True)
    timestamp = serializers.DecimalField(read_only=True, max_digits=13, decimal_places=3)
    text = serializers.CharField(read_only=True)

    def create(self, validated_data):
        return Message.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.sender_id = validated_data.get('sender_id', instance.sender_id)
        instance.recipient_id = validated_data.get('recipient_id', instance.recipient_id)
        instance.timestamp = validated_data.get('timestamp', instance.timestamp)
        instance.text = validated_data.get('text', instance.text)
        return instance

class HobbySerializer(serializers.serializer):
    created_at = serializers.DecimalField(read_only=True, max_digits=13, decimal_places=3)
    user = serializers.CharField(read_only=True)
    value = serializers.CharField(read_only=True)
    
    def create(self, validated_data):
        return Hobby.object.create(**validated_data)

    def update(self, instance, validated_data):
        instance.created_at = validated_data.get("created_at", instance.created_at)
        instance.user = validated_data.get("user", instance.user)
        instance.value = validated_data.get("value", instance.value)
        return instance