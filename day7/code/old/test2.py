import paramiko

ip = "192.168.0.89"
username = "admin"
password = "Cisco123"

cmd = "show flow monitor name qytang-monitor cache format table"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(ip, username=username, password=password)

stdin, stdout, stderr = ssh.exec_command(cmd)

result = stdout.read().decode()

print("===== 返回结果 =====")
print(result)

ssh.close()