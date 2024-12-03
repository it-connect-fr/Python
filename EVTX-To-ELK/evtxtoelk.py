#!/usr/bin/python3
# -*- coding: utf-8 -*-
# coding=utf8
# Author : Mickael Dorigny (IT-Connect.fr)
# original script from https://github.com/dgunter/evtxtoelk

import contextlib
import mmap
import traceback
import json
import argparse
from collections import OrderedDict
from datetime import datetime

from Evtx.Evtx import FileHeader
from Evtx.Views import evtx_file_xml_view
from elasticsearch import Elasticsearch, helpers
import xmltodict
import sys


class EvtxToElk:
    @staticmethod
    def bulk_to_elasticsearch(es, bulk_queue):
        try:
            helpers.bulk(es, bulk_queue)
            return True
        except Exception:
            print(traceback.print_exc())
            return False

    @staticmethod
    def evtx_to_elk(
        kibana_url, evtx_file, username, password,
        elk_index, bulk_queue_len_threshold, metadata
    ):
        bulk_queue = []
        es = Elasticsearch([kibana_url], basic_auth=(username, password))
        with open(evtx_file) as infile:
            with contextlib.closing(mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ)) as buf:
                fh = FileHeader(buf, 0x0)
                for xml, record in evtx_file_xml_view(fh):
                    try:
                        log_line = xmltodict.parse(xml)

                        # Format the date field
                        date = log_line.get("Event").get("System").get("TimeCreated").get("@SystemTime")
                        if "." not in str(date):
                            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                        else:
                            date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
                        log_line['@timestamp'] = str(date.isoformat())
                        log_line["Event"]["System"]["TimeCreated"]["@SystemTime"] = str(date.isoformat())

                        # Process the data field to be searchable
                        data = log_line.get("Event")
                        if data and data.get("EventData"):
                            event_data = data.get("EventData").get("Data")
                            if isinstance(event_data, list):
                                data_vals = {}
                                for dataitem in event_data:
                                    try:
                                        if dataitem.get("@Name"):
                                            data_vals[str(dataitem.get("@Name"))] = str(dataitem.get("#text"))
                                    except Exception:
                                        pass
                                log_line["Event"]["EventData"]["Data"] = data_vals
                            else:
                                log_line["Event"]["EventData"]["RawData"] = (
                                    json.dumps(event_data) if isinstance(event_data, OrderedDict)
                                    else str(event_data)
                                )
                                del log_line["Event"]["EventData"]["Data"]
                        else:
                            if isinstance(data, OrderedDict):
                                log_line = dict(data)
                            else:
                                log_line["RawData"] = str(data)
                                del log_line["Event"]

                        # Insert data into queue
                        event_data = json.loads(json.dumps(log_line))
                        event_data["_index"] = elk_index
                        event_data["meta"] = metadata
                        bulk_queue.append(event_data)

                        if len(bulk_queue) == bulk_queue_len_threshold:
                            print(f'Bulking records to ES: {len(bulk_queue)}')
                            if EvtxToElk.bulk_to_elasticsearch(es, bulk_queue):
                                bulk_queue = []
                            else:
                                print('Failed to bulk data to Elasticsearch')
                                sys.exit(1)

                    except Exception:
                        print("***********")
                        print("Parsing Exception")
                        print(traceback.print_exc())
                        print(json.dumps(log_line, indent=2))
                        print("***********")

                # Check for any remaining records in the bulk queue
                if bulk_queue:
                    print(f'Bulking final set of records to ES: {len(bulk_queue)}')
                    if EvtxToElk.bulk_to_elasticsearch(es, bulk_queue):
                        bulk_queue = []
                    else:
                        print('Failed to bulk data to Elasticsearch')
                        sys.exit(1)


if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser()
    # Add arguments
    parser.add_argument("-f", "--file", required=True, help="Evtx file to parse")
    parser.add_argument("-k", "--kibana", required=True, default="localhost",
                        help="IP (and port) of ELK instance (e.g. http://127.0.0.1:9200)")
    parser.add_argument("-i", "--index", default="hostlogs", help="ELK index to load data into")
    parser.add_argument("-s", "--size", default=500, help="Size of queue")
    parser.add_argument("-u", "--username", default="elastic", help="Username for Kibana authentication")
    parser.add_argument("-p", "--password", default="changeme", help="Password for Kibana authentication")
    parser.add_argument("-meta", default={}, type=json.loads, help="Metadata to add to records")
    # Parse arguments and call evtx_to_elk function
    args = parser.parse_args()
    EvtxToElk.evtx_to_elk(
        kibana_url=args.kibana, evtx_file=args.file, username=args.username,
        password=args.password, elk_index=args.index, bulk_queue_len_threshold=int(args.size),
        metadata=args.meta
    )
