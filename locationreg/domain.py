from pydantic import BaseModel
from typing import Optional

class Registration(BaseModel):
    location_name: str | None = None
    contact_details: str 
    id: Optional[int] = None

class Location(BaseModel):
    location_name: str 
    latitude: float 
    longitude: float
    registrations: list[Registration] = []

class LocationsManager(BaseModel):
    registration_count : int = 0
    bergen: Location = Location(location_name="bergen", latitude=60.3911838, longitude=5.3255599)
    trondheim: Location = Location(location_name="trondheim", latitude=63.4304427, longitude=10.3952956)
    oslo: Location = Location(location_name="oslo", latitude=59.9112197, longitude=10.7330275)

