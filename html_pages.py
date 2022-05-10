import streamlit as st

def flights_html(origin, dests, prices):
    
    html = "<b>" + origin.replace(' ', '_') + "</b><br>"

    if len(dests) > 0:
        html += "<em>Has_Ryanair_connections_to: </em><br><table>"
        
        for dest, price in zip(dests, prices):
            html += "<tr><p><th>" + dest.replace(' ', '_').replace(',', '') + "</th><th>&nbsp" + str(price) + "<span>&#8364;</span></th></p></tr>"
        
        html += "<table>"

    else:
        html += "<b>Has no Ryanair flight connections<b>"

    return html


def departures_html(departure):

    html = "<p>" + departure['origin'].upper() + " is connected to: </p><br>"

    for event, date, price in zip(departure['event'], departure['date'], departure['price']):
        html += "<p><b>------>" + event + "</b> " + str(date) + " flight price: " + str(price) + " euros.</p><br>"

    return html

def concerts_html(data):
    
    html = "<table><tr><th>Event </th><th>Date </th><th>City </th><th>Country </th><th> Website</th></tr><br>"

    cols = ['Event date', 'Event name', 'City', 'Country', 'Website']

    for i, event in data.iterrows():
        html += "<tr>"
         
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

    #st.button('Show Airports', on_click=click_action)

    return html

