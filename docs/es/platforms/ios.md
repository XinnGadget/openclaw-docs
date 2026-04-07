---
read_when:
    - Emparejar o volver a conectar el nodo de iOS
    - Ejecutar la app de iOS desde el código fuente
    - Depurar el descubrimiento del gateway o los comandos de canvas
summary: 'App de iOS para nodos: conectarse al Gateway, emparejamiento, canvas y solución de problemas'
title: App de iOS
x-i18n:
    generated_at: "2026-04-07T05:03:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: f3e0a6e33e72d4c9f1f17ef70a1b67bae9ebe4a2dca16677ea6b28d0ddac1b4e
    source_path: platforms/ios.md
    workflow: 15
---

# App de iOS (Nodo)

Disponibilidad: vista previa interna. La app de iOS todavía no se distribuye públicamente.

## Qué hace

- Se conecta a un Gateway mediante WebSocket (LAN o tailnet).
- Expone capacidades del nodo: Canvas, instantánea de pantalla, captura de cámara, ubicación, modo hablar, activación por voz.
- Recibe comandos `node.invoke` e informa eventos de estado del nodo.

## Requisitos

- Gateway en ejecución en otro dispositivo (macOS, Linux o Windows mediante WSL2).
- Ruta de red:
  - La misma LAN mediante Bonjour, **o**
  - Tailnet mediante DNS-SD unicast (dominio de ejemplo: `openclaw.internal.`), **o**
  - Host/puerto manual (respaldo).

## Inicio rápido (emparejar + conectar)

1. Inicia el Gateway:

```bash
openclaw gateway --port 18789
```

2. En la app de iOS, abre Ajustes y elige un gateway detectado (o habilita Host manual e introduce host/puerto).

3. Aprueba la solicitud de emparejamiento en el host del gateway:

```bash
openclaw devices list
openclaw devices approve <requestId>
```

Si la app reintenta el emparejamiento con detalles de autenticación modificados (rol/scopes/clave pública),
la solicitud pendiente anterior se reemplaza y se crea un nuevo `requestId`.
Ejecuta `openclaw devices list` de nuevo antes de aprobar.

4. Verifica la conexión:

```bash
openclaw nodes status
openclaw gateway call node.list --params "{}"
```

## Push con relay para compilaciones oficiales

Las compilaciones oficiales distribuidas de iOS usan el relay push externo en lugar de publicar el token bruto de APNs
en el gateway.

Requisito del lado del gateway:

```json5
{
  gateway: {
    push: {
      apns: {
        relay: {
          baseUrl: "https://relay.example.com",
        },
      },
    },
  },
}
```

Cómo funciona el flujo:

- La app de iOS se registra en el relay usando App Attest y el recibo de la app.
- El relay devuelve un identificador opaco del relay junto con una concesión de envío con alcance de registro.
- La app de iOS obtiene la identidad del gateway emparejado y la incluye en el registro del relay, de modo que el registro respaldado por relay quede delegado a ese gateway específico.
- La app reenvía ese registro respaldado por relay al gateway emparejado con `push.apns.register`.
- El gateway usa ese identificador de relay almacenado para `push.test`, activaciones en segundo plano y avisos de activación.
- La URL base del relay del gateway debe coincidir con la URL del relay integrada en la compilación oficial/TestFlight de iOS.
- Si la app se conecta después a otro gateway o a una compilación con una URL base de relay distinta, actualiza el registro del relay en lugar de reutilizar el enlace anterior.

Lo que el gateway **no** necesita para esta ruta:

- Ningún token de relay para toda la implementación.
- Ninguna clave directa de APNs para envíos oficiales/TestFlight respaldados por relay.

Flujo esperado para el operador:

