from abc import abstractmethod
import os
from locationreg.domain import Location, LocationsManager, Registration
from minio import Minio
from io import BytesIO
from pathlib import Path
from psycopg2 import connect
from pymongo import MongoClient




class AbstractRepository:
    
    @abstractmethod
    def read(self) -> LocationsManager:
        pass

    @abstractmethod
    def create_registration(self, location: str, contact: str) -> Registration:
        pass
    
    @abstractmethod
    def delete_registration(self, location: str, id: int):
        pass



class FileRepository(AbstractRepository):
    """
    using the local file system for persistence
    """

    def __init__(self, file_name: str = "storage.json") -> None:
        self.file_name = file_name
        self.locations = None


    def read(self) -> LocationsManager:
        if Path("storage.json").exists():
            fil = open("storage.json", "rt")
            parsed = LocationsManager.model_validate_json(fil.read())
            self.locations = parsed
            fil.close()
            return parsed
        else:
            return LocationsManager()
    
    def _persist(self, locations: LocationsManager):
        file = open(self.file_name, 'wt')
        file.write(locations.model_dump_json())
        file.close()

    def create_registration(self, location: str, contact: str) -> Registration:
        if self.locations is None:
            self.read()
        assert self.locations is not None
        if location not in {'bergen', 'oslo', 'trondheim'}:
            errmsg = f"Location '{location}' does not exist"
            raise ValueError(errmsg)
        next_id = self.locations.registration_count
        self.locations.registration_count += 1
        r = Registration(id=next_id, contact_details=contact, location_name=location)
        if location == "bergen":
            self.locations.bergen.registrations.append(r)
        elif location == "oslo":
            self.locations.oslo.registrations.append(r)
        if location == "trondheim":
            self.locations.trondheim.registrations.append(r)
        self._persist(self.locations)
        return r


    def _delete_at_location(self, location: Location, id: int):
        for r in location.registrations:
            if r.id == id:
                location.registrations.remove(r)

    def delete_registration(self, location: str, id: int):
        if self.locations is None:
            self.read()
        assert self.locations is not None
        if location not in {'bergen', 'oslo', 'trondheim'}:
            errmsg = f"Location '{location}' does not exist"
            raise ValueError(errmsg)
        if location == "bergen":
            self._delete_at_location(self.locations.bergen, id)
        elif location == "oslo":
            self._delete_at_location(self.locations.oslo, id)
        if location == "trondheim":
            self._delete_at_location(self.locations.trondheim, id)
        self._persist(self.locations)


    def update(self, locations: LocationsManager):
        file = open(self.file_name, 'wt')
        file.write(locations.model_dump_json())
        file.close()


class MinioRepository(AbstractRepository):


    def __init__(self, file_name: str = "storage.json") -> None:
        self.file_name = file_name
        self.client = Minio(
            endpoint=os.environ["OBJECT_STORAGE_URL"],
            access_key=os.environ["OBJECT_STORAGE_ACCESS_KEY"],
            secret_key=os.environ["OBJECT_STORAGE_SECRET_KEY"],
            secure=False
        )
        self.bucket_name = os.environ['OBJECT_STORAGE_BUCKET_NAME']
        self.locations = None

    def read(self) -> LocationsManager:
        found = False
        for o in self.client.list_objects(self.bucket_name):
            if o.object_name == self.file_name:
                found = True 
                break
        if not found:
            self.locations = LocationsManager()
            return self.locations
        response = self.client.get_object(self.bucket_name, self.file_name)
        if response.status == 200:
            parsed =  LocationsManager.model_validate_json(response.read().decode())
            self.locations = parsed
            response.close()
            return parsed
        else:
            print(f"Error {response.status} {response.data.decode()}")
            response.close()
            self.locations = LocationsManager()
            return self.locations

    def _persist(self, locations: LocationsManager):
        content = locations.model_dump_json().encode()
        self.client.put_object(self.bucket_name, self.file_name, BytesIO(content), len(content))


    def create_registration(self, location: str, contact: str) -> Registration:
        if self.locations is None:
            self.read()
        assert self.locations is not None
        if location not in {'bergen', 'oslo', 'trondheim'}:
            errmsg = f"Location '{location}' does not exist"
            raise ValueError(errmsg)
        next_id = self.locations.registration_count
        self.locations.registration_count += 1
        r = Registration(id=next_id, contact_details=contact, location_name=location)
        if location == "bergen":
            self.locations.bergen.registrations.append(r)
        elif location == "oslo":
            self.locations.oslo.registrations.append(r)
        if location == "trondheim":
            self.locations.trondheim.registrations.append(r)
        self._persist(self.locations)
        return r


    def _delete_at_location(self, location: Location, id: int):
        for r in location.registrations:
            if r.id == id:
                location.registrations.remove(r)

    def delete_registration(self, location: str, id: int):
        if self.locations is None:
            self.read()
        assert self.locations is not None
        if location not in {'bergen', 'oslo', 'trondheim'}:
            errmsg = f"Location '{location}' does not exist"
            raise ValueError(errmsg)
        if location == "bergen":
            self._delete_at_location(self.locations.bergen, id)
        elif location == "oslo":
            self._delete_at_location(self.locations.oslo, id)
        if location == "trondheim":
            self._delete_at_location(self.locations.trondheim, id)
        self._persist(self.locations)


