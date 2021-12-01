#!/bin/bash

aws ecs list-tasks --cluster phoenixstage-stateless --output text | awk '{print $2}' | cut -d "/" -f 3 > phoenixstage_task_stateLess_list.txt

while read -r tasks_list; do
	aws ecs describe-tasks --cluster arn:aws:ecs:us-east-1:361870911536:cluster/phoenixstage-stateless --task $tasks_list --query tasks[*].containers[*].image --output text
done < phoenixstage_task_stateLess_list.txt
