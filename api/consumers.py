import json
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import AnonymousUser



class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.user = self.scope["user"]

        if isinstance(self.user, AnonymousUser):
            self.close()

        else:
            self.group_name = f'user-{self.user.id}'
            async_to_sync(self.channel_layer.group_add)(
                self.group_name,
                self.channel_name
            )
            self.accept()

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        to_user_id = message['to_user']['id']

        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

        async_to_sync(self.channel_layer.group_send)(
            f'user-{to_user_id}',
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def chat_message(self, event):
        message = event['message']

        self.send(text_data=json.dumps({
            'type': 'message',
            'message': message
        }))
        

    def disconnect(self, code):
        if not isinstance(self.user, AnonymousUser):
            async_to_sync(self.channel_layer.group_discard)(
                self.group_name,
                self.channel_name
            )
