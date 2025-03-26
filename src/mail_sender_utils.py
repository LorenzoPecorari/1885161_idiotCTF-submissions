import redis
import json

queue_name = "email_queue"

class MailSender:
    def __init__(self, redis_host='redis', redis_port=6379, queue_name='email_queue'):
        self.queue_name = queue_name
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

    def user_notification(self, email):
        email_data = {
            "to_email": email,
            "subject": "Correct submission",
            "body": "Hi! You have sent the right submission. Try to have fun with other challenges!"
        }
        email_data_json = json.dumps(email_data)
        print(email_data_json)
        self.redis_client.lpush(queue_name, email_data_json)