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

floatingIcon.addEventListener('click', () => {
  popupWrapper.style.display = popupWrapper.style.display === 'none' ? 'block' : 'none';
});

const inputDataLabel = document.createElement('label');
inputDataLabel.setAttribute('for', 'inputData');
inputDataLabel.innerText = 'Input Data:';
popupWrapper.appendChild(inputDataLabel);

const inputDataField = document.createElement('input');
inputDataField.type = 'text';
inputDataField.id = 'inputData';
popupWrapper.appendChild(inputDataField);

const sendPostRequestButton = document.createElement('button');
sendPostRequestButton.id = 'sendPostRequest';
sendPostRequestButton.innerText = 'Send POST Request';
popupWrapper.appendChild(sendPostRequestButton);

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
