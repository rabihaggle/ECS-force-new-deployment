import json
import logging
import os
import pprint
import time

import boto3

pp = pprint.PrettyPrinter(indent=4)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)
current_directory = os.path.dirname(os.path.abspath(__file__))
error_file_path = os.path.join(current_directory, "error.txt")

error_handler = logging.FileHandler(error_file_path)
error_handler.setLevel(logging.ERROR)
error_formatter = logging.Formatter("%(asctime)s ; %(levelname)s ; %(message)s")
error_handler.setFormatter(error_formatter)
logging.getLogger("").addHandler(error_handler)


def init_clients(profile_aws: str):
    session = boto3.session.Session(profile_name=profile_aws)
    clients = {}
    # clients["cloudwatch"] = session.client("cloudwatch")
    # clients["application_autoscaling"] = session.client("application-autoscaling")
    # clients["resourcegroupstaggingapi"] = session.client("resourcegroupstaggingapi")
    clients["ecs"] = session.client("ecs")
    return clients


def list_cluster(environment: str, all_clients: dict) -> list:
    client_ecs = all_clients.get("ecs")

    if not client_ecs:
        logger.error("Invalid client -> func list_cluster")
        exit(1)

    response = client_ecs.list_clusters()
    if response["clusterArns"]:
        iclusters = response["clusterArns"]
        return iclusters


def force_new_deployment_services_by_cluster(environment: str, all_clients: dict):
    list_clusters = list_cluster(environment, all_clients)
    client_ecs = all_clients.get("ecs")
    if not client_ecs:
        logger.error("Invalid client -> func list_cluster")
        exit(1)

    for cluster in list_clusters:
        name_cluster = (cluster.split(":")[-1]).split("/")[-1]
        logger.info(f"Cluster -> {name_cluster}")
        response = client_ecs.list_services(cluster=name_cluster, maxResults=100)
        list_services = response["serviceArns"]

        a = 0
        for service in list_services:
            a += 1
            name_service = (service.split(":")[-1]).split("/")[-1]

            response2 = client_ecs.describe_services(
                cluster=name_cluster, services=[name_service]
            )
            desired: int = response2["services"][0]["desiredCount"]
            logger.info(f"{a} -> {name_service} -> {desired}")
            if desired > 0:
                response_force_new_deployment = client_ecs.update_service(
                    cluster=name_cluster, service=name_service, forceNewDeployment=True
                )
                logger.info(f"{service} force new deployment")


################## EXECUTION SCRIPT ##################
if __name__ == "__main__":
    start_time = time.perf_counter()
    logger.info("Start Script")

    profile_aws = "xxxxx"

    all_clients = init_clients(profile_aws)

    force_new_deployment_services_by_cluster(profile_aws, all_clients)

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    logger.info(f"Execution time is {execution_time:.3f} seconds")
################## EXECUTION SCRIPT ##################
