import json
import os

import logging
import traceback

import sys
from typing import Optional

from tracardi.context import get_context, ContextError
from tracardi.logging import log_stack_trace_as, log_stack_trace_for, log_bulk_size
from tracardi.service.adapter.logger.logger_adapter import log_format_adapter
from tracardi.service.logging.tools import _get_logging_level
from tracardi.service.utils.date import now_in_utc
from logging import Handler, LogRecord
from time import time
import threading

_env = os.environ
_logging_level = _get_logging_level(_env['LOGGING_LEVEL']) if 'LOGGING_LEVEL' in _env else logging.WARNING


def stack_trace(level):
    if level not in log_stack_trace_for:
        return {}

    # Extract the traceback object
    tb = sys.exc_info()[2]

    # Convert the traceback to a list of structured frames
    stack = traceback.extract_tb(tb)

    if not stack:
        stack = traceback.extract_stack()

    try:
        context = get_context()
        metadata = context.get_metadata()
    except ContextError:
        metadata = {}

    # Format the stack trace as a list of dictionaries
    return {
        "context": metadata,
        "stack": [
            {
                "filename": frame.filename,
                "line_number": frame.lineno,
                "function_name": frame.name,
                "code_context": frame.line
            }
            for frame in stack
        ]}


class StackInfoLogger(logging.Logger):
    def error(self, msg, *args, **kwargs):
        kwargs['stack_info'] = True
        kwargs['exc_info'] = True
        if msg is None:
            msg = "None"
        super().error(msg, *args, **kwargs)

    def critical(self, msg, *args, **kwargs):
        kwargs['stack_info'] = True
        kwargs['exc_info'] = True
        super().error(msg, *args, **kwargs)


logging.setLoggerClass(StackInfoLogger)
logging.basicConfig(level=logging.INFO)
_log_format_adapter = log_format_adapter()


def get_logger(name, level=None):
    # Replace the default logger class with your custom class
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level or _logging_level)

    # Elastic log formatter

    logger.addHandler(log_handler)

    # Loki log handler (if enabled)
    global loki_handler
    if loki_handler is None:
        try:
            from tracardi.config import loki
            if loki.enabled:
                loki_handler = LokiLogHandler(loki_config=loki)
        except Exception as e:
            print(f"Failed to initialize Loki handler: {e}", file=sys.stderr)
    
    if loki_handler is not None:
        logger.addHandler(loki_handler)

    # Console log handler

    clh = logging.StreamHandler()
    clh.setFormatter(_log_format_adapter)
    logger.addHandler(clh)

    return logger


def get_installation_logger(name, level=None):
    # Replace the default logger class with your custom class
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(level or _logging_level)

    # Console log handler

    clh = logging.StreamHandler()
    clh.setFormatter(_log_format_adapter)
    logger.addHandler(clh)

    return logger


class ElasticLogHandler(Handler):

    def __init__(self, level=0, collection=None):
        super().__init__(level)
        if collection is None:
            collection = []
        self.collection = collection
        self.last_save = time()

    def _get(self, record, value, default_value):
        return record.__dict__.get(value, default_value)

    def emit(self, record: LogRecord):

        # Skip info and debug.
        if record.levelno <= 25:
            return

        _trace = stack_trace(record.levelname)
        if log_stack_trace_as == 'json':
            if _trace:
                stack_trace_str = f"JSON:{json.dumps(_trace)}"
            else:
                stack_trace_str = None
        else:
            stack_trace_str = record.stack_info

        log = {  # Maps to tracardi-log index
            "date": now_in_utc(),
            "message": record.msg,
            "logger": record.name,
            "file": record.filename,
            "line": record.lineno,
            "level": record.levelname,
            "stack_info": stack_trace_str,
            # "exc_info": record.exc_info  # Can not save this to TrackerPayload
            "module": self._get(record, "package", record.module),
            "class_name": self._get(record, "class_name", record.funcName),
            "origin": self._get(record, "origin", "root"),
            "event_id": self._get(record, "event_id", None),
            "profile_id": self._get(record, "profile_id", None),
            "flow_id": self._get(record, "flow_id", None),
            "node_id": self._get(record, "node_id", None),
            "user_id": self._get(record, "user_id", None),
        }

        self.collection.append(log)

    def has_logs(self, min_log_size=None):
        if min_log_size is None:
            min_log_size = log_bulk_size
        if not isinstance(self.collection, list):
            return False
        return len(self.collection) >= min_log_size or (time() - self.last_save) > 60

    def reset(self):
        self.collection = []
        self.last_save = time()


