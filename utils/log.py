class Log:
    def __init__(self, max_display=30):
        self.messages = []
        self.max_display = max_display
        self.start = 0
        self.log_area = None

    def add_message(self, message, color):
        try:
            self.messages.append((message, color))
            if len(self.messages) > self.max_display:
                self.start += 1
        except Exception as e:
            import traceback
            traceback.print_exc()

    def get_visible_log(self):
        return self.messages[self.start:self.start + self.max_display]
    
    def scroll_up(self):
        if self.start > 0:
            self.start -= 1

    def scroll_down(self):
        if self.start + self.max_display < len(self.messages):
            self.start += 1
            
    def clear(self):
        self.messages = []