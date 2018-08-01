#!/usr/bin/python
# -*- coding: utf8 -*-
import logging
def setup_logger(logger_name, log_file, level=logging.DEBUG, stream="N"):
    lz = logging.getLogger(logger_name)
    formatter = logging.Formatter('[PID: %(process)d - %(asctime)s] : %(message)s')
    fileHandler = logging.FileHandler(log_file, mode='w')
    fileHandler.setFormatter(formatter)
    lz.setLevel(level)
    lz.addHandler(fileHandler)
    if stream == "Y":
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        lz.addHandler(streamHandler) 