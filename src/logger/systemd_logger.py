from cysystemd import journal
import logging


class SystemdLogger:
    """Class for logging to systemd in linux.
    logs can be viewed in journalctl (example):

    $ sudo journalctl -u cameraServer.service -b -e
    """

    def __init__(self, name: str = __name__) -> None:
        logging.basicConfig(level=logging.DEBUG)
        self.logger = logging.getLogger(name)
        self.logger.addHandler(journal.JournaldLogHandler())

    def log_info(self, msg: str) -> None:
        """Log message at info level."""
        try:
            self.logger.info(msg)
        except Exception as e:
            raise Exception(f"systemd logging error: {e}")
