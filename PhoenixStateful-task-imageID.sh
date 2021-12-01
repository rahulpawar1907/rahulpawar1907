#!/bin/bash

aws ecs list-tasks --cluster phoenixstage-stateful --output text | awk '{print $2}' | cut -d "/" -f 3 > /var/phoenixstage_task_stateFul_list.txt

while read -r tasks_list; do
	aws ecs describe-tasks --cluster arn:aws:ecs:us-east-1:361870911536:cluster/phoenixstage-stateful --task $tasks_list --query tasks[*].containers[*].image --output text
done < /var/phoenixstage_task_stateFul_list.txt
