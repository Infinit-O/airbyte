# WHY
I'm documenting all the problems I encounter while working with the Zoho Desk API so I can gripe about them later.

* The following scopes were used
* Desk.basic.READ,Desk.tickets.READ,Desk.contacts.READ,Desk.settings.READ,Desk.community.READ,Desk.activities.events.READ,Desk.activities.tasks.READ,Desk.search.READ

* &from and &limit are defined as the two pagination params in the documentation, but certain endpoints do NOT honor those params and will throw a 422 back at you if you try and pass them in. This means that I need to override the request_params method to return an empty object after all the time I spent getting it to work the other way.
* Thus far, every endpoint stores the results in a "data" key within the json object. But the `teams` endpoint returns an object that uses "teams" as the key instead. WHY!?
* With the `departments` endpoint there are 11 records, however if you specify limit=10&from=11, it will return an empty result, so I had to adjust next_page_token() to account for that (i.e record # 11 is omitted).
* The `channels` endpoint does not `from` or `limit` params. 
* Documentation states that the default # of items returned is 10, yet the `channels` one returns 16. This is causing the pagination to fail because part of the logic for checking to see if there is another page involves checking to see if the number of results returned is less than the specified limit. At the time this note was written there is no check to see if the number of results returned is GREATER THAN the limit, and it will default to a "true" condition and attempt to paginate, resulting in a 422 error that triggers Airbyte's backoff mechanisms.
* The `tickets` endpoint requires the `Desk.tickets.READ` permission and is not covered by `Desk.basic.READ`. so I had to re-issue the auth code
* The `contacts` endpoint requires `Desk.contacts.READ` and is not covered by `Desk.basic.READ`. So I had to re-issue the auth code
* Multiple endpoints are missing, or just don't work despite being present in the documentation. API Endpoint Checklist has a detailed list.
* The `modules` endpoint 422's when `from` or `limit` params are present.
* The `modules` endpoint uses "modules" as the key as opposed to "data".
* The `modules` endpoint returns 20 results when the default is supposed to be 10, and it ruins the default pagination
* The `countries` endpoint 422's when `from` or `limit` params are present.
* The `countries` endpoint returns more than the supposed global default limit of 10.
* The `languages` endpoint response has an almost toally different shape from the rest of the API.
* The `timezones` endpoint 422s when `from` or `limit` params are present.
* The `timezones` endpoint returns more than the supposed global default limit of 10.
* The `businessHours` endpoint requires a different set of permissions `Desk.settings.READ` and required that the auth token be re-issued
* I am not currently authorized to pull data down from the `businessHours` endpoint, and cannot create a schema or pull data through Airbyte at this time..
* I am not authorized to pull data from the `dashboards/createdTickets`, `dashboards/onholdTickets`, `dashboards/solvedTickets`, `dashboards/backlogTickets` endpoints, error message notes `"errorMessage": "Insufficient previlleges to perform this operation"`, it is unclear if that means my account isn't privileged enough, or if it means the Oauth token lacks the necessary scopes. I believe it is the former because I already have the Desk.tickets.READ scope, which the documentation says I require.
* The `dashboards/createdTickets` set of endpoints requires a `groupBy` param, and a `duration` param. `duration` is very clearly an enum but the list of valid values is not visible in the documentation. `groupBy=date` and `duration=LAST_7_DAYS` are the settings used in testing.
* `dashboards/ticketResolutionTime` response has a different shape from everything else in the API.
* `dashboards/ticketREsolutionTIme`, like a number of other endpoints, breaks my pagination, and I don't know if its worth fixing in this particular case.
* `communityTopicTypes/` was 404'ing when I tested it yesterday, but now responds properly after adding the `Desk.community.READ` scope to the token. I suspect that a lot of the other "missing" API endpoints are simply 404'ing because I don't have the right scope.
* `communityModeration/` was 404'ing when I tested it yesterday, but now responds properly after adding the `Desk.community.READ` scope to the token. I suspect that a lot of the other "missing" API endpoints are simply 404'ing because I don't have the right scope.

* It's worth noting that the error messages indicating that I'm not authorized to access something are not consistent and don't indicate if I'm missing scopes (unlikely, according to documentation) or if my account simply isn't authorized.
* I suspect that many of the "missing" APIs in the checklist are 404'ing simply because I'm providing the incorrect scope. I will have to go back and check.
