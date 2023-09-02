function fetchData() {
    var selectedDate = document.getElementById('selectedDate').value;
    var date = JSON.stringify({ date: selectedDate });
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/filght', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var responseData = JSON.parse(xhr.responseText);
            renderTable(responseData.air_list);

        }
    }
    xhr.send(date);
}

function renderTable(data) {
    var flightTableBody = document.getElementById('flight-table-body');
    flightTableBody.innerHTML = '';

    var checkboxes = document.getElementsByName('flight-checkbox1');
    checkboxes.forEach(function(checkbox) {
        checkbox.removeEventListener('change', updateFlightTotal);
    });

    data.forEach(function(flight, index) {
        var row = document.createElement('tr');

        var checkboxCell = document.createElement('td');
        checkboxCell.style.width = '20px';
        checkboxCell.innerHTML = '<div class="custom-control custom-checkbox"> \
                                    <input type="checkbox" name="flight-checkbox1" class="custom-control-input" id="customCheck1' + (index + 1) + '"> \
                                    <label class="custom-control-label" for="customCheck1' + (index + 1) + '">&nbsp;</label> \
                                  </div>';

        var dateCell = document.createElement('td');
        var dateString = flight.date;
        var dateObj = new Date(dateString);
        var formattedDate = dateObj.toISOString().slice(0, 10);
        dateCell.textContent = formattedDate;

        var dayCell = document.createElement('td');
        dayCell.textContent = flight.day;

        var nameCell = document.createElement('td');
        nameCell.textContent = flight.name;

        var airportCell = document.createElement('td');
        airportCell.textContent = flight.airport;

        var leavetimeCell = document.createElement('td');
        leavetimeCell.textContent = flight.leavetime;

        var reachtimeCell = document.createElement('td');
        reachtimeCell.textContent = flight.reachtime;

        var seatCell = document.createElement('td');
        seatCell.textContent = flight.seat;

        var chargeCell = document.createElement('td');
        chargeCell.textContent = flight.charge;

        row.appendChild(checkboxCell);
        row.appendChild(dateCell);
        row.appendChild(dayCell);
        row.appendChild(nameCell);
        row.appendChild(airportCell);
        row.appendChild(leavetimeCell);
        row.appendChild(reachtimeCell);
        row.appendChild(seatCell);
        row.appendChild(chargeCell);

        flightTableBody.appendChild(row);
    });
}

document.getElementById('selectedDate').addEventListener('change', fetchData);