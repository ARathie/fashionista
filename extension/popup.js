document.addEventListener('DOMContentLoaded', () => {
    const sendPostRequestButton = document.getElementById('sendPostRequest');
    sendPostRequestButton.addEventListener('click', () => {
      const backendServerURL = 'http://127.0.0.1:5000/post';
      const inputData = document.getElementById('inputData').value;
      const requestData = {
        message: inputData
      };
  
      chrome.runtime.sendMessage(
        { type: 'sendPostRequest', backendServerURL, requestData },
        (response) => {
          if (response.error) {
            alert('An error occurred while sending the POST request. Error: ' + response.error);
          } else {
            alert('POST request sent successfully! Response: ' + response.text);
          }
        }
      );
    });
  });
  