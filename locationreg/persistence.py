from pydantic import BaseModel
from locationreg.domain import Registration
import json


class StoreRegistrations(BaseModel):
    registrations : list[Registration]

class RegistrationRepository:

    def __init__(self) -> None:
        self.registrations_dict : dict[int, Registration] = {}
        self.id_counter = 0
        self._read_state()

    def _read_state(self):
        fil = open("storage.json", "rt")
        parsed = StoreRegistrations.model_validate_json(fil.read())
        self.registrations_dict = {}
        self.id_counter = len(parsed.registrations)
        for r in parsed.registrations:
            assert r.id is not None
            self.registrations_dict[r.id] = r
        fil.close()

    def _write_current_state(self):
        fil = open("storage.json", "wt")
        storage = []
        for value in self.registrations_dict.values():
            storage.append(value)
        
        fil.write(StoreRegistrations(registrations=storage).model_dump_json())
        fil.close()

    def create_registration(self, contect_details: str, location: str) -> Registration:
        next_id = self.id_counter 
        self.id_counter += 1
        result = Registration(contact_details=contect_details, location_name=location, id=next_id)
        self.registrations_dict[next_id] = result
        self._write_current_state()
        return result

    def read_registrations(self):
        # TODO: implement
        pass 

    def update_registration(self):
        # TODO: implement
        pass 

    def delete_registrations(self):
        # TODO: implement
        pass



# Writing
# p = RegistrationRepository()
# p.create_registration("past@hvl.no", "bergen")
# p.create_registration("bob@example.org", "oslo")


# Reading
p = RegistrationRepository()
for v in p.registrations_dict.values():
    print(v.contact_details)
