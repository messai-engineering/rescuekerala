import datetime

import requests
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from mainapp.models import Request, ParsedSMSData

PAGING_SIZE = 100

def get_request_data_queue():

    # Manager object for the model
    request_manager = Request.objects
    max_id = 0
    request_data_queue = list()

    # Just has one row to manage stats
    parsed_data_info = ParsedSMSData.objects.first()
    if parsed_data_info.max_id is not 0:
        max_id = parsed_data_info.max_id

    all_request_objects = request_manager.filter(id__gte=max_id)
    paginator = Paginator(all_request_objects, PAGING_SIZE)

    num_pages = paginator.num_pages

    for page_num in range(num_pages):
        try:
            request_data = paginator.page(page_num)
        except EmptyPage:
            request_data = paginator.page(paginator.num_pages)

        request_data_queue.append(request_data)

    return request_data_queue


def handle_requests(request_values):
    return_data = list()
    for message in request_values:
        messai_payload = dict()
        messai_payload['body'] = message['detailrescue']
        messai_payload['date'] = str(datetime.date.today())
        messai_payload['addr'] = 'ADDRPH'

        try:
            r = requests.post('https://keralafloods.messai.in/v1/kerala/parse', json=[messai_payload], timeout=60)
            r.raise_for_status()
            return_data.append(r.json())
        except Exception as e:
            return_data.append({'status': 'error'})
    return return_data

def queue_requests():

    # handle = lambda x: handle_requests(x.values())
    # map(handle,request_data_queue)

    # Create a job queue and publish these into them
    # Right now, just using list comprehension
    result_list = [handle_requests(x.values('id','detailrescue')) for x in get_request_data_queue()]
