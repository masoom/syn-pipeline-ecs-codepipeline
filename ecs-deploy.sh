#!/bin/bash

DOCKER_IMAGE=$1
CLUSTER_NAME=$(aws ssm get-parameter --name "/data-syn-poc-gpu/group-1/cluster-name" | jq --raw-output .Parameter | jq -r ."Value")

TASK_DEFINITION=$(aws ssm get-parameter --name "/data-syn-poc-gpu/group-1/task-name" | jq --raw-output .Parameter | jq -r ."Value")
TASK_FAMILY=$(aws ecs describe-task-definition --task-definition ${TASK_DEFINITION}  | jq --raw-output '.taskDefinition.family')
OLD_TASK_DEF=$(aws ecs describe-task-definition --task-definition ${TASK_FAMILY} --output json)
NEW_TASK_DEF=$(echo $OLD_TASK_DEF)

FINAL_TASK=$(echo $NEW_TASK_DEF | jq '.taskDefinition|{family: .family, volumes: .volumes, containerDefinitions: .containerDefinitions, requiresCompatibilities: .requiresCompatibilities}')

REGISTERED_TASK=$(aws ecs register-task-definition \
--family $TASK_FAMILY  \
--requires-compatibilities EC2 \
--task-role-arn "arn:aws:iam::456686683148:role/data-syn-poc-gpu-group-1-task-execution-role" \
--execution-role-arn "arn:aws:iam::456686683148:role/data-syn-poc-gpu-group-1-task-execution-role" \
--memory 102400 \
--cpu 10240 \
--cli-input-json "$(echo $FINAL_TASK)")

# Set your memory. For example --memory 200356 \ --network-mode awsvpc \

NEW_REVISION=$(echo $REGISTERED_TASK | jq --raw-output '.taskDefinition.revision')

if [ -n "$NEW_REVISION" ]; then
    echo "ECS Cluster: " $CLUSTER_NAME
    echo "Task Definition: " $TASK_FAMILY:$NEW_REVISION
    echo "Creation of $TASK_DEFINITION starts"

# Runs new task. Ref https://docs.aws.amazon.com/cli/latest/reference/ecs/run-task.html
aws ecs run-task --cluster $CLUSTER_NAME --task-definition "${TASK_FAMILY}":"${NEW_REVISION}" --launch-type EC2

    # aws ecs update-service --service ${SNAME} --task-definition "${TASK_FAMILY}":"${NEW_REVISION}" --cluster $CLUSTER_NAME --force-new-deployment
aws ecs create-service --service-name ${SNAME} --task-definition "${TASK_FAMILY}":"${NEW_REVISION}" --cluster $CLUSTER_NAME --desired-count 0 \
--network-configuration "awsvpcConfiguration={subnets=[your-subnet-id],securityGroups=[your-sg],assignPublicIp=DISABLED}"

    echo "Creation of $TASK_DEFINITION completed"
else
    echo "exit: No task definition"
    exit;
fi