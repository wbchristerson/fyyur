const onVenueDelete = function(e) {
    e.preventDefault();
    const venueId = e.target.dataset.id;
    fetch('/venues/' + venueId, {
        method: 'DELETE',
    })
    .then(() => {
        window.location.href="/";
    })
    .catch((error) => error);
};

const venueDeleteButton = document.getElementById("delete-button");
if (venueDeleteButton) {
    venueDeleteButton.onclick = onVenueDelete;
}


const onArtistEditClick = function(e) {
    e.preventDefault();
    const artistId = e.target.dataset.id;
    fetch('/artists/' + artistId + '/edit', {
        method: 'GET',
    })
    .then((data) => {
        window.location.href = data.url;
    })
    .catch((error) => error);
};

const artistEditButton = document.getElementById("edit-artist");
if (artistEditButton) {
    artistEditButton.onclick = onArtistEditClick;
}


const onVenueEditClick = function(e) {
    e.preventDefault();
    const venueId = e.target.dataset.id;
    fetch('/venues/' + venueId + '/edit', {
        method: 'GET',
    })
    .then((data) => {
        window.location.href = data.url;
    })
    .catch((error) => error);
};

const venueEditButton = document.getElementById("edit-venue");
if (venueEditButton) {
    venueEditButton.onclick = onVenueEditClick;
}