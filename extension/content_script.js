const floatingIcon = document.createElement('div');
floatingIcon.id = 'website-talker-floating-icon';
floatingIcon.title = 'Open Website Talker';

const iconImage = document.createElement('img');
iconImage.src = chrome.runtime.getURL('icon.png');
iconImage.width = 48;
iconImage.height = 48;
floatingIcon.appendChild(iconImage);

document.body.appendChild(floatingIcon);

const popupWrapper = document.createElement('div');
popupWrapper.id = 'website-talker-popup-wrapper';
popupWrapper.style.display = 'none';
document.body.appendChild(popupWrapper);

const inputDataLabel = document.createElement('label');
inputDataLabel.setAttribute('for', 'inputData');
inputDataLabel.innerText = 'Input Data:';
popupWrapper.appendChild(inputDataLabel);

const inputDataField = document.createElement('input');
inputDataField.type = 'text';
inputDataField.id = 'inputData';
popupWrapper.appendChild(inputDataField);

const responseMessageLabel = document.createElement('label');
responseMessageLabel.setAttribute('for', 'responseMessage');
responseMessageLabel.innerText = 'Server Response:';
popupWrapper.appendChild(responseMessageLabel);

const responseMessageField = document.createElement('textarea');
responseMessageField.id = 'responseMessage';
responseMessageField.disabled = true;
responseMessageField.style.width = '100%';
responseMessageField.style.height = '100px';
popupWrapper.appendChild(responseMessageField);

const sendPostRequestButton = document.createElement('button');
sendPostRequestButton.id = 'sendPostRequest';
sendPostRequestButton.innerText = 'Send POST Request';
popupWrapper.appendChild(sendPostRequestButton);

function sendPostRequest() {
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
        document.getElementById('responseMessage').value = response.text;
      }
    }
  );
}

sendPostRequestButton.addEventListener('click', sendPostRequest);
inputDataField.addEventListener('keydown', (event) => {
  if (event.keyCode === 13) {
    event.preventDefault();
    sendPostRequestButton.click();
  }
});

floatingIcon.addEventListener('click', () => {
  popupWrapper.style.display = popupWrapper.style.display === 'none' ? 'block' : 'none';
});

chrome.runtime.sendMessage({ type: 'openPopup' });
