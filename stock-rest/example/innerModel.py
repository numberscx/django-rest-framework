from django.contrib.postgres.fields import JSONField


class HttpSuccess:
    success = True
    msg = "http success"
    data = JSONField(default=dict)

    def serialize(self):
        return self.data

class HttpFailure:
    success = False
    msg = "http failure"
    data = JSONField(default=dict)
    def serialize(self):
        return self.data