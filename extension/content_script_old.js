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
  if (popupWrapper.style.display === 'none') {
    popupWrapper.style.display = 'block';
    fetch(chrome.runtime.getURL('popup.html'))
      .then((response) => response.text())
      .then((html) => {
        popupWrapper.innerHTML = html;

        const sendPostRequestButton = document.getElementById('sendPostRequest');
        sendPostRequestButton.addEventListener('click', () => {
          const backendServerURL = '<backend_server_url>';
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
  } else {
    popupWrapper.style.display = 'none';
  }
});
