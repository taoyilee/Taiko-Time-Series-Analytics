# Taiko Data Analysis Toolbox
## Requirements
1. numpy==1.14.2
2. opencv-python==3.4.0.12
3. matplotlib==2.2.2
4. mysql-connector-python==8.0.6
5. numpy==1.14.2
6. pandas==0.22.0
7. scipy==1.0.1
8. seaborn==0.8.1
9. Pillow==5.1.0
10. mysql-connector-python==8.0.6

## Quick Start
First copy ***config.ini.sample*** to ***config.ini***, modify settings accordingly

```commandline
python main.py
```

if you would like to save frames from captures database, use -f flag in command line option
```commandline
python -f main.py
```

## Todo
1. Combine capture and sensor data to generate a new video