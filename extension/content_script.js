const floatingIcon = document.createElement('img');
floatingIcon.src = chrome.runtime.getURL('icon.png');
floatingIcon.id = 'website-talker-floating-icon';
floatingIcon.title = 'Fashionista AI';

// const iconImage = document.createElement('img');
// iconImage.src = chrome.runtime.getURL('icon.png');
// iconImage.width = 48;
// iconImage.height = 48;
// floatingIcon.appendChild(iconImage);

document.body.appendChild(floatingIcon);

// const popupWrapper = document.createElement('div');
// popupWrapper.id = 'website-talker-popup-wrapper';
// popupWrapper.style.display = 'none';
// document.body.appendChild(popupWrapper);

const popupWrapper = document.createElement('div');
popupWrapper.id = 'website-talker-popup-wrapper';
popupWrapper.style.display = 'none';
popupWrapper.style.width = '450px';
popupWrapper.style.height = '704px';
// popupWrapper.style.padding = '10px';
popupWrapper.style.boxSizing = 'border-box';
document.body.appendChild(popupWrapper);

const popupFrame = document.createElement('iframe');
popupFrame.id = 'website-talker-popup-frame';
popupFrame.src = chrome.runtime.getURL('popup.html');
popupFrame.style.border = 'none';
popupFrame.style.width = '450px';
popupFrame.style.height = '704px';
// popupWrapper.style.padding = '10px';
popupWrapper.style.boxSizing = 'border-box';
popupWrapper.appendChild(popupFrame);

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
  // fade out current image and popup
  floatingIcon.classList.remove('fade-in');
  floatingIcon.classList.add('fade-out');
  popupWrapper.classList.remove('fade-in');
  popupWrapper.classList.add('fade-out');

  setTimeout(() => {
    // after fade out, change the image source and display popup
    if (floatingIcon.src === chrome.runtime.getURL('icon.png')) {
      floatingIcon.src = chrome.runtime.getURL('arrow2.png');
      popupWrapper.style.display = 'block';
    } else {
      floatingIcon.src = chrome.runtime.getURL('icon.png');
      popupWrapper.style.display = 'none';
    }

    // force a reflow
    void floatingIcon.offsetHeight;
    void popupWrapper.offsetHeight;

    // fade in new image and popup
    floatingIcon.classList.remove('fade-out');
    floatingIcon.classList.add('fade-in');
    popupWrapper.classList.remove('fade-out');
    popupWrapper.classList.add('fade-in');
  }, 250); // matches the adjusted transition duration
});

chrome.runtime.sendMessage({ type: 'openPopup' });
