---
summary: "Запустить OpenClaw Gateway в режиме 24/7 на виртуальной машине Azure Linux с устойчивым состоянием"
read_when:
  - Вам нужно, чтобы OpenClaw работал в режиме 24/7 в Azure с усиленной защитой группы безопасности сети (NSG)
  - Вам нужен OpenClaw Gateway промышленного уровня, работающий постоянно, на вашей собственной виртуальной машине Azure Linux
  - Вам нужно безопасное администрирование с использованием Azure Bastion SSH
title: "Azure"
---

# OpenClaw на виртуальной машине Azure Linux

Это руководство описывает настройку виртуальной машины Azure Linux с помощью Azure CLI, применение усиленной защиты группы безопасности сети (NSG), настройку Azure Bastion для доступа по SSH и установку OpenClaw.

## Что вы сделаете

- Создадите сетевые ресурсы Azure (VNet, подсети, NSG) и вычислительные ресурсы с помощью Azure CLI
- Примените правила группы безопасности сети, чтобы доступ по SSH к виртуальной машине был разрешён только через Azure Bastion
- Используете Azure Bastion для доступа по SSH (без публичного IP-адреса на виртуальной машине)
- Установите OpenClaw с помощью скрипта установки
- Проверите работу шлюза

## Что вам понадобится

- Подписка Azure с правами на создание вычислительных и сетевых ресурсов
- Установленный Azure CLI (при необходимости см. [инструкции по установке Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli))
- Пара ключей SSH (в руководстве описано, как сгенерировать их при необходимости)
- Около 20–30 минут

## Настройка развёртывания

<Steps>
  <Step title="Войдите в Azure CLI">
    ```bash
    az login
    az extension add -n ssh
    ```

    Расширение `ssh` необходимо для нативного туннелирования SSH через Azure Bastion.

  </Step>

  <Step title="Зарегистрируйте необходимые поставщики ресурсов (однократно)">
    ```bash
    az provider register --namespace Microsoft.Compute
    az provider register --namespace Microsoft.Network
    ```

    Проверьте регистрацию. Дождитесь, пока оба показателя не покажут `Registered`.

    ```bash
    az provider show --namespace Microsoft.Compute --query registrationState -o tsv
    az provider show --namespace Microsoft.Network --query registrationState -o tsv
    ```

  </Step>

  <Step title="Задайте переменные развёртывания">
    ```bash
    RG="rg-openclaw"
    LOCATION="westus2"
    VNET_NAME="vnet-openclaw"
    VNET_PREFIX="10.40.0.0/16"
    VM_SUBNET_NAME="snet-openclaw-vm"
    VM_SUBNET_PREFIX="10.40.2.0/24"
    BASTION_SUBNET_PREFIX="10.40.1.0/26"
    NSG_NAME="nsg-openclaw-vm"
    VM_NAME="vm-openclaw"
    ADMIN_USERNAME="openclaw"
    BASTION_NAME="bas-openclaw"
    BASTION_PIP_NAME="pip-openclaw-bastion"
    ```

    Измените имена и диапазоны CIDR в соответствии с вашей средой. Подсеть Bastion должна быть как минимум `/26`.

  </Step>

  <Step title="Выберите ключ SSH">
    Используйте существующий открытый ключ, если он у вас есть:

    ```bash
    SSH_PUB_KEY="$(cat ~/.ssh/id_ed25519.pub)"
    ```

    Если у вас ещё нет ключа SSH, сгенерируйте его:

    ```bash
    ssh-keygen -t ed25519 -a 100 -f ~/.ssh/id_ed25519 -C "you@example.com"
    SSH_PUB_KEY="$(cat ~/.ssh/id_ed25519.pub)"
    ```

  </Step>

  <Step title="Выберите размер виртуальной машины и размер диска ОС">
    ```bash
    VM_SIZE="Standard_B2as_v2"
    OS_DISK_SIZE_GB=64
    ```

    Выберите размер виртуальной машины и размер диска ОС, доступные в вашей подписке и регионе:

    - Для небольшого объёма использования начните с меньшего размера и затем увеличьте его
    - Используйте больше виртуальных ЦП, ОЗУ и дискового пространства для более интенсивной автоматизации, большего количества каналов или более крупных рабочих нагрузок с моделями/инструментами
    - Если размер виртуальной машины недоступен в вашем регионе или по квоте подписки, выберите ближайший доступный SKU

    Выведите список размеров виртуальных машин, доступных в целевом регионе:

    ```bash
    az vm list-skus --location "${LOCATION}" --resource-type virtualMachines -o table
    ```

    Проверьте текущее использование и квоту виртуальных ЦП и диска:

    ```bash
    az vm list-usage --location "${LOCATION}" -o table
    ```

  </Step>
