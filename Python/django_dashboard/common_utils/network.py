import os

class NetworkUtil:
    @staticmethod
    def check_ping(hostname):
        response = os.system("ping " + hostname + " -n 1")
        if response == 0:
            return True
        else:
            return False