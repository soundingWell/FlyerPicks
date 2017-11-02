function onSignIn(googleUser) {
  // Useful data for your client-side scripts:
  var profile = googleUser.getBasicProfile();
  window.console.log("ID: " + profile.getId()); // Don't send this directly to your server!
  window.console.log("Name: " + profile.getName());
  window.console.log("Image URL: " + profile.getImageUrl());
  window.console.log("Email: " + profile.getEmail());

  // The ID token you need to pass to your backend:
  var id_token = googleUser.getAuthResponse().id_token;
  window.console.log("ID Token: " + id_token);
        
  var xhr = new XMLHttpRequest();
  xhr.open('POST', 'http://localhost:8080/authenticated');
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onload = function() {
    window.console.log('Signed in as: ' + xhr.responseText);
  };
        
  xhr.send('idtoken=' + id_token);
}