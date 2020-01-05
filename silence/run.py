import main
import logging

# Get the logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

global_config = main.generate_config()
global_config = main.create_clients(global_config)

while True:
    main.send_notifications(global_config)
