# Importing the library
import psutil
import time
import socket
import subprocess
import logging
import logging.handlers
import datetime


my_logger = logging.getLogger('MyLogger')
my_logger.setLevel(logging.INFO)
handler = logging.handlers.SysLogHandler(address = ('192.168.0.1',514), socktype=socket.SOCK_DGRAM)
my_logger.addHandler(handler)

# Getting Memory Utilization Percentage
def get_ram_usage_pct():
    """
    Obtains the system's current RAM usage.
    :returns: System RAM usage as a percentage.
    :rtype: float
    """
    return psutil.virtual_memory().percent

# Getting Swap Utilization Percentage
def get_swap_usage_pct():
    """
    Obtains the system's current Swap usage.
    :returns: System Swap usage as a percentage.
    :rtype: float
    """
    return psutil.swap_memory().percent

def currenttime():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

#Return Hostname
def get_hostname():
    return socket.gethostname()

#Return StorageNode container id
def get_storage_container_id():
    container_id=subprocess.check_output("docker ps | grep -i \"storagenode\" | awk '{print $1}' ", shell=True).strip()
    return container_id

#Exporting docker container logs and validating the container is up and running
def contaner_logs():
    container_id = '{}'.format(get_storage_container_id())
    hostname = '{}'.format(get_hostname())
    subprocess.check_call('docker logs "{}" > /var/log/docker_container.log'.format(container_id), shell=True)
    file1 = open("/var/log/docker_container.log", "r")
    data = file1.read()
    occurrences = data.count("HandoverSvc serving on")
    #occurrences = data.count("robo Storage Node Started at")
    if occurrences == 1:
        my_logger.info("[] [{}] [Info] Successfully job handover on new container [Host]:{} [Container-ID]:{}".format(currenttime(),hostname, container_id))
        my_logger.handlers[0].flush()
    else:
        my_logger.critical("[] [{}] [critical] There is problem with handover job on new container [Host]:{} [Container-ID]:{}".format(currenttime(),hostname, container_id))
        my_logger.handlers[0].flush()

#Checking system memory and swap utilizaiton 
#If threshold is high as defined memory and swap utilization
#Script will wait 20 min and again check system memory and swap utilization
#If still Memory and swap utilization is high defined threshold, it will return True status
def System_Threshold_Check():
    swap_per = float(50)
    mem_per = float(85)

    memory_percentage = float('{}'.format(get_ram_usage_pct()))
    swap_percentage = float('{}'.format(get_swap_usage_pct()))

    if memory_percentage < mem_per and swap_percentage < swap_per:
        exit()

    memory_percentage = float('{}'.format(get_ram_usage_pct()))
    swap_percentage = float('{}'.format(get_swap_usage_pct()))
    
    if memory_percentage > mem_per and swap_percentage > swap_per:
        time.sleep(1200)

        memory_percentage = float('{}'.format(get_ram_usage_pct()))
        swap_percentage = float('{}'.format(get_swap_usage_pct()))

        if memory_percentage > mem_per and swap_percentage > swap_per:
            container_status = True
            return container_status


#It will check status is True then it will execute "IF" block
#it will restart the docker container
#New container will spawn up in 5-7 sec and job handover start 
#Old container will kill
def StorageNode_Container():
   container_status = System_Threshold_Check()
   hostname = '{}'.format(get_hostname())
   if container_status == True:
        old_container_id = '{}'.format(get_storage_container_id())
        subprocess.check_call('docker restart "{}" > /dev/null 2>&1'.format(old_container_id),shell=True)
        my_logger.info("[] [{}] [Info] Container killed due to high memory and swap utilization on [Host]:{} [Container-ID]:{}".format(currenttime(),hostname, old_container_id))
        my_logger.handlers[0].flush()
        time.sleep(20)
        new_container_id='{}'.format(get_storage_container_id())
        my_logger.info("[] [{}] [Info] New container launch on [Host]:{} [Container-ID]:{}".format(currenttime(), hostname, new_container_id))
        my_logger.handlers[0].flush()
        contaner_logs()


#StorageNode Script Initialization 
StorageNode_Container()