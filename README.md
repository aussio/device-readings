# Summary
👋🏻 Hello brightwheel! 🌟🎡 Thanks for reading!

* Flask app
* Marshmallow for validation
* in-memory cache using a global variable in `device_reading/model.py`

The interesting bits of code can all be found within `./device_reading`.

# Local Dev

The development environment is entirely contained within a Docker container to ensure consistent results between developers and environments.

## Run

```
make run
```

Or if you don't have `make` installed, you can just run the same command it does:

```
docker run -it -v ${PWD}:/app -p 8000:8000 -e FLASK_DEBUG=true device-readings
```

## Calls to the API

**Add a device reading:**

```
curl -s localhost:8000/reading -d '
{
  "id": "12256582-6908-559e-887e-a949ec199272",
  "readings": [
    {
      "timestamp": "2021-09-29T14:08:15+01:00",
      "count": 2
    },
    {
      "timestamp": "2021-09-29T15:09:15+01:00",
      "count": 20
    }
  ]
}
' -H "Content-Type: application/json"
```

**Retrieve a device reading:**

```
curl -s localhost:8000/reading/12256582-6908-559e-887e-a949ec199272
```

**List all device readings (not in spec, but nice for debugging):

```
curl -s localhost:8000/reading
```


## Test

```
make test
```

or

```
docker run -it -v ${PWD}:/app device-readings python -m pytest -v -p no:cacheprovider
```

# Note:
My in-memory 'cache' implementation is wiped on server reload. So if you do any of the following, it will be wiped:

* Restart the container
* Modify the code - I have Flask debug mode turned on, so it hot reloads, wiping the cache.

# Project Reflection

> What roadblocks did you run into when writing your code (i.e., where did you spend the bulk of your time)?

* Over thought "in-memory cache" for a moment. Didn't realize I could just have a package-scoped global that stuck around. Googled around for a bit on how to store stuff between requests without Redis or a database. Really over thought needing something special. 😅
* I'm not fluent in using Marshmallow, so I definitely had some silly mistakes and things I needed to debug. I'm happy with the library choice and where it landed though.

> If you had more time, what part of your project would you
refactor? What other tradeoffs did you make?

* **Ordering of timestamps**: I think it would make the most sense for the `readings` to be ordered by timestamp. I didn't implement any sort of heap in my cache to keep it ordered, nor a sort anywhere to order it on response.
* **Cache serialization**: My cache in model.py is essentially my DAO layer. I ended up hand-performing the serialization between the validated input/output JSON and the cache format to support using dictionaries for quick lookup and updating. In a real project, I would have used Marshmallow's ability to [serialize directly into Python objects](https://marshmallow.readthedocs.io/en/stable/quickstart.html#deserializing-to-objects) which would have made that code considerably more readable. Then my database would keep the data nice and efficiently organized/accessible in storage.
    * Related to the above reflection - I actually went down that path originally, and you can see the commented code left over in models.py.
* **Handling of UUIDs**: Flask validates UUIDs in an unobvious way, imo. If you pass /readings/<id> a non-UUID, it gives a 404 for the URL as opposed to a 400 for it being a bad UUID. That's why I'm treating `id` as a string so everything plays nicely. I'm sure this is totally fixable.
* **Testing**: I'm a huge HUGE advocate for automated tests. I'll transparently admit that I don't tend to have the best habits around TDD though. 😅 With that, I would have added more robust tests to this project. I spent more than my 2 allotted hours on the homework, so I decided to save some time here. My integration tests cover our main acceptance criteria, but I wrote nothing automated to poke at our error cases. I'm also not asserting on the shape of the body, which is critical to testing the contract as would absolutely be included in production code.