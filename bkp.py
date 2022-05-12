
def safe_call_ryanair_apis(airport_code, date_from, date_to):
 
    ryanair = Ryanair("EUR")
    date_today = str(date.today())
    f_name = 'ryan_' + airport_code + date_from + date_to + date_today + '.pkl'
    f_tmp = os.path.join('tmp', f_name)

    flights = ryanair.get_flights(airport_code, date_from, date_to)

    """
    if not os.path.isfile(f_tmp):
        flights = ryanair.get_flights(airport_code, date_from, date_to)
        
        with open(f_tmp, 'wb') as f:
            pkl.dump(flights, f)
    else:
        with open(f_tmp, 'rb') as f:
            flights = pkl.load(f)
    """

    return flights


def find_one_way_flights(airport_code, date_from, date_event, date_to):
    
    flights = safe_call_ryanair_apis(airport_code, date_from, date_event, date_event, date_to)
    destinations = []
    prices = []
    codes = []

    for flight in flights:
        codes.append(flight.destination)
        destinations.append(flight.destinationFull)
        prices.append(flight.price)
   
        if flight.destination in airports.keys():
            this_city = airports[flight.destination]['city']
            this_country = airports[flight.destination]['country']
            countries_list.append(this_country)

            if not this_city in city2airports.keys():
                city2airports[this_city] = flight.destination

            if this_country in cities_list.keys():

                if not this_city in cities_list[this_country]:
                    cities_list[this_country].append(this_city)

            else:
                cities_list[this_country] = [this_city]

    return destinations, prices, codes


