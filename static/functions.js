// My Website's Functions

// Display Info about Playlists When Requested
// called from "playlists"
function playlistModal(button) {
    const xhttp = new XMLHttpRequest();
    // get the API endpoint, which is associated with the element clicked
    const endpoint = button.getAttribute("data-playlistendpoint");

    // once x.http.send() ran
    xhttp.onload = function() {
        if (this.status == 200) {
          const plModal = document.getElementById("plModal");
          // show the box
          plModal.style.display = "block";

          const playlistInfo = JSON.parse(this.responseText);
          const items = playlistInfo["items"];
          showPlaylistInfo(items);

        }
        
    }
  xhttp.open("POST", "playlistModal", true);
  xhttp.setRequestHeader("Content-Type", "application/json");  // Set content type as JSON
  xhttp.send(JSON.stringify({ endpoint: endpoint }));
}

// display information about the playlist, creating elements to display
// called by function above, playlistModal()
function showPlaylistInfo(info) {
  const container = document.getElementById("playlist-tracks-container"); 
  container.innerHTML = ""; // wipe it clean, in case data was already there

  // create a row, for Boostrap CSS styling
  const row = document.createElement('div');
  row.className = "row g-3";

  info.forEach(function(entry) {
    // create a column, for Boostrap CSS styling
    const col = document.createElement('div');
    col.className = "col-md-6";

      // create a card to contain the info about a specific track
      const card = document.createElement('div');
      card.className = "card";

        // create a card that stores the information
        const cardBody = document.createElement('div');
        cardBody.className = "card-body text-center";

          // create an element for the name of the track
          const nameP = document.createElement('p');
          nameP.innerHTML = entry.track.name;
          nameP.className = "card-text fw-bold";
          // add this element as a child of the track-specific div
          cardBody.appendChild(nameP);

          // create an element for the artist of the song
          const artistsP = document.createElement('p');
          artistsInfo = entry.track.artists;
          let artistsStr = "";

          artistsInfo.forEach(function(artist, index) {
            if (index < 3) { // limit to three iterations
              artistsStr += artist.name;
              if (index < artistsInfo.length - 1) { // Check if it's not the last element
                if (index )
                artistsStr += ", "; // Add a comma and space
              }
            }
          });
          artistsP.innerHTML = artistsStr;
          artistsP.className = "card-text text-muted";
          cardBody.appendChild(artistsP);

          // create an element for the popularity of the song
          const popularityP = document.createElement('p');
          popularityP.innerHTML = "Popularity: " + entry.track.popularity;
          popularityP.className = "card-text text-success";
          cardBody.appendChild(popularityP);

          // add a button that let's the user add song to favorites
          const favButton = document.createElement('button');
          // set the button's onclick attribute
          favButton.setAttribute('onclick', 'addFavorite(this);');
          // set the button's data-songEndpoint attribute
          favButton.setAttribute('data-songEndpoint', entry.track.href);
          favButton.className = "addFavButton btn btn-outline-success btn-sm mt-3";
          favButton.setAttribute('id', 'playlists-addfav-button')
          favButton.innerHTML = "Add to Favorites";
          cardBody.appendChild(favButton);

        // add the card body to the card
        card.appendChild(cardBody);
              
      // add the card to the column for styling
      col.appendChild(card);

    // add the col as a child of the row
    row.appendChild(col);

  container.appendChild(row);
  })
}

// close the playlist popup when clicking the x
function closePlaylistModal() {
  const xhttp = new XMLHttpRequest();

  // once x.http.send() ran
  xhttp.onload = function() {
      if (this.status == 200) {
        const plModal = document.getElementById("plModal");
        // show the box
        plModal.style.display = "none";
      }
      
  }
xhttp.open("POST", "closePlaylistModal", true);
xhttp.send();
}

// add a song to favorites
function addFavorite(button) {
  const xhttp = new XMLHttpRequest();
  const songEndpoint = button.getAttribute("data-songEndpoint");
  const addFavButton = document.querySelector(`[data-songEndpoint="${songEndpoint}"]`);
  addFavButton.style.backgroundColor = "#1db954";
  addFavButton.innerHTML = "Added to Favorites";
  addFavButton.style.color = "#fff";
  button.disabled = "true";

  xhttp.open("POST", "addFavorite", true);
  xhttp.setRequestHeader("Content-Type", "application/json");  // Set content type as JSON
  xhttp.send(JSON.stringify({ songEndpoint: songEndpoint }));
}

// remove a song from favorites
function removeFavorite(button) {
  const xhttp = new XMLHttpRequest();
  const songEndpoint = button.getAttribute("data-songEndpoint");
  const removeFavButton = document.querySelector(`[data-songEndpoint="${songEndpoint}"]`);
  
  removeFavButton.style.backgroundColor = "#dc3545";
  removeFavButton.innerHTML = "Removed from Favorites";
  removeFavButton.style.color = "#fff";
  button.disabled = "true";

  xhttp.open("POST", "removeFavorite", true);
  xhttp.setRequestHeader("Content-Type", "application/json");  // Set content type as JSON
  xhttp.send(JSON.stringify({ songEndpoint: songEndpoint }));
}

// create a playlist from user's favorite songs
function playlistFavSongs() {
  const xhttp = new XMLHttpRequest();
  const button = document.getElementById("plfavsong-button")
  button.innerHTML = "Working...";
  button.disabled = "true";

  xhttp.onload = function() {
    if (this.status == 200) {
      button.innerHTML = "Created Playlist";
      button.style.backgroundColor = "#138238";
      button.style.color = "#ffffff";
    }
  }
  xhttp.open("POST", "playlistFavSongs", true)
  xhttp.send()
}