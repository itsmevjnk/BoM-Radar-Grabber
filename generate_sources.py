import json
import csv
from collections import namedtuple

# output list (we put the national radar here)
radars = [
    {
        "id": "national",
        "description": "National Radar Image",
        "interval": 600,
        "url": "http://www.bom.gov.au/radar/IDR00004.jpg"
    }
]

Source = namedtuple("Source", "description interval suffix")
sources = {
    '64': Source('64 km', 300, '4'),
    '128': Source('128 km', 300, '3'),
    '256': Source('256 km', 300, '2'),
    '512': Source('512 km composite', 300, '1'),
    'dopp': Source('Doppler wind', 300, 'I'),
    'rf5m': Source('rainfall in 5 min', 300, 'A'),
    'rf1h': Source('rainfall in 1 hour', 300, 'B'),
    'rf9am': Source('rainfall since 9am', 3600, 'C'),
    'rf24h': Source('rainfall in 24 hours', 86400, 'D'),
}

with open('radars.csv', 'r') as fi:
    radars_csv = csv.DictReader(fi)
    states = dict()
    for row in radars_csv:
        # print(row)
        state = states.get(row['Region ID'])
        if state is None:
            # new state
            radars.append({
                "id": row['Region ID'],
                "description": row['Region'],
                "items": []
            })
            state = radars[-1]
            states[state['id']] = state
        
        url_base = f'http://www.bom.gov.au/radar/IDR{int(row['Location ID']):02d}'
        radar = {
            "id": row['Radar ID'],
            "description": row['Location'],
            "items": []
        }

        for src in sources:
            if int(row[src]) != 0:
                # add source to list
                radar['items'].append({
                    "id": src,
                    "description": sources[src].description,
                    "interval": sources[src].interval,
                    "url": f'{url_base}{sources[src].suffix}.gif'
                })
        
        state['items'].append(radar)
    
    with open('sources.json', 'w') as fo:
        json.dump(radars, fo, indent=4)
