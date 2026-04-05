---
read_when:
    - Kubernetes 클러스터에서 OpenClaw를 실행하려는 경우
    - Kubernetes 환경에서 OpenClaw를 테스트하려는 경우
summary: Kustomize로 Kubernetes 클러스터에 OpenClaw Gateway 배포
title: Kubernetes
x-i18n:
    generated_at: "2026-04-05T12:46:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: aa39127de5a5571f117db3a1bfefd5815b5e6b594cc1df553e30fda882b2a408
    source_path: install/kubernetes.md
    workflow: 15
---

# Kubernetes에서 OpenClaw 실행

Kubernetes에서 OpenClaw를 실행하기 위한 최소 시작점입니다. 프로덕션 준비가 완료된 배포는 아니며, 핵심 리소스만 다루고 있고 환경에 맞게 조정하는 것을 전제로 합니다.

## 왜 Helm이 아닌가요?

OpenClaw는 일부 config 파일이 포함된 단일 컨테이너입니다. 흥미로운 사용자 지정 지점은 인프라 템플릿이 아니라 agent 콘텐츠(markdown 파일, Skills, config overrides)에 있습니다. Kustomize는 Helm chart의 오버헤드 없이 overlays를 처리합니다. 배포가 더 복잡해지면 이 manifests 위에 Helm chart를 얹을 수 있습니다.

## 필요한 것

- 실행 중인 Kubernetes 클러스터(AKS, EKS, GKE, k3s, kind, OpenShift 등)
- 클러스터에 연결된 `kubectl`
- 최소 하나의 모델 provider용 API 키

## 빠른 시작

```bash
# provider를 선택해 교체: ANTHROPIC, GEMINI, OPENAI 또는 OPENROUTER
export <PROVIDER>_API_KEY="..."
./scripts/k8s/deploy.sh

kubectl port-forward svc/openclaw 18789:18789 -n openclaw
open http://localhost:18789
```

Control UI용으로 구성된 shared secret을 가져옵니다. 이 deploy 스크립트는 기본적으로 token auth를 생성합니다.

```bash
kubectl get secret openclaw-secrets -n openclaw -o jsonpath='{.data.OPENCLAW_GATEWAY_TOKEN}' | base64 -d
```

로컬 디버깅용으로는 `./scripts/k8s/deploy.sh --show-token`이 배포 후 토큰을 출력합니다.

## Kind를 사용한 로컬 테스트

