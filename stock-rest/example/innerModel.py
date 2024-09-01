

class HttpSuccess:
    success = True
    msg = "http success"
    def to_representation(self):
        return {
            'success': self.success,
            'msg': self.msg
        }

class HttpFailure:
    success = False
    msg = "http failure"
    def to_representation(self):
        return {
            'success': self.success,
            'msg': self.msg
        }