1. Instala la compilación oficial/TestFlight de iOS.
2. Establece `gateway.push.apns.relay.baseUrl` en el gateway.
3. Empareja la app con el gateway y deja que termine de conectarse.
4. La app publica `push.apns.register` automáticamente después de tener un token de APNs, de que la sesión del operador esté conectada y de que el registro en el relay se complete correctamente.
5. Después de eso, `push.test`, las activaciones de reconexión y los avisos de activación pueden usar el registro almacenado respaldado por relay.

Nota de compatibilidad:

- `OPENCLAW_APNS_RELAY_BASE_URL` sigue funcionando como anulación temporal de entorno para el gateway.

## Flujo de autenticación y confianza

El relay existe para aplicar dos restricciones que APNs directo en el gateway no puede proporcionar para
las compilaciones oficiales de iOS:

- Solo las compilaciones auténticas de OpenClaw para iOS distribuidas a través de Apple pueden usar el relay alojado.
- Un gateway solo puede enviar pushes respaldados por relay a dispositivos iOS que se hayan emparejado con ese gateway
  específico.

Salto por salto:

1. `iOS app -> gateway`
   - La app primero se empareja con el gateway mediante el flujo normal de autenticación de Gateway.
   - Eso proporciona a la app una sesión de nodo autenticada y una sesión de operador autenticada.
   - La sesión de operador se usa para llamar a `gateway.identity.get`.

2. `iOS app -> relay`
   - La app llama a los endpoints de registro del relay mediante HTTPS.
   - El registro incluye prueba de App Attest junto con el recibo de la app.
   - El relay valida el bundle ID, la prueba de App Attest y el recibo de Apple, y exige la
     ruta de distribución oficial/de producción.
   - Esto es lo que impide que las compilaciones locales de Xcode/desarrollo usen el relay alojado. Una compilación local puede estar
     firmada, pero no cumple la prueba oficial de distribución de Apple que espera el relay.

3. `gateway identity delegation`
   - Antes del registro en el relay, la app obtiene la identidad del gateway emparejado desde
     `gateway.identity.get`.
   - La app incluye esa identidad del gateway en la carga útil del registro del relay.
   - El relay devuelve un identificador de relay y una concesión de envío con alcance de registro que quedan delegados a
     esa identidad del gateway.

4. `gateway -> relay`
   - El gateway almacena el identificador de relay y la concesión de envío de `push.apns.register`.
   - En `push.test`, las activaciones de reconexión y los avisos de activación, el gateway firma la solicitud de envío con su
     propia identidad de dispositivo.
   - El relay verifica tanto la concesión de envío almacenada como la firma del gateway frente a la identidad
     del gateway delegada desde el registro.
   - Otro gateway no puede reutilizar ese registro almacenado, incluso si de algún modo obtiene el identificador.

5. `relay -> APNs`
   - El relay es quien posee las credenciales de producción de APNs y el token bruto de APNs para la compilación oficial.
   - El gateway nunca almacena el token bruto de APNs para compilaciones oficiales respaldadas por relay.
   - El relay envía el push final a APNs en nombre del gateway emparejado.

Por qué se creó este diseño:

- Para mantener las credenciales de producción de APNs fuera de los gateways de usuario.
- Para evitar almacenar tokens brutos de APNs de compilaciones oficiales en el gateway.
- Para permitir el uso del relay alojado solo para compilaciones oficiales/TestFlight de OpenClaw.
- Para impedir que un gateway envíe pushes de activación a dispositivos iOS de otro gateway.

Las compilaciones locales/manuales siguen usando APNs directo. Si estás probando esas compilaciones sin el relay, el
gateway todavía necesita credenciales directas de APNs:

```bash
export OPENCLAW_APNS_TEAM_ID="TEAMID"
export OPENCLAW_APNS_KEY_ID="KEYID"
export OPENCLAW_APNS_PRIVATE_KEY_P8="$(cat /path/to/AuthKey_KEYID.p8)"
```

Estas son variables de entorno de tiempo de ejecución del host del gateway, no ajustes de Fastlane. `apps/ios/fastlane/.env` solo almacena
autenticación de App Store Connect / TestFlight como `ASC_KEY_ID` y `ASC_ISSUER_ID`; no configura
la entrega directa de APNs para compilaciones locales de iOS.

