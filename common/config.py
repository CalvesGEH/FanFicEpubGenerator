import logging
import os

class RoyalRoadEpubConfig():
    def __init__(self):
        self.INGEST_DIR='/cwa-book-ingest' # Directory for calibre-web-automated to ingest books. Should only transfer full epubs here.

        self.ROYAL_ROAD_DOWNLOAD_FOLLOWS = False # If True, will download all fictions that you follow.
        self.ROYAL_ROAD_DOWNLOAD_FILE = None # File that contains a list of fictions to download. If None, will ignore.
        self.ROYAL_ROAD_EMAIL = None
        self.ROYAL_ROAD_PASSWORD = None

        self.UPDATE_INTERVAL_MINUTES = 60 * 24 # Default to once a day

        # This is used to limit the number of threads that can run at once while downloading chapters.
        # Can be raised/lowered as needed. More threads will download chapters faster, but will get throttled by the server.
        self.MAX_NUM_THREADS = 1

        self.LOG_LEVEL = logging.INFO

    def construct_from_env(self):
        for key in self.__dict__:
            env_value = os.getenv(key)
            if env_value:
                attr_value = getattr(self, key)
                if key == 'LOG_LEVEL':
                    # LOG_LEVEL is a special case, as it's an enum.
                    setattr(self, key, getattr(logging, str(env_value).upper()))
                    continue
                # We want to convert the env_value to the same type as the attribute as they are defaulted to strings.
                match attr_value:
                    case bool(attr_value):
                        setattr(self, key, eval(env_value.capitalize()))
                    case int(attr_value):
                        setattr(self, key, int(env_value))
                    case str(attr_value):
                        setattr(self, key, env_value)
                    case None:
                        setattr(self, key, env_value)
                    case _:
                        raise ValueError(f"Unknown type {type((attr_value))} for attribute {key}.")

    def __str__(self):
        return str(self.__dict__)
        

# This will run the first time the module is imported.
config = RoyalRoadEpubConfig()
config.construct_from_env()

def get_config():
    return config