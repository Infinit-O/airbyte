# WHY
I'm documenting all the problems I encounter while working with the Zoho Desk API so I can gripe about them later.

* &from and &limit are defined as the two pagination params in the documentation, but certain endpoints do NOT honor those params and will throw a 422 back at you if you try and pass them in. This means that I need to, at times, override the request_params method to return an empty object after all the time I spent getting it to work the other way.
* Thus far, every endpoint stores the results in a "data" key within the json object. But the "teams" endpoint returns an object that uses "teams" as the key instead. WHY!?
* With the departments endpoint there are 11 records, however if you specify limit=10&from=11, it will return an empty result (i.e record # 11 is omitted).
