import paramiko


def ssh_run(ip, username, password, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    ssh.connect(ip, username=username, password=password)

    stdin, stdout, stderr = ssh.exec_command(cmd)

    result = stdout.read().decode()

    ssh.close()

    return result