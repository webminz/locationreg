
from typing import Optional
from pydantic import BaseModel
from fastapi import FastAPI, Response

app = FastAPI()


class Registration(BaseModel):
    location_name: str | None = None
    contact_details: str 
    id: Optional[int] = None


class Location(BaseModel):
    location_name: str 
    latitude: float 
    longitude: float
    registrations: list[Registration] = []

location_map = {
    "bergen": Location(location_name='bergen', latitude=60.3911838, longitude=5.3255599),
    "trondheim": Location(location_name='trondheim', latitude=63.4304427, longitude=10.3952956),
    "oslo": Location(location_name='oslo', latitude=59.9112197, longitude=10.7330275),
}

counter = 0

# 'hello word' to see if everyting is running
@app.get("/checkhealth")
def read_root():
    return "alive"



@app.get("/locations/{location}/registrations")
def show_registrations(location:str):
    if location in location_map:
        return location_map[location]
    else:
        return Response(content=f"Unknown location: {location}", status_code=404)

@app.post("/locations/{location}/registrations")
def make_registrations(location: str, registration: Registration):
    if location in location_map:
        global counter
        loc = location_map[location]
        registration.id = counter
        registration.location_name = location
        counter += 1
        loc.registrations.append(registration)
        return registration
    else:
        return Response(content=f"Unknown location: {location}", status_code=404)



