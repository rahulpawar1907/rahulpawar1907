#!/bin/bash
sys_mem(){
        free -t | awk 'NR ==2 {printf ("%.0f"), $3/$2*100}'
        return
}
sys_swap(){
        free -t | awk 'FNR == 3 {printf("%.0f"), $3/$2*100}'
        return
}

sys_date(){
        date
        return
}

hname=$(hostname)

container_logs() {
        docker_id=$(docker ps | grep -i "storagenode" | awk '{print $1}')
        docker logs $docker_id > /var/log/container_logs.log

        job_sessions=$(grep "WorkerSvc serving on" /var/log/container_logs.log | wc -l)

        if [[ $job_sessions -eq 32 ]]; then
                echo $( sys_date ) "Successfully job handover on $hname $docker_id" >> /var/log/docker_container.log
        else
                echo $( sys_date ) "There is problem with handover job on $hname $docker_id" >> /var/log/docker_container.log
        fi
}


should_restart_docker(){
        swap_p=50
        memu_p=85

        swap_percentage=$( sys_swap )
        mem_per=$( sys_mem )
        if [[ $swap_percenrage -le $swap_p ]] && [[ $mem_per -le $memu_p ]]; then
                container_status=false
                exit 1
        fi

        swap_percentage=$( sys_swap )
        mem_per=$( sys_mem )

        if [[ $swap_percentage -ge $swap_p && $mem_per -ge $memu_p ]]; then
                sleep 1200
                new_swap_percentage=$( sys_swap )
                new_mem_per=$( sys_mem )
                if [[ $new_swap_percentage -ge $swap_p &&  $new_mem_per -ge $memu_p ]]; then
                        container_status=true
                        return
                fi
                container_status=false

        fi
}

function main() {
        while [ 1 ]; do
                should_restart_docker
                if [[ "$container_status"==true ]] ; then
                        Storage_container_id=$(docker ps | grep -i "storagenode" | awk '{print $1}')
                        echo $( sys_date ) "StorageNode container $Storage_container_id going to restart due to high memory and swap utilization." >> /var/log/docker_container.log
                        docker restart $Storage_container_id >> /var/log/docker_container.log
                        echo $( sys_date ) "$Storage_container_id $hname Container restarted." >> /var/log/docker_container.log
                        sleep 20
                        new_docker_id=$(docker ps | grep -i "storagenode" | awk '{print $1}')
                        echo $( sys_date ) "launch new container $hname $new_docker_id" >> /var/log/docker_container.log
                        sleep 60
                        container_logs
                fi
                break
        done
}

main
