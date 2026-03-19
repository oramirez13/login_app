// ========================================
// CTF ORAMI - script.js
// ========================================


// ========================================
// FLAGS SEGÚN LA RUTA (CTF)
// ========================================

// obtener la ruta actual
const path = window.location.pathname;

// compatibilidad con entorno local (archivos .html)
if (path.includes("/blog")) {
    console.log("FLAG{blog_console}");
}

if (path.includes("/acerca")) {
    console.log("FLAG{acerca_console}");
}

if (path.includes("/contacto")) {
    console.log("FLAG{contacto_console}");
}


// ========================================
// CUANDO EL DOCUMENTO ESTÉ LISTO
// ========================================
$(document).ready(function() {

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
                  .text("Acceso concedido 😈")
                  .css("color", "lightgreen");

                setTimeout(function() {
                    window.location.href = "/dashboard";
                }, 1000);
            },

            error: function() {
                $("#msg")
                  .text("Credenciales incorrectas 💀")
                  .css("color", "red");
            }
        });

    });

});