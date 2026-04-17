---
read_when:
    - Quieres ejecutar el Gateway en un servidor Linux o un VPS en la nube
    - Necesitas una guía rápida de las opciones de alojamiento
    - Quieres ajustes generales de servidor Linux para OpenClaw
sidebarTitle: Linux Server
summary: Ejecuta OpenClaw en un servidor Linux o un VPS en la nube — selector de proveedor, arquitectura y ajuste fino
title: Servidor Linux
x-i18n:
    generated_at: "2026-04-14T02:08:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: e623f4c770132e01628d66bfb8cd273bbef6dad633b812496c90da5e3e0f1383
    source_path: vps.md
    workflow: 15
---

# Servidor Linux

Ejecuta el Gateway de OpenClaw en cualquier servidor Linux o VPS en la nube. Esta página te ayuda a elegir un proveedor, explica cómo funcionan los despliegues en la nube y cubre ajustes generales de Linux que se aplican en cualquier entorno.

## Elige un proveedor

<CardGroup cols={2}>
  <Card title="Railway" href="/es/install/railway">Configuración con un clic en el navegador</Card>
  <Card title="Northflank" href="/es/install/northflank">Configuración con un clic en el navegador</Card>
  <Card title="DigitalOcean" href="/es/install/digitalocean">VPS de pago sencillo</Card>
  <Card title="Oracle Cloud" href="/es/install/oracle">Nivel ARM Always Free</Card>
  <Card title="Fly.io" href="/es/install/fly">Fly Machines</Card>
  <Card title="Hetzner" href="/es/install/hetzner">Docker en VPS de Hetzner</Card>
  <Card title="Hostinger" href="/es/install/hostinger">VPS con configuración con un clic</Card>
  <Card title="GCP" href="/es/install/gcp">Compute Engine</Card>
  <Card title="Azure" href="/es/install/azure">VM Linux</Card>
  <Card title="exe.dev" href="/es/install/exe-dev">VM con proxy HTTPS</Card>
  <Card title="Raspberry Pi" href="/es/install/raspberry-pi">Alojamiento propio ARM</Card>
</CardGroup>

**AWS (EC2 / Lightsail / nivel gratuito)** también funciona bien.
Hay disponible un video explicativo de la comunidad en
[x.com/techfrenAJ/status/2014934471095812547](https://x.com/techfrenAJ/status/2014934471095812547)
(recurso de la comunidad; puede dejar de estar disponible).

## Cómo funcionan las configuraciones en la nube

- El **Gateway se ejecuta en el VPS** y mantiene el estado + espacio de trabajo.
- Te conectas desde tu laptop o teléfono mediante la **Control UI** o **Tailscale/SSH**.
- Trata el VPS como la fuente de verdad y haz **copias de seguridad** del estado + espacio de trabajo con regularidad.
- Valor predeterminado seguro: mantén el Gateway en loopback y accede a él mediante un túnel SSH o Tailscale Serve.
  Si lo enlazas a `lan` o `tailnet`, exige `gateway.auth.token` o `gateway.auth.password`.

Páginas relacionadas: [Acceso remoto al Gateway](/es/gateway/remote), [Centro de plataformas](/es/platforms).

## Agente compartido de empresa en un VPS

Ejecutar un solo agente para un equipo es una configuración válida cuando todos los usuarios están dentro del mismo límite de confianza y el agente es solo para uso empresarial.

- Mantenlo en un entorno de ejecución dedicado (VPS/VM/contenedor + usuario/cuentas de SO dedicados).
- No inicies sesión en ese entorno con cuentas personales de Apple/Google ni con perfiles personales de navegador/gestor de contraseñas.
- Si los usuarios son adversariales entre sí, sepáralos por gateway/host/usuario de SO.

Detalles del modelo de seguridad: [Seguridad](/es/gateway/security).

## Uso de nodes con un VPS

Puedes mantener el Gateway en la nube y emparejar **nodes** en tus dispositivos locales
(Mac/iOS/Android/headless). Los nodes proporcionan capacidades locales de pantalla/cámara/canvas y `system.run`
mientras el Gateway permanece en la nube.

Documentación: [Nodes](/es/nodes), [CLI de Nodes](/cli/nodes).

## Ajuste de inicio para VM pequeñas y hosts ARM

Si los comandos de la CLI se sienten lentos en VM de baja potencia (o hosts ARM), habilita la caché de compilación de módulos de Node:

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

- `NODE_COMPILE_CACHE` mejora los tiempos de inicio de comandos repetidos.
- `OPENCLAW_NO_RESPAWN=1` evita sobrecarga adicional de inicio por una ruta de autorreinicio.
- La primera ejecución del comando calienta la caché; las ejecuciones posteriores son más rápidas.
- Para detalles específicos de Raspberry Pi, consulta [Raspberry Pi](/es/install/raspberry-pi).

### Lista de verificación de ajuste de `systemd` (opcional)

Para hosts VM que usan `systemd`, considera lo siguiente:

- Agrega variables de entorno del servicio para una ruta de inicio estable:
  - `OPENCLAW_NO_RESPAWN=1`
  - `NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache`
- Mantén explícito el comportamiento de reinicio:
  - `Restart=always`
  - `RestartSec=2`
  - `TimeoutStartSec=90`
- Prefiere discos con SSD para las rutas de estado/caché para reducir las penalizaciones de arranque en frío por E/S aleatoria.

Para la ruta estándar `openclaw onboard --install-daemon`, edita la unidad de usuario:

```bash
systemctl --user edit openclaw-gateway.service
```

```ini
[Service]
Environment=OPENCLAW_NO_RESPAWN=1
Environment=NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
Restart=always
RestartSec=2
TimeoutStartSec=90
```

Si instalaste deliberadamente una unidad del sistema en su lugar, edita
`openclaw-gateway.service` mediante `sudo systemctl edit openclaw-gateway.service`.

Cómo ayudan las políticas `Restart=` a la recuperación automatizada:
[systemd puede automatizar la recuperación de servicios](https://www.redhat.com/en/blog/systemd-automate-recovery).
