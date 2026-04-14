---
read_when:
    - Você quer executar o Gateway em um servidor Linux ou VPS em nuvem
    - Você precisa de um guia rápido dos guias de hospedagem
    - Você quer um ajuste fino genérico de servidor Linux para OpenClaw
sidebarTitle: Linux Server
summary: Execute o OpenClaw em um servidor Linux ou VPS em nuvem — seletor de provedor, arquitetura e ajuste fino
title: Servidor Linux
x-i18n:
    generated_at: "2026-04-14T02:08:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: e623f4c770132e01628d66bfb8cd273bbef6dad633b812496c90da5e3e0f1383
    source_path: vps.md
    workflow: 15
---

# Servidor Linux

Execute o Gateway do OpenClaw em qualquer servidor Linux ou VPS em nuvem. Esta página ajuda você
a escolher um provedor, explica como as implantações em nuvem funcionam e cobre o
ajuste fino genérico de Linux que se aplica em qualquer lugar.

## Escolha um provedor

<CardGroup cols={2}>
  <Card title="Railway" href="/pt-BR/install/railway">Configuração em um clique, no navegador</Card>
  <Card title="Northflank" href="/pt-BR/install/northflank">Configuração em um clique, no navegador</Card>
  <Card title="DigitalOcean" href="/pt-BR/install/digitalocean">VPS pago simples</Card>
  <Card title="Oracle Cloud" href="/pt-BR/install/oracle">Camada ARM Always Free</Card>
  <Card title="Fly.io" href="/pt-BR/install/fly">Fly Machines</Card>
  <Card title="Hetzner" href="/pt-BR/install/hetzner">Docker em VPS da Hetzner</Card>
  <Card title="Hostinger" href="/pt-BR/install/hostinger">VPS com configuração em um clique</Card>
  <Card title="GCP" href="/pt-BR/install/gcp">Compute Engine</Card>
  <Card title="Azure" href="/pt-BR/install/azure">VM Linux</Card>
  <Card title="exe.dev" href="/pt-BR/install/exe-dev">VM com proxy HTTPS</Card>
  <Card title="Raspberry Pi" href="/pt-BR/install/raspberry-pi">ARM self-hosted</Card>
</CardGroup>

**AWS (EC2 / Lightsail / camada gratuita)** também funciona muito bem.
Um vídeo explicativo da comunidade está disponível em
[x.com/techfrenAJ/status/2014934471095812547](https://x.com/techfrenAJ/status/2014934471095812547)
(recurso da comunidade -- pode ficar indisponível).

## Como as configurações em nuvem funcionam

- O **Gateway é executado na VPS** e mantém o estado + workspace.
- Você se conecta do seu laptop ou telefone pela **Control UI** ou por **Tailscale/SSH**.
- Trate a VPS como a fonte da verdade e faça **backup** do estado + workspace regularmente.
- Padrão seguro: mantenha o Gateway em loopback e acesse-o por túnel SSH ou Tailscale Serve.
  Se você vinculá-lo a `lan` ou `tailnet`, exija `gateway.auth.token` ou `gateway.auth.password`.

Páginas relacionadas: [Acesso remoto ao Gateway](/pt-BR/gateway/remote), [Central de plataformas](/pt-BR/platforms).

## Agente compartilhado da empresa em uma VPS

Executar um único agente para uma equipe é uma configuração válida quando todos os usuários estão no mesmo limite de confiança e o agente é usado apenas para negócios.

- Mantenha-o em um runtime dedicado (VPS/VM/contêiner + usuário/contas de SO dedicados).
- Não conecte esse runtime a contas pessoais Apple/Google nem a perfis pessoais de navegador/gerenciador de senhas.
- Se os usuários forem adversariais entre si, separe por gateway/host/usuário de SO.

Detalhes do modelo de segurança: [Segurança](/pt-BR/gateway/security).

## Usando nodes com uma VPS

Você pode manter o Gateway na nuvem e parear **nodes** nos seus dispositivos locais
(Mac/iOS/Android/headless). Nodes fornecem recursos locais de tela/câmera/canvas e `system.run`
enquanto o Gateway permanece na nuvem.

Documentação: [Nodes](/pt-BR/nodes), [CLI de Nodes](/cli/nodes).

## Ajuste fino de inicialização para VMs pequenas e hosts ARM

Se os comandos da CLI parecerem lentos em VMs de baixa potência (ou hosts ARM), habilite o cache de compilação de módulos do Node:

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

- `NODE_COMPILE_CACHE` melhora os tempos de inicialização de comandos repetidos.
- `OPENCLAW_NO_RESPAWN=1` evita sobrecarga extra na inicialização causada por um caminho de auto-reinicialização.
- A primeira execução de comando aquece o cache; as execuções seguintes ficam mais rápidas.
- Para detalhes específicos do Raspberry Pi, consulte [Raspberry Pi](/pt-BR/install/raspberry-pi).

### Checklist de ajuste fino do systemd (opcional)

Para hosts de VM que usam `systemd`, considere:

- Adicionar variáveis de ambiente ao serviço para um caminho de inicialização estável:
  - `OPENCLAW_NO_RESPAWN=1`
  - `NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache`
- Manter o comportamento de reinício explícito:
  - `Restart=always`
  - `RestartSec=2`
  - `TimeoutStartSec=90`
- Prefira discos com SSD para caminhos de estado/cache para reduzir penalidades de cold start por E/S aleatória.

Para o caminho padrão `openclaw onboard --install-daemon`, edite a unit de usuário:

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

Se você instalou deliberadamente uma unit de sistema, edite
`openclaw-gateway.service` com `sudo systemctl edit openclaw-gateway.service`.

Como as políticas `Restart=` ajudam na recuperação automatizada:
[systemd pode automatizar a recuperação de serviços](https://www.redhat.com/en/blog/systemd-automate-recovery).
