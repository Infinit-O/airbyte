# WHY
I'm documenting all the problems I encounter while working with the Zoho Desk API so I can gripe about them later.

* &from and &limit are defined as the two pagination params in the documentation, but certain endpoints do NOT honor those params and will throw a 422 back at you if you try and pass them in. This means that I need to, at times, override the request_params method to return an empty object after all the time I spent getting it to work the other way.
* Thus far, every endpoint stores the results in a "data" key within the json object. But the `teams` endpoint returns an object that uses "teams" as the key instead. WHY!?
* With the `departments` endpoint there are 11 records, however if you specify limit=10&from=11, it will return an empty result, so I had to adjust next_page_token() to account for that (i.e record # 11 is omitted).
* The `channels` endpoint does not `from` or `limit` params. 
* Documentation states that the default # of items returned is 10, yet the `channels` one returns 16. This is causing the pagination to fail because part of the logic for checking to see if there is another page involves checking to see if the number of results returned is less than the specified limit. At the time this note was written there is no check to see if the number of results returned is GREATER THAN the limit, and it will default to a "true" condition and attempt to paginate, resulting in a 422 error that triggers Airbyte's backoff mechanisms.
* The `tickets` endpoint requires the `Desk.tickets.READ` permission and is not covered by `Desk.basic.READ`....