class LokiLogHandler(Handler):
    """
    Handler for sending logs to Grafana Loki.
    
    This handler batches log records and sends them to Loki in bulk.
    It can be configured via environment variables:
    - LOKI_ENABLED: Enable/disable Loki logging (yes/no)
    - LOKI_URL: Loki push endpoint URL
    - LOKI_USERNAME: Optional basic auth username
    - LOKI_PASSWORD: Optional basic auth password
    - LOKI_LABELS: Comma-separated labels (e.g., "service=tracardi,env=prod")
    - LOKI_BATCH_SIZE: Number of logs to batch before sending
    - LOKI_BATCH_INTERVAL: Time in seconds before sending batch
    """

    def __init__(self, level=0, loki_config=None):
        super().__init__(level)
        self.loki_config = loki_config
        self.collection = []
        self.last_send = time()
        self._session = None
        self._lock = threading.Lock()  # Thread safety for collection
        
    def _get(self, record, value, default_value):
        return record.__dict__.get(value, default_value)
    
    def _get_auth(self) -> Optional[tuple]:
        """Get basic auth credentials if configured"""
        if self.loki_config and self.loki_config.username and self.loki_config.password:
            return (self.loki_config.username, self.loki_config.password)
        return None
    
    def _format_log_entry(self, record: LogRecord) -> dict:
        """Format a log record for Loki"""
        _trace = stack_trace(record.levelname)
        if log_stack_trace_as == 'json':
            if _trace:
                stack_trace_str = f"JSON:{json.dumps(_trace)}"
            else:
                stack_trace_str = None
        else:
            stack_trace_str = record.stack_info
        
        return {
            "timestamp": str(int(time() * 1e9)),  # Nanosecond timestamp
            "line": json.dumps({
                "date": str(now_in_utc()),
                "message": str(record.msg),
                "logger": record.name,
                "file": record.filename,
                "line": record.lineno,
                "level": record.levelname,
                "stack_info": stack_trace_str,
                "module": self._get(record, "package", record.module),
                "class_name": self._get(record, "class_name", record.funcName),
                "origin": self._get(record, "origin", "root"),
                "event_id": self._get(record, "event_id", None),
                "profile_id": self._get(record, "profile_id", None),
                "flow_id": self._get(record, "flow_id", None),
                "node_id": self._get(record, "node_id", None),
                "user_id": self._get(record, "user_id", None),
            })
        }

    def emit(self, record: LogRecord):
        """Emit a log record to Loki batch"""
        if not self.loki_config or not self.loki_config.enabled:
            return
        
        # Skip debug and info logs if needed
        if record.levelno <= 25:
            return
        
        try:
            log_entry = self._format_log_entry(record)
            
            with self._lock:
                self.collection.append(log_entry)
                
                # Send batch if size or time threshold reached
                if self.should_send():
                    self.send_batch()
        except Exception as e:
            # Don't let logging errors break the application
            print(f"Error in LokiLogHandler: {e}", file=sys.stderr)

    def should_send(self) -> bool:
        """Check if batch should be sent"""
        if not self.loki_config:
            return False
        
        batch_size = self.loki_config.batch_size
        batch_interval = self.loki_config.batch_interval
        max_size = batch_size * 10  # Emergency limit
        
        # Force send if collection too large (prevent memory leak)
        if len(self.collection) >= max_size:
            return True
        
        return (len(self.collection) >= batch_size or 
                (time() - self.last_send) >= batch_interval and len(self.collection) > 0)

    def send_batch(self):
        """Send batched logs to Loki"""
        if not self.loki_config or not self.loki_config.url:
            return
        
        # Copy and clear collection atomically
        with self._lock:
            if not self.collection:
                return
            batch = self.collection.copy()
            self.collection = []
            self.last_send = time()
        
        try:
            import requests
            from requests.exceptions import RequestException, Timeout, ConnectionError
            
            # Prepare Loki push payload
            streams = [{
                "stream": self.loki_config.labels_dict,
                "values": [[entry["timestamp"], entry["line"]] for entry in batch]
            }]
            
            payload = {"streams": streams}
            
            # Send to Loki
            auth = self._get_auth()
            headers = {"Content-Type": "application/json"}
            
            try:
                response = requests.post(
                    f"{self.loki_config.url}/loki/api/v{self.loki_config.version}/push",
                    json=payload,
                    headers=headers,
                    auth=auth,
                    timeout=self.loki_config.timeout
                )
                
                if response.status_code not in [200, 204]:
                    print(f"Loki returned non-success status {response.status_code}: {response.text[:200]}", 
                          file=sys.stderr)
            except Timeout:
                print(f"Loki request timeout after {self.loki_config.timeout}s", file=sys.stderr)
            except ConnectionError as e:
                print(f"Loki connection error: {e}", file=sys.stderr)
            except RequestException as e:
                print(f"Loki request error: {e}", file=sys.stderr)

            
        except Exception as e:
            print(f"Error sending logs to Loki: {e}", file=sys.stderr)
            # Note: batch already cleared, failed logs are lost
            # This is intentional to prevent memory buildup

    def flush(self):
        """Flush any remaining logs"""
        if self.collection:
            self.send_batch()

    def close(self):
        """Close handler and flush logs"""
        self.flush()
        super().close()


log_handler = ElasticLogHandler()
loki_handler: Optional[LokiLogHandler] = None