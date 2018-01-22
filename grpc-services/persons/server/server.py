from concurrent import futures
import time
import grpc
import persons_pb2_grpc as persons_service
import persons_pb2 as persons_messages

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class PersonsService(persons_service.PersonsServicer):
    def CreatePerson(self, request, context):
        metadata = dict(context.invocation_metadata())
        print(metadata)

    def GetPersons(self, request, context):
        print('get persons call')

        mydict = [
            {
                'id': 1,
                'email': 'duynguyen@gmail.com',
                'fullname': 'Shirour'
            },
            {
                'id': 2,
                'email': 'admin@gmail.com',
                'fullname': 'Admin'
            }
        ]

        for person in mydict:
            person = persons_messages.Person(
                id = person['id'],
                email = person['email'],
                fullname = person['fullname']
            )

            yield persons_messages.GetPersonsResult(person=person)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    persons_service.add_PersonsServicer_to_server(PersonsService(), server)
    server.add_insecure_port('0.0.0.0:50051')
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
