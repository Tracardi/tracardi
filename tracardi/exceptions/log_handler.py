from logging import Handler, LogRecord


class ElasticLogHandler(Handler):

    def emit(self, record: LogRecord):
        print("created", record.created)
        print("messsage", str(record))
        print("d", record.module)
        print("filename", record.filename)
        print("path", record.pathname)
        print("num", record.lineno)
        print("msg", record.msg)
        pass
