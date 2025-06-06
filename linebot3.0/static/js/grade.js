console.log(new URLSearchParams(window.location.search).get('uid'))

document.addEventListener('DOMContentLoaded', () => {
  fetchEvents();

  document.getElementById('ratingForm').addEventListener('submit', function (e) {
    e.preventDefault();
    const formData = new FormData(this);

    if (!window.confirm("你確定要送出評分與評論嗎？送出後將無法修改。")) {
     return; //使用者取消，終止送出
    }

    const uid = new URLSearchParams(window.location.search).get('uid');
    formData.append('uid', uid);
    fetch('/api/grade', {
      method: 'POST',
      body: formData
    })
    .then(res => res.text())
    .then(response => {
      alert(response);
      closeModal();
      fetchEvents(); //重新載入活動
    });
  });
});

function fetchEvents() {
  const uid = new URLSearchParams(window.location.search).get('uid');
  fetch(`/api/grade?uid=${uid}`)
    .then(response => {
      if (!response.ok) {
        return response.text().then(err => { throw new Error(err); });
      }
      return response.json();
    })
    .then(data => {
      if (!Array.isArray(data)) {
        console.error('回傳格式錯誤', data);
        alert('伺服器回傳格式錯誤');
        return;
      }

      window.eventsData = data;

      data.sort((a, b) => new Date(a.time) - new Date(b.time));

      const container = document.getElementById('eventsList');
      container.innerHTML = '';

      data.forEach(event => {
        const div = document.createElement('div');
        div.classList.add('event-card');
        div.innerHTML = `
          <h3>${event.orderid}</h3>
          <p>地點：${event.location}</p>
          <p>時間：${event.time}</p>
          <p>發起者：${event.booker_username}</p>
          <p>參與者：${event.participants.map(p => p.username).join(', ')}</p>
          ${event.can_rate ? `<button onclick="openModal(${event.orderid})">評分/評論</button>` : '<p>已評分</p>'}
        `;
        container.appendChild(div);
      });
    })
    .catch(err => {
      console.error('發生錯誤:', err.message);
      alert('載入活動時發生錯誤：' + err.message);
    });
}

function openModal(orderid) {
  document.getElementById('orderid').value = orderid;

  const event = window.eventsData.find(e => e.orderid === orderid);
  const targetContainer = document.getElementById('ratingTargets');
  targetContainer.innerHTML = '';

  const uid = new URLSearchParams(window.location.search).get('uid');

  if (uid === event.booker) {
    event.participants
      .filter(p => p.uid !== uid)
      .forEach(participant => {
        const div = document.createElement('div');
        div.innerHTML = `
          <label>${participant.username}</label>
          <input type="hidden" name="uid_list[]" value="${participant.uid}">
          <input type="text" name="comment_list[]" placeholder="留下評語" required>
          <select name="evaluation_list[]">
            <option value="1">👍 讚</option>
            <option value="-1">👎 倒讚</option>
          </select>
          <hr>
        `;
        targetContainer.appendChild(div);
      });
  } else {
    const div = document.createElement('div');
    div.innerHTML = `
      <label>${event.booker_username}（發起者）</label>
      <input type="hidden" name="uid_list[]" value="${event.booker}">
      <input type="text" name="comment_list[]" placeholder="留下評語" required>
      <select name="evaluation_list[]">
        <option value="1">👍 讚</option>
        <option value="-1">👎 倒讚</option>
      </select>
      <hr>
    `;
    targetContainer.appendChild(div);
  }

  document.getElementById('rateModal').style.display = 'block';
}

function closeModal() {
  document.getElementById('rateModal').style.display = 'none';
}