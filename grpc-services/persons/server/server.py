from concurrent import futures
import time
import grpc
import persons_pb2_grpc as persons_service
import persons_pb2 as persons_messages
from simplemysql import SimpleMysql
from stream_framework.feeds.redis import RedisFeed
from stream_framework.feed_managers.base import Manager
from stream_framework.activity import Activity
from stream_framework.verbs import register
from stream_framework.verbs.base import Verb
from datetime import datetime

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

class Pin(Verb):
    id = 5
    infinitive = 'pin'
    past_tense = 'pinned'

register(Pin)

class PostFeed(RedisFeed):
    key_format = 'feed:normal:%(user_id)s'

class UserPostFeed(PostFeed):
    key_format = 'feed:user:%(user_id)s'

class PostManager(Manager):
    feed_classes = dict(
        normal=PostFeed,
    )
    user_feed_class = UserPostFeed

    def add_pin(self, post):
        activity = post.create_activity()
        # add user activity adds it to the user feed, and starts the fanout
        self.add_user_activity(post.user_id, activity)

    def get_user_follower_ids(self, user_id):
        ids = Follow.objects.filter(target=user_id).values_list('user_id', flat=True)
        return {FanoutPriority.HIGH:ids}

manager = PostManager()

class PersonsService(persons_service.PersonsServicer):
    def __init__(self):
        self.db = SimpleMysql(
            host="127.0.0.1",
            db="php-rethink",
            user="root",
            passwd="root",
            keep_alive=True # try and reconnect timedout mysql connections?
        )
        return None

    def CreatePerson(self, request, context):
        metadata = dict(context.invocation_metadata())
        print(metadata)

    def GetPersons(self, request, context):
        print('get persons call')
        feed = UserPostFeed(13)

        activity = Activity(
            actor=13,
            verb=Pin,
            object=1, # The id of the newly created Pin object
            target=1,
            time=datetime.utcnow()
        )

        feed.add(activity)

        # persons = self.db.getAll('pr_person', ['pe_id', 'pe_full_name'])
        # # print(persons)
        # for person in persons:
        #     print(person.pe_id)
        # mydict = [
        #     {
        #         'id': 1,
        #         'email': 'duynguyen@gmail.com',
        #         'fullname': 'Shirour'
        #     },
        #     {
        #         'id': 2,
        #         'email': 'admin@gmail.com',
        #         'fullname': 'Admin'
        #     }
        # ]
        #
        # for person in mydict:
        #     person = persons_messages.Person(
        #         id = person['id'],
        #         email = person['email'],
        #         fullname = person['fullname']
        #     )
        #
        #     yield persons_messages.GetPersonsResult(person=person)

def test():
    service = PersonsService()
    service.GetPersons([], [])

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
    # serve()
    test()
