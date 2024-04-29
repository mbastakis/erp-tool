from datetime import datetime
import os


class Logger:
    def __init__(self, sup_name):
        self.sup_name = sup_name
        self.datetime_str = datetime.now().strftime("%d-%m-%Y--%H-%M-%S")

        # Check if output/ folder exists and create it if it doesn't
        if not os.path.exists("output/"):
            os.mkdir("output/")

        # Create Folder
        os.mkdir("output/" + self.datetime_str + " " + self.sup_name)
        # Create log file
        with open("output/" + self.datetime_str + " " + self.sup_name + "/" + "log.txt", "w") as log:
            log.write("Log file created at " + self.datetime_str + "\n")

    def log(self, message):
        with open("output/" + self.datetime_str + " " + self.sup_name + "/" + "log.txt", "a") as log:
            log.write(message + "\n")

    def get_datetime_str(self):
        return self.datetime_str
