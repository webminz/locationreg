# Locationreg

This is the repository of `locationreg`: a super-simple REST-API where one may create registrations for locations.
It is used mainly for demonstration purposes in the course [ADA502 Cloud Computing and Software Systems](https://www.hvl.no/en/studies-at-hvl/study-programmes/courses/ADA502/) taught at [Western Norway University of Applied Sciences](https://www.hvl.no).

For instance,

- how to containerize a Python application,
- how to add authentication/authorization,
- how to add persistence via cloud storage or databases,
...


## Usage

Currently, there are three _locations_: `bergen`, `trondheim`, and `oslo`.
You can retrieve registrations at a location with GET and create new ones with POST:

**Getting all registrations for Bergen**:
```bash
curl -s http://0.0.0.0:8000/locations/bergen/registrations
```

**Creating a new registration for Oslo**:
```bash
curl -s --json '{"contact_details": "YOUR_MAIL@example.org"}' http://0.0.0.0:8000/locations/bergen/registrations
```


