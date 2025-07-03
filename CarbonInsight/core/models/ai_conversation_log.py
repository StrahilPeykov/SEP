from django.db import models

class AIConversationLog(models.Model):
    """
    Class modeling AI conversation logs for AI advice. Facilitates the logging of AI advices for reducing carbon
    footprint of a product for future reference.
    """
    user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="ai_conversation_logs",
    )
    product = models.ForeignKey(
        "Product",
        on_delete=models.CASCADE,
        related_name="ai_conversation_logs",
    )
    user_prompt = models.TextField()
    instructions = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "AI conversation log"
        verbose_name_plural = "AI conversation logs"
        ordering = ["-created_at"]
