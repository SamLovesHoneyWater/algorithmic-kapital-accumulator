class myLogger(object):
    def __init__(self, logger, print_level):
        self.logger = logger
        self.set_level(print_level)
        
    def set_level(self, print_level):
        if print_level.lower() == "debug":
            self.level = 0
        elif print_level.lower() == "info":
            self.level = 1
        elif print_level.lower() == "warning":
            self.level = 2
        elif print_level.lower() == "error":
            self.level = 3
        else:
            raise ValueError("Invalid print level")

    def debug(self, msg):
        if self.level <= 0:
            print(f"DEBUG - {msg}")
        self.logger.debug(msg)

    def info(self, msg):
        if self.level <= 1:
            print(f"INFO - {msg}")
        self.logger.info(msg)
    
    def warning(self, msg):
        if self.level <= 2:
            print(f"WARNING - {msg}")
        self.logger.warning(msg)
    
    def error(self, msg):
        if self.level <= 3:
            print(f"ERROR - {msg}")
        self.logger.error(msg)
