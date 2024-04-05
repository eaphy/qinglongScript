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
      "content": "用java实现限流算法"
    }
  ],
  "stream": true
};

axios.post('https://free-gpt-q5t3.onrender.com/v1/chat/completions', data, { headers })
  .then(response => {
    console.log('Response:', response.data);
  })
  .catch(error => {
    console.error('Error:', error);
  });
