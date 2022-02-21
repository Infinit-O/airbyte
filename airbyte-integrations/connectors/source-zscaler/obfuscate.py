import time
import sys


def obfuscateApiKey(seed):
    now = int(time.time() * 1000)
    n = str(now)[-6:]
    r = str(int(n) >> 1).zfill(6)
    key = ""
    for i in range(0, len(str(n)), 1):
        key += seed[int(str(n)[i])]
    for j in range(0, len(str(r)), 1):
        key += seed[int(str(r)[j])+2]
 
    print("Timestamp:", now, "\tKey", key)

if __name__ == "__main__":
    try:
        api_key = sys.argv[1]
    except IndexError:
        print("First argument needs to be the API key itself.")
        sys.exit()

    print(obfuscateApiKey(api_key))
    
