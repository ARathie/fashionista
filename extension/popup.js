document.addEventListener('DOMContentLoaded', () => {
  const chatForm = document.getElementById('chatForm');
  chatForm.addEventListener('submit', (event) => {
    event.preventDefault();
    sendPostRequest();
  });
});

function sendPostRequest() {
  const backendServerURL = 'http://127.0.0.1:5000/post';
  const inputData = document.getElementById('inputData').value;
  const requestData = {
    message: inputData
  };

  // Add typing indicator
  const chatList = document.getElementById('chatList');
  const typingIndicator = document.createElement('li');
  typingIndicator.id = 'typingIndicator';
  const typingImage = document.createElement('img');
  typingImage.src = 'typing.gif'; // Replace this with the URL of your typing indicator gif
  typingIndicator.appendChild(typingImage);
  chatList.appendChild(typingIndicator);

  // Scroll to the bottom of the chat history
  document.getElementById('chatHistory').scrollTop = chatList.scrollHeight;

  chrome.runtime.sendMessage(
    { type: 'sendPostRequest', backendServerURL, requestData },
    (response) => {
      const userMessage = document.createElement('li');
      userMessage.style.fontWeight = 'bold';
      userMessage.textContent = `You: ${inputData}`;

      const serverMessage = document.createElement('li');
      if (response.error) {
        serverMessage.textContent = 'An error occurred while sending the POST request. Error: ' + response.error;
      } else {
        serverMessage.textContent = `Server: ${response.text}`;

        if (response.outfit_pieces) {
          response.outfit_pieces.forEach((piece) => {
            const pieceContainer = document.createElement('div');
            pieceContainer.style.marginTop = '10px';

            const pieceName = document.createElement('p');
            pieceName.textContent = piece.name;
            pieceContainer.appendChild(pieceName);
  
            if (piece.image_urls && piece.image_urls.length > 0) {
              const pieceImage = document.createElement('img');
              pieceImage.src = piece.image_urls[0];
              pieceImage.style.width = '100px'; // Adjust the image size if necessary
              pieceImage.style.cursor = 'pointer';
  
              pieceImage.addEventListener('click', () => {
                window.open(piece.url, '_blank');
              });
  
              pieceContainer.appendChild(pieceImage);
            }
  
            serverMessage.appendChild(pieceContainer);
          });
        }
      }
  
      // Remove typing indicator and add user and server messages
      chatList.removeChild(document.getElementById('typingIndicator'));
      chatList.appendChild(userMessage);
      chatList.appendChild(serverMessage);
  
      // Scroll to the bottom of the chat history
      document.getElementById('chatHistory').scrollTop = chatList.scrollHeight;
  
      // Clear the input field after sending the message
      document.getElementById('inputData').value = '';
    }
  );
}
