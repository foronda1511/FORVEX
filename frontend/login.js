const formularioLogin = document.getElementById("form-login");
const mensajeLogin = document.getElementById("mensaje-login");

formularioLogin.addEventListener("submit", async function(evento) {
    evento.preventDefault();

    const correo = document.getElementById("correo").value.trim();
    const password = document.getElementById("password").value;

    mensajeLogin.textContent = "Verificando datos...";
    mensajeLogin.style.color = "#ffffff";

    try {
        const respuesta = await fetch("/api/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                correo: correo,
                password: password
            })
        });

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            mensajeLogin.textContent = datos.error;
            mensajeLogin.style.color = "#ff4545";
            return;
        }

        mensajeLogin.textContent = datos.mensaje;
        mensajeLogin.style.color = "#00ff88";

        window.location.href = "/";

    } catch (error) {
        mensajeLogin.textContent = "No se pudo conectar con el servidor.";
        mensajeLogin.style.color = "#ff4545";
    }
});