import streamlit as st
from ipyleaflet import Marker


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

