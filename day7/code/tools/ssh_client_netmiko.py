from netmiko import Netmiko
import hashlib


def netmiko_show_cred(host, username, password, cmd, enable='P@ssw0rd123', ssh=True):

    

    device_info = {
                    'host': host,
                    'username': username,
                    'password': password,
                    'device_type': 'cisco_ios' if ssh else 'cisco_ios_telnet',
                    'secret': enable
    }
    try:
        print(f"DEBUG -> {host} | {username} | {password}")
        net_connect = Netmiko(**device_info)
        net_connect.enable()

        if isinstance(cmd,list):
            result = net_connect.send_config_set(cmd)
        else:
            result = net_connect.send_command(cmd,expect_string=r"#") 

        
            
        net_connect.disconnect() 
        #print("RESULT:", result)
        
            
        return result
        

    except Exception as e:
        print(f'connection error ip: {host} error: {str(e)}')
        return None


def compute_hash(s, algorithm='sha256'):
    hash_object = hashlib.new(algorithm)
    hash_object.update(s.encode('utf-8'))
    return hash_object.hexdigest()


def get_show_run(host, username, password):
    show_run_raw = netmiko_show_cred(host, username, password, "show run")
    show_run = 'hostname ' + show_run_raw.split('\nhostname ')[1]

    return show_run, compute_hash(show_run)


if __name__ == '__main__':
    print(get_show_run("192.168.0.89", "admin", "Cisc0123"))
    print(get_show_run("192.168.0.107", "admin", "Cisc0123"))
    