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
        xhr.send(JSON.stringify({ address  : walletAddress, token: token }));
    }
}

document.addEventListener('DOMContentLoaded', () => {

    const optionMenu = document.querySelector(".select-menu"),
            selectBtn = optionMenu.querySelector(".select-btn"),
            options = optionMenu.querySelectorAll(".option"),
            sBtn_text = optionMenu.querySelector(".sBtn-text");

    const optionMenu2 = document.querySelector(".select-menu-2"),
            selectBtn2 = optionMenu2.querySelector(".select-btn"),
            options2 = optionMenu2.querySelectorAll(".option"),
            sBtn_text2 = optionMenu2.querySelector(".sBtn-text");

    selectBtn.addEventListener("click", () => {
        optionMenu.classList.toggle('active');
        if (optionMenu2.classList.contains("active")) {
            optionMenu2.classList.remove("active");
        }
    });

    selectBtn2.addEventListener("click", () => {
        optionMenu2.classList.toggle('active');
        if (optionMenu.classList.contains("active")) {
            optionMenu.classList.remove("active");
        }
    });

    //Need to nerd out a bit here, what is supposed to be in the () after "click"
    document.addEventListener("click", (event) => {
        const targetElement = event.target;

        if (!optionMenu.contains(targetElement)) {
            optionMenu.classList.remove("active");
        }
        if (!optionMenu2.contains(targetElement)) {
            optionMenu2.classList.remove("active");
        }
    })
  
    options.forEach(option => {
        option.addEventListener("click", () => {
            let selectedOption = option.querySelector(".option-text").innerText;
            sBtn_text.innerText = selectedOption;
            console.log(selectedOption);
            document.getElementById('selectedToken').value = selectedOption;
            optionMenu.classList.remove('active');
        });
    });
    
    
    options2.forEach(option => {
        option.addEventListener("click", () => {
            let selectedOption = option.querySelector(".option-text").innerText;
            sBtn_text2.innerText = selectedOption;
            console.log(selectedOption);
            document.getElementById('selectedNetwork').value = selectedOption;
            optionMenu2.classList.remove('active')
        })
    })
});