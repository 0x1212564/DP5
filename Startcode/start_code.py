import json
from datetime import datetime
from pathlib import Path
import requests

from database_wrapper import Database

# Maakt connectie met de database
db = Database(host="localhost", gebruiker="user", wachtwoord="password", database="attractiepark_software")

def haal_weer_op():
        """
        Haalt de temperatuur en neerslagstatus op via de OpenWeatherMap API.

        Parameters:
        - stad (str): De naam van de stad waarvoor je het weer wilt ophalen.
        - api_key (str): Jouw OpenWeatherMap API-sleutel.

        Returns:
        - temperatuur (float): De huidige temperatuur in graden Celsius.
        - regent (bool): True als het regent, anders False.
        """

        # API URL voor huidige weersinformatie op basis van stad
        api_url = "https://api.openweathermap.org/data/2.5/weather?lat=52.374&lon=4.8897&appid=a71b7d54c15964ca3068d3a856b2f399&units=metric"

        try:
            response = requests.get(api_url)
            weer_data = response.json()

            # Haal de huidige temperatuur op
            temperatuur = weer_data['main']['temp']

            # Controleer of er regen is
            regent = 'rain' in weer_data
            print(weer_data)
            return temperatuur, regent

        except Exception as e:
            print(f"Fout bij het ophalen van de weerdata: {e}")
            return None, None

