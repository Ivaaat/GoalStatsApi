const DOMAIN = 'http://127.0.0.1:8000'
// const DOMAIN = 'https://www.goalstatsapi.ru'
const defSelectSeasonOption = document.createElement('option');
defSelectSeasonOption.value = 'Выберите сезон';
defSelectSeasonOption.textContent = 'Выберите сезон';
const seasonSelect = document.getElementById('season');
seasonSelect.appendChild(defSelectSeasonOption)

const defSelectChampOption = document.createElement('option');
defSelectChampOption.value = 'Выберите чемпионат';
defSelectChampOption.textContent = 'Выберите чемпионат';
const champSelect = document.getElementById('champ');
champSelect.appendChild(defSelectChampOption)

const defSelectTeamOption = document.createElement('option');
defSelectTeamOption.value = 'Выберите клуб';
defSelectTeamOption.textContent = 'Выберите клуб';
const teamSelect = document.getElementById('team');
teamSelect.appendChild(defSelectTeamOption)

function jsonDisplay(val)  {
    const element = document.getElementById('jsonWindow');
    element.style.display = val;
};

document.getElementById('search-form').addEventListener('submit', function(event) {
    event.preventDefault();
    // Здесь будет логика отправки формы и отображения результатов
    fetchStatistics();
});

// Пример функции для получения данных статистики
function fetchStatistics() {
    const season = document.querySelector('select[name="season"]').value;
    const league = document.querySelector('select[name="league"]').value;
    const club = document.querySelector('select[name="club"]').value;
    const country = document.querySelector('select[name="country"]').value;
    const player = document.querySelector('input[name="player"]').value;

    // Пример AJAX-запроса
    fetch(`/api/statistics?season=${season}&league=${league}&club=${club}&country=${country}&player=${player}`)
        .then(response => response.json())
        .then(data => {
            displayResults(data);
        })
        .catch(error => console.error('Ошибка:', error));
}

