"""
arq/views.py
Stop-and-Wait ARQ simulation views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import ARQSession, ARQEvent
from .simulation import run_simulation


@login_required
def arq_home(request):
    """Show simulation form and user's past sessions."""
    sessions = ARQSession.objects.filter(user=request.user)[:10]
    return render(request, 'arq/home.html', {'sessions': sessions})


@login_required
@require_POST
def run_arq(request):
    """Run a new ARQ simulation."""
    try:
        total_packets = int(request.POST.get('total_packets', 5))
        loss_prob     = float(request.POST.get('loss_prob', 0.2))
        timeout_ms    = int(request.POST.get('timeout_ms', 2000))
        max_retries   = int(request.POST.get('max_retries', 3))

        # Clamp values
        total_packets = max(1, min(20, total_packets))
        loss_prob     = max(0.0, min(0.9, loss_prob))
        timeout_ms    = max(500, min(10000, timeout_ms))
        max_retries   = max(1, min(5, max_retries))

        session = run_simulation(
            user=request.user,
            total_packets=total_packets,
            loss_prob=loss_prob,
            timeout_ms=timeout_ms,
            max_retries=max_retries,
        )
        return redirect('arq:result', pk=session.pk)
    except Exception as e:
        messages.error(request, f"Simulation error: {e}")
        return redirect('arq:home')


@login_required
def arq_result(request, pk):
    """Show detailed results of an ARQ session."""
    session = get_object_or_404(ARQSession, pk=pk, user=request.user)
    events  = session.events.all()
    return render(request, 'arq/result.html', {
        'session': session,
        'events':  events,
    })


@login_required
def arq_result_json(request, pk):
    """Return ARQ session events as JSON (for animated frontend)."""
    session = get_object_or_404(ARQSession, pk=pk, user=request.user)
    events  = list(session.events.values(
        'event_type', 'packet_number', 'attempt', 'message', 'timestamp_ms'
    ))
    return JsonResponse({
        'session': {
            'id':                  session.pk,
            'status':              session.status,
            'total_packets':       session.total_packets,
            'packets_sent_ok':     session.packets_sent_ok,
            'total_transmissions': session.total_transmissions,
            'efficiency':          session.efficiency,
        },
        'events': events,
    })
