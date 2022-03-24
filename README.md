# SSHeesh

`SSHeesh` is a multi-threaded red team tool for SSH credential spraying.

## Dependencies

- Linux/Unix/MacOS
- `timeout`
- `ssh`
- `sshpass`
- `ulimit` (built-in)

## Usage

```
usage: sheesh.py [-h] [-i IP] [-iL LIST] [-c CREDS] [-o OUTPUT] [-p PORT] [-t THREADS] [-T TIMEOUT]

SSHeesh - a multi-threaded red team utility for SSH credential spraying

optional arguments:
  -h, --help			show this help message and exit
  -i IP, --ip IP		for use with a single IP address, which can sometimes be useful
  -iL LIST, --list LIST		/path/to/ip_list
  -c CREDS, --creds CREDS	delimited credential string [username:password]
  -o OUTPUT, --output OUTPUT	/path/to/output_file to save successful attempts
  -p PORT, --port PORT		TCP port to use (default: 22)
  -t THREADS, --threads THREADS	number of threads to use
  -T TIMEOUT, --timeout TIMEOUT	TCP connection timeout
```

### Details

This script has been tested successfully with up to 30k threads.

Make sure to run `ulimit -n unlimited` before running the script with lots of threads in order to make sure you don't run into any issues with too many file descriptors.
