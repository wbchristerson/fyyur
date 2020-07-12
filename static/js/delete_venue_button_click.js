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
venueDeleteButton.onclick = onVenueDelete;