from database import crear_tablas, crear_administrador
from getpass import getpass

crear_tablas()

print("\n===== FORVEX ADMINISTRADOR =====")

correo = input("Correo del administrador: ")
password = getpass("Crea tu contraseña: ")
confirmar = getpass("Confirma tu contraseña: ")

if password != confirmar:
    print("Las contraseñas no coinciden.")

elif len(password) < 8:
    print("La contraseña debe tener mínimo 8 caracteres.")

else:
    resultado = crear_administrador(correo, password)

    if resultado:
        print("Administrador creado correctamente.")

    else:
        print("Ese correo ya está registrado.")