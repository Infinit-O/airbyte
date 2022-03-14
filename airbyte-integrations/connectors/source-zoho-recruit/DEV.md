# Required Scopes
ZohoRecruit.settings.modules.READ
ZohoRecruit.settings.fields.READ
ZohoRecruit.settings.custom_views.READ
ZohoRecruit.settings.layouts.READ
ZohoRecruit.settings.related_lists.READ
ZohoRecruit.settings.note_type.READ
ZohoRecruit.settings.roles.READ
ZohoRecruit.settings.profiles.READ
ZohoRECRUIT.settings.tags.READ
ZohoRecruit.setup.operation.ALL
ZohoRecruit.modules.notes.READ
ZohoRecruit.org.ALL
ZohoRECRUIT.modules.ALL
ZohoRecruit.users.READ

# Maybe we can condense this?
ZohoRecruit.settings.READ

# Scope list for easy copying
ZohoRecruit.setup.operation.all,ZohoRecruit.settings.modules.read,ZohoRecruit.settings.fields.read,ZohoRecruit.settings.custom_views.read,ZohoRecruit.settings.layouts.read,ZohoRecruit.settings.related_lists.read,ZohoRecruit.modules.notes.READ,ZohoRecruit.settings.note_type.READ,ZohoRecruit.settings.roles.READ,ZohoRecruit.settings.profiles.READ,ZohoRecruit.org.all,ZohoRECRUIT.modules.all,ZohoRECRUIT.settings.tags.read,ZohoRecruit.users.READ

# Ignore the above its bugged I'm trying to figure out which ones are bad.
ZohoRecruit.setup.operation.READ,ZohoRecruit.settings.note_type.all,ZohoRECRUIT.settings.roles.read,ZohoRecruit.settings.profiles.read,ZohoRecruit.org.all


# CURRENTLY BAD
ZohoRecruit.modules.notes.READ

# NOTES:
* https://recruit.zoho.com/recruit/v2/settings/roles will throw an exception when you don't have the correct scopes on your token. Other endpoints will (properly) report that you don't have the correct scope.
