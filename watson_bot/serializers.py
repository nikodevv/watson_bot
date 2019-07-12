from rest_framework import serializers
from watson_bot.models import Message, Hobby

class MessageSerializer(serializers.Serializer):
    id = serializers.TextField(read_only=True)
    sender_id = serializers.TextField(read_only=True)
    recipient_id = serializers.TextField(read_only=True)
    timestamp = serializers.DecimalField(read_only=True)
    text = serializers.TextField(read_only=True)

    def create(self, validated_data):
        return Message.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.id = validated_data.get('id', instance.id)
        instance.sender_id = validated_data.get('sender_id', instance.sender_id)
        instance.recipient_id = validated_data.get('recipient_id', instance.recipient_id)
        instance.timestamp = validated_data.get('timestamp', instance.timestamp)
        instance.text = validated_data.get('text', instance.text)
        return instance