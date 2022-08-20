function toast(text, ttl=3000) {
  let elem = document.createElement('div');
  elem.classList.add('toast');
  elem.innerHTML = text;
  document.body.appendChild(elem);
  setTimeout(() => {
    elem.classList.add('dead');
    setTimeout(() => {
      document.body.removeChild(elem);
    }, 400);
  }, ttl);
}

function updateStatusLed(elem) {
  fetch(`is_alive/${elem.dataset.ip}/`).then((response) => {
    return response.json();
  }).then((json) => {
    elem.classList.toggle('alive', json.alive);
    elem.classList.toggle('dead', !json.alive);
  });
}

[...document.getElementsByClassName('wake-btn')].forEach((elem) => {
  elem.addEventListener('click', (event) => {
    target = event.target.dataset;
    fetch('wake/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(target),
    }).then((response) => {
      if (!response.ok) throw `${response.status} ${response.statusText}`;
      return response.json()
    }).then((json) => {
      if (json.error) throw json.error;
      toast(`Sent WoL packet to ${target.name}`);
      statusLed = document.querySelector(`.status-led[data-ip="${target.ip}"]`);
      setTimeout(() => {
        updateStatusLed(statusLed);
      }, 8000);
    }).catch((error) => {
      console.error(error);
      toast(`!! ${error} !!`);
    })
  });
});

setInterval(() => {
  [...document.getElementsByClassName('status-led')].forEach(updateStatusLed);
}, 30000);
