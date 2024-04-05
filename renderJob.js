/*
cron:  0/5 * * * *
*/


const axios = require('axios');

const headers = {
  'Authorization': 'Bearer freegpt',
  'Content-Type': 'application/json'
};

const data = {
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "user",
      "content": "介绍下自己"
    }
  ],
  "stream": true
};

// 生成10到30之间的随机延迟时间（单位：毫秒）
const delay = Math.floor(Math.random() * (30000 - 10000 + 1)) + 10000;

// 使用setTimeout延迟执行axios请求
setTimeout(() => {
  axios.post('https://free-gpt-q5t3.onrender.com/v1/chat/completions', data, { headers })
    .then(response => {
      console.log('Response:', response.data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
}, delay);

