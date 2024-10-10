import json
import sys
from datetime import datetime
from pathlib import Path

import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QMessageBox, QComboBox,
                             QGridLayout, QCheckBox)

from database_wrapper import Database


# Functie om voorzieningen uit de database op te halen
def overzicht_attracties():
    db.connect()
    select_query = "SELECT naam, type FROM voorziening"
    results = db.execute_query(select_query)
    db.close()
    return results


# Maakt connectie met de database
db = Database(host="localhost", gebruiker="user", wachtwoord="password", database="attractiepark_software")


# PyQt5 venster voor invoer van voorkeuren
class VoorkeurenWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Voorkeuren")

        # Set up the layout for the dialog using QGridLayout
        self.layout = QGridLayout(self)

        # Naam entry label
        self.naam_label = QLabel("Naam:")
        self.naam_entry = QLineEdit(self)
        self.layout.addWidget(self.naam_label, 1, 0)
        self.layout.addWidget(self.naam_entry, 1, 1)

        # Gender entry label
        self.gender_label = QLabel("Gender:")
        self.gender_entry = QComboBox(self)
        self.gender_entry.addItems(["Man", "Vrouw"])
        self.layout.addWidget(self.gender_label, 2, 0)
        self.layout.addWidget(self.gender_entry, 2, 1)

        # Leeftijd entry label
        self.leeftijd_label = QLabel("Leeftijd:")
        self.leeftijd_entry = QLineEdit(self)
        self.layout.addWidget(self.leeftijd_label, 3, 0)
        self.layout.addWidget(self.leeftijd_entry, 3, 1)

        # Lengte entry label
        self.lengte_label = QLabel("Lengte (cm's):")
        self.lengte_entry = QLineEdit(self)
        self.layout.addWidget(self.lengte_label, 4, 0)
        self.layout.addWidget(self.lengte_entry, 4, 1)

        # Gewicht entry label
        self.gewicht_label = QLabel("Gewicht (kg's):")
        self.gewicht_entry = QLineEdit(self)
        self.layout.addWidget(self.gewicht_label, 5, 0)
        self.layout.addWidget(self.gewicht_entry, 5, 1)

        # Verblijfsduur entry label
        self.verblijfsduur_label = QLabel("Verblijfsduur (min's):")
        self.verblijfsduur_entry = QLineEdit(self)
        self.layout.addWidget(self.verblijfsduur_label, 6, 0)
        self.layout.addWidget(self.verblijfsduur_entry, 6, 1)

        # Attractie voorkeur
        self.attractievoorkeur_label = QLabel("Attractie voorkeur:")
        self.attractievoorkeur_entry = QComboBox(self)
        self.attractievoorkeur_entry.addItems(["Achtbaan", "Water", "Familie", "Simulator", "Draaien"])
        self.layout.addWidget(self.attractievoorkeur_label, 7, 0)
        self.layout.addWidget(self.attractievoorkeur_entry, 7, 1)

        # Eten voorkeuren(Checkboxes)
        self.etensvoorkeur_label = QLabel("Eten's voorkeuren:")
        self.checkbox_snoep = QCheckBox("Snoep")
        self.checkbox_patat = QCheckBox("Patat")
        self.checkbox_ijs = QCheckBox("Ijs")
        self.checkbox_pizza = QCheckBox("Pizza")
        self.checkbox_pasta = QCheckBox("Pasta")
        self.checkbox_pannenkoeken = QCheckBox("Pannenkoeken")
        self.layout.addWidget(self.etensvoorkeur_label, 8, 0)
        self.layout.addWidget(self.checkbox_snoep, 9, 0)
        self.layout.addWidget(self.checkbox_patat, 9, 1)
        self.layout.addWidget(self.checkbox_ijs, 9, 2)
        self.layout.addWidget(self.checkbox_pizza, 10, 0)
        self.layout.addWidget(self.checkbox_pasta, 10, 1)
        self.layout.addWidget(self.checkbox_pannenkoeken, 10, 2)

        # Lievelings attractie('s) entry label
        self.lievelingsattracties_label = QLabel("Lievelings attractie('s)")
        self.lievelingsattracties_entry = QLineEdit(self)
        self.layout.addWidget(self.lievelingsattracties_label, 11, 0)
        self.layout.addWidget(self.lievelingsattracties_entry, 11, 1)

        # Rekingen weer entry label
        self.weer_label = QLabel("Rekening houden met weer:")
        self.weer_entry = QComboBox(self)
        self.weer_entry.addItems(["Ja", "Nee"])
        self.layout.addWidget(self.weer_label, 12, 0)
        self.layout.addWidget(self.weer_entry, 12, 1)

        # Opslaan en annuleren knoppen
        self.opslaan_button = QPushButton("Opslaan", self)
        self.opslaan_button.clicked.connect(self.opslaan)
        self.annuleren_button = QPushButton("Annuleren", self)
        self.annuleren_button.clicked.connect(self.annuleren)

        self.layout.addWidget(self.opslaan_button, 13, 0)
        self.layout.addWidget(self.annuleren_button, 13, 1)

    def get_IOdata(self):
        # Retrieves data and returns it.


        eten_voorkeuren = []
        if self.checkbox_snoep.isChecked():
            eten_voorkeuren.append("Snoep ")
        if self.checkbox_patat.isChecked():
            eten_voorkeuren.append("Patat ")
        if self.checkbox_ijs.isChecked():
            eten_voorkeuren.append("Ijs ")
        if self.checkbox_pizza.isChecked():
            eten_voorkeuren.append("Pizza ")
        if self.checkbox_pasta.isChecked():
            eten_voorkeuren.append("Pasta ")
        if self.checkbox_pannenkoeken.isChecked():
            eten_voorkeuren.append("Pannenkoeken ")

        return {
            "naam": self.naam_entry.text(),
            "gender": self.gender_entry.currentText(),
            "leeftijd": self.leeftijd_entry.text(),
            "lengte": self.lengte_entry.text(),
            "gewicht": self.gewicht_entry.text(),
            "verblijfsduur": self.verblijfsduur_entry.text(),
            "attractie_voorkeuren": self.attractievoorkeur_entry.currentText(),
            "eten_voorkeuren": eten_voorkeuren,
            "lievelings_attracties": self.lievelingsattracties_entry.text(),
            "weer": self.weer_entry.currentText(),
        }

    def haal_weer_op(self):
        api_url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': 'Amsterdam',  # Verander naar locatie van attractiepark
            'appid': 'YOUR_API_KEY',  # Vervang door een geldige API-sleutel
            'units': 'metric'
        }
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            data = response.json()
            temperatuur = data['main']['temp']
            regent = 'rain' in data['weather'][0]['main'].lower()
            return temperatuur, regent
        else:
            return None, None

    def generate_day_program(self):
        # Haal voorkeuren op van de gebruiker
        data = self.get_IOdata()
        db.connect()

        # Weer informatie ophalen: temperatuur en regenstatus
        temperatuur, regent = self.haal_weer_op()

        verblijfsduur = int(data["verblijfsduur"])  # in minuten
        tijd_resterend = verblijfsduur

        # Query voor attracties
        query = """
            SELECT naam, type, geschatte_wachttijd, doorlooptijd, attractie_min_lengte, attractie_max_lengte, attractie_max_gewicht, attractie_min_leeftijd, overdekt
            FROM voorziening 
            WHERE actief = 1  
            AND attractie_min_lengte <= %s
            AND (attractie_max_lengte IS NULL OR attractie_max_lengte >= %s)
            AND attractie_min_leeftijd <= %s
            AND (attractie_max_gewicht IS NULL OR attractie_max_gewicht >= %s)
        """

        params = (
            int(data["lengte"]),
            int(data["lengte"]),
            int(data["leeftijd"]),
            int(data["gewicht"])
        )

        attracties = db.execute_query(query, params)

        # Query voor horeca-gelegenheden op basis van voorkeuren
        horeca_query = """
            SELECT naam, type, doorlooptijd, productaanbod
            FROM voorziening
            WHERE actief = 1
            AND type = 'horeca'
            AND productaanbod IN ({})
        """.format(','.join(['%s'] * len(data["eten_voorkeuren"])))  # Dynamische lijst van placeholders

        horeca_params = tuple(data["eten_voorkeuren"])
        horeca_gelegenheden = db.execute_query(horeca_query, horeca_params)

        # Query voor souvenirwinkels (A-TC7)
        winkel_query = """
            SELECT naam, type, doorlooptijd, productaanbod
            FROM voorziening
            WHERE actief = 1
            AND type = 'winkel'
            AND (productaanbod = 'souvenirs' OR productaanbod = 'souveniers')
        """

        souvenir_winkels = db.execute_query(winkel_query)

        # Query voor winkels met zomerartikelen (A-TC9)
        zomer_winkel_query = """
            SELECT naam, type, doorlooptijd, productaanbod
            FROM voorziening
            WHERE actief = 1
            AND type = 'winkel'
            AND productaanbod = 'zomerartikelen'
        """

        zomer_winkels = db.execute_query(zomer_winkel_query)

        # Aangepaste query voor winkels met ijs (A-TC10)
        ijs_winkel_query = """
            SELECT naam, type, doorlooptijd, productaanbod
            FROM voorziening
            WHERE actief = 1
            AND type = 'winkel'
            AND productaanbod = 'ijs'
        """

        ijs_winkels = db.execute_query(ijs_winkel_query)

        # Query voor winkels met regenaccessoires (A-TC11)
        regen_winkel_query = """
            SELECT naam, type, doorlooptijd, productaanbod
            FROM voorziening
            WHERE actief = 1
            AND type = 'winkel'
            AND productaanbod = 'regenaccessoires'
        """

        regen_winkels = db.execute_query(regen_winkel_query)

        db.close()

        dagprogramma = []

        # A-TC9: Voeg een winkel met zomerartikelen toe als de temperatuur > 20 graden
        if temperatuur > 20 and zomer_winkels:
            dagprogramma.append(zomer_winkels[0])  # Voeg de eerste zomerwinkel toe
            tijd_resterend -= zomer_winkels[0]['doorlooptijd']

        # A-TC11: Voeg een winkel met regenaccessoires toe als het gaat regenen
        if regent and regen_winkels:
            dagprogramma.append(regen_winkels[0])  # Voeg de eerste regenaccessoirewinkel toe
            tijd_resterend -= regen_winkels[0]['doorlooptijd']

        # Attracties splitsen in voorkeur, lievelings en overige
        voorkeur_attracties = []
        lievelings_attracties = []
        overige_attracties = []

        for attractie in attracties:
            if attractie['type'].lower() in [voorkeur.lower() for voorkeur in data['attractie_voorkeuren']]:
                voorkeur_attracties.append(attractie)
            elif attractie['naam'].lower() in [lievelings.lower() for lievelings in data['lievelings_attracties']]:
                lievelings_attracties.append(attractie)
            else:
                overige_attracties.append(attractie)

        # A-TC3: Voeg voorkeurattracties, lievelingsattracties (maximaal 2x) en overige attracties toe
        for attractie in voorkeur_attracties:
            if tijd_resterend >= (attractie['doorlooptijd'] + attractie['geschatte_wachttijd']):
                dagprogramma.append(attractie)
                tijd_resterend -= (attractie['doorlooptijd'] + attractie['geschatte_wachttijd'])

        for attractie in lievelings_attracties:
            # Voeg lievelingsattracties toe, maximaal 2x
            for _ in range(2):  # Lievelingsattracties mogen maximaal 2 keer
                if tijd_resterend >= (attractie['doorlooptijd'] + attractie['geschatte_wachttijd']):
                    dagprogramma.append(attractie)
                    tijd_resterend -= (attractie['doorlooptijd'] + attractie['geschatte_wachttijd'])

        for attractie in overige_attracties:
            if tijd_resterend >= (attractie['doorlooptijd'] + attractie['geschatte_wachttijd']):
                dagprogramma.append(attractie)
                tijd_resterend -= (attractie['doorlooptijd'] + attractie['geschatte_wachttijd'])

        # A-TC5: Minstens één horecagelegenheid toevoegen gebaseerd op voorkeuren
        if horeca_gelegenheden:
            dagprogramma.append(horeca_gelegenheden[0])  # Voeg de eerste gevonden horeca toe
            tijd_resterend -= horeca_gelegenheden[0]['doorlooptijd']

        # A-TC6: Voeg iedere 2 uur horeca toe bij langer verblijf (>4 uur)
        if verblijfsduur > 240:  # 4 uur is 240 minuten
            uren_in_programma = verblijfsduur // 120  # 2 uur = 120 minuten
            for i in range(uren_in_programma - 1):  # Voeg per 2 uur een horeca toe
                if horeca_gelegenheden and tijd_resterend >= horeca_gelegenheden[0]['doorlooptijd']:
                    dagprogramma.append(horeca_gelegenheden[0])
                    tijd_resterend -= horeca_gelegenheden[0]['doorlooptijd']

        # A-TC7: Voeg souvenirwinkel aan het einde van het programma toe
        if souvenir_winkels:
            dagprogramma.append(souvenir_winkels[0])  # Voeg de eerste gevonden souvenirwinkel toe

        # A-TC10: Voeg minimaal één ijswinkel toe als de temperatuur > 20 graden
        if temperatuur > 20 and ijs_winkels:
            dagprogramma.append(ijs_winkels[0])  # Voeg de eerste ijswinkel toe
            tijd_resterend -= ijs_winkels[0]['doorlooptijd']

        return dagprogramma

    def opslaan(self):
        data = self.get_IOdata()

        if not self.naam_entry.text() or not self.gender_entry.currentText() or not self.leeftijd_entry.text() or not self.lengte_entry.text() or not self.gewicht_entry.text():
            QMessageBox.warning(self, "Fout", "Er mogen geen lege velden zijn")
            return

        huidige_datum_tijd = datetime.now()
        datum = huidige_datum_tijd.strftime("%d-%m-%Y")  # Datum in formaat dag-maand-jaar
        tijd = huidige_datum_tijd.strftime("%H:%M")  # Tijd in formaat uren: minuten

        # Haal attracties op gebaseerd op voorkeuren en verblijfsduur
        attracties = self.generate_day_program()
        print(attracties[0])
        print(type(attracties))

        if not attracties:  # Check of er geen attracties gevonden zijn
            QMessageBox.warning(self, "Geen Attracties",
                                "Er zijn geen attracties gevonden op basis van de ingevoerde voorkeuren.")
            return

        dagprogramma = {
            "voorkeuren": {
                "naam": data["naam"],
                "gender": data["gender"],
                "leeftijd": data["leeftijd"],
                "lengte": data["lengte"],
                "gewicht": data["gewicht"],
                "verblijfsduur": data["verblijfsduur"],
                "attractie voorkeur(en)": data["attractie_voorkeuren"],
                "eten's voorkeur(en)": data["eten_voorkeuren"],
                "lieveling's attractie('s)": data["lievelings_attracties"],
                "Rekening houden met weer": data["weer"],
            },
            "dagprogramma": [
                {
                    "attractie_naam": attractie['naam'],  # Change here
                    "type": attractie['type'],  # Change here
                    "geschatte_wachttijd": attractie['geschatte_wachttijd'],  # Change here
                    "doorlooptijd": attractie['doorlooptijd'],  # Change here
                    "attractie_min_lengte": attractie['attractie_min_lengte'],
                    "attractie_max_lengte": attractie['attractie_max_lengte'],
                    "attractie_max_gewicht": attractie['attractie_max_gewicht'],
                    "attractie_min_leeftijd": attractie['attractie_min_leeftijd'],
                } for attractie in attracties
            ],
            "metadata": {
                "aanmeldzuil_id": 23,
                "transactie_id": 509,
                "datum_tijd": [datum, tijd]  # Huidige datum en tijd
            }
        }

        # Sla het programma op in een JSON-bestand
        with open('persoonlijk_programma_bezoeker_x.json', 'w') as json_bestand:
            json.dump(dagprogramma, json_bestand, indent=4)

        QMessageBox.information(self, "Succes", "Voorkeuren en dagprogramma opgeslagen!")
        self.close()

    def annuleren(self):
        self.close()


# Hoofdprogramma voor PyQt5
def main():
    app = QApplication(sys.argv)

    # Open JSON-bestand met bestaande voorkeuren
    bestand_pad = Path(__file__).parent / 'persoonlijke_voorkeuren_bezoeker_1.json'
    try:
        with open(bestand_pad) as json_bestand:
            json_dict = json.load(json_bestand)
            print(json_dict["naam"])  # Test om de naam te printen
    except FileNotFoundError:
        print("JSON-bestand niet gevonden!")

    # Toon de PyQt5 venster voor invoer
    window = VoorkeurenWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
