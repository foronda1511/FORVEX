const formularioRegistro = document.getElementById("form-registro");
const mensajeRegistro = document.getElementById("mensaje-registro");

formularioRegistro.addEventListener("submit", async function(evento) {
    evento.preventDefault();

    const nombre = document.getElementById("nombre").value.trim();
    const correo = document.getElementById("correo").value.trim();
    const password = document.getElementById("password").value;

    mensajeRegistro.textContent = "Creando cuenta...";
    mensajeRegistro.style.color = "#ffffff";

    try {
        const respuesta = await fetch("/api/registro", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                nombre: nombre,
                correo: correo,
                password: password
            })
        });

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            mensajeRegistro.textContent = datos.error;
            mensajeRegistro.style.color = "#ff4545";
            return;
        }

        mensajeRegistro.textContent = datos.mensaje;
        mensajeRegistro.style.color = "#00ff88";

        formularioRegistro.reset();

    } catch (error) {
        mensajeRegistro.textContent = "No se pudo conectar con el servidor.";
        mensajeRegistro.style.color = "#ff4545";
    }
});