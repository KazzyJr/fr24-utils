from FlightRadar24 import FlightRadar24API
from pprint import pprint
from datetime import datetime

def unix_to_iso(unix_ts):
    if unix_ts is not None:
        dt = datetime.fromtimestamp(unix_ts)
        return dt.isoformat() + 'Z'
    return '-'


def are_there_any_flights_for_me_today(source: str, destination: str):
    fr_api = FlightRadar24API()

    flights = fr_api.get_airport_details(code=destination)
    for flight in flights['airport']['pluginData']['schedule']['arrivals']['data']:
        airport_code = flight['flight']['airport']['origin']['code']['iata']
        scheduled = unix_to_iso(flight['flight']['time']['scheduled']['arrival'])
        estimated = unix_to_iso(flight['flight']['time']['estimated']['arrival'])

        if airport_code == source:
            departed = flight['flight']['status']['text']
            if departed or estimated:
                print(f'Flight from <{source}> is scheduled to arrive at <{destination}> at {scheduled} and is estimated to arrive at {estimated}. Current status is: {departed} local time')
            else:
                print(f'Flight from <{source}> is scheduled to arrive at <{destination}> at {scheduled}')


def main():
    source = input('Source airport: ')
    destination = input('Destination airport: ')
    are_there_any_flights_for_me_today(source=source, destination=destination)


if __name__ == "__main__":
    main()