class Program:
    def __init__(self, ctx):
        self.put = ctx["putgui"]
        self.queue = ctx["queues"][1]

    def run(self):
        self.put("log", "Entrer une valeur")
        self.put('input', 'input2')
        item = self.queue.get(True)
        print(item)