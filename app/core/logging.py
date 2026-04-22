import logging
import json
import sys


app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)
    
if not app_logger.handlers:
    app_logger.addHandler(logging.StreamHandler(sys.stdout))

app_logger.propagate = False


def app_log_event(event_name: str, **fields) -> None:
    """
    Logs an application event with a standardized format.

    Args:
        event_name (str): The name of the event to log.
        **fields: Additional key-value pairs to include in the log message.
    """
    log_data = {"event": event_name, **fields}
    app_logger.info("app_event=%s", json.dumps(log_data, default=str))


