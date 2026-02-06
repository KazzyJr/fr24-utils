"""FR24 tools"""
from datetime import datetime

from zoneinfo import ZoneInfo

import json

from FlightRadar24 import FlightRadar24API

def unix_to_iso(unix_ts: float, tz: ZoneInfo):
    """
    Converts a UNIX time to an ISO timestamp
    
    :param unix_ts: UNIX timestamp
    :param tz: Timezone object
    :type tz: ZoneInfo
    :return: A string with an ISO time
    :rtype: str
    """
    if unix_ts is not None:
        dt = datetime.fromtimestamp(unix_ts, tz)
        offset = dt.utcoffset()
        total_seconds = int(offset.total_seconds())
        sign = '+' if total_seconds >= 0 else '-'
        hours = abs(total_seconds) // 3600
        minutes = abs(total_seconds) % 3600 // 60
        suffix = f"{sign}{hours:02d}:{minutes:02d}"
        return dt.isoformat() + 'Z' + suffix
    return ''


def timestamp_to_hms(unix_ts, dep: bool):
    total_seconds = int(unix_ts)
    if total_seconds < 0 and dep:
        return 'Departed'
    
    if total_seconds < 0:
        return 'Arrived'
    
    hours = (total_seconds % 86400) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def are_there_any_flights_for_me_today(source: str, destination: str):
    fr_api = FlightRadar24API()
    
    for page in range(3):
        flights = fr_api.get_airport_details(code=destination, flight_limit=100, page=page)
        found = False

        for flight in flights['airport']['pluginData']['schedule']['arrivals']['data']:
            fl = flight['flight']
            airport_code = fl['airport']['origin']['code']['iata']

            if airport_code == source:
                found = True

                # Flight status
                status = fl['status']['text']

                origin_tz = fl['airport']['origin']['timezone']['name']
                origin_tz_obj = ZoneInfo(origin_tz)
                dst_tz = fl['airport']['destination']['timezone']['name']
                dst_tz_obj = ZoneInfo(dst_tz)
                now_dep = datetime.now(origin_tz_obj)
                now_arr = datetime.now(dst_tz_obj)
                timediff_dep = fl['time']['scheduled']['departure'] - now_dep.timestamp()
                delta_dep = timestamp_to_hms(timediff_dep, True)
                if est_arr := fl['time']['estimated']['arrival']:
                    timediff_arr = est_arr - now_arr.timestamp()
                else:
                    timediff_arr = fl['time']['scheduled']['arrival'] - now_arr.timestamp()
                delta_arr = timestamp_to_hms(timediff_arr, False)

                airline = fl['airline']['name']
                flight_number = fl['identification']['number']['default']
                # Arrives at destination at
                scheduled = unix_to_iso(fl['time']['scheduled']['arrival'], tz=origin_tz_obj)
                estimated = unix_to_iso(fl['time']['estimated']['arrival'], tz=dst_tz_obj)


                print('='*50 + 'FLIGHT INFO' + '='*50)
                if status and estimated:
                    print(
                        f'{airline} > {flight_number} > {source}-{destination}\nScheduled arrival: {scheduled}\nEstimated arrival: {estimated}\n'
                        f'Time to departure: {delta_dep}\nTime to arrival: {delta_arr}\nStatus: {status}'
                    )
                elif status != 'Scheduled':
                    print(f'{airline} > {flight_number} > {source}-{destination}\nScheduled arrival: {scheduled}\nTime to departure: {delta_dep}\nTime to arrival: {delta_arr}\nStatus: {status}')
                else:
                    print(f'{airline} > {flight_number} > {source}-{destination}\nScheduled arrival: {scheduled}\nTime to departure: {delta_dep}\nTime to arrival: {delta_arr}')
                print('='*111)

    if not found:
        print('No upcoming flights!')


def gather_info():
    reuse = input('Reuse values? y/n ')
    if reuse == 'y':
        return load_airports()
    return dump_airports()


def load_airports():
    with open('history.json', 'r', encoding='UTF-8') as h:
        file = json.load(h)
        return file['source'], file['destination']


def dump_airports():
    source = input('Source airport: ')
    destination = input('Destination airport: ')
    with open('history.json', 'w', encoding='UTF-8') as h:
        h.write(json.dumps({'source': source, 'destination': destination}))
    return source, destination


def main():
    source, destination = gather_info()
    are_there_any_flights_for_me_today(source=source, destination=destination)


if __name__ == "__main__":
    main()
