let userEmail = '';
// const baseServerUrl = "https://y41pim9ut5.execute-api.us-west-1.amazonaws.com/dev";
const baseServerUrl = 'http://127.0.0.1:5001';

function getEmail(callback) {
  console.log('Getting user email...');
  chrome.identity.getAuthToken({ interactive: true, scopes: ['openid', 'email', 'profile'] }, (token) => {
    if (chrome.runtime.lastError) {
      console.log(chrome.runtime.lastError.message);
      callback(null);
    } else {
      const xhr = new XMLHttpRequest();
      xhr.open('GET', 'https://people.googleapis.com/v1/people/me?personFields=emailAddresses&access_token=' + token);
      xhr.onload = () => {
        if (xhr.status === 200) {
          const user_info = JSON.parse(xhr.responseText);
          if (user_info.emailAddresses && user_info.emailAddresses.length > 0) {
            callback(user_info.emailAddresses[0].value);
          } else {
            console.log('No email addresses found.');
            callback(null);
          }
        } else {
          console.log(xhr.status, xhr.responseText);
          callback(null);
        }
      };
      xhr.send();
    }
  });
}

function getFirstMessage(storeName) {
  return "Hello! I'm Fai, your personal fashion advisor here at " + 
  storeName +
  ". Need help finding a style or item? Preparing for an event? Or simply seeking fashion inspiration? Just let me know - I'm at your service."
}

function storeUserEmail(email) {
  const backendServerURL = baseServerUrl + '/insert_user_into_db';
  const requestData = {
    email: email,
  };

  fetch(backendServerURL, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(requestData),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.error) {
        console.error('Error storing user email:', data.error);
      } else {
        console.log('User email stored successfully:', data);
      }
    })
    .catch((error) => {
      console.error('Error:', error);
    });
}

// set images
let button = document.getElementById('sendPostRequest');
let img = document.createElement('img');
img.src = chrome.runtime.getURL('send_icon.png');
img.className = 'send-icon'
button.appendChild(img);

const messagerIcon = document.getElementById('messager-icon');
messagerIcon.src = chrome.runtime.getURL('icon.png');

function createMessageElement(text, isUserMessage) {
  const messageContainer = document.createElement('div');
  messageContainer.classList.add('message-container');
  if (isUserMessage) {
    messageContainer.classList.add('user-message');
  } else {
    messageContainer.classList.add('server-message');
  }

  const messageText = document.createElement('p');
  messageText.textContent = text;
  messageText.classList.add('message-text');

  messageContainer.appendChild(messageText);

  return messageContainer;
}

document.addEventListener('DOMContentLoaded', () => {
  getEmail((email) => {
    if (email) {
      userEmail = email;
      console.log('User email:', email);
      // Insert the user email into the database
      storeUserEmail(email);
    } else {
      console.log('Failed to get user email');
    }
  });
  const chatForm = document.getElementById('chatForm');
  chatForm.addEventListener('submit', (event) => {
    event.preventDefault();
    sendPostRequest();
  });

  // set first message
  const chatList = document.getElementById('chatList');
  console.log('DOMcoontentloaded')
  chatList.appendChild(createMessageElement(getFirstMessage('Turtleson'), false));
});

function sendPostRequest() {
  console.log('Sending POST request...');
  const backendServerURL = baseServerUrl + '/post';
  const inputData = document.getElementById('inputData').value;
  console.log('inputData:', inputData);
  console.log('email:', userEmail);
  const requestData = {
    message: inputData,
    email: userEmail,
  };

  // Add typing indicator
  const chatList = document.getElementById('chatList');

  // Send the user message
  const userMessageElement = createMessageElement(inputData, true);
  chatList.appendChild(userMessageElement);

  // Clear the input field after sending the message
  document.getElementById('inputData').value = '';

  // Add the typing indicator
  const typingIndicator = document.createElement('li');
  typingIndicator.id = 'typingIndicator';
  const typingImage = document.createElement('img');
  typingImage.src = 'typing.gif'; // Replace this with the URL of your typing indicator gif
  typingImage.width = 60; // Set the width of the gif
  typingImage.height = 40; // Set the height of the gif
  typingIndicator.appendChild(typingImage);
  chatList.appendChild(typingIndicator);

  // Scroll to the bottom of the chat history
  document.getElementById('chatHistory').scrollTop = chatList.scrollHeight;

  console.log('inputData:', inputData);
  console.log('requestData:', requestData);

  chrome.runtime.sendMessage({ type: 'sendPostRequest', backendServerURL, requestData }, (response) => {
    const serverMessageText = response.error
      ? `An error occurred while sending the POST request. Error: ${response.error}`
      : `${response.text}`;
    const serverMessageElement = createMessageElement(serverMessageText, false);

    // Remove typing indicator and add user and server messages
    chatList.removeChild(document.getElementById('typingIndicator'));
    chatList.appendChild(serverMessageElement);

    console.log('response:', response);

    if (response.outfit_pieces && response.outfit_pieces.length > 0) {
      // Create a single server message element for all pieces
      const messageElement = createMessageElement('', false); // Initial text is empty
      messageElement.classList.add('pieces-message');
    
      response.outfit_pieces.forEach((piece) => {
        // Create a flex container for each row (image and title)
        const rowContainer = document.createElement('div');
        rowContainer.classList.add('pieces-container');
    
        // Create a piece name element
        const pieceName = document.createElement('p');
        pieceName.textContent = `${piece.name}`;
        pieceName.classList.add('piece-text');
    
        // Create a piece image element, if an image URL exists
        if (piece.image_urls && piece.image_urls.length > 0) {
          const pieceImage = document.createElement('img');
          // If the image doesn't start with http:// or https://, then add https://
          if (!piece.image_urls[0].startsWith('http://') && !piece.image_urls[0].startsWith('https://')) {
            pieceImage.src = 'https://' + piece.image_urls[0];
          } else {
            pieceImage.src = piece.image_urls[0];
          }
          pieceImage.classList.add("piece-image");
    
          pieceImage.addEventListener('click', () => {
            window.open(piece.url, '_blank');
          });
    
          rowContainer.appendChild(pieceImage);
        }
    
        // Append the piece name to the row container
        rowContainer.appendChild(pieceName);
    
        // Append the row container to the message element
        messageElement.appendChild(rowContainer);
      });
    
      // Append the message element to the chat list
      chatList.appendChild(messageElement);
    }    

    // Scroll to the bottom of the chat history
    document.getElementById('chatHistory').scrollTop = chatList.scrollHeight;
  });
}
