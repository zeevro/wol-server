import {
  createApp,
  onMounted,
  ref,
} from 'https://unpkg.com/vue@3/dist/vue.esm-browser.js';

createApp({
  setup() {
    const toast = (text, ttl = 3000) => {
      const elem = document.createElement('div');
      elem.classList.add('toast');
      elem.innerHTML = text;
      document.body.appendChild(elem);
      setTimeout(() => {
        elem.classList.add('dead');
        setTimeout(() => document.body.removeChild(elem), 400);
      }, ttl);
    };

    const targets = ref([{ name: 'Loading', ip: '...' }]);

    const fetchTargets = async () => {
      const response = await fetch('/targets/');
      const data = await response.json();
      targets.value = data;
    };

    const checkAlive = async (target) => {
      const response = await fetch(`/is_alive/${target.ip}/`);
      const data = await response.json();
      targets.value.forEach((t) => {
        if (t.ip === data.ip) t.isAlive = data.alive;
      });
    };

    const wake = async (target) => {
      try {
        const response = await fetch('/wake/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ip: target.ip, mac: target.mac }),
        });
        const data = await response.json();
        if (data.error != null) throw error;
        toast(`Sent WoL packet to ${target.name}`);
        setTimeout(() => {
          checkAlive(target);
        }, 8000);
      } catch (error) {
        console.error(error);
        toast(`!! ${error} !!`);
      }
    };

    onMounted(() => {
      fetchTargets();
    });

    return { targets, fetchTargets, checkAlive, wake };
  },
}).mount('#app');
