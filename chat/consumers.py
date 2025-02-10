import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        color = text_data_json.get('color', '#000000')  # Asegúrate de que siempre haya un color, por si no se envía

        # Send message to room group with color
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'color': color  # Incluimos el color en los datos enviados
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        color = event['color']  # Recibimos el color que se envió desde el cliente

        # Send message to WebSocket, incluyendo el color
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'color': color  # Enviamos el color junto con el mensaje
        }))


import logging

# Configurar logging
logger = logging.getLogger(__name__)

class PrivateChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.notification_sent = False  # Estado para controlar si se ha enviado la notificación

    async def connect(self):
        self.user1 = self.scope['url_route']['kwargs']['user1'].replace('private_', '')
        self.user2 = self.scope['url_route']['kwargs']['user2'].replace('private_', '')
        
        self.room_name = f"private_{min(self.user1, self.user2)}_{max(self.user1, self.user2)}"
        self.room_group_name = f'chat_{self.room_name}'
        
        logger.info(f"🔌 Conectando chat privado entre {self.user1} y {self.user2}")
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message = data['message']
            sender = data['username'].replace('private_', '')  # Limpiamos el username
            color = data.get('color', '#000000')
            
            # Determinamos el receptor (sin el prefijo 'private_')
            receiver = self.user2 if sender == self.user1 else self.user1
            
            logger.info(f"📨 Mensaje de {sender} para {receiver}")
            
            # Enviamos el mensaje al grupo de chat
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': sender,
                    'color': color
                }
            )

            # Enviamos la notificación solo si no se ha enviado antes
            if not self.notification_sent:
                notification_group = f"notifications_{receiver}"
                logger.info(f"🔔 Enviando notificación al grupo: {notification_group}")
                
                await self.channel_layer.group_send(
                    notification_group,
                    {
                        'type': 'private_notification',
                        'username': sender,
                        'color': color
                    }
                )
                logger.info(f"✅ Notificación enviada a {notification_group}")
                self.notification_sent = True  # Marcamos que la notificación ha sido enviada

        except Exception as e:
            logger.error(f"❌ Error en receive: {str(e)}")
            raise

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'color': event.get('color', '#000000')
        }))

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Limpiamos el username quitando el prefijo 'private_' si existe
        self.username = self.scope['url_route']['kwargs']['username'].replace('private_', '')
        self.room_group_name = f"notifications_{self.username}"
        
        logger.info(f"🔌 Conectando NotificationConsumer para: {self.username}")
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        logger.info(f"✅ NotificationConsumer conectado para: {self.username}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def private_notification(self, event):
        try:
            logger.info(f"🔔 Enviando notificación al cliente {self.username}")
            
            await self.send(text_data=json.dumps({
                'type': 'notification',
                'username': event['username'],
                'color': event.get('color', '#000000')
            }))
            logger.info(f"✅ Notificación enviada al cliente {self.username}")
        except Exception as e:
            logger.error(f"❌ Error enviando notificación: {str(e)}")
            raise