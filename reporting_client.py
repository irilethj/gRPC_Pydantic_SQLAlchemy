from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, ForeignKey
import spaceship_pb2_grpc as s_pb2_grpc
import spaceship_pb2 as s_pb2
import grpc
import json
from sys import argv
from pydantic import BaseModel, Field, root_validator
from copy import deepcopy


class Spaceship(BaseModel):
    alignment: str
    name: str
    ship_class: str = Field(alias='class')
    length: float
    crew_size: int
    armed: bool
    officers: list

    @root_validator
    def check_spaceship(cls, values):
        alignment = values.get('alignment')
        ship_class = values.get('ship_class')
        length = values.get('length')
        crew_size = values.get('crew_size')
        armed = values.get('armed')
        length = values.get('length')
        if ship_class == 'Corvette' and not (80 <= length <= 250 and 4 <= crew_size <= 10):
            raise ValueError('Invalid Corvette data')
        elif ship_class == 'Frigate' and not (300 <= length <= 600 and 10 <= crew_size <= 15 and alignment != 'Enemy'):
            raise ValueError('Invalid Frigate data')
        elif ship_class == 'Cruiser' and not (500 <= length <= 1000 and 15 <= crew_size <= 30):
            raise ValueError('Invalid Cruiser data')
        elif ship_class == 'Destroyer' and not (800 <= length <= 2000 and 50 <= crew_size <= 80 and alignment != 'Enemy'):
            raise ValueError('Invalid Destroyer data')
        elif ship_class == 'Carrier' and not (1000 <= length <= 4000 and 120 <= crew_size <= 250 and armed == False):
            raise ValueError('Invalid Carrier data')
        elif ship_class == 'Dreadnought' and not (5000 <= length <= 20000 and 300 <= crew_size <= 500):
            raise ValueError('Invalid Dreadnought data')
        return values


def parse_coordinates():
    args = argv[2:]
    try:
        coordinates = s_pb2.Coordinates(right_ascention=s_pb2.Coordinates.RightAscention(
            hours=int(args[0]), minutes=int(args[1]), seconds=float(args[2])
        ),
            declination=s_pb2.Coordinates.Declination(
                degrees=int(args[3]), minutes=int(args[4]), seconds=float(args[5])
        ),)
        return coordinates
    except Exception:
        print("Something wrong with coordinates")
        exit(1)


def spaceship_to_dict(spaceship):
    officers_json = [
        {"first_name": officer.first_name,
            "last_name": officer.last_name, "rank": officer.rank}
        for officer in spaceship.officers
    ]

    return {
        "alignment": s_pb2.Spaceship.Alignment.Name(spaceship.alignment),
        "name": spaceship.name,
        "class": s_pb2.Spaceship.Class.Name(spaceship.ship_class),
        "length": spaceship.length,
        "crew_size": spaceship.crew_size,
        "armed": spaceship.armed,
        "officers": officers_json,
    }


try:
    Base = declarative_base()
    engine = create_engine(
        "postgresql+psycopg://postgres:postgres@localhost:5432/db_spaceship")
    Session = sessionmaker(bind=engine)
    session = Session()
except Exception as err:
    print(f"Problem with connection to DB: {err}")
    exit(1)


class OrmSpaceShip(Base):
    __tablename__ = "spaceships"

    id = Column(Integer, primary_key=True, autoincrement=True)
    alignment = Column(String, nullable=False)
    name = Column(String, nullable=False)
    ship_class = Column(String, name="class", nullable=False)
    length = Column(Float, nullable=False)
    crew_size = Column(Integer, nullable=False)
    armed = Column(Boolean, nullable=False)


class OrmOfficers(Base):
    __tablename__ = "officers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    rank = Column(String, nullable=False)
    ship_id = Column(Integer, ForeignKey(
        "spaceships.id"), nullable=False)


def get_and_record_spaceships():
    channel = grpc.insecure_channel('localhost:50051')
    stub = s_pb2_grpc.SpaceshipServiceStub(channel)
    request = parse_coordinates()
    responses = stub.GetSpaceshipInfo(request)
    for response in responses:
        spaceship_dict = spaceship_to_dict(response)
        try:
            spaceship_info = Spaceship(**spaceship_dict)
            print(json.dumps(spaceship_dict, indent=2))
            Base.metadata.create_all(engine)
            spaceship_data = deepcopy(spaceship_dict)
            officers_data = spaceship_data.pop('officers')
            spaceship_data['ship_class'] = spaceship_data.pop('class')
            spaceship = OrmSpaceShip(**spaceship_data)
            session.add_all([spaceship,])
            session.commit()
            print("\n\nShip's data successfully downloaded\n\n")
            for officer_data in officers_data:
                officer_data['ship_id'] = spaceship.id
                officer = OrmOfficers(**officer_data)
                session.add_all([officer,])
                session.commit()
                print("\n\nOfficer data successfully uploaded\n\n")
        except Exception as e:
            pass


def list_traitors():
    try:
        spaceships = session.query(OrmSpaceShip)
        officers = session.query(OrmOfficers)
        ally_ship_id = [sp.id for sp in spaceships if sp.alignment == 'Ally']
        enemy_ship_id = [sp.id for sp in spaceships if sp.alignment == 'Enemy']

        ally_officers = []
        enemy_officers = []
        for officer in officers:
            dict_of = {"first_name": officer.first_name,
                       "last_name": officer.last_name,
                       "rank": officer.rank}
            if officer.ship_id in ally_ship_id and dict_of not in ally_officers:
                ally_officers.append(dict_of)
            elif officer.ship_id in enemy_ship_id and dict_of not in enemy_officers:
                enemy_officers.append(dict_of)

        traitors = []
        for ally_officer in ally_officers:
            for enemy_officer in enemy_officers:
                if ally_officer == enemy_officer:
                    traitors.append(enemy_officer)

        if not traitors:
            print("\nThere are no traitors!\n")
        else:
            for officer_traitors in traitors:
                print(json.dumps(officer_traitors))

    except Exception:
        print("\nNo ship or officer database!\n")


def main():
    args = argv[1:]
    if len(args) == 0:
        print("Arguments not provided")
        exit(1)
    elif args[0] == "scan":
        get_and_record_spaceships()
    elif args[0] == "list_traitors":
        list_traitors()
    else:
        print("\nInvalid action. Use 'scan' or 'list_traitors'\n")


if __name__ == '__main__':
    main()


