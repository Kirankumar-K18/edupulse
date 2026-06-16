"""
arq/simulation.py
Pure-Python Stop-and-Wait ARQ simulation engine.
Deterministic when seed is provided; stores events to DB.
"""

import random
from django.utils import timezone
from .models import ARQSession, ARQEvent
from apps.accounts.models import ActivityLog


def run_simulation(user, total_packets=5, loss_prob=0.2,
                   timeout_ms=2000, max_retries=3, seed=None):
    """
    Run a complete Stop-and-Wait ARQ simulation.
    Returns the ARQSession instance with all events saved.
    """
    rng = random.Random(seed)

    session = ARQSession.objects.create(
        user=user,
        total_packets=total_packets,
        loss_probability=loss_prob,
        timeout_seconds=timeout_ms / 1000,
        max_retries=max_retries,
        status=ARQSession.Status.RUNNING,
    )

    events      = []
    time_ms     = 0
    total_tx    = 0
    success_cnt = 0

    def add_event(etype, pkt_num, attempt, message):
        nonlocal time_ms
        events.append(ARQEvent(
            session=session,
            event_type=etype,
            packet_number=pkt_num,
            attempt=attempt,
            message=message,
            timestamp_ms=time_ms,
        ))

    for pkt in range(1, total_packets + 1):
        delivered = False
        attempt   = 0

        while not delivered:
            attempt  += 1
            total_tx += 1

            # ── SEND ──────────────────────────────────────────────
            add_event(ARQEvent.EventType.SEND, pkt, attempt,
                      f"Packet {pkt} sent (attempt {attempt})")
            time_ms += 500   # propagation delay

            # ── SIMULATE LOSS ─────────────────────────────────────
            packet_lost = rng.random() < loss_prob
            if packet_lost:
                add_event(ARQEvent.EventType.DROP, pkt, attempt,
                          f"Packet {pkt} lost in transit (simulated {loss_prob*100:.0f}% loss)")
                time_ms += timeout_ms
                add_event(ARQEvent.EventType.TIMEOUT, pkt, attempt,
                          f"Timeout waiting for ACK of packet {pkt} after {timeout_ms}ms")

                if attempt >= max_retries:
                    add_event(ARQEvent.EventType.TIMEOUT, pkt, attempt,
                              f"Packet {pkt} FAILED — max retries ({max_retries}) exceeded")
                    break
                else:
                    add_event(ARQEvent.EventType.RETRANSMIT, pkt, attempt + 1,
                              f"Retransmitting packet {pkt} (attempt {attempt+1}/{max_retries})")
                    time_ms += 200
            else:
                # ── ACK received ──────────────────────────────────
                time_ms += 300   # ACK propagation
                add_event(ARQEvent.EventType.ACK, pkt, attempt,
                          f"ACK received for packet {pkt} (RTT: ~800ms)")
                add_event(ARQEvent.EventType.SUCCESS, pkt, attempt,
                          f"Packet {pkt} delivered successfully in {attempt} attempt(s)")
                success_cnt += 1
                delivered    = True
                time_ms     += 100   # inter-packet gap

    # ── Bulk-create events ─────────────────────────────────────────
    ARQEvent.objects.bulk_create(events)

    # ── Finalise session ──────────────────────────────────────────
    all_success = success_cnt == total_packets
    session.status              = ARQSession.Status.COMPLETED if all_success else ARQSession.Status.FAILED
    session.packets_sent_ok     = success_cnt
    session.total_transmissions = total_tx
    session.completed_at        = timezone.now()
    session.save()

    ActivityLog.log(
        user,
        ActivityLog.Action.ARQ_EVENT,
        (f"ARQ simulation #{session.pk}: {success_cnt}/{total_packets} packets delivered, "
         f"{total_tx} total transmissions, efficiency {session.efficiency}%"),
        extra_data={
            'session_id':   session.pk,
            'total_packets': total_packets,
            'success':       success_cnt,
            'total_tx':      total_tx,
            'efficiency':    session.efficiency,
        },
    )

    return session
