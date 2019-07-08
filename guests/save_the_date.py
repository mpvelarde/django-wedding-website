from __future__ import unicode_literals
from copy import copy
from email.mime.image import MIMEImage
import os
from datetime import datetime
import random
from django.utils.timezone import make_aware

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from guests.models import Party
from django.db.models import Q


SAVE_THE_DATE_TEMPLATE = 'guests/email_templates/save_the_date.html'
SAVE_THE_DATE_CONTEXT_MAP = {

        'scotland': {
            'title': 'savethedate',
            'header_filename': 'save-the-date-purple.jpeg',
            'main_image': 'save-the-date-purple.jpeg',
            'main_color': '#ffffff',
            'font_color': '#000000',
        },
        'ecuador': {
            'title': 'savethedate',
            'header_filename': 'save-the-date-pink-es.jpeg',
            'main_image': 'save-the-date-pink-es.jpeg',
            'main_color': '#ffffff',
            'font_color': '#000000',
        }
    }


def send_all_save_the_dates(test_only=False, mark_as_sent=False, ptype=None):
    pending_parties = Party.in_default_order().filter(is_invited=True, save_the_date_sent=None)
    if ptype == None:
        to_send_to = pending_parties
    elif ptype == 'scotland':
        to_send_to = pending_parties.filter(Q(type=ptype) | Q(type='both'))
    else:
        to_send_to = pending_parties.filter(type=ptype)
    for party in to_send_to:
        send_save_the_date_to_party(party, test_only=test_only)
        if mark_as_sent:
            naive_datetime = datetime.now()
            aware_datetime = make_aware(naive_datetime)
            party.save_the_date_sent = aware_datetime
            party.save()

def send_save_the_date_to_party(party, test_only=False):
    context = get_save_the_date_context(get_template_id_from_party(party))
    recipients = party.guest_emails
    context['party_name'] = party.name
    if not recipients:
        print('===== WARNING: no valid email addresses found for {} =====').format(party)
    else:
        send_save_the_date_email(
            context,
            recipients,
            test_only=test_only
        )


def get_template_id_from_party(party):
    if party.type == 'ecuador':
        return 'ecuador'
    elif party.type == 'scotland' or party.type == 'both':
        # all non-formal dimagis get dimagi invites
        return 'scotland'
    else:
        return None


def get_save_the_date_context(template_id):
    template_id = (template_id or '').lower()
    if template_id not in SAVE_THE_DATE_CONTEXT_MAP:
        template_id = 'scotland'
    context = copy(SAVE_THE_DATE_CONTEXT_MAP[template_id])
    context['name'] = template_id

    if template_id == 'scotland':
        context['page_title'] = 'Daniel and Maria Paz - Save our date!'
        context['preheader_text'] = (
            "The date that you've eagerly been waiting for is finally here. "
            "Daniel and Maria Paz are getting married! Save the date!"
        )
    else:
        context['page_title'] = 'Daniel and Maria Paz - ¡Reserva la fecha!'
        context['preheader_text'] = (
            "Al fin tenemos fecha."
            "¡Daniel and Maria Paz se casan! ¡Reserva la fecha!"
        )
    return context


def send_save_the_date_email(context, recipients, test_only=False):
    context['email_mode'] = True
    context['rsvp_address'] = settings.DEFAULT_WEDDING_REPLY_EMAIL
    template_html = render_to_string(SAVE_THE_DATE_TEMPLATE, context=context)

    if context['name'] == 'scotland':
        template_text = "Save the date for Maria Paz and Daniel's wedding! May 1st, 2020. Scone, Perth, UK."
        subject = 'Save the Date!'
    else:
        template_text = "¡María Paz y Daniel se casan el 1ro de mayo del 2020. Scone, Perth, UK"
        subject = '¡Reserva la fecha!'
    # https://www.vlent.nl/weblog/2014/01/15/sending-emails-with-embedded-images-in-django/
    msg = EmailMultiAlternatives(subject, template_text, settings.DEFAULT_WEDDING_FROM_EMAIL, recipients,
                                 reply_to=[settings.DEFAULT_WEDDING_REPLY_EMAIL])
    msg.attach_alternative(template_html, "text/html")
    msg.mixed_subtype = 'related'
    for filename in (context['main_image'],):
        attachment_path = os.path.join(os.path.dirname(__file__), 'static', 'save-the-date', 'images', filename)
        with open(attachment_path, "rb") as image_file:
            msg_img = MIMEImage(image_file.read())
            msg_img.add_header('Content-ID', '<{}>'.format(filename))
            msg.attach(msg_img)

    print('sending {} to {}'.format(context['name'], ', '.join(recipients)))
    if not test_only:
        msg.send()


def clear_all_save_the_dates():
    for party in Party.objects.exclude(save_the_date_sent=None):
        party.save_the_date_sent = None
        party.save()
