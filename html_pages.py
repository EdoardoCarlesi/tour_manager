#import streamlit as st

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

    #html = "<table><tr><th> Date </th><th> Event </th><th> Arrival </th><th> Distance to event </th><th> Return flight price from </th><th> </th></tr>"
    html = "<table><tr><th> Date </th><th> Event </th><th> Arrival </th><th> Return flight price from </th><th> </th></tr>"
    
    #for event, date, price, airport, distance in zip(departure['event'], departure['date'], departure['price'], departure['event_airport_name'], departure['distance_to_event']):
    for event, date, price, airport in zip(departure['event'], departure['date'], departure['price'], departure['event_airport_name']):
        #if int(distance) < 0:
        #    distance = 'N/A'

        tag_name = event.replace(' ', '').replace(',', '').lower()
        #html += "<tr><th>" + str(date) + "</th><th>" + event + "</th><th>" + airport['city'] + "</th><th>" + str(distance) + "</th><th>" + str(int(price)) + "&#8364;</th><th><a href='#" + tag_name + "'>INFO</a></th></tr>"
        html += "<tr><th>" + str(date) + "</th><th>" + event + "</th><th>" + airport['city'] + "</th><th>" + str(int(price)) + "&#8364;</th><th><a href='#" + tag_name + "'>INFO</a></th></tr>"

    return html


def concerts_html(data):
    """ Just show the concert list """

    html = "<table><tr><th> Date </th><th> Event </th><th>City </th><th>Country </th><th> Website</th></tr>"

    cols = ['Event date', 'Event name', 'City', 'Country', 'Website']

    for i, event in data.iterrows():
        tag_name = event['Event name'].lower().replace(' ', '').replace(',', '')
        html += "<tr id='" + tag_name + "'>"
         
        # Fill the columns of this row
        for col in cols:
            if col == 'Website':
                html += "<th><a href='" + event['Website'] + "' target=_blank>LINK</a></th>"
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

