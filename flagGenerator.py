import os, hashlib

def generate_flags(username, challenge):

    uHash = hashlib.md5(username.encode('UTF-8')).hexdigest()
    cHash = hashlib.md5(challenge.encode('UTF-8')).hexdigest()

    return f"{challenge.capitalize()}: {uHash}:{cHash}"



banner = '''

   _____ ______ _____ _  _   _____  ___                                            
  / ____|  ____/ ____| || | | ____|/ _ \                                           
 | (___ | |__ | |    | || |_| |__ | | | |                                          
  \___ \|  __|| |    |__   _|___ \| | | |                                          
  ____) | |___| |____   | |  ___) | |_| |                                          
 |_____/|______\_____|  |_| |____/ \___/_                                          
 | |        /\   |  _ \       / _ \____  |                                         
 | |       /  \  | |_) |_____| | | |  / /                                          
 | |      / /\ \ |  _ <______| | | | / /                                           
 | |____ / ____ \| |_) |     | |_| |/ /                                            
 |______/_/    \_\____/_ _    \___//_/__ _____            _____ _  ________ _____  
 | |  | |   /\    / ____| |  | |  / ____|  __ \     /\   / ____| |/ /  ____|  __ \ 
 | |__| |  /  \  | (___ | |__| | | |    | |__) |   /  \ | |    | ' /| |__  | |__) |
 |  __  | / /\ \  \___ \|  __  | | |    |  _  /   / /\ \| |    |  < |  __| |  _  / 
 | |  | |/ ____ \ ____) | |  | | | |____| | \ \  / ____ \ |____| . \| |____| | \ \ 
 |_|  |_/_/    \_\_____/|_|  |_|  \_____|_|  \_\/_/    \_\_____|_|\_\______|_|  \_\
                                                                                   
                                                                                   
'''
print(banner)
username = input("Enter the username:")

if len(username) == 0:
    username = os.getlogin()
    print(f"\nUSERNAME set to: {username}")
print("\n")

for i in range(1, 11):
    print(generate_flags(username=username, challenge=f"phase{i}"))