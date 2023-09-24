import subprocess


process = subprocess.Popen(
    ['bash', 'openvpn-1day.sh'],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    text=True,
)
process.stdout.readline()
process.stdin.write('1\n')
process.stdin.flush()
process.stdin.write('lol4\n')
process.stdin.flush()
process.wait()
