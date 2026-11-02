# Grepolis Bot

Bot HTTP Python para construcciones y recogida de recursos de aldeas. Funciona en Windows y Linux sin Selenium ni navegador durante la ejecucion.

## Windows

```powershell
.\venv\Scripts\Activate.ps1
python -m pytest -q
python -m src.main --once --dry-run
```

## Linux

```bash
source venv/bin/activate
python -m pytest -q
python -m src.main --once --dry-run
```

Copia `.env.example` a `.env`. Mantiene `DRY_RUN=true` por defecto. No desactives `DRY_RUN` hasta validar logs, estado JSON y una prueba controlada. Las credenciales, cookies, CSRF y capturas de Network nunca deben versionarse.

El estado se guarda en `data/state.json`. El proceso mantiene ciclos independientes: construcciones y aldeas pueden fallar por separado.

El modo normal ejecuta una comprobacion, programa el siguiente vencimiento en `data/state.json` y termina. No deja un proceso residente.

Instala el primer disparador del sistema:

```powershell
python -m src.main --install-scheduler
```

Cada ejecución crea el siguiente disparador exacto. Las aldeas usan 300 segundos; la construcción usa su finalización del servidor más el margen configurado. Windows usa Task Scheduler; Linux usa `at`.

Para quitarlo:

```powershell
python -m src.main --uninstall-scheduler
```

Conserva `--dry-run` durante las pruebas.

Para diagnostico detallado:

```powershell
python -m src.main --logs
```

Los logs muestran login, peticiones, cola, decision de edificio y motivo por el que cada aldea espera. No muestran cookies ni CSRF.
`data/scheduler.log` se reinicia al primer arranque de cada dia y conserva las ejecuciones del mismo dia.

Especificacion: `specs/003-grepolis-autonomous-bot/`.
