WiFi Reset
==========

What is it?
-----------
WiFiReset is a tool created to solved a very specific problem:
my main wifi router sometimes stops transmitting WiFi signal,
and would typically need a manual restart. But its wired ports work all the time.

So I come up with this workaround.

1. Runs WiFiReset on a device connected to main router M, via ethernet wire.
   (In my case, I have a cascading router C, connecting to main router via wire,
   and my WiFiReset runs on a device wirelessly connecting to router C.
   That still counts as a wired connection, from main router's perspective.)
2. WiFiReset pings a neighbor in the network, periodically (i.e. via crontab).
3. If the neighbor is unreachable, WiFiReset logs in to the main router,
   and reset WiFi radio, automatically.

It works. Currently this script supports my main router ArrisSbg6580 only.


How to Use?
-----------

1. It is written in Python, so you will need to have Python already installed.
2. Checkout or download this repo
3. Run `pip install -r requirements.txt` once, to install the dependency
4. Run `python wifireset.py -h` to see command-line help
5. Typically usage would look like 
   `python wifireset.py --model ArrisSbg6580 --password router_password 192.168.0.4`
6. You would like to add the above command into your crontab (assuming on Linux).

