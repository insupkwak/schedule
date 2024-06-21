window.onload = function() {
    const dateInput = document.getElementById('date');
    if (localStorage.getItem('savedDate')) {
        dateInput.value = localStorage.getItem('savedDate');
    }
    dateInput.addEventListener('change', function() {
        localStorage.setItem('savedDate', dateInput.value);
    });

    // Populate minute options
    const startTimeInput = document.getElementById('start_time');
    const endTimeInput = document.getElementById('end_time');
    populateMinutes(startTimeInput);
    populateMinutes(endTimeInput);

    // Set initial times based on last schedule's end time
    const lastEndTime = getLastEndTime();
    if (lastEndTime) {
        startTimeInput.value = lastEndTime;
        endTimeInput.value = lastEndTime;
    }

    // Sync end time with start time
    startTimeInput.addEventListener('change', function() {
        endTimeInput.value = startTimeInput.value;
    });
}

function populateMinutes(timeInput) {
    const minutes = ['00', '10', '20', '30', '40', '50'];
    let newTimeInput = timeInput.cloneNode(true);
    newTimeInput.innerHTML = ''; // Clear existing options
    for (let hour = 0; hour < 24; hour++) {
        for (let minute of minutes) {
            let timeOption = document.createElement('option');
            timeOption.value = `${String(hour).padStart(2, '0')}:${minute}`;
            timeOption.text = `${String(hour).padStart(2, '0')}:${minute}`;
            newTimeInput.appendChild(timeOption);
        }
    }
    timeInput.parentNode.replaceChild(newTimeInput, timeInput);
}

function getLastEndTime() {
    // This function simulates getting the last end time.
    // Replace with actual implementation, for example, by fetching from the server.
    let lastEndTime = localStorage.getItem('lastEndTime');
    return lastEndTime;
}

// Assuming the server updates the lastEndTime in localStorage when a new plan is added
document.querySelector('form').addEventListener('submit', function() {
    localStorage.setItem('lastEndTime', document.getElementById('end_time').value);
});
