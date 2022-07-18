class GenId:
    def __init__(self, start):
        self.start = start
        self.current_id = start

    def get_id(self):
        ret_id = self.current_id
        self.current_id += 1

        return ret_id