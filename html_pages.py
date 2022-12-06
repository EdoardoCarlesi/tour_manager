def convert_date(date):

    date = str(date)
    year = date[0:4]
    month = date[5:7]
    day = date[8:10]
    
    return f'{day}/{month}/{year[2:]}'


def flights_html(origin, dests, prices):
    
    html = "<b>" + origin.replace(' ', '_') + "</b><br>"

    if len(dests) > 0:
        html += "<em>Has_Ryanair_connections_to: </em><br><table>"
        
        for dest, price in zip(dests, prices):
            html += "<tr><p><th>" + dest.replace(' ', '_').replace(',', '') + "</th><th>&nbsp" + str(int(price)) + "<span>&#8364;</span></th></p></tr>"
        
        html += "<table>"

    else:
        html += "<b>Has no Ryanair flight connections<b>"

    return html


def departures_html(departure):
    """ Given a departure city, show a table with all the available flight connections """

    html = "<table><tr><th> Date </th><th> Event </th><th> Arrival </th><th> Flight price from </th><th> Link </th></tr>"
    
    for event, date, price, airport, distance, site in zip(departure['event'], departure['date'], departure['price'], departure['event_airport_name'], departure['distance_to_event'], departure['site']):

        event = event.replace('Nanowar Of Steel at ', '')
        #tag_name = event.replace(' ', '').replace(',', '').lower()
        #link_to = "&#8364;</th><th><a href='#" + tag_name + "'>INFO</a></th></tr>"
        link_to = f"&#8364;</th><th><a href='{site}' target='_blank'>WWW</a></th></tr>"
        date = convert_date(date) 
        html += "<tr><th>" + date + "</th><th>" + event + "</th><th>" + airport['city'] + " (" + distance + " km)</th><th>" + str(int(price)) + link_to

    return html


def concerts_html(data):
    """ Just show the concert list """

    html = "<table><tr><th> Date </th><th> Event </th><th>City </th><th>Country </th><th> Link</th></tr>"

    cols = ['Event date', 'Event name', 'City', 'Country', 'Website']

    for i, event in data.iterrows():
        tag_name = event['Event name'].lower().replace(' ', '').replace(',', '')
        html += "<tr id='" + tag_name + "'>"

        remove_words = ['Nanowar Of Steel', ' at ', ' with ', 'Frozen Crown', 'Tragedy']

        # Clean some formats
        for rmw in remove_words:
            event['Event name'] = event['Event name'].replace(rmw, '')

        event['Event date'] = convert_date(event['Event date'])
        
        # Fill the columns of this row
        for col in cols:
            if col == 'Website':
                html += "<th><a href='" + event['Website'] + "' target=_blank>WWW</a></th>"
            else:
                html += "<th>" + event[col] + " </th>"

        # Skip to a new row
        html += "</tr>"
    html += "</table>"

    return html


def popup_html(event):
    
    html = """
    <table>
    <tr>
    <th>Event</th>
    <th>""" + event['Event name'].replace(' ', '_') + """</th>
    </tr>
    
    <tr>
    <th>Date</th>
    <th>""" + event['Event date'] + """</th>
    </tr>
    
    <tr>
    <th>City</th>
    <th>""" + event['City'] + """</th>
    </tr>
    
    <tr>
    <th>Country</th>
    <th>""" + event['Country'] + """</th>
    </tr>
    </tr>
    <th><a href='""" + event['Website'] + """' target=_blank>WEBSITE</a></th>

    </table>
    """

    return html


if __name__ == '__main__':

    date = '2023-02-12'
    
    print(date)
    print(convert_date(date))
