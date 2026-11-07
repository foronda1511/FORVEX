const formulario = document.getElementById("form-login");

if (formulario) {
    formulario.addEventListener("submit", async function(evento) {
        evento.preventDefault();

        const correo = formulario.querySelector('input[type="email"]').value;
        const password = formulario.querySelector('input[type="password"]').value;

        try {
            const respuesta = await fetch("/api/admin/login", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ correo, password })
            });

            const datos = await respuesta.json();

            if (respuesta.ok) {
                alert("¡Bienvenido a FORVEX!");
                window.location.href = "/admin";
            } else {
                alert(datos.error);
            }

        } catch (error) {
            alert("Error al conectar con el servidor.");
        }
    });
}

const formularioTorneo = document.getElementById("form-torneo");

if (formularioTorneo) {
    formularioTorneo.addEventListener("submit", async function(evento) {
        evento.preventDefault();

        const torneo = {
            nombre: document.getElementById("nombre").value,
            juego: document.getElementById("juego").value,
            cupos: document.getElementById("cupos").value,
            premios: document.getElementById("premios").value,
            fecha: document.getElementById("fecha").value,
            reglas: document.getElementById("reglas").value,
            sala_id: document.getElementById("sala_id").value,
            sala_password: document.getElementById("sala_password").value
        };

        const respuesta = await fetch("/api/admin/torneos", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(torneo)
        });

        const datos = await respuesta.json();

        if (respuesta.ok) {
            alert("¡Torneo creado correctamente!");
            formularioTorneo.reset();
            cargarTorneos();
        } else {
            alert(datos.error);
        }
    });
}

async function cargarTorneos() {

    const lista = document.getElementById("lista-torneos");

    if (!lista) return;

    const respuesta = await fetch("/api/admin/torneos");

    if (!respuesta.ok) {
        lista.innerHTML = "<p>No se pudieron cargar los torneos.</p>";
        return;
    }

    const torneos = await respuesta.json();

    if (torneos.length === 0) {
        lista.innerHTML = "<p>Aún no hay torneos creados.</p>";
        return;
    }

    lista.innerHTML = "";

    torneos.forEach(torneo => {

        const tarjeta = document.createElement("div");

        tarjeta.innerHTML = `
        <h3>${torneo.nombre}</h3>
        <p>Juego: ${torneo.juego}</p>
        <p>Cupos: ${torneo.cupos}</p>
        <p>Premios: ${torneo.premios}</p>
        <p>Fecha: ${torneo.fecha}</p>
        <p>Estado: ${torneo.estado}</p>
        <button class="btn-eliminar" data-id="${torneo.id}">
            ELIMINAR TORNEO
        </button>

        ${
            torneo.estado === "borrador"
            ? `<button class="btn-publicar" data-id="${torneo.id}">
                PUBLICAR TORNEO
            </button>`
            : `<p>Este torneo ya está publicado.</p>`
        }
    `;

        lista.appendChild(tarjeta);

        const botonPublicar = tarjeta.querySelector(".btn-publicar");

if (botonPublicar) {
    botonPublicar.addEventListener("click", async function() {
        const id = this.dataset.id;

        const respuesta = await fetch(`/api/admin/torneos/${id}/publicar`, {
            method: "POST"
        });

        const datos = await respuesta.json();

        if (respuesta.ok) {
            alert("¡Torneo publicado correctamente!");
            cargarTorneos();
        } else {
            alert(datos.error);
        }
    });
}

const botonEliminar = tarjeta.querySelector(".btn-eliminar");

botonEliminar.addEventListener("click", async function() {

    const confirmar = confirm(
        "¿Estás seguro de eliminar este torneo? También se eliminarán sus inscripciones. Esta acción no se puede deshacer."
    );

    if (!confirmar) return;

    const id = this.dataset.id;

    const respuesta = await fetch(`/api/admin/torneos/${id}/eliminar`, {
        method: "DELETE"
    });

    const datos = await respuesta.json();

    if (respuesta.ok) {
        alert("Torneo eliminado correctamente.");
        cargarTorneos();
    } else {
        alert(datos.error);
    }
});

    });
}



cargarTorneos();