Almacenamiento recomendado en el host del gateway:

```bash
mkdir -p ~/.openclaw/credentials/apns
chmod 700 ~/.openclaw/credentials/apns
mv /path/to/AuthKey_KEYID.p8 ~/.openclaw/credentials/apns/AuthKey_KEYID.p8
chmod 600 ~/.openclaw/credentials/apns/AuthKey_KEYID.p8
export OPENCLAW_APNS_PRIVATE_KEY_PATH="$HOME/.openclaw/credentials/apns/AuthKey_KEYID.p8"
```

No confirmes el archivo `.p8` ni lo coloques dentro del checkout del repositorio.

## Rutas de descubrimiento

### Bonjour (LAN)

La app de iOS explora `_openclaw-gw._tcp` en `local.` y, cuando está configurado, el mismo
dominio de descubrimiento DNS-SD de área amplia. Los gateways de la misma LAN aparecen automáticamente desde `local.`;
el descubrimiento entre redes puede usar el dominio de área amplia configurado sin cambiar el tipo de beacon.

### Tailnet (entre redes)

Si mDNS está bloqueado, usa una zona DNS-SD unicast (elige un dominio; ejemplo:
`openclaw.internal.`) y DNS dividido de Tailscale.
Consulta [Bonjour](/es/gateway/bonjour) para ver el ejemplo de CoreDNS.

### Host/puerto manual

En Ajustes, habilita **Host manual** e introduce el host + puerto del gateway (predeterminado `18789`).

## Canvas + A2UI

El nodo iOS renderiza un canvas WKWebView. Usa `node.invoke` para controlarlo:

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.navigate --params '{"url":"http://<gateway-host>:18789/__openclaw__/canvas/"}'
```

Notas:

- El host canvas del Gateway sirve `/__openclaw__/canvas/` y `/__openclaw__/a2ui/`.
- Se sirve desde el servidor HTTP del Gateway (el mismo puerto que `gateway.port`, predeterminado `18789`).
- El nodo iOS navega automáticamente a A2UI al conectarse cuando se anuncia una URL de host canvas.
- Vuelve al andamiaje integrado con `canvas.navigate` y `{"url":""}`.

### Evaluación / instantánea de canvas

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.eval --params '{"javaScript":"(() => { const {ctx} = window.__openclaw; ctx.clearRect(0,0,innerWidth,innerHeight); ctx.lineWidth=6; ctx.strokeStyle=\"#ff2d55\"; ctx.beginPath(); ctx.moveTo(40,40); ctx.lineTo(innerWidth-40, innerHeight-40); ctx.stroke(); return \"ok\"; })()"}'
```

```bash
openclaw nodes invoke --node "iOS Node" --command canvas.snapshot --params '{"maxWidth":900,"format":"jpeg"}'
```

## Activación por voz + modo hablar

- La activación por voz y el modo hablar están disponibles en Ajustes.
- iOS puede suspender el audio en segundo plano; trata las funciones de voz como de mejor esfuerzo cuando la app no está activa.

## Errores comunes

- `NODE_BACKGROUND_UNAVAILABLE`: lleva la app de iOS al primer plano (los comandos de canvas/cámara/pantalla lo requieren).
- `A2UI_HOST_NOT_CONFIGURED`: el Gateway no anunció una URL de host canvas; revisa `canvasHost` en [Configuración de Gateway](/es/gateway/configuration).
- El aviso de emparejamiento nunca aparece: ejecuta `openclaw devices list` y aprueba manualmente.
- La reconexión falla después de reinstalar: se borró el token de emparejamiento del llavero; vuelve a emparejar el nodo.

## Documentación relacionada

- [Emparejamiento](/es/channels/pairing)
- [Descubrimiento](/es/gateway/discovery)
- [Bonjour](/es/gateway/bonjour)
