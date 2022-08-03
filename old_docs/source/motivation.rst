##########
Motivation
##########

This library was conceived as a way to standardize interfaces between
APIs that I use on a regular basis. I found myself building custom-tailored
client libraries for each API that required me to remember how each one
of them worked. The solution would be to come up with a standard interface
that was flexible enough to operate across several API types.

I realized what I loved doing was pulling data into a local database that
I could query using SQLAlchemy, Django's ORM, or other ORM libraries. So,
why not cut out the middle man? Build a library that looks like an ORM, but
on the back end, is actually accessing REST API's. And the task is simplified
by the fact that almost all patent data is read-only, so I only need to support
read operations.

So, which ORM should I copy? SQLAlchemy is popular, but I often find it too
tedious to deal with a session object. Django's ORM isn't as full-featured,
but it can do everything I want to, and only requires importing a single object - 
the model. So, that's when I came up with this solution:

*Build API client libraries that act like Django*