
let showMoreButton = document.getElementById("show-more");
let allRatings = {{ ratings|json_script:"ratings" }};
let displayedRatings = 4; // Number of ratings displayed initially

function showMore() {
    let ratingList = document.getElementById("rating-list");
    
    // Loop through the remaining ratings and append them to the list
    for (let i = displayedRatings; i < Math.min(displayedRatings + 4, allRatings.length); i++) {
        let li = document.createElement("li");
        li.innerHTML = `<strong>${allRatings[i].customer.username}:</strong> ${allRatings[i].content} <em>${allRatings[i].rating} Stars</em> <em>${allRatings[i].date_added}</em>`;
        ratingList.appendChild(li);
    }
    
    // Update displayed ratings count
    displayedRatings += 4;

    // Hide the button if all ratings are displayed
    if (displayedRatings >= allRatings.length) {
        showMoreButton.style.display = "none";
    }
}

