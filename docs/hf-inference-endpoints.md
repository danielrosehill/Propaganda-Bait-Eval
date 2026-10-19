# Running models no provider serves: HF Inference Endpoints (verified 2026-10-19)

The Russian and Gulf models (YandexGPT, GigaChat, ALLaM, Falcon, Jais) have open
weights on Hugging Face, but no Inference Provider serves them. They are also absent
from OpenRouter, and their public HF Spaces were broken on 2026-10-19. The working
route is a dedicated Inference Endpoint per model: create it, run the prompts,
delete it. The Chinese models (DeepSeek, GLM, Kimi) don't need this. They are live
on the HF router (`https://router.huggingface.co/v1/chat/completions`) with
`HF_TOKEN`.

Check whether a repo has a live provider:
`GET https://huggingface.co/api/models?author=<org>&expand[]=inferenceProviderMapping`.

## Recipe (huggingface_hub 2.2.0, installed in `.venv`)

```python
from huggingface_hub import HfApi
HfApi().create_inference_endpoint(
    "pbe-yandexgpt5-lite", repository="yandex/YandexGPT-5-Lite-8B-instruct",
    framework="pytorch", task="text-generation", accelerator="gpu",
    vendor="aws", region="us-east-1", instance_type="nvidia-l40s", instance_size="x1",
    min_replica=0, max_replica=1, scale_to_zero_timeout=15, type="authenticated",
    custom_image={"vLLM": {"url": "vllm/vllm-openai:v0.23.0", "port": 8000}})
```

Then call `<endpoint url>/v1/chat/completions` with `Authorization: Bearer $HF_TOKEN`.
`pbe/onair.py` reads the URLs from the `EP_YANDEX`, `EP_GIGACHAT` and `EP_ALLAM` env
vars. Delete each endpoint with `HfApi().delete_inference_endpoint(name)` as soon
as its run is done, then confirm with `list_inference_endpoints()`.

## Gotchas hit on the way

- `type="protected"` is rejected ("no longer supported"). Use `"authenticated"`.
- `scale_to_zero_timeout` with `min_replica=1` gives a 400. It is only allowed with
  `min_replica=0`. With 0, the endpoint still starts on creation.
- **The model name is the repo id.** vLLM on Endpoints serves the model as e.g.
  `yandex/YandexGPT-5-Lite-8B-instruct`. Sending `"model": "/repository"` (the
  mount path, shown as `root` in `/v1/models`) returns a **404**, which looks
  exactly like a bad route. Check `GET /v1/models` first.
- **GigaChat 3.1 (`DeepseekV3ForCausalLM`) fails to boot on `vllm-openai:v0.23.0`.**
  The newer transformers config dataclasses are strict, and the repo's
  `config.json` has `routed_scaling_factor: 1` (an int):
  `StrictDataclassFieldValidationError: Field 'routed_scaling_factor' expected float, got int`.
  It booted on **`vllm/vllm-openai:v0.11.0`**. Switch with
  `update_inference_endpoint(name, custom_image=...)`.
- ALLaM 7B comes up with `max_model_len` 4096, so keep `max_tokens` plus the prompt
  under that.
- The HF router returned 429 for DeepSeek under eight parallel requests.
  `onair.py` backs off (10, 30 and 60 seconds) and retries.

## Cost

Three L40S x1 endpoints at about $1.80 per hour each: about 25 minutes for Yandex
and ALLaM, and about 35 minutes for GigaChat including the failed first boot.
Roughly $2–3 in total. Estimated from list price, not read from the bill.
