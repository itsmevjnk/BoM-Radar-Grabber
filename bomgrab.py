import os
import sys
from sys import exit
from time import sleep

# set up argument parsing
import argparse
parser = argparse.ArgumentParser(
    description='scrape radar/rainfall images from the Australian Bureau of Meteorology'

)
group_src = parser.add_mutually_exclusive_group(required=True)
group_src.add_argument('-u', '--url', help='source image URL', metavar='URL', type=str)
group_src.add_argument('-id', '--source-id', help='source image ID (defaults to national radar image)', nargs='?', metavar='RADAR_ID', type=str, default='national')
group_src.add_argument('-sid', '--show-ids', help='show list of image IDs', action='store_true')
parser.add_argument('-i', '--interval', help='nominal interval between image scrape attempts in seconds (defaults to 300, or default value for specified radar if ID is given)', metavar='INTERVAL', type=int, default=0)
parser.add_argument('-rd', '--rx-delay', help='additional delay from expected next reception time in seconds (defaults to 150)', metavar='DURATION', type=int, default=150)
parser.add_argument('-ip', '--poll-interval', help='interval for polling for image updates before scrape attempt in seconds (defaults to 30)', metavar='POLL_INTERVAL', type=int, default=30)
parser.add_argument('-ua', '--user-agent', help='User-Agent string to be used for requests', metavar='USER_AGENT', type=str, default='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246') # just use some random string here
parser.add_argument('-o', '--output', help='output directory (defaults to current working directory)', metavar='OUTPUT_DIRECTORY', type=str, default=os.getcwd())
args = parser.parse_args()

# read sources file
from collections import namedtuple
Source = namedtuple("Source", "description interval url")
sources = dict()
if args.source_id is not None or args.show_ids:
    import json
    try:
        with open(os.path.dirname(os.path.realpath(__file__)) + '/sources.json', 'r') as f:
            sources_raw = json.load(f)
            # parse source items
            def parse_item(item, id_prefix='', desc_prefix=''): # recursive function to parse and add items to sources
                id_prefix += item['id'] # get state/station/image ID
                desc_prefix += item['description'] # get description

                url = item.get('url') # attempt to get URL if it exists
                if url is not None: # bingo!
                    sources[id_prefix] = Source(desc_prefix, item['interval'], url)
                else:
                    id_prefix += '/'; desc_prefix += ' '
                    for subitem in item['items']: # otherwise we should have subitems
                        parse_item(subitem, id_prefix, desc_prefix)
            for item in sources_raw:
                parse_item(item)
    except FileNotFoundError:
        print('ERROR: sources file (sources.json) not found')
        exit(1)

# functions

if args.show_ids:
    # show sources
    print(f'there are {len(sources)} sources available:')
    for id, info in sources.items():
        print(f'{id}: {info.description} (updates every {info.interval}s)')
    exit()

# at this point we'll be scraping

url = args.url
interval = args.interval
rx_delay = args.rx_delay
poll_interval = args.poll_interval # alias here

if interval < 0:
    print(f'ERROR: interval must be larger than 0')
    exit(2)

if url is None: # then args.source_id must be available
    if args.source_id in sources:
        src = sources[args.source_id]
        url = src.url
        if interval == 0: interval = src.interval
    else:
        print(f'ERROR: invalid source {args.source_id}')
        exit(2)

print(f'scraping {url} in {interval}+{rx_delay}s interval ({poll_interval}s polling interval).')

# extract file name
file_name = os.path.splitext(os.path.basename(url))
file_ext = file_name[1] # get extension
file_name = file_name[0] # and get name without extension

import requests
from datetime import datetime, timezone

# headers to bypass BoM firewall
headers = {
    'User-Agent': args.user_agent
}

def log(str): # function to output log
    print(f'{file_name} {datetime.now()}: {str}')

prev_last_modified = ''
while True:
    # fetch image
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f'ERROR: unexpected status code {resp.status_code}, exiting')
        print(f'response headers: {resp.headers}')
        exit(3)
    
    # get image timestamp
    def get_last_modified(resp_hdr: dict) -> str: # function to get Last-Modified field
        result = resp_hdr.get('Last-Modified')
        if result is None:
            print(f'ERROR: expected response header field Last-Modified')
            exit(3)
        return result
    last_modified = get_last_modified(resp.headers)

    if last_modified == prev_last_modified:
        log(f'new image has not been received - will try again in {poll_interval}s')
        sleep(poll_interval)
        continue
    prev_last_modified = last_modified

    last_modified_dt = datetime.strptime(last_modified, '%a, %d %b %Y %H:%M:%S %Z').replace(tzinfo=timezone.utc) # convert to datetime
    
    # save image
    out_path = os.path.join(args.output, f'{file_name}_{last_modified_dt.strftime('%Y%m%d_%H%M%S')}{file_ext}') # output path
    log(f'received image from {last_modified_dt} - saving to {out_path}')
    with open(out_path, 'wb') as f:
        f.write(resp.content)

    # delay until next turn
    duration = interval - (datetime.now(timezone.utc) - last_modified_dt).total_seconds() + rx_delay
    sleep(duration)

    
