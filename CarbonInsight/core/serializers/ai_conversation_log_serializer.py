from rest_framework import serializers

from core.models.ai_conversation_log import AIConversationLog


class AIConversationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIConversationLog
        fields = ["id", "user_prompt", "response", "created_at"]
        read_only_fields = ["id", "response", "created_at"]
