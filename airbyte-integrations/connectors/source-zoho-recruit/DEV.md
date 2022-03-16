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

# Ignore the above its bugged I'm trying to figure out which ones are bad.
ZohoRecruit.setup.operation.READ,ZohoRecruit.settings.note_type.all,ZohoRECRUIT.settings.roles.read,ZohoRecruit.settings.profiles.read,ZohoRecruit.org.all,ZohoRecruit.users.read,ZohoRecruit.settings.fields.read,ZohoRecruit.settings.custom_views.read,ZohoRecruit.settings.layouts.read,ZohoRecruit.settings.related_lists.read,ZohoRECRUIT.modules.read,ZohoRECRUIT.settings.tags.read


# CURRENTLY BAD
ZohoRecruit.modules.notes.READ

# NOTES:
* At the beginning of this project I put together a list of API endpoints and the scopes I needed for each one, so I could just copy the list of scopes into the dev console when generating the authorization code. However, there are 
* https://recruit.zoho.com/recruit/v2/settings/roles will throw an exception when you don't have the correct scopes on your token. Other endpoints will (properly) report that you don't have the correct scope.
* This isn't exactly game-breaking for us but data from https://recruit.zoho.com/recruit/v2/users uses "null" (a string containing the word 'null') as opposed to the proper JSON null value.
* https://recruit.zoho.com/recruit/v2/settings/fields?module=Approvals returns 204 NO CONTENT causing failure of stream
* https://recruit.zoho.com/recruit/v2/settings/custom_views/{id_redacted}?module=Approvals retrns 204 NO CONTENT which will cause failure of stream. Added workaround
* https://recruit.zoho.com/recruit/v2/settings/fields?module=Referrals returns 401 Unauthorized for Enrico. going to skip this module via bad_api_list while I sort the permissions out.
* The module names listed on the following page are incorrect! https://www.zoho.com/recruit/developer-guide/apiv2/layouts-meta.html I'm using the module names from the modules endpoint and even then they're incorrect! To top it all off the URL is also incorrect as well! The documentation specifies "https://recruit.zoho.com/recruit/v2/settings/layouts/module={module_api_name}" however, when used as-is it returns 404 not found. The correct form is "https://recruit.zoho.com/recruit/v2/settings/layouts?module={module_api_name}" 
* The Records endpoint at https://recruit.zoho.com/recruit/v2/{module_api_name} has no consistent schema! Each module has differently shaped responses! The JSONSchema therefore is {"type": "object"} and NOTHING MORE. WAAH
* The Tags endpoint at https://recruit.zoho.com/recruit/v2/settings/tags?module={module_api_name} has an inconsistent data envelope shape. Whereas other endpoints will feature an array of objects, the tags endpoint will only return a single JSON object.
