# Guía para Colaboradores

## Flujo de Trabajo

### Paso 1: Sincronizar con la rama principal

Antes de empezar cualquier tarea, asegúrate de que tu copia local de la rama `main` esté actualizada. Abre tu terminal y asegurate de estar en la carpeta raíz del proyecto.

```bash
git checkout main
git pull origin main
```

### Paso 2: Crear una rama para tu tarea

Nunca trabajes directamente en la rama `main`. Crea una nueva rama para cada funcionalidad o corrección que vayas a realizar.

1.  Crea y cambia a tu nueva rama.

    ```bash
    git checkout -b feat/nombre-de-la-tarea
    ```

    *Ejemplo: `git checkout -b fix/problema-con-botones`*

### Paso 3: Trabajar y guardar tus cambios

Una vez que termines de programar, guarda tus cambios en la rama local.

1.  Agrega los archivos modificados.

    ```bash
    git add .
    ```

2.  Crea un "commit" con un mensaje claro y conciso.

    ```bash
    git commit -m "feat: [Descripción breve de lo que hiciste]"
    ```

### Paso 4: Subir la rama a GitHub y crear una Pull Request (PR)

Sube tu rama al repositorio remoto y solicita que se revise tu código.

1.  Sube tu rama.

    ```bash
    git push -u origin feat/nombre-de-la-tarea
    ```

2.  Ve a GitHub, encuentra la rama que acabas de subir y crea una **Pull Request** (`PR`).

### Paso 5: Revisión y Fusión

Espera a que un compañero revise tu código.

1.  Una vez que la PR tenga la aprobación requerida (al menos 1), fúsionala (`merge`) a la rama `main`.

---

### **Recordatorios Importantes**

* La rama `main` está protegida. Todos los cambios deben pasar por una **Pull Request** y ser aprobados por al menos una persona.
* Mantén tus mensajes de `commit` claros y descriptivos.
* Cuando termines de fusionar tu PR, puedes eliminar la rama de trabajo para mantener el repositorio limpio.
