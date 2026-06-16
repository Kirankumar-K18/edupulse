"""
arq/models.py
Stop-and-Wait ARQ protocol simulation models.
Each ARQSession holds multiple ARQEvents (send, ack, timeout, retransmit).
"""

from django.db import models
from apps.accounts.models import User


class ARQSession(models.Model):
    """One simulation run of the Stop-and-Wait ARQ protocol."""

    class Status(models.TextChoices):
        RUNNING   = 'running',   'Running'
        COMPLETED = 'completed', 'Completed'
        FAILED    = 'failed',    'Failed'

    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='arq_sessions')
    total_packets  = models.PositiveSmallIntegerField(default=5)
    loss_probability = models.FloatField(default=0.2,
                        help_text="Simulated packet loss probability (0.0 – 1.0)")
    timeout_seconds  = models.FloatField(default=2.0)
    max_retries      = models.PositiveSmallIntegerField(default=3)
    status           = models.CharField(max_length=15, choices=Status.choices, default=Status.RUNNING)
    packets_sent_ok  = models.PositiveSmallIntegerField(default=0)
    total_transmissions = models.PositiveSmallIntegerField(default=0)
    created_at       = models.DateTimeField(auto_now_add=True)
    completed_at     = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"ARQ Session #{self.pk} by {self.user.full_name} — {self.status}"

    @property
    def efficiency(self):
        """Transmission efficiency = successful / total transmissions (%)."""
        if self.total_transmissions == 0:
            return 0.0
        return round((self.packets_sent_ok / self.total_transmissions) * 100, 1)


class ARQEvent(models.Model):
    """One event within an ARQ simulation (send, ack, timeout, retransmit, drop)."""

    class EventType(models.TextChoices):
        SEND       = 'send',       'Packet Sent'
        ACK        = 'ack',        'ACK Received'
        TIMEOUT    = 'timeout',    'Timeout'
        RETRANSMIT = 'retransmit', 'Retransmission'
        DROP       = 'drop',       'Packet Dropped (Simulated Loss)'
        SUCCESS    = 'success',    'Packet Delivered'

    session      = models.ForeignKey(ARQSession, on_delete=models.CASCADE, related_name='events')
    event_type   = models.CharField(max_length=15, choices=EventType.choices)
    packet_number = models.PositiveSmallIntegerField()
    attempt      = models.PositiveSmallIntegerField(default=1)
    message      = models.CharField(max_length=300)
    timestamp_ms = models.IntegerField(default=0,
                    help_text="Simulated time offset in milliseconds from session start")

    class Meta:
        ordering = ['timestamp_ms', 'pk']

    def __str__(self):
        return f"[{self.session_id}] P{self.packet_number} {self.event_type}"
