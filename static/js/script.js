// ========================================
// CTF ORAMI - script.js
// ========================================


// ========================================
// FLAGS BY ROUTE (CTF)
// ========================================

// get the current path
const path = window.location.pathname;

// compatibility with local environment (static .html files)
if (path.includes("/blog")) {
    console.log("FLAG{blog_console}");
}

if (path.includes("/about")) {
    console.log("FLAG{about_console}");
}

if (path.includes("/contact")) {
    console.log("FLAG{contact_console}");
}


// ========================================
// WHEN THE DOCUMENT IS READY
// ========================================
$(document).ready(function() {
    // character counter in the contact form
    $("#message").on("input", function() {
        $("#counter").text($(this).val().length);
    });

    $("#loginForm").submit(function(e) {
        e.preventDefault();

        let username = $("#username").val();
        let password = $("#password").val();

        $.ajax({
            url: "/login",
            method: "POST",
            contentType: "application/json",
            data: JSON.stringify({
                username: username,
                password: password
            }),

            success: function(response) {
                $("#msg")
                  .text("Access granted 😈")
                  .css("color", "lightgreen");

                setTimeout(function() {
                    window.location.href = "/dashboard";
                }, 1000);
            },

            error: function() {
                $("#msg")
                  .text("Wrong credentials 💀")
                  .css("color", "red");
            }
        });
    });
});