def generate_day_program():
    try:
        bestand_pad = Path(__file__).parent / 'persoonlijke_voorkeuren_bezoeker_1.json'
        try:
            with open(bestand_pad) as json_bestand:
                json_dict = json.load(json_bestand)
        except FileNotFoundError:
            print("JSON-bestand niet gevonden!")
            return

        db.connect()

        temperatuur, regent = haal_weer_op()
        print(temperatuur, regent)

        verblijfsduur = int(json_dict["verblijfsduur"])  # in minuten
        tijd_resterend = verblijfsduur

        # Query voor attracties
        query = """
            SELECT naam, type, geschatte_wachttijd, doorlooptijd, attractie_min_lengte, attractie_max_lengte, attractie_max_gewicht, attractie_min_leeftijd, productaanbod
            FROM voorziening 
            WHERE actief = 1  
            AND attractie_min_lengte <= %s
            AND (attractie_max_lengte IS NULL OR attractie_max_lengte >= %s)
            AND attractie_min_leeftijd <= %s
            AND (attractie_max_gewicht IS NULL OR attractie_max_gewicht >= %s)
        """

        params = (
            json_dict["lengte"],
            json_dict["lengte"],
            json_dict["leeftijd"],
            json_dict["gewicht"],
        )

        attracties = db.execute_query(query, params)
        print(attracties)
        # Get the food preferences list from the JSON
        food_preferences = json_dict.get("voorkeuren_eten", [])  # Default to an empty list if key doesn't exist

        # If there are food preferences, adjust the query
        if food_preferences:
            # Create a string of '%s' placeholders for each item in the list
            placeholders = ', '.join(['%s'] * len(food_preferences))

            # Update the query to use the IN clause
            horeca_query = f"""
                SELECT naam, type, geschatte_wachttijd, doorlooptijd, attractie_min_lengte, attractie_max_lengte, attractie_min_leeftijd, attractie_max_gewicht, productaanbod
                FROM voorziening
                WHERE actief = 1
                AND type = 'horeca'
                AND productaanbod IN ({placeholders})
            """

            # Execute the query, passing the food preferences as the parameters
            horeca_gelegenheden = db.execute_query(horeca_query, tuple(food_preferences))

            print(horeca_gelegenheden)
        # Query voor souvenirwinkels (A-TC7)
        winkel_query = """
            SELECT naam, type, geschatte_wachttijd, doorlooptijd, attractie_min_lengte, attractie_max_lengte, attractie_min_leeftijd, attractie_max_gewicht, productaanbod
            FROM voorziening
            WHERE actief = 1
            AND type = 'winkel'
            AND (productaanbod = 'souvenirs' OR productaanbod = 'souveniers')
        """
        souvenir_winkels = db.execute_query(winkel_query)

        # Query voor winkels met zomerartikelen (A-TC9)
        zomer_winkel_query = """
            SELECT naam, type, geschatte_wachttijd, doorlooptijd, attractie_min_lengte, attractie_max_lengte, attractie_min_leeftijd, attractie_max_gewicht, productaanbod
            FROM voorziening
            WHERE actief = 1
            AND type = 'winkel'
            AND productaanbod = 'zomerartikelen'
        """
        zomer_winkels = db.execute_query(zomer_winkel_query)

        # Query voor winkels met ijs (A-TC10)
        ijs_winkel_query = """
            SELECT naam, type, geschatte_wachttijd, doorlooptijd, attractie_min_lengte, attractie_max_lengte, attractie_min_leeftijd, attractie_max_gewicht, productaanbod
            FROM voorziening
            WHERE actief = 1
            AND type = 'winkel'
            AND productaanbod = 'ijs'
        """
        ijs_winkels = db.execute_query(ijs_winkel_query)

        # Query voor winkels met regenaccessoires (A-TC11)
        regen_winkel_query = """
            SELECT naam, type, geschatte_wachttijd, doorlooptijd, attractie_min_lengte, attractie_max_lengte, attractie_min_leeftijd, attractie_max_gewicht, productaanbod
            FROM voorziening
            WHERE actief = 1
            AND type = 'winkel'
            AND productaanbod = 'regenaccessoires'
        """
        regen_winkels = db.execute_query(regen_winkel_query)

        db.close()

        dagprogramma = []

        # A-TC9: Voeg een winkel met zomerartikelen toe als de temperatuur > 20 graden
        if json_dict["rekening_houden_met_weer"] and temperatuur > 20 and zomer_winkels:
            dagprogramma.append(zomer_winkels[0])
            tijd_resterend -= (zomer_winkels[0]['doorlooptijd'] + zomer_winkels[0]['geschatte_wachttijd'])

        if json_dict["rekening_houden_met_weer"] and regent and regen_winkels:
            dagprogramma.append(regen_winkels[0])
            tijd_resterend -= (regen_winkels[0]['doorlooptijd'] + regen_winkels[0]['geschatte_wachttijd'])

        # Attracties splitsen in voorkeur, lievelings en overige
        voorkeur_attracties = []
        lievelings_attracties = []
        overige_attracties = []

        for attractie in attracties:
            if attractie['type'].lower() in [voorkeur.lower() for voorkeur in json_dict['voorkeuren_attractietypes']]:
                voorkeur_attracties.append(attractie)
            elif attractie['naam'].lower() in [lievelings.lower() for lievelings in json_dict['lievelings_attracties']]:
                lievelings_attracties.append(attractie)
            else:
                overige_attracties.append(attractie)

        # Voeg attracties toe op basis van beschikbare tijd
        for attractie in voorkeur_attracties:
            if tijd_resterend >= (attractie['doorlooptijd'] + attractie['geschatte_wachttijd']):
                dagprogramma.append(attractie)
                tijd_resterend -= (attractie['doorlooptijd'] + attractie['geschatte_wachttijd'])

        for attractie in lievelings_attracties:
            for _ in range(2):
                if tijd_resterend >= (attractie['doorlooptijd'] + attractie['geschatte_wachttijd']):
                    dagprogramma.append(attractie)
                    tijd_resterend -= (attractie['doorlooptijd'] + attractie['geschatte_wachttijd'])

        for attractie in overige_attracties:
            if tijd_resterend >= (attractie['doorlooptijd'] + attractie['geschatte_wachttijd']):
                dagprogramma.append(attractie)
                tijd_resterend -= (attractie['doorlooptijd'] + attractie['geschatte_wachttijd'])

        # Voeg horeca toe
        if horeca_gelegenheden:
            dagprogramma.append(horeca_gelegenheden[0])
            tijd_resterend -= horeca_gelegenheden[0]['doorlooptijd']

        if verblijfsduur > 240:  # Voeg extra horeca toe bij langer verblijf
            uren_in_programma = verblijfsduur // 120
            for i in range(uren_in_programma - 1):
                if horeca_gelegenheden and tijd_resterend >= horeca_gelegenheden[0]['doorlooptijd']:
                    dagprogramma.append(horeca_gelegenheden[0])
                    tijd_resterend -= horeca_gelegenheden[0]['doorlooptijd']

        if souvenir_winkels:
            dagprogramma.append(souvenir_winkels[0])

        huidige_datum_tijd = datetime.now()
        datum = huidige_datum_tijd.strftime("%d-%m-%Y")
        tijd = huidige_datum_tijd.strftime("%H:%M")

        if not attracties:
            print("Geen attracties gevonden")
            return

        dagprogramma = {
            "voorkeuren": {
                "naam": json_dict["naam"],
                "gender": json_dict["gender"],
                "leeftijd": json_dict["leeftijd"],
                "lengte": json_dict["lengte"],
                "gewicht": json_dict["gewicht"],
                "verblijfsduur": json_dict["verblijfsduur"],
                "attractie voorkeur(en)": json_dict["voorkeuren_attractietypes"],
                "eten's voorkeur(en)": json_dict["voorkeuren_eten"],
                "lieveling's attractie('s)": json_dict["lievelings_attracties"],
                "Rekening houden met weer": json_dict["rekening_houden_met_weer"],
            },
            "dagprogramma": [
                {
                    "attractie_naam": attractie["naam"],
                    "type": attractie["type"],
                    "geschatte_wachttijd": attractie["geschatte_wachttijd"],
                    "doorlooptijd": attractie["doorlooptijd"],
                    "attractie_min_lengte": attractie["attractie_min_lengte"],
                    "attractie_max_lengte": attractie["attractie_max_lengte"],
                    "attractie_max_gewicht": attractie["attractie_max_gewicht"],
                    "attractie_min_leeftijd": attractie["attractie_min_leeftijd"],
                    "productaanbod": attractie["productaanbod"],
                } for attractie in dagprogramma  # Fixed reference here
            ],
            "metadata": {
                "aanmeldzuil_id": 23,
                "transactie_id": 509,
                "datum_tijd": [datum, tijd]
            }
        }

        # Sla het programma op in een JSON-bestand
        with open('persoonlijk_programma_bezoeker_1.json', 'w') as json_bestand:
            json.dump(dagprogramma, json_bestand, indent=4)

    except Exception as e:
        print(f"Fout: {e}")


haal_weer_op()
generate_day_program()



