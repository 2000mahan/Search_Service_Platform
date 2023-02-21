import json
from ibm_cloud import *


def create_statistics_file(k, champion_lists_status, u_id, bucket_name):

    statistics = dict()
    statistics["top_k_results"] = k
    statistics["champion_lists_status"] = champion_lists_status
    try:
        file_name = "statistics" + u_id + ".json"
        file_content = json.dumps(statistics).encode('utf-8')
        create_file(bucket_name, file_name, file_content)
    except Exception as e:
        log_error("Main Program Error: {0}".format(e))
