from email.mime.image import MIMEImage
import os
from datetime import datetime
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.http import Http404
from django.template.loader import render_to_string
from guests.models import Party, Invitation, Event, MEALS, RSVP
from django.db.models import Q

INVITATION_TEMPLATE = 'guests/email_templates/invitation.html'


def get_or_make_rsvp(guest, invitation, is_attending, meal):
    try:
        rsvp = RSVP.objects.get(guest=guest, invitation=invitation)
        rsvp.is_attending = is_attending
        rsvp.meal = meal
        rsvp.date_of_reply = datetime.utcnow()
        return rsvp
    except RSVP.DoesNotExist:
        return RSVP(guest=guest, invitation=invitation, is_attending=is_attending, meal=meal, date_of_reply = datetime.utcnow())


def guess_party_by_invite_id_or_404(invite_id):
    try:
        return Invitation.objects.get(invitation_id=invite_id).party
    except Invitation.DoesNotExist:
        raise Http404()

def get_invite_by_id_or_404(invite_id):
    try:
        return Invitation.objects.get(invitation_id=invite_id)
    except Invitation.DoesNotExist:
        raise Http404()


def get_invitation_context(party, invitation_id):
    return {
        'title': "Lion's Head",
        'main_image': 'save-the-date-purple.jpeg',
        'main_color': '#ffffff',
        'font_color': '#000000',
        'page_title': "Maria Paz and Daniel - You're Invited!",
        'preheader_text': "You are invited!",
        'invitation_id': invitation_id,
        'party_name': party.name,
        'SITE_URL': settings.SITE_URL,
        'party': party,
        'meals': MEALS,
    }


def send_invitation_email(party, invitation_id, test_only=False, recipients=None):
    if recipients is None:
        recipients = party.guest_emails
    if not recipients:
        print(('===== WARNING: no valid email addresses found for {} =====').format(party))
        return

    context = get_invitation_context(party, invitation_id)
    context['email_mode'] = True
    template_html = render_to_string(INVITATION_TEMPLATE, context=context)
    template_text = "You're invited to Cory and Rowena's wedding. To view this invitation, visit {} in any browser.".format(
        reverse('invitation', args=[context['invitation_id']])
    )
    subject = "You're invited"
    # https://www.vlent.nl/weblog/2014/01/15/sending-emails-with-embedded-images-in-django/
    msg = EmailMultiAlternatives(subject, template_text, settings.DEFAULT_WEDDING_FROM_EMAIL, recipients,
                                 cc=settings.WEDDING_CC_LIST,
                                 reply_to=[settings.DEFAULT_WEDDING_REPLY_EMAIL])
    msg.attach_alternative(template_html, "text/html")
    msg.mixed_subtype = 'related'
    for filename in (context['main_image'], ):
        attachment_path = os.path.join(os.path.dirname(__file__), 'static', 'save-the-date', 'images', filename)
        with open(attachment_path, "rb") as image_file:
            msg_img = MIMEImage(image_file.read())
            msg_img.add_header('Content-ID', '<{}>'.format(filename))
            msg.attach(msg_img)

    print('sending invitation to {} ({})'.format(party.name, ', '.join(recipients)))
    if not test_only:
        msg.send()


def send_all_invitations(test_only, mark_as_sent):
    to_send_to = Party.in_default_order().filter(is_invited=True).exclude(is_attending=False)
    for party in to_send_to:
        send_invitation_email(party, test_only=test_only)
        if mark_as_sent:
            party.invitation_sent = datetime.now()
            party.save()

def send_invitations_for_event(party_type, test_only, mark_as_sent):
    event_for_invitations = Event.objects.get(type=party_type)
    invitations_to_send = Invitation.in_default_order().filter(Q(event=event_for_invitations))
    for invitation in invitations_to_send:
        print('prepare to send {}'.format(invitation))
        print('party to send to {}'.format(invitation.party))
        send_invitation_email(invitation.party, invitation.invitation_id, test_only=test_only)

def generate_invitations_for_event(test_only, party_type):
    parties_by_type = Party.in_default_order().filter(Q(type=party_type) | Q(type='both')).filter(is_invited=True)
    event_for_party_type = Event.objects.get(type=party_type)
    for party in parties_by_type:
        print('generate invitation for party {} ({})'.format(party.name, party_type))
        invitation = Invitation(party=party, event=event_for_party_type)
        if not test_only:
            invitation.save()