class PostgresRepository(AbstractRepository):


    def __init__(self) -> None:
        db_host = os.environ["PG_HOST"]
        db_name = os.environ["PG_NAME"]
        db_user = os.environ["PG_USER"]
        db_pass = os.environ["PG_PASS"]
        db_port = os.environ['PG_PORT']
        self.connection = connect(f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}")

    def _fetch_for_location(self, cursor,  location: Location, location_id: int):
        cursor.execute("SELECT id, contact_details FROM registrations WHERE location_id = %s", (location_id,))
        for registration_row in cursor.fetchall():
            location.registrations.append(Registration(id=registration_row[0], location_name=location.location_name, contact_details=registration_row[1]))


    def create_registration(self, location: str, contact: str) -> Registration:
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM locations WHERE name = %s", (location,))
        result_row = cursor.fetchone()
        if result_row:
            cursor.execute("INSERT INTO registrations (location_id, contact_details) VALUES (%s, %s) RETURNING id", (result_row[0], contact))
            update_row = cursor.fetchone()
            assert update_row is not None
            new_id = update_row[0]
            self.connection.commit()
            cursor.close()
            return Registration(id=new_id, location_name=location, contact_details=contact)
        else:
            errmsg = f"Location '{location} not found"
            raise ValueError(errmsg)


    def delete_registration(self, location: str, id: int):
        cursor = self.connection.cursor()
        cursor.execute("DELTE FROM registrations WHERE id = %s", (id,))
        self.connection.commit()
        cursor.close()



    def read(self) -> LocationsManager:
        result = LocationsManager()
        cursor = self.connection.cursor()

        cursor.execute("SELECT id FROM locations WHERE name = %s", ('bergen',))
        result_row = cursor.fetchone()
        if result_row:
            self._fetch_for_location(cursor, result.bergen, result_row[0])

        cursor.execute("SELECT id FROM locations WHERE name = %s", ('oslo',))
        result_row = cursor.fetchone()
        if result_row:
            self._fetch_for_location(cursor, result.oslo, result_row[0])

        cursor.execute("SELECT id FROM locations WHERE name = %s", ('trondheim',))
        result_row = cursor.fetchone()
        if result_row:
            self._fetch_for_location(cursor, result.trondheim, result_row[0])

        cursor.close()
        return result

    def update(self, locations: LocationsManager):
        cursor = self.connection.cursor()
        cursor.execute("SELECT id FROM locations WHERE name = %s", ('bergen',))
        result_row = cursor.fetchone()
        if result_row:
            self._fetch_for_location(cursor, locations.bergen, result_row[0])

        cursor.execute("SELECT id FROM locations WHERE name = %s", ('oslo',))
        result_row = cursor.fetchone()
        if result_row:
            self._fetch_for_location(cursor, locations.oslo, result_row[0])

        cursor.execute("SELECT id FROM locations WHERE name = %s", ('trondheim',))
        result_row = cursor.fetchone()
        if result_row:
            self._fetch_for_location(cursor, locations.trondheim, result_row[0])
        cursor.close()

class MongoRepository(AbstractRepository):

    def __init__(self) -> None:
        mongo_host = os.environ["MONGO_HOST"]
        mongo_port = os.environ["MONGO_PORT"]
        mongo_user = os.environ["MONGO_USER"]
        mongo_pass = os.environ["MONGO_PASS"]
        self.client = MongoClient(mongo_host, int(mongo_port), username=mongo_user, password=mongo_pass)
        self.db = self.client['locationreg']


    def read(self) -> LocationsManager:
        locations = self.db['locations']
        result = LocationsManager()
        count = locations.find_one({'registration_count': {"$exists": True}})
        if count is not None:
            result.registration_count = count['registration_count']
        else:
            locations.insert_one({'registration_count': 0})
        
        d = locations.find_one({'location_name': 'bergen'})
        if d is None:
            locations.insert_one(result.bergen.model_dump())
        else:
            result.bergen = Location(**d)

        d = locations.find_one({'location_name': 'oslo'})
        if d is None:
            locations.insert_one(result.oslo.model_dump())
        else:
            result.oslo = Location(**d)

        d = locations.find_one({'location_name': 'trondheim'})
        if d is None:
            locations.insert_one(result.trondheim.model_dump())
        else:
            result.trondheim = Location(**d)

        return result

    def create_registration(self, location: str, contact: str) -> Registration:
        self.read()
        locations = self.db['locations']
        count = locations.find_one({'registration_count': {"$exists": True}})
        assert count is not None
        next_id = count['registration_count']
        d = locations.find_one({'location_name': location})
        assert d is not None
        loc = Location(**d)
        r = Registration(id=next_id, location_name=location, contact_details=contact)
        loc.registrations.append(r)
        locations.find_one_and_replace({'location_name': location}, loc.model_dump())
        locations.find_one_and_replace({'registration_count': {'$exists': True}}, {'registration_count': next_id + 1})
        return r

    def delete_registration(self, location: str, id: int):
        # TODO
        pass






