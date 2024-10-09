document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const voorzieningenContainer = document.getElementById('sessions');
    const voorkeurenContainer = document.getElementById('persoonlijkeVoorkeuren');

    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (!file) {
            return;
        }

        const reader = new FileReader();
        reader.onload = function(e) {
            const data = JSON.parse(e.target.result);

            document.getElementById('sessions').innerHTML = "";

            // Voorkeuren weergeven
            const nameHeader = document.createElement('h1');
            nameHeader.textContent = `${data.voorkeuren["naam"]}s dagprogramma 🎢🎉🎉`;
            voorkeurenContainer.appendChild(nameHeader);

            const voorkeurDiv = document.createElement('div');
            voorkeurDiv.classList.add('voorkeur');
            let voorkeurenHTML = ``;
            Object.keys(data.voorkeuren).forEach(key => {
                voorkeurenHTML += `<div class="voorkeur-info">${key.charAt(0).toUpperCase() + key.slice(1)}: ${data.voorkeuren[key]}</div>`;
            });
            voorkeurDiv.innerHTML = voorkeurenHTML;
            voorkeurenContainer.appendChild(voorkeurDiv);

            // Voorzieningen weergeven
            data.dagprogramma.forEach((dagprogramma, index) => {
                const div = document.createElement('li');
                //div.classList.add('li');
                div.innerHTML = `
                                 <div class="time"><b>#${index + 1} - ${voorziening.naam} (${voorziening.type})</b></div>
                                    <p>
                                        Wachttijd: ${dagprogramma.geschatte_wachttijd} minuten (doorlooptijd: ${dagprogramma.doorlooptijd} minuten)<br>
                                        Minimum-maximum lengte: ${dagprogramma.attractie_min_lengte || 'Geen beperking'} - ${dagprogramma.attractie_max_lengte || 'Geen beperking'}<br>
                                        Minimum leeftijd: ${dagprogramma.attractie_min_leeftijd || 'Geen beperking'}<br>
                                        Maximum gewicht: ${dagprogramma.attractie_max_gewicht || 'Geen beperking'}
                                    </p>`;
                voorzieningenContainer.appendChild(div);
            });
        };
        reader.readAsText(file);
    });
});
