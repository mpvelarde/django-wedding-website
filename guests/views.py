import base64
from collections import namedtuple
import random
from datetime import datetime
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.views.generic import ListView
from guests import csv_import
from guests.invitation import get_invitation_context, INVITATION_TEMPLATE, guess_party_by_invite_id_or_404, \
    send_invitation_email, get_invite_by_id_or_404, get_or_make_rsvp, get_event_by_id_or_404
from guests.models import Guest, MEALS, Party, RSVP, Invitation
from guests.save_the_date import get_save_the_date_context, send_save_the_date_email, SAVE_THE_DATE_TEMPLATE, \
    SAVE_THE_DATE_CONTEXT_MAP


class GuestListView(ListView):
    model = Guest


@login_required
def export_guests(request):
    export = csv_import.export_guests()
    response = HttpResponse(export.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=all-guests.csv'
    return response


@login_required
def dashboard(request, event_id):
    event = get_event_by_id_or_404(event_id)
    total_invites = Invitation.objects.filter(
        party__is_invited=True, event=event
    ).order_by(
        'party__category', 'party__name'
    )
    pending_invites = total_invites.filter(
        party__is_invited=True, is_attending=None, event=event
    ).order_by(
        'party__category', 'party__name'
    )
    invited_parties = Party.objects.filter(
        is_invited=True
    ).filter(
        Q(type=event.type) | Q(type='both')
    ).order_by(
        'party__category', 'party__name'
    )
    parties_with_unopen_invites = pending_invites.filter(invitation_opened=None)
    parties_with_open_unresponded_invites = pending_invites.exclude(invitation_opened=None)
    attending_rsvp = RSVP.objects.filter(is_attending=True, invitation__event=event)

    meal_breakdown = attending_rsvp.exclude(meal=None).values('meal').annotate(count=Count('*'))
    category_breakdown = attending_rsvp.values('invitation__party__category').annotate(count=Count('*'))

    not_coming_guests = RSVP.objects.filter(is_attending=False, invitation__event=event)

    count_rsvp_guests_yes = RSVP.objects.filter(is_attending=True, invitation__event=event).count()
    count_rsvp_guests_no = not_coming_guests.count()
    count_invited_guests = Guest.objects.filter(party__is_invited=True).filter(Q(party__type=event.type) | Q(party__type='both')).count()
    return render(request, 'guests/dashboard.html', context={
        'event': event,
        'guests': count_rsvp_guests_yes,
        'possible_guests':  count_invited_guests - count_rsvp_guests_no,
        'not_coming_guests': not_coming_guests,
        'not_coming_guests_count': count_rsvp_guests_no,
        'invited_parties': invited_parties.count(),
        'pending_invites': pending_invites.count(),
        'pending_guests': count_invited_guests - count_rsvp_guests_yes - count_rsvp_guests_no,
        'attending_rsvp': attending_rsvp,
        'parties_with_unopen_invites': parties_with_unopen_invites,
        'parties_with_open_unresponded_invites': parties_with_open_unresponded_invites,
        'unopened_invite_count': parties_with_unopen_invites.count(),
        'total_invites': total_invites.count(),
    })

def vhandler404(request, exception=None):
    return render(request, 'errors/404.html', status=404)
def vhandler500(request, exception=None):
    return render(request, 'errors/500.html', status=500)

def invitation(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    invitation = get_invite_by_id_or_404(invite_id)
    rsvps = RSVP.objects.filter(invitation=invitation)
    if invitation.invitation_opened is None:
        # update if this is the first time the invitation was opened
        invitation.invitation_opened = datetime.utcnow()
        invitation.save()
    if request.method == 'POST':
        for response in _parse_invite_params(request.POST):
            guest = Guest.objects.get(pk=response.guest_pk)
            assert guest.party == party
            rsvp = get_or_make_rsvp(guest=guest, invitation=invitation, is_attending=response.is_attending, meal=response.meal)
            rsvp.save()
        if request.POST.get('comments'):
            comments = request.POST.get('comments')
            party.comments = comments if not party.comments else '{}; {}'.format(party.comments, comments)
        invitation.is_attending = invitation.any_guests_attending
        invitation.save()
        return HttpResponseRedirect(reverse('rsvp-confirm', args=[invite_id]))
    return render(request, template_name='guests/invitation.html', context={
        'party': party,
        'invitation': invitation,
        'rsvps': rsvps,
        'meals': MEALS,
        'main_image': 'save-the-date-purple.jpeg',
        'SITE_URL': settings.SITE_URL,
    })


InviteResponse = namedtuple('InviteResponse', ['guest_pk', 'is_attending', 'meal'])


def _parse_invite_params(params):
    responses = {}
    for param, value in params.items():
        if param.startswith('attending'):
            pk = int(param.split('-')[-1])
            response = responses.get(pk, {})
            response['attending'] = True if value == 'yes' else False
            responses[pk] = response
        elif param.startswith('meal'):
            pk = int(param.split('-')[-1])
            response = responses.get(pk, {})
            response['meal'] = value
            responses[pk] = response

    for pk, response in responses.items():
        yield InviteResponse(pk, response['attending'], response.get('meal', None))


def rsvp_confirm(request, invite_id=None):
    party = guess_party_by_invite_id_or_404(invite_id)
    invitation = get_invite_by_id_or_404(invite_id)
    return render(request, template_name='guests/rsvp_confirmation.html', context={
        'party': party,
        'invitation': invitation,
        'support_email': settings.DEFAULT_WEDDING_REPLY_EMAIL,
    })


@login_required
def invitation_email_preview(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    context = get_invitation_context(party)
    return render(request, INVITATION_TEMPLATE, context=context)


@login_required
def invitation_email_test(request, invite_id):
    party = guess_party_by_invite_id_or_404(invite_id)
    send_invitation_email(party, recipients=[settings.DEFAULT_WEDDING_TEST_EMAIL])
    return HttpResponse('sent!')


def save_the_date_random(request):
    template_id = random.choice(list(SAVE_THE_DATE_CONTEXT_MAP.keys()))
    return save_the_date_preview(request, template_id)


def save_the_date_preview(request, template_id):
    context = get_save_the_date_context(template_id)
    context['email_mode'] = False
    context['rsvp_address'] = settings.DEFAULT_WEDDING_REPLY_EMAIL
    return render(request, SAVE_THE_DATE_TEMPLATE, context=context)


@login_required
def test_email(request, template_id):
    context = get_save_the_date_context(template_id)
    send_save_the_date_email(context, [settings.DEFAULT_WEDDING_TEST_EMAIL])
    return HttpResponse('sent!')


def _base64_encode(filepath):
    with open(filepath, "rb") as image_file:
        return base64.b64encode(image_file.read())
