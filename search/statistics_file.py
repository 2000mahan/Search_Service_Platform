import json
from ibm_cloud import *


def create_statistics_file(k, champion_lists_status, u_id):

    statistics = dict()
    statistics["top_k_results"] = k
    statistics["champion_lists_status"] = champion_lists_status
    try:
        file_name = "statistics" + u_id + ".json"
        with open(file_name, "w") as write_file:
            json.dump(statistics, write_file)
    except Exception as e:
        log_error("Main Program Error: {0}".format(e))
