
import os

import parameters as pa

def system_info():
    pa.windows_env = os.environ

if __name__ == '__main__':
    system_info()

    for n,v in pa.windows_env.items():
        print(n,v)