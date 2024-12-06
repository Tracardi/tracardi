import os

from tracardi.service.utils.environment import get_env_as_int

log_stack_trace_as = os.environ.get('LOG_STACK_TRACE_AS', 'string')
log_stack_trace_for = os.environ.get('LOG_STACK_TRACE_AS', 'CRITICAL,ERROR').split(',')
log_bulk_size = get_env_as_int('LOG_BULK_SIZE', 500)