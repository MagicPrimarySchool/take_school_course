class Lesson:
    def __init__(self, name, code, teacher_name, Time, number):
        self.name = name
        self.code = code
        self.teacher_name = teacher_name
        self.time = Time
        self.number = number

    def show(self):
        print('name: ' + self.name +
              '\n code: ' + self.code +
              '\n teacher_name' + self.teacher_name +
              '\n time:' + self.time)