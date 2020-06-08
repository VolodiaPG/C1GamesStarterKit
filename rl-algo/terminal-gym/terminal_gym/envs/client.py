# import rpyc
#
# import logging
#
# LOG_FMT = logging.Formatter('%(levelname)s '
#                             '[%(filename)s:%(lineno)d] %(message)s',
#                             '%Y-%m-%d %H:%M:%S')
#
# PORT = 4242
# HOST = "localhost"
#
#
# class Client(rpyc.Service):
#     def __init__(self):
#         self.flag_step = False
#         self.conn = rpyc.connect(HOST, PORT)
#
#     def on_connect(self):
#         """
#         Handle the connection from the server
#         """
#         logging.warning("Server connected back")
#
#     def on_disconnect(self):
#         logging.warning("Server disconnected")
#
#     def exposed_ask_for_move(self):
#         self.flag_step = True
#
#     def is_step_available(self):
#         return self.flag_step
#
#     def do_step(self, movement):
#         self.flag_step = False
#         self.conn.root.add_movement(movement)
#
#     def set_log_level_by(self, verbosity):
#         """Set log level by verbosity level.
#         verbosity vs log level:
#             0 -> logging.ERROR
#             1 -> logging.WARNING
#             2 -> logging.INFO
#             3 -> logging.DEBUG
#         Args:
#             verbosity (int): Verbosity level given by CLI option.
#         Returns:
#             (int): Matching log level.
#         """
#         if verbosity == 0:
#             level = 40
#         elif verbosity == 1:
#             level = 30
#         elif verbosity == 2:
#             level = 20
#         elif verbosity >= 3:
#             level = 10
#
#         logger = logging.getLogger()
#         logger.setLevel(level)
#         if len(logger.handlers):
#             handler = logger.handlers[0]
#         else:
#             handler = logging.StreamHandler()
#             logger.addHandler(handler)
#
#         handler.setLevel(level)
#         handler.setFormatter(LOG_FMT)
#         return level
