from django.contrib import admin
from .models import Guest, Party, Invitation, Event, RSVP


class GuestInline(admin.TabularInline):
    model = Guest
    fields = ('first_name', 'last_name', 'email', 'is_attending', 'meal', 'is_child')
    readonly_fields = ('first_name', 'last_name', 'email')


class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'type','category', 'save_the_date_sent', 'invitation_sent', 'invitation_opened',
                    'is_invited', 'is_attending')
    list_filter = ('type', 'category', 'is_invited', 'is_attending', 'rehearsal_dinner', 'invitation_opened')
    inlines = [GuestInline]


class GuestAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'party', 'email', 'is_attending', 'is_child', 'meal')
    list_filter = ('is_attending', 'is_child', 'meal', 'party__is_invited', 'party__category', 'party__rehearsal_dinner')


class InvitationAdmin(admin.ModelAdmin): 
    list_display = ('party', 'event', 'save_the_date_sent', 'save_the_date_opened', 'invitation_id', 'invitation_sent', 'invitation_opened')
    list_filter = ('party', 'event')


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'date')
    list_filter = ()

class RSVPAdmin(admin.ModelAdmin):
    list_display = ('guest', 'invitation', 'date_of_reply', 'is_attending', 'meal')
    list_filter = ('is_attending', 'meal')

admin.site.register(Party, PartyAdmin)
admin.site.register(Guest, GuestAdmin)
admin.site.register(Invitation, InvitationAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(RSVP, RSVPAdmin)
