---
read_when:
    - OpenClaw와 함께 Hugging Face Inference를 사용하려는 경우
    - HF 토큰 환경 변수 또는 CLI 인증 선택이 필요한 경우
summary: Hugging Face Inference 설정(인증 + 모델 선택)
title: Hugging Face (Inference)
x-i18n:
    generated_at: "2026-04-05T12:52:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 692d2caffbaf991670260da393c67ae7e6349b9e1e3ed5cb9a514f8a77192e86
    source_path: providers/huggingface.md
    workflow: 15
---

# Hugging Face (Inference)

[Hugging Face Inference Providers](https://huggingface.co/docs/inference-providers)는 단일 라우터 API를 통해 OpenAI 호환 chat completions를 제공합니다. 하나의 토큰으로 많은 모델(DeepSeek, Llama 등)에 접근할 수 있습니다. OpenClaw는 **OpenAI 호환 엔드포인트**(chat completions 전용)를 사용합니다. 텍스트-이미지, 임베딩 또는 음성을 사용하려면 [HF inference clients](https://huggingface.co/docs/api-inference/quicktour)를 직접 사용하세요.

- 제공자: `huggingface`
- 인증: `HUGGINGFACE_HUB_TOKEN` 또는 `HF_TOKEN` (**Make calls to Inference Providers** 권한이 있는 세분화된 토큰)
- API: OpenAI 호환 (`https://router.huggingface.co/v1`)
- 과금: 단일 HF 토큰; [요금](https://huggingface.co/docs/inference-providers/pricing)은 제공자 요율을 따르며 무료 티어가 있습니다.

## 빠른 시작

1. [Hugging Face → Settings → Tokens](https://huggingface.co/settings/tokens/new?ownUserPermissions=inference.serverless.write&tokenType=fineGrained)에서 **Make calls to Inference Providers** 권한이 있는 세분화된 토큰을 만드세요.
2. 온보딩을 실행하고 제공자 드롭다운에서 **Hugging Face**를 선택한 다음, 프롬프트가 표시되면 API 키를 입력하세요:

```bash
openclaw onboard --auth-choice huggingface-api-key
```

3. **기본 Hugging Face 모델** 드롭다운에서 원하는 모델을 선택하세요(유효한 토큰이 있으면 목록이 Inference API에서 로드되고, 그렇지 않으면 내장 목록이 표시됩니다). 선택한 항목은 기본 모델로 저장됩니다.
4. 나중에 설정에서 기본 모델을 지정하거나 변경할 수도 있습니다:

```json5
{
  agents: {
    defaults: {
      model: { primary: "huggingface/deepseek-ai/DeepSeek-R1" },
    },
  },
}
```

## 비대화형 예시

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice huggingface-api-key \
  --huggingface-api-key "$HF_TOKEN"
```

이렇게 하면 `huggingface/deepseek-ai/DeepSeek-R1`이 기본 모델로 설정됩니다.

## 환경 참고

Gateway가 데몬(launchd/systemd)으로 실행되는 경우, `HUGGINGFACE_HUB_TOKEN` 또는 `HF_TOKEN`이
해당 프로세스에서 사용 가능하도록 해야 합니다(예: `~/.openclaw/.env` 또는
`env.shellEnv`를 통해).

## 모델 탐색 및 온보딩 드롭다운

OpenClaw는 **Inference 엔드포인트를 직접 호출**하여 모델을 탐색합니다:

```bash
GET https://router.huggingface.co/v1/models
```

(선택 사항: 전체 목록을 보려면 `Authorization: Bearer $HUGGINGFACE_HUB_TOKEN` 또는 `$HF_TOKEN`을 보내세요. 일부 엔드포인트는 인증 없이 하위 집합만 반환합니다.) 응답은 OpenAI 스타일의 `{ "object": "list", "data": [ { "id": "Qwen/Qwen3-8B", "owned_by": "Qwen", ... }, ... ] }`입니다.

Hugging Face API 키를 설정하면(온보딩, `HUGGINGFACE_HUB_TOKEN` 또는 `HF_TOKEN`을 통해) OpenClaw는 이 GET을 사용해 사용 가능한 chat-completion 모델을 탐색합니다. **대화형 설정** 중에는 토큰을 입력한 뒤 이 목록(또는 요청 실패 시 내장 카탈로그)으로 채워진 **기본 Hugging Face 모델** 드롭다운이 표시됩니다. 런타임(예: Gateway 시작)에는 키가 있으면 OpenClaw가 다시 **GET** `https://router.huggingface.co/v1/models`를 호출해 카탈로그를 새로 고칩니다. 이 목록은 내장 카탈로그(컨텍스트 윈도우 및 비용 같은 메타데이터용)와 병합됩니다. 요청이 실패하거나 키가 설정되지 않은 경우에는 내장 카탈로그만 사용됩니다.

## 모델 이름 및 편집 가능한 옵션

- **API의 이름:** 모델 표시 이름은 API가 `name`, `title` 또는 `display_name`을 반환할 때 **GET /v1/models에서 가져와 채워집니다**. 그렇지 않으면 모델 ID에서 파생됩니다(예: `deepseek-ai/DeepSeek-R1` → “DeepSeek R1”).
- **표시 이름 재정의:** 설정에서 모델별 사용자 지정 레이블을 지정하면 CLI와 UI에 원하는 방식으로 표시할 수 있습니다:

```json5
{
  agents: {
    defaults: {
      models: {
        "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1 (fast)" },
        "huggingface/deepseek-ai/DeepSeek-R1:cheapest": { alias: "DeepSeek R1 (cheap)" },
      },
    },
  },
}
```

- **정책 접미사:** OpenClaw의 번들된 Hugging Face 문서와 도우미는 현재 이 두 접미사를 내장 정책 변형으로 취급합니다:
  - **`:fastest`** — 가장 높은 처리량.
  - **`:cheapest`** — 출력 토큰당 가장 낮은 비용.

  이를 `models.providers.huggingface.models`에 별도 항목으로 추가하거나 접미사를 포함해 `model.primary`를 설정할 수 있습니다. [Inference Provider settings](https://hf.co/settings/inference-providers)에서 기본 제공자 순서를 설정할 수도 있습니다(접미사 없음 = 해당 순서 사용).

- **설정 병합:** `models.providers.huggingface.models`의 기존 항목(예: `models.json` 내)은 설정 병합 시 유지됩니다. 따라서 সেখানে 설정한 사용자 지정 `name`, `alias` 또는 모델 옵션은 보존됩니다.

## 모델 ID 및 설정 예시

모델 참조는 `huggingface/<org>/<model>` 형식(Hub 스타일 ID)을 사용합니다. 아래 목록은 **GET** `https://router.huggingface.co/v1/models`의 결과이며, 카탈로그에는 더 많은 항목이 포함될 수 있습니다.

**예시 ID(추론 엔드포인트 기준):**

| 모델                  | 참조(`huggingface/` 접두사 포함)    |
| --------------------- | ----------------------------------- |
| DeepSeek R1           | `deepseek-ai/DeepSeek-R1`           |
| DeepSeek V3.2         | `deepseek-ai/DeepSeek-V3.2`         |
| Qwen3 8B              | `Qwen/Qwen3-8B`                     |
| Qwen2.5 7B Instruct   | `Qwen/Qwen2.5-7B-Instruct`          |
| Qwen3 32B             | `Qwen/Qwen3-32B`                    |
| Llama 3.3 70B Instruct | `meta-llama/Llama-3.3-70B-Instruct` |
| Llama 3.1 8B Instruct | `meta-llama/Llama-3.1-8B-Instruct`  |
| GPT-OSS 120B          | `openai/gpt-oss-120b`               |
| GLM 4.7               | `zai-org/GLM-4.7`                   |
| Kimi K2.5             | `moonshotai/Kimi-K2.5`              |

모델 ID 뒤에 `:fastest` 또는 `:cheapest`를 붙일 수 있습니다. [Inference Provider settings](https://hf.co/settings/inference-providers)에서 기본 순서를 설정하세요. 전체 목록은 [Inference Providers](https://huggingface.co/docs/inference-providers)와 **GET** `https://router.huggingface.co/v1/models`를 참고하세요.

### 전체 설정 예시

**기본 DeepSeek R1, 폴백으로 Qwen 사용:**

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "huggingface/deepseek-ai/DeepSeek-R1",
        fallbacks: ["huggingface/Qwen/Qwen3-8B"],
      },
      models: {
        "huggingface/deepseek-ai/DeepSeek-R1": { alias: "DeepSeek R1" },
        "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
      },
    },
  },
}
```

**기본값으로 Qwen 사용, `:cheapest` 및 `:fastest` 변형 포함:**

```json5
{
  agents: {
    defaults: {
      model: { primary: "huggingface/Qwen/Qwen3-8B" },
      models: {
        "huggingface/Qwen/Qwen3-8B": { alias: "Qwen3 8B" },
        "huggingface/Qwen/Qwen3-8B:cheapest": { alias: "Qwen3 8B (cheapest)" },
        "huggingface/Qwen/Qwen3-8B:fastest": { alias: "Qwen3 8B (fastest)" },
      },
    },
  },
}
```

**별칭과 함께 DeepSeek + Llama + GPT-OSS 사용:**

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "huggingface/deepseek-ai/DeepSeek-V3.2",
        fallbacks: [
          "huggingface/meta-llama/Llama-3.3-70B-Instruct",
          "huggingface/openai/gpt-oss-120b",
        ],
      },
      models: {
        "huggingface/deepseek-ai/DeepSeek-V3.2": { alias: "DeepSeek V3.2" },
        "huggingface/meta-llama/Llama-3.3-70B-Instruct": { alias: "Llama 3.3 70B" },
        "huggingface/openai/gpt-oss-120b": { alias: "GPT-OSS 120B" },
      },
    },
  },
}
```

**정책 접미사가 있는 여러 Qwen 및 DeepSeek 모델:**

```json5
{
  agents: {
    defaults: {
      model: { primary: "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest" },
      models: {
        "huggingface/Qwen/Qwen2.5-7B-Instruct": { alias: "Qwen2.5 7B" },
        "huggingface/Qwen/Qwen2.5-7B-Instruct:cheapest": { alias: "Qwen2.5 7B (cheap)" },
        "huggingface/deepseek-ai/DeepSeek-R1:fastest": { alias: "DeepSeek R1 (fast)" },
        "huggingface/meta-llama/Llama-3.1-8B-Instruct": { alias: "Llama 3.1 8B" },
      },
    },
  },
}
```
