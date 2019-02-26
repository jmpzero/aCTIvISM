# aCTIvISM - ConTiuous Internet connectIon Speed Measurement

This tool, written in python, will measure the speed of your internet connection with the help of speedtest.net and the speedtest python package.

The tool does not run periodically and instead is just single shot. I recommend you add it to your cron jobs to run periodically.

The tool provides you with the current statistics after one run. However, all runs are saved in an SQLite database, and together with an analysis script you will receive some nice statistics.

## Requirements
- Python 2.7
- speedtest-cli (python)
- sqlite3 (python)

## How to run it
The requirements.txt file contains all necessary requirements for your installation. We recommend that you use a virtual environment for the installation, unless you want to have the libraries installed system wide, and we recommend virtualenv for this task.

```
virtualenv myEnv
source myEnv/bin/activate
pip install < requirements.txt
```

# Todo
- [ ] Configuration file
- [ ] Placement of database
- [ ] Server selection
- [ ] Analysis of multiple servers, etc.
