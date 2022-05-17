import os

os.system("hcitool lescan > scanner.txt & sleep 2 && pkill --signal SIGINT hcito")
mac=None
with open("scanner.txt", "r") as f:
    lines = f.readlines()
for line in lines:
    if 'Polar' in line:
        mac = line.split(" Polar")[0]
        print("Found {}".format(mac))

if(mac):
    with open("scan.txt", "w") as f:
        f.write(mac)