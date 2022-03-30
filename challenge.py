import argparse
from collections import defaultdict
import requests

# keep apikey globally visible
api_key = ''

# --------------------------------------------- Question 1 ---------------------------------------------

def q1():
    for route in get_all_subway_routes():
        print(route["attributes"]["long_name"])
    print()

def get_all_subway_routes() -> object:

    # Approach: Rely on server to filter
    # Logic: The MBTA API is versioned / strongly documented, and any changes which would break 
    #        my code would be in a new version of the API. In addition, by filtering out by type,
    #        we're reducing the amount of bandwith needed to make the call. If this call needed to
    #        happen repeatedly, the extra bandwith needed would compound.

    return get_cached('https://api-v3.mbta.com/routes?filter[type]=0,1').json()['data']

# --------------------------------------------- Question 2 ---------------------------------------------

def q2():
    

    print("Route with most stops:")

    route, num_stops = compute_route_with_most_stops()
    print(f"\t{route}, with {num_stops} stops.")
    print()
    print("Route with least stops:")
    route, num_stops = compute_route_with_least_stops()
    print(f"\t{route}, with {num_stops} stops.")
    print()
    print("Stops which connect multiple routes:")
    # get_stop_to_routes computes [stop]->list-of routes
    for stop, routes in get_stop_to_routes().items():
        if len(routes) > 1:
            print(f"\t{stop} connects {len(routes)} routes: {', '.join(routes)}")

    print()

# get the name of the route with the least stops
def compute_route_with_least_stops() -> tuple[str, int]:
    route_to_stops = get_route_to_stops()

    # get the minimum route, according to the number of stops
    route = min(route_to_stops, key=lambda val: len(route_to_stops[val])) 
    # return route with its number of stops
    return route, len(route_to_stops[route])

# get the name of the route with the most stops
def compute_route_with_most_stops() -> tuple[str, int]:
    route_to_stops = get_route_to_stops()

    # get the maximum route, according to the number of stops
    route = max(route_to_stops, key=lambda val: len(route_to_stops[val])) 
    # return route with its number of stops
    return route, len(route_to_stops[route])


def get_route_to_stops() -> dict[str, list[str]]:
    route_to_stops_dict = {}

    for route in get_all_subway_routes():
        stops = get_all_stops_for_route(route['id'])

        route_name = route['attributes']['long_name']
        route_to_stops_dict[route_name] = [stop['attributes']['name'] for stop in stops]

    return route_to_stops_dict

def get_stop_to_routes() -> dict[str, list[str]]:
    stop_to_routes_dict = defaultdict(lambda: [])

    for route in get_all_subway_routes():
        stops = get_all_stops_for_route(route['id'])

        route_name = route['attributes']['long_name']
        for stop in stops:
            stop_name = stop['attributes']['name']
            stop_to_routes_dict[stop_name].append(route_name)

    return stop_to_routes_dict


def get_all_stops_for_route(route_id: str) -> object:
    return get_cached(f'https://api-v3.mbta.com/stops?filter[route]={route_id}').json()['data']

# --------------------------------------------- Question 3 ---------------------------------------------

def q3():
    print('Input stops to get possible route.')
    print()
    print('Example:')
    print('Stop 1: Ashmont')
    print('Stop 2: Arlington')
    stop1 = 'Ashmont'
    stop2 = 'Arlington'
    print(f"Route: {' -> '.join(compute_route_between(stop1,stop2))}")
    print()
    stop1 = input('Stop 1: ')
    stop2 = input('Stop 2: ')
    print(f"Route: {' -> '.join(compute_route_between(stop1,stop2))}")

# finds a path between any two T stops, if it exists
# arguments: first stop, second stop
# returns: path taken as a list
def compute_route_between(stop1: str, stop2: str) -> list[str]:
    # approach: consider stops and routes as edges in a graph.
    #           then, run a standard bfs implementation to find
    #           path
    # justification: BFS is a standard algorithm / simple to implement
    #                generically; all we need to do is create a dict of
    #                edges/neighbors, which is simple. This also provides
    #                guarantees, e.g. it's the shortest path in number of hops.
    neighbors = defaultdict(lambda: set())
    for route in get_all_subway_routes():
        for stop in get_all_stops_for_route(route['id']):
            stop_name = stop['attributes']['name']
            route_name = route['attributes']['long_name']
            neighbors[stop_name].add(route_name)
            neighbors[route_name].add(stop_name)
    
    return bfs(neighbors, stop1, stop2)

# standard bfs implementation
# arguments: neighbors (dict of node -> connected nodes), start node, end node
# returns: path taken as a list
def bfs(neighbors: dict[str, list[str]], start: str, end: str) -> list[str]:
    visited = [start]
    queue = [(start, [])] # (node, path_to_node), so we can keep track of how we got there.

    while queue:
        curr_node, path = queue.pop(0)

        if curr_node == end:
            return path + [curr_node]
        
        for neighbor in neighbors[curr_node]:
            if neighbor not in visited:
                visited.append(neighbor)
                queue.append((neighbor, path + [curr_node]))
    
    return None

# ------------------------------------------------------------------------------------------------------

# cache is currently just a dictionary, but could upgrade to 
# something like 'requests-cache' for a more performant solution
cache = {}

# caching responses to not make unnecessary repeated calls
def get_cached(url: str) -> object:
    if url in cache:
        return cache[url]

    resp = requests.get(url, headers=headers())
    resp.raise_for_status() # if any non 200 status code occurs, error out.

    cache[url] = resp

    return resp

def headers() -> dict[str,str]:
    return {"X-API-KEY": api_key} if api_key else {}

def main():
    parser = argparse.ArgumentParser(description='Broad challenge code.')
    parser.add_argument('--q', default='all', choices=['all', 'q1', 'q2', 'q3'])

    parser.add_argument('--apikey', default='')

    args = parser.parse_args()

    api_key = args.apikey

    if args.q in ['all', 'q1']:
        print("----- Question 1 -----")
        q1()

    if args.q in ['all', 'q2']:
        print("----- Question 2 -----")
        q2()

    if args.q in ['all', 'q3']:
        print("----- Question 3 -----")
        q3()

if __name__ == "__main__":
    main()
