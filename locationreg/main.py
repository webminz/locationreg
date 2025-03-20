from locationreg.domain import Location, LocationsManager, Registration
from fastapi import FastAPI, Response
from uvicorn import run
import sys

import os
from locationreg.persistence import MinioRepository, MongoRepository, PostgresRepository, FileRepository


app = FastAPI()


if 'PERSISTENCE' in os.environ:
    persistence_type = os.environ['PERSISTENCE']
    if persistence_type == "MINIO":
        p = MinioRepository()
    elif persistence_type == "POSTGRES":
        p = PostgresRepository() # type: ignore
    elif persistence_type == "MONGO":
        p = MongoRepository() # type: ignore
    elif persistence_type == "FILE":
        p = FileRepository() # type: ignore
    else:
        print(f"Unsupported persistence type: {persistence_type}!")
        sys.exit(1)
else:
    print("Environment var PERSISTENCE not specified! Falling back to FILE!")
    p = FileRepository() # type: ignore


locations = LocationsManager()


# 'hello word' to see if everyting is running
@app.get("/checkhealth")
def read_root():
    return "alive"


@app.get("/locations/{location}/registrations")
def show_registrations(location: str):
    locations = p.read()
    if location == "bergen":
        return locations.bergen
    elif location == "oslo":
        return locations.oslo
    elif location == "trondheim":
        return locations.trondheim
    else:
        return Response(content=f"Unknown location: {location}", status_code=404)


@app.post("/locations/{location}/registrations")
def make_registrations(location: str, registration: Registration):
    if location in {'bergen', 'trondheim', 'oslo'}:
        result = p.create_registration(location, registration.contact_details)
        return result
    else:
        return Response(content=f"Unknown location: {location}", status_code=404)


@app.delete("/locations/{location}/registrations/{registration}")
def delete_registration(location: str, registration: int):
    p.delete_registration(location, registration)


def main():
    run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
