var ConversationBox = function () {
    // Creating the heading and the messagebox
  var heading = $('<p id="chat-preview-title">Conversations</p>');
  var messageBox = $('<div id="chat-preview-message-box"></div>');

  // Appending to the chat preview element
  var chatPreview = $('#chat-preview');
  chatPreview.append(heading);
  chatPreview.append(messageBox);

    this.render = function (data) {
        this.reset();
        // Looping through the data array and creating message elements
        data.forEach(function (message) {
          var messageElement = $('<p class="chat-preview-message"><b>[' + message[1] + '] -> [' + message[2] + '] [Step: ' + message[3] + ']:</b> ' + message[0] + '</p>');
          messageBox.append(messageElement);
        });
    }

    this.reset = function () {
        messageBox.empty();
    }
}