async function cargarTorneosPublicos() {
    const lista = document.getElementById("lista-torneos-publicos");

    if (!lista) return;

    try {
        const respuesta = await fetch("/api/torneos/publicados");
        const torneos = await respuesta.json();

        if (torneos.length === 0) {
            lista.innerHTML = "<p>No hay torneos publicados todavía.</p>";
            return;
        }

        lista.innerHTML = "";

        torneos.forEach(async torneo => {

            const respuestaInscripcion = await fetch(
                `/api/torneos/${torneo.id}/mi-inscripcion`
            );

            const datosInscripcion = await respuestaInscripcion.json();
            const tarjeta = document.createElement("div");
            tarjeta.className = "tarjeta-torneo";

            tarjeta.innerHTML = `
            <div class="torneo-etiqueta">TORNEO FORVEX</div>

            <h3>${torneo.nombre}</h3>

            <div class="torneo-datos">
                <p><strong>JUEGO</strong><br>${torneo.juego}</p>
                <p><strong>PREMIOS</strong><br>${torneo.premios}</p>
                <p><strong>CUPOS</strong><br>${torneo.cupos}</p>
                <p><strong>FECHA</strong><br>${torneo.fecha}</p>
                ${
                datosInscripcion.inscrito
                ? `<button class="btn-entrar-sala" data-id="${torneo.id}">
                    ENTRAR A LA SALA
                </button>`
                : `<button class="btn-inscribirse" data-id="${torneo.id}">
                    INSCRIBIRME
                </button>`
            }
            </div>
        `;

            lista.appendChild(tarjeta);
            const botonInscribirse = tarjeta.querySelector(".btn-inscribirse");

            if (botonInscribirse) {
                botonInscribirse.addEventListener("click", function() {
                    inscribirEnTorneo(torneo.id);
                });
            }
        const botonSala = tarjeta.querySelector(".btn-entrar-sala");

        if (botonSala) {
            botonSala.addEventListener("click", function() {
                entrarSala(torneo.id);
            });
        }
        });

    } catch (error) {
        lista.innerHTML = "<p>Error al cargar los torneos.</p>";
    }
}

cargarTorneosPublicos();

async function inscribirEnTorneo(torneoId) {
    try {
        const respuesta = await fetch("/api/inscripciones", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                torneo_id: torneoId
            })
        });

        const datos = await respuesta.json();

        if (respuesta.status === 401) {
            alert("Debes iniciar sesión para inscribirte.");
            window.location.href = "/login";
            return;
        }

        if (!respuesta.ok) {
            alert(datos.error);
            return;
        }

        alert(datos.mensaje);

    } catch (error) {
        alert("No se pudo conectar con el servidor.");
    }
}

// COMPROBAR SESIÓN DEL JUGADOR

async function comprobarSesionJugador() {

    const menu = document.getElementById("menu-principal");
    const estadoUsuario = document.getElementById("estado-usuario");

    if (!menu || !estadoUsuario) return;

    try {
        const respuesta = await fetch("/api/me");

        if (!respuesta.ok) {
            return;
        }

        const usuario = await respuesta.json();

        // Cambiar menú para el jugador conectado
        menu.innerHTML = "";

        estadoUsuario.innerHTML = `
        <div class="usuario-bienvenida">
            <span>Bienvenido, ${usuario.nombre}</span>
        </div>

        <div class="usuario-acciones">
            <a href="/">INICIO</a>
            <button id="btn-cerrar-sesion">CERRAR SESIÓN</button>
        </div>
    `;

        // Cerrar sesión
        document.getElementById("btn-cerrar-sesion")
            .addEventListener("click", async function() {

                const respuesta = await fetch("/api/logout", {
                    method: "POST"
                });

                if (respuesta.ok) {
                    window.location.reload();
                }

            });

    } catch (error) {
        console.error("Error al comprobar la sesión:", error);
    }
}

comprobarSesionJugador();

const botonCerrarAdmin = document.getElementById("cerrar-sesion");

if (botonCerrarAdmin) {
    botonCerrarAdmin.addEventListener("click", async function() {
        try {
            const respuesta = await fetch("/api/admin/logout", {
                method: "POST"
            });

            if (respuesta.ok) {
                window.location.href = "/admin/login";
            } else {
                alert("No se pudo cerrar la sesión.");
            }
        } catch (error) {
            alert("Error al conectar con el servidor.");
        }
    });
}


async function entrarSala(torneoId) {

    // Comprobar que el jugador tiene acceso
    try {
        const respuesta = await fetch(`/api/torneos/${torneoId}/sala`);

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            alert(datos.error);
            return;
        }

        // Abrir la página de la sala
        window.location.href = `/sala.html?id=${torneoId}`;

    } catch (error) {
        alert("Error al intentar entrar a la sala.");
    }
}
