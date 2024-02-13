import grpc
from concurrent import futures
import time

import spaceship_pb2 as s_pb2
import spaceship_pb2_grpc as s_pb2_grpc
import random

SPACESHIP_NAMES = [
    "Shenzhou",
    "Almaz",
    "Mir",
    "Boeing Starliner",
    "Soyuz",
    "SpaceX Crew-8",
    "Concord",
    "Normandy",
]

SPACESHIP_LENGTH = [50, 100, 500, 1000, 2000]


OFFICERS = [{"first_name": "John", "last_name": "Gagarin", "rank": "Commander"},
            {"first_name": "William", "last_name": "Ivanishin", "rank": "Leutenant"},
            {"first_name": "James", "last_name": "Ivanchenkov", "rank": "Captain"},
            {"first_name": "Robert", "last_name": "Afanasyev", "rank": "Commander"},
            {"first_name": "Michael", "last_name": "Artemyev", "rank": "Commander"},
            {"first_name": "Adrian", "last_name": "Avdeev", "rank": "Leutenant"},
            {"first_name": "Albert", "last_name": "Aymakhanov", "rank": "Captain"},]

FIRST_NAME = ["Albert", "Adrian", "Michael",
              "Robert", "James", "William", "John",]
LAST_NAME = ["Smith", "Johnson", "Brown",
             "Wilson", "Moore", "Anderson", "Thomas",]
RANK = ["Commander", "Leutenant", "Captain", "Entrepreneur"]


class SpaceshipService(s_pb2_grpc.SpaceshipServiceServicer):
    def identify_the_name(self, alignment):
        name = random.choice(SPACESHIP_NAMES)
        if alignment == 1:
            name = random.choice([name, 'Unknown'])
        return name


    def generate_officer(self, alignment):
        count = random.randint(1, 10)
        if alignment == 'Enemy':
            count = random.randint(0, 10)
        officers = []
        for _ in range(count):
            officer_pb2 = s_pb2.Officer(
                first_name=random.choice(FIRST_NAME),
                last_name=random.choice(LAST_NAME),
                rank=random.choice(RANK)
            )
            if officer_pb2 not in officers:
                officers.append(officer_pb2)
        return officers

    def generate_spaceship(self):
        alignment = random.choice(s_pb2.Spaceship.Alignment.values())
        name = self.identify_the_name(alignment)
        ship_class = random.choice(s_pb2.Spaceship.Class.values())
        armed = random.randint(0, 1)
        officers = self.generate_officer(alignment)
        if ship_class == 0:
            length = random.choice([80, 100, 250])
            crew_size = random.choice([5, 7, 10])
        elif ship_class == 1:
            length = random.choice([300, 450, 590])
            crew_size = random.choice([10, 12, 15])
        elif ship_class == 2:
            length = random.choice([500, 700, 1000])
            crew_size = random.choice([15, 25, 30])
        elif ship_class == 3:
            length = random.choice([800, 1500, 2000])
            crew_size = random.choice([50, 65, 78])
        elif ship_class == 4:
            length = random.choice([1000, 2500, 4000])
            crew_size = random.choice([130, 195, 240])
        elif ship_class == 5:
            length = random.choice([5000, 10000, 20000])
            crew_size = random.choice([300, 400, 500])
        response = s_pb2.Spaceship(
            alignment=alignment,
            name=name,
            ship_class=ship_class,
            length=length,
            crew_size=crew_size,
            armed=armed,
            officers=officers,
        )
        return response

    def GetSpaceshipInfo(self, request, context):
        # for _ in range(1):
        for _ in range(random.randint(1, 10)):
            response = self.generate_spaceship()
            yield response


def serve():
    try:
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        s_pb2_grpc.add_SpaceshipServiceServicer_to_server(
            SpaceshipService(), server)
        server.add_insecure_port('[::]:50051')
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
