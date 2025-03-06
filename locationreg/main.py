
from locationreg.domain import Location, Registration
from fastapi import FastAPI, Response
from uvicorn import run

from locationreg.persistence import RegistrationRepository


app = FastAPI()



location_map = {
    "bergen": Location(location_name='bergen', latitude=60.3911838, longitude=5.3255599),
    "trondheim": Location(location_name='trondheim', latitude=63.4304427, longitude=10.3952956),
    "oslo": Location(location_name='oslo', latitude=59.9112197, longitude=10.7330275),
}

p = RegistrationRepository()

# 'hello word' to see if everyting is running
@app.get("/checkhealth")
def read_root():
    return "alive"



@app.get("/locations/{location}/registrations")
def show_registrations(location:str):
    if location in location_map:
        loc = location_map[location]
        return [reg for reg in p.read_registrations() if reg.location_name == location]
    else:
        return Response(content=f"Unknown location: {location}", status_code=404)

@app.post("/locations/{location}/registrations")
def make_registrations(location: str, registration: Registration):
    if location in location_map:
        loc = location_map[location]
        reg = p.create_registration(registration.contact_details, location)
        loc.registrations.append(registration)
        return registration
    else:
        return Response(content=f"Unknown location: {location}", status_code=404)



def main():
    run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