function displayResults(data) {
    const tbody = document.querySelector('#results tbody');
    tbody.innerHTML = ''; // Очистить текущее содержимое

    data.forEach(item => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><a href="#" class="player-link" data-id="${item.playerId}">${item.playerName}</a></td>
            <td>${item.club}</td>
            <td>${item.league}</td>
            <td>${item.season}</td>
            <td>${item.country}</td>
            <td><button class="btn btn-info view-stats" data-id="${item.playerId}">Посмотреть статистику</button></td>
        `;
        tbody.appendChild(row);
    });

    // Добавить обработчик событий для кнопок статистики игроков
    document.querySelectorAll('.view-stats').forEach(button => {
        button.addEventListener('click', function() {
            const playerId = this.getAttribute('data-id');
            fetchPlayerStatistics(playerId);
        });
    });
}

function fetchPlayerStatistics(playerId) {
    fetch(`/api/player/statistics/${playerId}`)
        .then(response => response.json())
        .then(data => {
            document.getElementById('json-output').textContent = JSON.stringify(data, null, 2);
            document.getElementById('statistic-details').style.display = 'block';
            document.getElementById('results').style.display = 'none';
        })
        .catch(error => console.error('Ошибка:', error));
}

document.getElementById('back-button').addEventListener('click', function() {
    document.getElementById('statistic-details').style.display = 'none';
    document.getElementById('results').style.display = 'block';
});

async function fetchSeasons() {
    const response = await fetch('/api/seasons/');
    return await response.json();
}

async function fetchStatisticsSeasonId(seasonId) { 
    const response = await fetch(`${DOMAIN}/api/statistics/?season_id=${seasonId}`);
    return await response.json();
}

async function fetchChampionships(seasonId) {
    const response = await fetch(`${DOMAIN}/api/championships/?season_id=${seasonId}`);
    return await response.json();
}

async function fetchChampionshipId(championshipId) {
    const response = await fetch(`${DOMAIN}/api/statistics/?championship_id=${championshipId}`);
    return await response.json();
}

async function fetchTeams(championshipId) {
    const response = await fetch(`${DOMAIN}/api/teams/?championship_id=${championshipId}`);
    return await response.json();
}

async function fetchStatisticsTeamId(teamId) {
    const response = await fetch(`${DOMAIN}/api/teams/${teamId}/statistics`);
    return await response.json();
}

async function fetchAllTeams() {
    const response = await fetch('/api/teams'); 
    return await response.json();
}

async function fetchTeam(query) {
    const response = await fetch(`/api/teams/search/?query=${encodeURIComponent(query)}`);
    return await response.json();
}

async function fetchAllStatTeam(teamName) {
    const response = await fetch(`${DOMAIN}/api/statistics/?team_name=${teamName}`);
    return await response.json();
}


async function updateSeasons() {
    if (seasonSelect.options.length == 1) {
        const seasons = await fetchSeasons();
        seasons.forEach(season => {
            sessionStorage.setItem(season['name'] , parseInt(season['id']) );
            const option = document.createElement('option');
            option.value = season['name'] ;
            option.textContent = season['name'] ;
            seasonSelect.appendChild(option);
        });
    } else {
        jsonDisplay('none');
    }

    champSelect.innerHTML = '';
    champSelect.appendChild(defSelectChampOption)
    teamSelect.innerHTML = '';
    teamSelect.appendChild(defSelectTeamOption)
    await updateChampionships();
}


async function updateChampionships() {
    if (seasonSelect.value != defSelectSeasonOption.value) {
        const seasonId = sessionStorage.getItem(seasonSelect.value);
        const championships = await fetchChampionships(seasonId);
        championships.forEach(championship => {
            sessionStorage.setItem(championship['name'], parseInt(championship['id']) );
            const option = document.createElement('option');
            option.value = championship['name'];
            option.textContent = championship['name'];
            champSelect.appendChild(option);
        });
        // Загрузить клубы, когда будут выбраны чемпионаты
        await updateTeams();
    } 
}


async function updateTeams() {
    if (champSelect.value != defSelectChampOption.value) {
        const championshipId = sessionStorage.getItem(champSelect.value);
        const teams = await fetchTeams(championshipId);
        const teamSearch = document.getElementById('team-search');
        teamSelect.innerHTML = '';
        teamSelect.appendChild(defSelectTeamOption)
        teams.forEach(team => {
            sessionStorage.setItem(team['name'], parseInt(team['id']) );
            const option = document.createElement('option');
            option.value = team['name'];
            option.textContent = team['name'];
            teamSelect.appendChild(option);
        });
        await updateStatistics();
        teamSearch.value = '';
    } else {
        teamSelect.innerHTML = '';
        teamSelect.appendChild(defSelectTeamOption)
    }
}


async function updateStatistics() {
    if (teamSelect.value != defSelectTeamOption.value) {
        const teamId = sessionStorage.getItem(teamSelect.value);
        const statistics = await fetchStatisticsTeamId(teamId);
        document.getElementById('statistics').textContent = JSON.stringify(statistics, null, 2);
        // Обновляем подсветку синтаксиса
        hljs.highlightElement(document.getElementById('statistics'));
        jsonDisplay('block');
        // sessionStorage.clear() 
    }
}


async function updateSelect(query) {
    searchInput.value = query;
    resultsList.innerHTML = '';
    resultsList.style.display = 'none';
    noResultsDiv.style.display = 'none';
    const statTeam = await fetchAllStatTeam(query);
    seasonSelect.innerHTML = ''; 
    seasonSelect.appendChild(defSelectSeasonOption)
    sessionStorage.clear() 
    sessionStorage.setItem('seasons', JSON.stringify(statTeam));
    const sortedKeys = Object.keys(statTeam).sort();
    sortedKeys.reverse().forEach(key => {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = key;
        seasonSelect.appendChild(option);
    });
    champSelect.innerHTML = ''
    champSelect.appendChild(defSelectChampOption)
    teamSelect.innerHTML = ''
    let option = document.createElement('option');
    option.value = query;
    option.textContent = query;
    teamSelect.appendChild(option) ;

    document.getElementById('season').removeEventListener('change', updateSeasons);
    document.getElementById('champ').removeEventListener('change', updateTeams);
    document.getElementById('team').removeEventListener('change', updateStatistics);
    jsonDisplay('none');

    document.getElementById('season').addEventListener('change', changeSeason);
    document.getElementById('champ').addEventListener('change', changeChamp);
}


async function changeSeason() {
    champSelect.innerHTML = ''
    champSelect.appendChild(defSelectChampOption)
    if (seasonSelect.value != defSelectSeasonOption.value) {
        const seasonStat = JSON.parse(sessionStorage.getItem('seasons'));
        Object.keys(seasonStat[seasonSelect.value]).forEach(champName => {
            const option = document.createElement('option');
            option.value = champName;
            option.textContent = champName;
            champSelect.appendChild(option);
        });
    } 
}


async function getStatistics(teamId) {
    const statistics = await fetchStatisticsTeamId(teamId);
    document.getElementById('statistics').textContent = JSON.stringify(statistics, null, 2);+
    hljs.highlightElement(document.getElementById('statistics'));
    jsonDisplay('block');
}


async function changeChamp() {
    if (champSelect.value != defSelectChampOption.value) {
        const season = document.getElementById('season').value;
        const seasonStat = JSON.parse(sessionStorage.getItem('seasons'));
        const champ = document.getElementById('champ').value;
        await getStatistics(seasonStat[seasonSelect.value][champSelect.value])
    }
    
    
}

let lastTime = 0;
async function searchTeams() {
    const currentTime = Date.now();
    const timeDiff = currentTime - lastTime;

    if (timeDiff < 300) return; // Лимит: 300 мс
    lastTime = currentTime;
    const query = document.getElementById('team-search').value.toLowerCase();
    if (!query) {
        document.getElementById('results').innerHTML = ''; // Очищаем предложения, если запрос пустой
        return;
    }
    const filteredTeams = await fetchTeam(query)
    resultsList.innerHTML = '';
    if (filteredTeams.length > 0) {
        filteredTeams.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = highlightMatches(item, query);
            li.addEventListener('click', () => updateSelect(item));
            resultsList.appendChild(li);
        });
        resultsList.style.display = 'block';
    } else {
        noResultsDiv.style.display = 'block'; 
    }
    loader.style.display = 'none';
}


function selectTeam() {
    const selectedTeam = document.getElementById('team-search').value;
    document.getElementById('team').value = selectedTeam;
    updateStatistics();
    // Очистка поля для поиска по клубам
    document.getElementById('team-search').value = '';
    document.getElementById('results').innerHTML = ''; // Очищаем список предложений
}


async function main(){
    document.getElementById('player').addEventListener('click', () => {
        document.getElementById('player').disabled = true;
        console.log("Тесты начались: поле ввода отключено.");
    });
    await updateSeasons(); // Загружаем сезоны
    document.getElementById('season').addEventListener('change', updateSeasons);
    document.getElementById('champ').addEventListener('change', updateTeams);
    document.getElementById('team').addEventListener('change', updateStatistics);

    document.getElementById('season').removeEventListener('change', changeSeason);
    document.getElementById('champ').removeEventListener('change', changeChamp);
    //document.getElementById('club-search').addEventListener('input', searchClubs);
    // await fetchClubs();

};


// Вызываем функцию после загрузки страницы
window.onload = main()

const searchInput = document.getElementById('team-search');
const resultsList = document.getElementById('results');
const noResultsDiv = document.getElementById('no-results');
const loader = document.getElementById('loader');
let selectedIndex = -1;
let debounceTimer;
let backspaceHoldTimer;
let previousValue = ''; // Для хранения предыдущего значения
let allDel = false

function highlightMatches(item, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return item.replace(regex, '<strong>$1</strong>');
}

function renderHistory() {
    // Ваш код для отображения истории
    // ...
}

searchInput.addEventListener('input', function() {
    clearTimeout(debounceTimer);
    const query = searchInput.value.toLowerCase();
    resultsList.innerHTML = '';
    resultsList.style.display = 'none';
    noResultsDiv.style.display = 'none';
    loader.style.display = 'none';
    selectedIndex = -1;
    debounceTimer = setTimeout(() => {
        if (query === '') {
            renderHistory();
            main() // Если пусто, показываем историю или ничего
            return;
        }
        searchTeams(query);
    }, 300);
});


searchInput.addEventListener('keydown', function(event) {
    const items = resultsList.getElementsByTagName('li');
    if (event.key === 'ArrowDown') {
        selectedIndex = (selectedIndex + 1) % items.length;
        highlightSelectedItem(items);
        event.preventDefault();
    } else if (event.key === 'ArrowUp') {
        selectedIndex = (selectedIndex - 1 + items.length) % items.length;
        highlightSelectedItem(items);
        event.preventDefault();
    } else if (event.key === 'Enter') {
        event.preventDefault(); // Предотвращение отправки формы
        if (selectedIndex >= 0 && selectedIndex < items.length) {
            const itemToSelect = items[selectedIndex].textContent;
            searchInput.value = itemToSelect;
            resultsList.innerHTML = '';
            resultsList.style.display = 'none';
            noResultsDiv.style.display = 'none';
            updateSelect(itemToSelect)
        }
    } else if (event.key === 'Backspace') {
        if (!allDel && searchInput.value == '') {
            seasonSelect.innerHTML = '';
            seasonSelect.appendChild(defSelectSeasonOption)
            jsonDisplay('none');
            main()
            allDel = true
        }
        if (searchInput.value !== previousValue) {
            allDel = false
            clearTimeout(debounceTimer);
            previousValue = searchInput.value; // Обновляем последнее значение
            searchInput.value = searchInput.value.slice(0, -1); // Удаление последнего символа
            searchTeams(searchInput.value); // Обновление результатов поиска
        }
        if (!backspaceHoldTimer) {
            backspaceHoldTimer = setInterval(() => {
                searchInput.value = searchInput.value.slice(0, -1); // Удаление последнего символа
                if (searchInput.value !== previousValue) {
                    previousValue = searchInput.value;
                    searchTeams(searchInput.value);
                }
            }, 100);
        }
        event.preventDefault()
    }
});

searchInput.addEventListener('keyup', function(event) {
    if (event.key === 'Backspace') {
        clearInterval(backspaceHoldTimer);
        backspaceHoldTimer = null; // Сбрасываем таймер
    }
});

function highlightSelectedItem(items) {
    for (let i = 0; i < items.length; i++) {
        items[i].classList.remove('selected');
    }
    if (items[selectedIndex]) {
        items[selectedIndex].classList.add('selected');
    }
}

document.addEventListener('click', function(event) {
    if (!searchInput.contains(event.target) && !resultsList.contains(event.target)) {
        resultsList.innerHTML = '';
        resultsList.style.display = 'none';
        noResultsDiv.style.display = 'none'; 
    }
});
