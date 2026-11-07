
// Obtener el ID del torneo desde la dirección
const parametros = new URLSearchParams(window.location.search);
const torneoId = parametros.get("id");

// Cargar los datos de la sala
async function cargarDatosSala() {

    const mensaje = document.getElementById("mensaje-sala");

    if (!torneoId) {
        mensaje.textContent = "No se especificó un torneo.";
        return;
    }

    try {
        const respuesta = await fetch(`/api/torneos/${torneoId}/sala`);
        const datos = await respuesta.json();

        if (!respuesta.ok) {
            mensaje.textContent = datos.error || "No tienes acceso a esta sala.";
            return;
        }

        document.getElementById("sala-id").textContent =
            datos.sala_id || "No configurado";

        document.getElementById("sala-password").textContent =
            datos.sala_password || "No configurada";

    } catch (error) {
        mensaje.textContent = "No se pudieron cargar los datos de la sala.";
    }
}

// Copiar información
function copiarTexto(elementoId) {

    const texto = document.getElementById(elementoId).textContent;

    if (!texto || texto.includes("Cargando") || texto.includes("No configurado")) {
        return;
    }

    navigator.clipboard.writeText(texto).then(() => {
        document.getElementById("mensaje-sala").textContent =
            "¡Copiado correctamente!";
    }).catch(() => {
        document.getElementById("mensaje-sala").textContent =
            "No se pudo copiar el texto.";
    });
}

document.getElementById("copiar-id").addEventListener("click", function() {
    copiarTexto("sala-id");
});

document.getElementById("copiar-password").addEventListener("click", function() {
    copiarTexto("sala-password");
});

cargarDatosSala();
