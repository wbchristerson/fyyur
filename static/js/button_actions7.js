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
        console.log("data.response: ", data.url);
        window.location.href = data.url;
    })
    .catch((error) => error);

    // fetch('/venues/' + venueId, {
    //     method: 'DELETE',
    // })
    //     .then(() => {
    //         window.location.href="/";
    //     })
    //     .catch((error) => error);
    // console.log(e);
};

const artistEditButton = document.getElementById("edit-artist");
if (artistEditButton) {
    artistEditButton.onclick = onArtistEditClick;
}