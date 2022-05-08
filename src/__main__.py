from bot import DNNClient
import sys
import traceback
import os
import json

def config():
    config_path = os.environ['SECRETS_PATH']
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config

def main():
    print('Initializing DNN...')
    print('Loading config...')
    config_file = config()
    print('Starting client...')
    client = None
    exit_code = 0
    try:
        client = DNNClient(config_file)
        client.run()
    except KeyboardInterrupt:
        print('Closing...')
    except Exception as e:
        print(f'Error: {e}')
        print(traceback.format_exc())
        exit_code = 1
    finally:
        print('Exiting...')
        if client is not None:
            client.close()
        sys.exit(exit_code)

if __name__ == '__main__':
    main()