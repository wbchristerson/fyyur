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
    console.log("e: ", e);
};

const venueDeleteButton = document.qetElementById("delete-button");
venueDeleteButton.onclick = onVenueDelete;