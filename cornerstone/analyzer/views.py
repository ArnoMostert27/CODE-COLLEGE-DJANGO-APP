from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from .engine import DealInputs, analyse
from .models import Deal
from .scoring import score_deal


@login_required
def deal_list(request):
    deals = Deal.objects.filter(owner=request.user)
    return render(request, "analyzer/deal_list.html", {"deals": deals})


@login_required
def deal_detail(request, pk):
    deal = get_object_or_404(Deal, pk=pk, owner=request.user)
    metrics = analyse(DealInputs.from_deal(deal))
    score = score_deal(metrics)
    return render(
        request,
        "analyzer/deal_detail.html",
        {"deal": deal, "metrics": metrics, "score": score},
    )