클러스터가 없다면 [Kind](https://kind.sigs.k8s.io/)로 로컬에 생성할 수 있습니다.

```bash
./scripts/k8s/create-kind.sh           # docker 또는 podman 자동 감지
./scripts/k8s/create-kind.sh --delete  # 정리
```

그런 다음 평소처럼 `./scripts/k8s/deploy.sh`로 배포하세요.

## 단계별 설명

### 1) 배포

**옵션 A** — 환경 변수에 API 키 설정(한 단계):

```bash
# provider를 선택해 교체: ANTHROPIC, GEMINI, OPENAI 또는 OPENROUTER
export <PROVIDER>_API_KEY="..."
./scripts/k8s/deploy.sh
```

이 스크립트는 API 키와 자동 생성된 gateway 토큰이 포함된 Kubernetes Secret을 만든 뒤 배포합니다. Secret이 이미 존재하면 현재 gateway 토큰과 변경하지 않는 provider 키는 유지합니다.

**옵션 B** — Secret을 따로 생성:

```bash
export <PROVIDER>_API_KEY="..."
./scripts/k8s/deploy.sh --create-secret
./scripts/k8s/deploy.sh
```

로컬 테스트용으로 토큰을 stdout에 출력하려면 어느 명령이든 `--show-token`을 사용하세요.

### 2) gateway 접근

```bash
kubectl port-forward svc/openclaw 18789:18789 -n openclaw
open http://localhost:18789
```

## 무엇이 배포되는가

```
Namespace: openclaw (OPENCLAW_NAMESPACE로 구성 가능)
├── Deployment/openclaw        # 단일 pod, init container + gateway
├── Service/openclaw           # 18789 포트의 ClusterIP
├── PersistentVolumeClaim      # agent 상태 및 config용 10Gi
├── ConfigMap/openclaw-config  # openclaw.json + AGENTS.md
└── Secret/openclaw-secrets    # Gateway 토큰 + API 키
```

## 사용자 지정

### 에이전트 지침

`scripts/k8s/manifests/configmap.yaml`의 `AGENTS.md`를 편집하고 다시 배포하세요.

```bash
./scripts/k8s/deploy.sh
```

### Gateway config

`scripts/k8s/manifests/configmap.yaml`의 `openclaw.json`을 편집하세요. 전체 참조는 [Gateway 구성](/gateway/configuration)을 참조하세요.

### Providers 추가

추가 키를 export한 상태로 다시 실행하세요.

```bash
export ANTHROPIC_API_KEY="..."
export OPENAI_API_KEY="..."
./scripts/k8s/deploy.sh --create-secret
./scripts/k8s/deploy.sh
```

기존 provider 키는 덮어쓰지 않는 한 Secret에 그대로 남아 있습니다.

또는 Secret을 직접 patch하세요.

```bash
kubectl patch secret openclaw-secrets -n openclaw \
  -p '{"stringData":{"<PROVIDER>_API_KEY":"..."}}'
kubectl rollout restart deployment/openclaw -n openclaw
```

### 사용자 지정 namespace

```bash
OPENCLAW_NAMESPACE=my-namespace ./scripts/k8s/deploy.sh
```

### 사용자 지정 이미지

`scripts/k8s/manifests/deployment.yaml`의 `image` 필드를 편집하세요.

```yaml
image: ghcr.io/openclaw/openclaw:latest # 또는 https://github.com/openclaw/openclaw/releases 의 특정 버전으로 고정
```

### port-forward를 넘어서 노출하기

기본 manifests는 pod 내부에서 gateway를 loopback에 바인딩합니다. 이는 `kubectl port-forward`에는 작동하지만, pod IP에 도달해야 하는 Kubernetes `Service` 또는 Ingress 경로에는 작동하지 않습니다.

Ingress 또는 load balancer를 통해 gateway를 노출하려면:

- `scripts/k8s/manifests/configmap.yaml`에서 gateway bind를 `loopback`에서 배포 모델에 맞는 non-loopback bind로 변경
- gateway auth를 계속 활성화하고 적절한 TLS 종료 진입점을 사용
- 지원되는 웹 보안 모델(예: HTTPS/Tailscale Serve 및 필요 시 명시적 허용 origin 설정)로 Control UI의 원격 접근 구성

## 재배포

```bash
./scripts/k8s/deploy.sh
```

이렇게 하면 모든 manifests가 적용되고 pod가 재시작되어 config 또는 secret 변경 사항을 반영합니다.

## 정리

```bash
./scripts/k8s/deploy.sh --delete
```

이 명령은 PVC를 포함해 namespace와 그 안의 모든 리소스를 삭제합니다.

## 아키텍처 참고

- gateway는 기본적으로 pod 내부에서 loopback에 바인딩되므로, 포함된 설정은 `kubectl port-forward`용입니다
- 클러스터 범위 리소스는 없으며 모든 것이 단일 namespace에 존재합니다
- 보안: `readOnlyRootFilesystem`, `drop: ALL` capabilities, non-root 사용자(UID 1000)
- 기본 config는 Control UI를 더 안전한 로컬 액세스 경로에 유지합니다: loopback bind + `kubectl port-forward`를 통한 `http://127.0.0.1:18789`
- localhost 접근을 넘어서려면 지원되는 원격 모델을 사용하세요: HTTPS/Tailscale과 적절한 gateway bind 및 Control UI origin 설정
- Secrets는 임시 디렉터리에서 생성되어 클러스터에 직접 적용됩니다. secret 자료는 리포지토리 체크아웃에 기록되지 않습니다

## 파일 구조

```
scripts/k8s/
├── deploy.sh                   # namespace + secret 생성, kustomize로 배포
├── create-kind.sh              # 로컬 Kind 클러스터(docker/podman 자동 감지)
└── manifests/
    ├── kustomization.yaml      # Kustomize base
    ├── configmap.yaml          # openclaw.json + AGENTS.md
    ├── deployment.yaml         # 보안 강화가 포함된 Pod 사양
    ├── pvc.yaml                # 10Gi 영구 스토리지
    └── service.yaml            # 18789의 ClusterIP
```
