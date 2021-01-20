#!/bin/bash
# echo $1
# scriptpath pid
# echo PYTHONPATH=$PYTHONPATH:"/mnt/e/storage/Soldier Of Fortune/alt_tab_manager/mayhem"
cmd.exe /C "set PYTHONUNBUFFERED=1 && set PYTHONPATH=e:/storage/Soldier Of Fortune/alt_tab_manager/mayhem && python.exe test.py $1 $2"
