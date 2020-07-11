console.log("Hello\n");
console.log("Hello\n");
console.log("Hello\n");
console.log("Hello\n");
console.log("Hello\n");
console.log("Hello\n");
console.log("Hello\n");
console.log("Hello\n");
console.log("Hello\n");
console.log("Hello\n");
console.log("Hello\n");

const onVenueDelete = function(e) {
    e.preventDefault();
    console.log("e.target.dataset.id: ", e.target.dataset.id);

    const venueId = e.target.dataset.id;
    fetch('/venues/' + venueId, {
        method: 'DELETE',
    })
        .then((data) => data)
        .catch((error) => error);
};

const venueDeleteButton = document.getElementById("delete-button");

console.log("\n");
console.log("\n");
console.log("venueDeleteButton: ", venueDeleteButton);

venueDeleteButton.onclick = onVenueDelete;