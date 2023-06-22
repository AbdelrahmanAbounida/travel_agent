import streamlit as st 
from streamlit_option_menu import option_menu
from utils.agents.PineconeAgent import PineconeAgent
from utils.agents.ItineraryQuery import get_pinecone_response, get_openai_response
from dotenv import load_dotenv
import pinecone 
import json
import os 
import sys

load_dotenv()


# *********************************
# Load environmental variables
# *********************************

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")
PINECONE_ENV = os.environ.get("PINECONE_ENV")
PINECONE_INDEX_NAME = os.environ.get("PINECONE_INDEX_NAME")

PINECONE_INDEX_NAME = "test-index"
# *********************************
# Initialize Pinecone
# *********************************
pinecone_agent = PineconeAgent(OPENAI_API_KEY=OPENAI_API_KEY,
                               PINECONE_API_KEY=PINECONE_API_KEY,
                               PINECONE_ENV=PINECONE_ENV,
                               PINECONE_INDEX_NAME=PINECONE_INDEX_NAME) # PINECONE_INDEX_NAME

pinecone_agent.init_pinecone()




st.header("Create Itinerary")
options = option_menu('',["With Pinecone", "Without Pinecone"], icons=['',''],orientation="horizontal")



if options == "With Pinecone":
    index = pinecone.Index(PINECONE_INDEX_NAME)
    all_cities = list(index.describe_index_stats()['namespaces'].keys())
    
    cols=st.columns(4)
    with cols[0]:
        # 1- select city
        city = st.selectbox(
        'City',
        all_cities) 
        num_of_vectors = index.describe_index_stats()['namespaces'][city]['vector_count']
        st.write(f"Pinecone has {num_of_vectors} vectors")

    with cols[1]:
        # 2- number of days
        num_of_days = st.selectbox(
            'Number of Days',
            list(range(1,8))
        )

    with cols[2]:
        # 3- hotel
        hotel = st.text_input("Hotel",value="Balneario de las Arenas")
    
    with cols[3]:
        source = st.selectbox(
            'Data Source',
            ('PDF','URL','CSV','')
        )
    
    # 4- User Persona
    user_persona = st.text_area("User Persoan",value="""I am american luxury traveler who loves culture, arts, gastronomy and local history, and like to embark in experiences such as lessons, wine tastings, private visits, and long walks exploring the location and nature.""")

    pinecone_response = ''

    # 3- Getting Pinecone Response
    if st.button(f"Create Pinecone {city} Entry"):
        pinecone_city_info = pinecone_agent.get_context(question=f"give me some information about {city}",city=city,source=source)['matches'][0]['metadata']['text']
        pinecone_hotels_info = pinecone_agent.get_context(question=f"recommend some hotels in {city}",city=city,source=source)['matches'][0]['metadata']['text']
        pinecone_places_info = pinecone_agent.get_context(question=f"recommend some places in {city}",city=city,source=source)['matches'][0]['metadata']['text']
        pinecone_restaurants_info = pinecone_agent.get_context(question=f"recommend some restaurants in {city}",city=city,source=source)['matches'][0]['metadata']['text']
        pinecone_venues_info = pinecone_agent.get_context(question=f"recommend some venues in {city}",city=city,source=source)['matches'][0]['metadata']['text']
        pinecone_self_explore_info = pinecone_agent.get_context(question=f"recommend some self-explore walks places in {city}",city=city,source=source)['matches'][0]['metadata']['text']

        with st.spinner("Loading Pinecone Context"):
            pinecone_response = get_pinecone_response(city=city,
                                                    pinecone_city_info=pinecone_city_info,
                                                    pinecone_hotels_info= pinecone_hotels_info,
                                                    pinecone_places_info = pinecone_places_info,
                                                    pinecone_restaurants_info = pinecone_restaurants_info,
                                                    pinecone_venues_info=pinecone_venues_info,
                                                    pinecone_self_explore_info = pinecone_self_explore_info,
                                                    num_of_days = num_of_days
                                                    )
        
        st.success("Entry Created. Ready for Queries")
        st.write("Pinecone Context:")
        
        try:
            st.json(pinecone_response)
        except Exception as e:
            print(e)
            st.write(pinecone_response)
            
    if st.button(f"Run Results"):   
        # 4- Getting Openai Response
        with st.spinner("Creating Itinerary.."):
            context = f"use the following information in your answer if it is helpful: {pinecone_response}"
            openai_response = get_openai_response(city=city,hotel=hotel,num_of_days=num_of_days,user_persona=user_persona,context=context)
        
        try:
            st.json(openai_response)
        except Exception as e:
            print(e)
            st.write(openai_response)


if options == 'Without Pinecone':
    all_cities = list(pinecone.Index(PINECONE_INDEX_NAME).describe_index_stats()['namespaces'].keys())
    
    cols=st.columns(4)
    with cols[0]:
        # 1- select city
        city = st.selectbox(
        'City',
        all_cities) 
    with cols[1]:
        # 2- number of days
        num_of_days = st.selectbox(
            'Number of Days',
            list(range(1,8))
        )
    with cols[2]:
        # 3- hotel
        hotel = st.text_input("Hotel",value="Balneario de las Arenas")

    with cols[3]:
        source = st.selectbox(
            'Data Source',
            ('PDF','URL','CSV','')
        )
        
    # 4- User Persona
    user_persona = st.text_area("User Persoan",value="""I am american luxury traveler who loves culture, arts, gastronomy and local history, and like to embark in experiences such as lessons, wine tastings, private visits, and long walks exploring the location and nature.""")

    # 5- Checking errors
    if not city:
        st.error("Please Make Sure that u selected a city")
        sys.exit()
    
    if not num_of_days:
        st.error("Please choose the required number of days")
    
    # 6- getting openai response
    if st.button(f"Run Results"): 
        with st.spinner("Creating Itinerary..."):
            
            openai_response = get_openai_response(city=city,hotel=hotel,num_of_days=num_of_days,user_persona=user_persona,context="")
        try:
            st.json(json.loads(openai_response))
        except Exception as e:
            print(e)
            try:
                st.json(pinecone_response)
            except Exception as e:
                print(e)
                st.write(pinecone_response)
