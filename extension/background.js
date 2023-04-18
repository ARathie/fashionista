chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'sendPostRequest') {
      const { backendServerURL, requestData } = message;
  
      fetch(backendServerURL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
      })
        .then(response => response.json())
        .then(data => sendResponse(data))
        .catch(error => sendResponse({ error: error.message }));
  
      return true;
    } else if (message.type === 'openPopup') {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        chrome.pageAction.show(tabs[0].id);
      });
    }
  });
  