function deleteWallet(button) {
    var walletAddress = button.getAttribute("data-address");
    var token = button.getAttribute("data-token");

    if (confirm("Are you sure you want to delete this token?")) {
        // Send an AJAX request to delete the specific row
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "/delete-wallet", true);
        xhr.setRequestHeader("Content-Type", "application/json");
        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    // Reload the page after successful deletion
                    location.reload();
                } else {
                    // Handle the error case
                    console.error("Error deleting row:", xhr.responseText);
                }
            }
        };
        xhr.send(JSON.stringify({ address: walletAddress, token: token }));
    }
}