</Steps>

## Развёртывание ресурсов Azure

<Steps>
  <Step title="Создайте группу ресурсов">
    ```bash
    az group create -n "${RG}" -l "${LOCATION}"
    ```
  </Step>

  <Step title="Создайте группу безопасности сети">
    Создайте NSG и добавьте правила, чтобы только подсеть Bastion могла подключаться к виртуальной машине по SSH.

    ```bash
    az network nsg create \
      -g "${RG}" -n "${NSG_NAME}" -l "${LOCATION}"

    # Разрешить SSH только из подсети Bastion
    az network nsg rule create \
      -g "${RG}" --nsg-name "${NSG_NAME}" \
      -n AllowSshFromBastionSubnet --priority 100 \
      --access Allow --direction Inbound --protocol Tcp \
      --source-address-prefixes "${BASTION_SUBNET_PREFIX}" \
      --destination-port-ranges 22

    # Запретить SSH из публичного интернета
    az network nsg rule create \
      -g "${RG}" --nsg-name "${NSG_NAME}" \
      -n DenyInternetSsh --priority 110 \
      --access Deny --direction Inbound --protocol Tcp \
      --source-address-prefixes Internet \
      --destination-port-ranges 22

    # Запретить SSH из других источников в VNet
    az network nsg rule create \
      -g "${RG}" --nsg-name "${NSG_NAME}" \
      -n DenyVnetSsh --priority 120 \
      --access Deny --direction Inbound --protocol Tcp \
      --source-address-prefixes VirtualNetwork \
      --destination-port-ranges 22
    ```

    Правила оцениваются по приоритету (сначала с наименьшим числом): трафик Bastion разрешён на уровне 100, затем весь другой SSH заблокирован на уровнях 110 и 120.

  </Step>

  <Step title="Создайте виртуальную сеть и подсети">
    Создайте VNet с подсетью виртуальной машины (с присоединённой NSG), затем добавьте подсеть Bastion.

    ```bash
    az network vnet create \
      -g "${RG}" -n "${VNET_NAME}" -l "${LOCATION}" \
      --address-prefixes "${VNET_PREFIX}" \
      --subnet-name "${VM_SUBNET_NAME}" \
      --subnet-prefixes "${VM_SUBNET_PREFIX}"

    # Прикрепить NSG к подсети виртуальной машины
    az network vnet subnet update \
      -g "${RG}" --vnet-name "${VNET_NAME}" \
      -n "${VM_SUBNET_NAME}" --nsg "${NSG_NAME}"

    # AzureBastionSubnet — имя требуется Azure
    az network vnet subnet create \
      -g "${RG}" --vnet-name "${VNET_NAME}" \
      -n AzureBastionSubnet \
      --address-prefixes "${BASTION_SUBNET_PREFIX}"
    ```

  </Step>

  <Step title="Создайте виртуальную машину">
    У виртуальной машины нет публичного IP-адреса. Доступ по SSH осуществляется исключительно через Azure Bastion.

    ```bash
    az vm create \
      -g "${RG}" -n "${VM_NAME}" -l "${LOCATION}" \
      --image "Canonical:ubuntu-24_04-lts:server:latest" \
      --size "${VM_SIZE}" \
      --os-disk-size-gb "${OS_DISK_SIZE_GB}" \
      --storage-sku StandardSSD_LRS \
      --admin-username "${ADMIN_USERNAME}" \
      --ssh-key-values "${SSH_PUB_KEY}" \
      --vnet-name "${VNET_NAME}" \
      --subnet "${VM_SUBNET_NAME}" \
      --public